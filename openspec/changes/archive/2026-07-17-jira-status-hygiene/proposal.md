## Why

The `psplit.atlassian.net` Jira instance carries **749 distinct status records** with 569 (76%) being duplicates. A migration in mid-April 2026 created a fresh "To Do" and "In Progress" record per team-managed project instead of referencing canonical ones, leaving the instance with 102 "To Do" records, 101 "In Progress" records, and 100 "Done" records. Cross-project JQL filters, dashboards, and saved filters break because "Done" is a different record ID per project. The goal is to collapse 749 records to ≤ 50 by eliminating duplicate clusters, fixing categorically mis-labeled records, and aliasing one-off project-private names to canonical equivalents.

## What Changes

- **New `canonical_statuses.yaml`** taxonomy in `tdt-meta` with 14 next-gen and 8 company-managed canonical statuses and their case-insensitive aliases.
- **New `status_registry` Google Sheet** with 5 tabs: `status_catalog` (749 rows), `project_manifest` (~200 rows), `merge_log`, `dedupe_log`, and `signoff_log`.
- **New `jira-skill status` CLI subcommand group** in `jira-skill`: `audit`, `diff`, `merge`, `dedupe`, `classify-singletons`, `preflight`, `render-sheet`, `standardize`.
- **New `tdt_core.clients.jira_workflow` module** in `tdt-core`: `WorkflowClient` extensions with team-managed and company-managed handlers.
- **Instance-wide `jira-skill status dedupe`** command that collapses the 47 duplicate clusters (569 records) into canonical targets, plus classifies and resolves 180 singleton records.
- **Daily DBOS audit workflow** (`jira-status-audit`, 07:00 UTC) that monitors for new divergence and alerts.
- **`setup-project` preflight integration** that runs `status preflight` automatically when setting up a new project.

## Capabilities

### New Capabilities

- `jira-status-taxonomy`: The canonical status taxonomy YAML defining the 14 next-gen statuses (Draft, To Do, In Progress, Code Review, API Review, FE/QA Review, PM Review, Deploy in DEV, Deploy to Sandbox, SIT, Test Done, Ready, Rejected/Duplicated, Done) and 8 company-managed statuses, with per-entry aliases and category mapping (`new`/`indeterminate`/`done`).
- `jira-status-registry-sheet`: The Google Sheet schema for `status_registry` — 5 tabs with the full column contract for `status_catalog`, `project_manifest`, `merge_log`, `dedupe_log`, and `signoff_log`.
- `jira-status-cli`: The `jira-skill status` CLI subcommand group with 8 commands covering audit, diff, merge, dedupe, singleton classification, preflight, sheet rendering, and batch standardize.
- `jira-workflow-client-extensions`: `tdt_core.clients.jira_workflow` with `TeamManagedWorkflowHandler` (per-project workflow via `PUT /rest/api/3/project/{key}/workflow`) and `CompanyManagedWorkflowHandler` (global workflow schemes via `POST /rest/api/3/workflow` and scheme assignment). Both support `bulk_transition`, `rename_status`, `add_status`, `delete_status`, and style-specific dedupe primitives.
- `jira-status-dedupe`: The `jira-skill status dedupe` command that reads the `status_catalog`, selects canonical targets deterministically (`max(used_by_projects), min(jira_id)`), bulk-transitions all issues from duplicate losers to winners, fixes category mis-labels, aliases singleton records, and writes one row per cluster to `dedupe_log`.

### Modified Capabilities

- `jira-workflow-validator` (existing): The workflow-validator spec is about transition validators, not status records. No requirement conflict; both operate at the workflow level but on different dimensions (transition rules vs. status record identity).

## Impact

- **Code**:
  - `tdt-meta/canonical_statuses.yaml` — new taxonomy file (~200 lines).
  - `jira-skill/src/jira_skill/status/` — new Python module with CLI group, `StatusRegistry`, `StyleHandler` hierarchy, `AuditCommand`, `DedupeCommand`, `MergeCommand`.
  - `tdt-core/src/tdt_core/clients/jira_workflow.py` — new `WorkflowClient` extensions (~250 LOC).
  - `jira-skill/src/jira_skill/schedule.py` — register `jira-status-audit` DBOS scheduled workflow.
  - `jira-skill/tests/status/` — unit tests for all commands and both style handlers.
- **APIs**: No new public APIs. Uses existing `tdt_core.clients.jira`, `tdt-sheets` (`SheetsClient`), and Jira Cloud REST API v3.
- **Dependencies**: `tdt_core.clients.jira` (existing), `tdt-sheets` (`SheetsClient`, `ServiceAccountAuth.from_env()`), `dbos` (existing via `tdt-core[scheduler]`). No new Python packages.
- **Operations**: One new DBOS scheduled workflow (`jira-status-audit`, daily 07:00 UTC). Sheet is managed by `tdt-sheets` (existing auth fallback). `--global-confirm` required for production dedupe; `--dry-run` available for preflight.
- **Non-Goals**: No cross-project ID unification for team-managed projects (impossible by design). No workflow transition changes. No historical issue re-classification. No rollback or fallback paths.
