## Context

The `psplit.atlassian.net` Jira instance has **749 status records** — a number that has grown organically without governance. A migration in mid-April 2026 (evidence: ~50% of "To Do" records carry `"(Migrated on 14-16 Apr 2026 HH:MM UTC)"` descriptions) created a fresh status record per team-managed project creation or template fork, instead of referencing existing canonical ones. The result:

- **47 duplicate clusters** holding 569 records (76% of the catalog).
- The worst three clusters: 102 "To Do" records, 101 "In Progress", 100 "Done".
- **180 singleton records** — unique names with no partner. Of those: ~25 are categorically mis-labeled (wrong `new`/`indeterminate`/`done` assignment), ~105 are one-offs aliased to canonical, ~10 are genuinely project-private kept by exception, ~40 are garbage.
- Cross-project JQL filters, dashboards, and saved filters break because "Done" is a different numeric ID on every team-managed project.

**Stakeholders**: Jira instance admin (owns the canonical taxonomy), project admins (own their project's status set), the hygiene agent (automated auditor).

**Constraints**: Team-managed status records are project-private (cannot be shared across projects). Company-managed statuses are global (can be shared across all company-managed projects). These are enforced by Jira's data model — not a constraint we can change.

## Goals / Non-Goals

**Goals:**

- Collapse the active status catalog from 749 records to ≤ 50.
- Eliminate all 47 duplicate clusters (at most 1 record per (name, category) pair per project for team-managed; at most 1 globally for company-managed).
- Classify and resolve all 180 singleton records into canonical, mis-labeled, project-private, or garbage buckets.
- Give every project on the instance a `project_manifest` row with a final `merge_status`.
- Establish daily automated audit that detects new divergence within 24 hours.

**Non-Goals:**

- Cross-project ID unification for team-managed projects (impossible by design — team-managed status records are project-private).
- Workflow *transition* changes (only status record identity is in scope; existing transitions are preserved).
- Schema migration of historical issues (no `status` field rewrite of closed issues).
- UI work in Jira (no dashboards, no JQL changes beyond the standard taxonomy).
- Rollback or fallback paths for failed operations (operation-only posture: fix and retry).
- Compatibility mode for old JQL queries that reference old status IDs.

## Decisions

### Decision 1: Taxonomy lives in code (YAML), not in the Sheet

The canonical status list is **PR-reviewable** and **version-controlled**. It lives at `tdt-meta/canonical_statuses.yaml` alongside other canonical references. The Sheet (`status_catalog` tab) is the live, mutable mirror — it tracks every instance record with its Jira ID, `canonical_key` pointer, `duplicate_cluster_id`, etc.

**Alternative considered**: Store the taxonomy in the Sheet itself (first tab as "Taxonomy"). **Rejected** because Sheet formulas and human edits make it hard to PR-review; version history in Sheets is inferior to git; the taxonomy is a stable contract that should be code, not spreadsheet.

### Decision 2: Canonical target selection is deterministic, not human-chosen

For each duplicate cluster, the record that survives (`is_canonical_target=true`) is chosen by **`max(used_by_projects), min(jira_id)`** — the record currently referenced by the most projects wins; ties broken by lowest Jira ID.

**Alternative considered**: Human chooses the canonical target per cluster via a decision column in the Sheet. **Rejected** because it creates 47 decision points that all follow the same rule anyway; the rule is reproducible and requires no human judgment for standard cases.

### Decision 3: Cluster identification is a Sheet concern; transition execution is a handler concern

The `status_catalog` Sheet holds `duplicate_cluster_id` (UUID per cluster), `cluster_size`, and `is_canonical_target`. The CLI reads the Sheet to build the dedupe plan. The `StyleHandler` implementations only execute transitions (`bulk_transition`, `rename_status`, `add_status`, `delete_status`).

**Alternative considered**: Have the handler discover clusters by querying Jira directly. **Rejected** because cluster identification requires matching against canonical aliases (case-insensitive), which is a YAML concern; mixing it into the handler blurs the layer contract and makes testing harder.

### Decision 4: Two `StyleHandler` implementations, not one

`TeamManagedWorkflowHandler` uses `GET/PUT /rest/api/3/project/{key}/workflow` — per-project, project-private status records. `CompanyManagedWorkflowHandler` uses `POST /rest/api/3/workflow` + scheme operations — global status records, shared across company-managed projects.

The dedupe semantics differ fundamentally: team-managed collapses N records within one project; company-managed collapses N records that affect every project using them simultaneously.

**Alternative considered**: One handler that dispatches on project style at runtime. **Rejected** because the API surfaces are completely different (one uses workflow payloads, the other uses scheme assignment); keeping them separate makes the implementation and testing surface cleaner.

### Decision 5: Sheet has 6 tabs, not 5 (split merge_log from dedupe_log)

`merge_log` records individual Jira operations (one per `bulk_transition`, `rename_status`, etc.). `dedupe_log` records cluster-level summaries (one per duplicate cluster deduped). Both are append-only.

**Alternative considered**: Single `operation_log` tab. **Rejected** because the two log types have different primary keys and different consumers: `merge_log` is for per-project audit trails, `dedupe_log` is for instance-level dedupe confirmation.

## Risks / Trade-offs

- **[Risk] Bulk transition during active sprint**: Bulk-transitioning hundreds of issues during an active sprint could disrupt team workflow.
  - **Mitigation**: `--dry-run` is mandatory before any production merge. Projects mid-active-sprint are excluded from the initial batch via `--exclude-projects`. The dedupe phase can be scheduled for a low-activity window.

- **[Risk] Rate limiting on bulk transitions**: Jira Cloud limits bulk transitions; 429 responses will abort the operation.
  - **Mitigation**: The handler implements 3 retries with 60s back-off before aborting. Partial success is logged with failed issue keys. The human operator resumes manually.

- **[Risk] Team-managed vs. company-managed misclassification**: Some projects may be misidentified as one style when they are actually the other.
  - **Mitigation**: `jira-skill status audit` reads the project's `style` from `project_manifest` (curated in the Sheet). The CLI falls back to `GET /rest/api/3/project/{key}` to confirm `projectTypeKey`.

- **[Risk] Sheet write failure mid-dedupe**: If `tdt-sheets` write fails, the Jira operation has already happened.
  - **Mitigation**: Every Jira API call that changes state writes a log entry *before* executing. If the process dies, the `merge_log` entry is marked `incomplete`. The human operator reviews and resumes or skips. Sheet auth has 3-level fallback (SA → ADC → key file); if all fail, abort and retry after auth fix.

- **[Risk] Category mis-label on live issues**: A status record like `id= 12841 'In Progress' cat=new` means some issues are in a `new` category status that should be `indeterminate`.
  - **Mitigation**: We fix the *record's* category metadata only, not the issues' `status` field. The issue still holds the status record — the record's category is a display concern. This is safe and does not re-classify any issue.

- **[Risk] The 8 CFD-family classic projects**: These are company-managed with 8 statuses each. Company-managed dedupe is global — collapsing a global "Done" affects all company-managed projects simultaneously.
  - **Mitigation**: `dedupe --dry-run` previews the global impact before `--global-confirm`. Project-level `merge` only runs after dedupe is complete and the `project_manifest` reflects the canonical state.

## Migration Plan

Four phases, executed sequentially. Each phase is a single CLI command or set of commands.

**Phase A — Dedupe (instance-wide, single command)**

```bash
# Pre-flight: generate the dedupe plan
jira-skill status dedupe --dry-run --output tabular

# Execute
jira-skill status dedupe --global-confirm
```

Expected outcome: 47 clusters collapsed, catalog drops from 749 to ~274 records (227 singletons + 47 survivors). Writes to `dedupe_log`.

**Phase B — Singleton classification (Sheet curation + apply)**

```bash
# Classify all 180 singletons (outputs proposed classifications to Sheet)
jira-skill status classify-singletons

# Review proposed classifications in Sheet (status_catalog tab, bucket column)
# Human reviews and corrects any mis-classifications
# Then apply:
jira-skill status apply-singleton-classifications --confirm
```

Expected outcome: catalog drops from ~274 to ~50 records.

**Phase C — Manifest sweep (automated)**

```bash
# Regenerate project_manifest for all projects
jira-skill status render-sheet --full

# Review manifest for projects that need merge
# Sign off:
jira-skill status signoff --project PDS --role instance_admin
jira-skill status signoff --project PDS --role project_admin
# ... repeat per project
```

**Phase D — Project-level merges (batch)**

```bash
# 5 Round 3 + 8 CFD-family + DA/STABI as single batch
jira-skill status standardize --projects PDS,PWM,RMD,SR,TJ,CFD,CFDAHP,CFDBO,CFDFO,CFDMO,CFDPRJ,CFDX,DA,STABI --dry-run
jira-skill status standardize --projects PDS,PWM,RMD,SR,TJ,CFD,CFDAHP,CFDBO,CFDFO,CFDMO,CFDPRJ,CFDX,DA,STABI --yes-i-understand-this-is-irreversible
```

Each subsequent batch covers a template group until all 200+ projects are addressed.

## Open Questions

- **Q1**: Should the daily `audit` DBOS workflow *alert* to Slack/Teams, or only write to `audit_log`? (Current design: alert on `newly_diverged > 0` or `fully_standard` dropping below threshold.)
- **Q2**: Should the taxonomy YAML (`canonical_statuses.yaml`) live in `tdt-meta/` or in `tdt-core/`? (`tdt-meta/` is better for PR-review by instance admins who don't own `tdt-core`.)
- **Q3**: For the 180 singleton records, who is the human reviewer for the `decision_note` column? The instance admin or the project admin?
- **Q4**: Should `Clarified` (currently used in company-managed) be added as a canonical next-gen status? (The 180 singleton probe found `Clarified` at `id= 10002` with 0 `used_by_projects` — it's not actively used by any team-managed project.)
