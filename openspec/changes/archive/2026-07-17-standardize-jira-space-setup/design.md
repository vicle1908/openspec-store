# Standardize Jira Space Setup Design

## Context

The TDT workspace already contains multiple partial standards for Jira setup, but they are fragmented across implementation-specific artifacts:

- `jira-skill` provides field comparison/alignment, board creation, filter creation, dashboard validation, and role/permission inspection.
- `tdt-core` provides the required Jira Cloud API v3 transport layer through `JiraClientFactory` and `PatchedJira`.
- Completed OpenSpec changes such as `jira-dashboard-automation`, `jira-ticket-intelligence`, and `jira-person-capacity-planning-alignment` define adjacent expectations for canonical filters, dashboards, and spreadsheet-backed automation inputs.
- Repo-local docs such as `jira-skill/docs/cross-project-workflow-alignment.md` and `jira-skill/docs/board-ecosystem-alignment-spec.md` capture useful standards, but they are not yet expressed as a single durable OpenSpec capability for onboarding or aligning Jira spaces.

The EW Jira setup research showed that operators repeatedly need the same decisions and checks:

- determine whether the target project is `next-gen` or `classic` before attempting field/screen alignment,
- route the run into a team-managed/modern setup workflow or a classic/legacy setup workflow instead of pretending one apply path fits both,
- verify estimation capability per issue type so required work-item types (`Story`, `Task`, `Bug`, `Subtask`) are validated consistently, using project+issue-type metadata for team-managed spaces rather than classic screen assumptions,
- choose a reference project with matching style and operational intent,
- verify board/filter consistency instead of assuming an existing board is correctly wired,
- create and share canonical filters with stable naming for later automation,
- validate dashboard gadget behavior against live Jira Cloud constraints,
- capture artifact IDs, names, and blocked/unsupported states for future runs.

Latest live `jira-skill`-driven research adds a sharper TMP diagnosis model:

- Jira instance-level evidence can prove that time tracking is enabled globally and that system fields such as `timeoriginalestimate` and `timetracking` exist, without proving that a given team-managed project exposes those fields to required work item types.
- Team-managed project readiness therefore needs a layered inspection model: global field registry, instance configuration, project properties/features, project+issue-type create metadata, and issue edit metadata for representative issues.
- `jira-skill` can already prove the symptom (`createmeta` / project issue-type visibility), but it does not yet emit a first-class diagnosis that distinguishes `field unavailable`, `instance capability disabled`, and `project exposure missing`.
- Current evidence supports a three-way support matrix for TMP setup work:
  - **Supported and implemented now** — read-only metadata inspection (`createmeta`, `editmeta`, field search), board/filter/dashboard validation reads, permission preflight, and setup evidence capture.
  - **Supported by public Jira Cloud APIs but not yet validated in this repo for the target gap** — project feature reads/writes and `PUT /rest/api/3/field/association`.
  - **Still unsupported or not sufficiently exposed for this use case** — a validated public write path that guarantees `Original Estimate` / `Time Tracking` exposure for the required team-managed issue types, plus direct issue-layout control semantics.
- The next valuable automation slice is therefore a dedicated team-managed diagnostic/evidence layer plus validation of the supported-but-unproven write surfaces, not broad new apply behavior.

Additional Atlassian public evidence makes the workflow split explicit rather than merely prudent:

- Team-managed projects are moving toward project-admin-managed field association and issue-layout semantics rather than classic screens.
- Public APIs expose some setup-related write surfaces, but coverage remains incomplete around project field applicability, issue-layout control, and end-to-end proof of required planning-field exposure for TMP issue types.
- Some custom-field context and mapping semantics remain incomplete or project-type-specific, reinforcing that the TMP path must stay detection-first and validation-heavy.

This design therefore standardizes the planning and evidence contract for two distinct setup workflow families that share a common preflight but diverge in control plane and remediation model:

- **Team-managed / modern setup** — detection-first, metadata-driven, API-surface-bound.
- **Classic / legacy setup** — screen/scheme-aware, explicit-alignment-oriented, conditionally automatable.

This change does not replace Jira Cloud limitations, nor does it require every historical project to be fully normalized before future setup work can proceed.

**Target repos / surfaces:**

- `tdt-meta/openspec`: new durable capability and guidance.
- Future implementation work is expected primarily in `jira-skill` and `.agents` Jira skills, with `tdt-core` remaining the shared Jira client layer.

## Goals / Non-Goals

- **Goals:**
-
- Define one canonical Jira space setup workflow for TDT agents and operators.
- Normalize the preflight checks required before any field, board, filter, or dashboard alignment is attempted.
- Standardize the minimum outputs of a setup/alignment run so downstream automation can rely on them.
- Make automation boundaries explicit: what SHALL be done through `jira-skill`/`tdt-core`, and what SHALL remain outside currently supported API surfaces.
- Reuse existing Jira Cloud API v3 patterns and existing completed OpenSpec changes instead of inventing a parallel architecture.

**Non-Goals:**

- Implementing the Jira setup changes themselves in this OpenSpec change.
- Replacing existing project-local docs that serve narrower audiences or historical records.
- Eliminating all unresolved setup states; unsupported project-type, workflow, or gadget operations remain blocked or unsupported where Jira Cloud API behavior is insufficient.
- Converting all current Jira projects to a single workflow or naming scheme in one step.
- Introducing new runtime dependencies or non-`tdt_core` Jira clients.

## Decisions

1. **Create a new capability instead of overloading dashboard or ticket-intelligence specs**
   - Rationale: setup/alignment spans fields, boards, filters, dashboards, permissions, and evidence capture. Existing specs cover downstream capabilities, not the onboarding contract itself.
   - Alternative considered: append requirements into `ticket-intelligence-core` or `jira-dashboard-automation`. Rejected because that would hide setup policy inside adjacent automation capabilities and make operator expectations harder to discover.

2. **Use a workflow-and-evidence standard, not a one-project template**
   - Rationale: EW, SR, PUB, PDS, TJ, and future projects do not share one exact Jira shape. The durable standard should define required decision points and outputs rather than hardcoding one project’s scheme.
   - Alternative considered: define a single canonical project schema. Rejected because `next-gen` and `classic` Jira projects expose materially different field/screen/workflow capabilities.

3. **Project-style detection is a mandatory preflight gate and workflow router**
   - Rationale: EW research showed that comparing a `next-gen` project against a `classic` project without acknowledging style differences creates false parity expectations and tool misuse.
   - Decision: every setup/alignment workflow SHALL identify project style before selecting a reference project or invoking field/screen alignment operations, and SHALL use that style to select the correct setup workflow family (`team-managed` or `classic`).
   - Alternative considered: let each operator infer style ad hoc. Rejected because it caused avoidable ambiguity during live research.

4. **Reference-project selection SHALL be explicit and evidence-backed**
   - Rationale: “make EW similar to other spaces” is too vague without documenting which reference project was chosen and why.
   - Decision: the standard SHALL require operators to record the selected reference project, the reason for choosing it, and any known style or workflow deltas.
   - Alternative considered: rely on implicit nearest-neighbor judgment. Rejected because later automation cannot reconstruct that decision reliably.

5. **Canonical filters are the main durable setup output**
   - Rationale: canonical filters bridge setup work into ticket-intelligence, dashboards, daily reports, and spreadsheet-backed registry workflows.
   - Decision: setup runs SHALL create or validate a stable set of shared filters, with predictable names, JQL, and captured IDs, before claiming a project is automation-ready.
   - Alternative considered: center the standard on boards first. Rejected because boards are often wrappers around filters, and filter correctness is more reusable across consumers.

6. **Estimation readiness SHALL be validated per issue type, not per project only**
   - Rationale: live research across AM, EW, TJ, and PUB showed that estimation support differs by issue type even within the same project, especially for team-managed spaces.
   - Decision: setup evidence SHALL record supported estimation fields and readiness separately for `Story`, `Task`, `Bug`, and `Subtask`, with all four work-item types treated as required by default. For team-managed spaces, the primary automated detection surface SHALL be project+issue-type metadata such as Jira create-metadata rather than classic screen configuration.
   - Alternative considered: use a single project-wide estimation-ready boolean. Rejected because it hides partial readiness and misclassifies projects like EW where some work item types are supported while others are not.

7. **The standard SHALL define two setup workflow families, not one generic apply path**
   - Rationale: Atlassian's public platform model now makes the split durable. Team-managed projects rely on project-scoped field association and issue-layout behavior that public APIs can observe only indirectly, while classic projects still align naturally to screens, tabs, and schemes.
   - Decision: the standard SHALL define a shared preflight followed by two workflow families: `team-managed / modern` setup and `classic / legacy` setup. The team-managed path SHALL be detection-first and API-surface-bound; the classic path SHALL be alignment-oriented and MAY perform explicit screen/tab operations when the required permissions and identifiers are available.
   - Alternative considered: keep a single `setup-project --apply` contract and describe style differences only in notes. Rejected because it overstates automation parity and obscures the real control-plane differences.

8. **Board and dashboard automation SHALL be treated as validation-sensitive layers above filters**
   - Rationale: live Jira Cloud behavior already proved that a board may point at the wrong filter and that gadget configuration writes may not persist.
   - Decision: the standard SHALL require explicit read-back validation for board/filter wiring and SHALL record unsupported or non-persisted dashboard gadget behavior as blocked/unsupported results rather than prescribing human UI action.
   - Alternative considered: assume successful API creation equals valid configuration. Rejected based on EW and dashboard-automation findings.

9. **The standard SHALL preserve blocked or unsupported checkpoints instead of pretending full API coverage exists**
   - Rationale: Jira Cloud still limits project-type conversion, some workflow/status edits, and many gadget/property operations.
   - Decision: the standard records blocked or unsupported operations as first-class evidence, not informal notes, and does not prescribe human UI action as a fallback.

10. **Observability and error handling are evidence outputs, not just implementation details**

- Rationale: setup work often fails because of permissions, unsupported API behavior, or project-shape differences. Operators need concise proof of what was checked and what failed.
- Decision: the standard SHALL require setup reports to capture permission findings, skipped operations, unsupported operations, validation mismatches, and resulting IDs/names.
- Alternative considered: keep logs ephemeral. Rejected because future sessions need durable evidence.

## Risks / Trade-offs

- **[Risk] The standard becomes too abstract to be actionable** → Mitigation: require concrete output artifacts (filters, IDs, validation results, blocked/unsupported states) rather than only principle-level guidance.
- **[Risk] Existing project docs drift from the new OpenSpec capability** → Mitigation: treat the OpenSpec capability as the normative contract and let repo-local docs reference or specialize it.
- **[Risk] Operators may expect full automation after reading the standard** → Mitigation: explicitly separate API-safe automation from blocked or unsupported states in both spec requirements and run outputs.
- **[Risk] Reference-project-driven setup can propagate legacy inconsistencies** → Mitigation: require recording known deltas and validation mismatches instead of claiming blind parity.
- **[Risk] Downstream consumers depend on unstable names or IDs** → Mitigation: require captured naming conventions, filter IDs, board IDs, dashboard IDs, and sharing state as part of the setup evidence contract.

## Implementation Status (verified 2026-06-08)

The execution slice has been wired into `setup-project` via `board/setup_evidence.py` (`SetupEvidenceCollector.build_setup_evidence`). This section is normative execution guidance for implementers so they can distinguish shipped coverage from remaining hardening work without weakening the target contract.

| Standard area | Current status | Notes |
| --- | --- | --- |
| Project-style + permission preflight | WIRED | `setup-project` records style + optional reference project, and runs a permission preflight via `JiraRoleChecker.has_permission` (CREATE_ISSUES, EDIT_ISSUES, CREATE_SHARED_OBJECTS) emitting `permission_preflight` blockers (cli.py:1181-1199). |
| Workflow-family routing | WIRED | `SetupEvidenceCollector.infer_workflow_family` emits a first-class `workflow_family` (`team-managed / modern` vs `classic / legacy`) in evidence and console output. |
| Team-managed estimation/readiness detection | DONE | `FieldConfig.get_estimation_support_by_issue_type()` uses `createmeta` for `next-gen` projects; `estimation-parity` and `setup-project` expose the results and baseline-vs-target messaging. |
| Team-managed required-field validation (`createmeta.required`) | WIRED (read-only) | `FieldConfig.get_required_fields_by_issue_type()` captures Jira REST v3 create-metadata required-field state per issue type. `setup-project` renders this as verification evidence only and does not claim a supported team-managed apply path for toggling Required checkboxes. |
| Team-managed layered diagnosis (`global exists` vs `project exposure missing`) | WIRED | `setup_evidence.py` emits a `tmp_layered_diagnosis` evidence field distinguishing `global_field_exists`, `instance_enabled` (timetracking), and project-exposure gaps per capability (lines 73-87, 402); covered by `tests/test_setup_evidence.py`. |
| Team-managed supported write surfaces (`project features`, `field/association`) | UNVALIDATED HERE | Public Jira Cloud docs expose these APIs, but this repo has not yet proven that they remediate the EW-style `Original Estimate` / `Time Tracking` exposure gap end-to-end for TMP issue types. |
| Team-managed guaranteed field-exposure remediation | UNSUPPORTED / UNPROVEN | There is not yet validated evidence in this repo that the current public API surface guarantees exposure of the required planning fields for the target team-managed issue types without additional hidden layout semantics. |
| Team-managed remediation boundary | DONE (reporting only) | `setup-project --apply` for `next-gen` explicitly refuses unsupported field-write remediation and preserves blocked/unsupported result semantics. |
| Classic alignment semantics | PARTIAL | `FieldConfig` already contains classic screen/tab discovery helpers, but `setup-project` does not yet orchestrate a real guarded classic apply flow. |
| Canonical filter outputs | WIRED | `collect_canonical_filter_candidates` discovers project-scoped filters (id, name, JQL, owner, sharePermissions) and captures them in evidence; rendered in `setup-project` output. |
| Existing board audit | WIRED | `collect_board_audit` discovers all project boards via `rest/agile/1.0/board`, reads each board configuration, and resolves filter wiring (id, name, JQL) per board — replacing the former hard-coded EW board `953` path. |
| Board + dashboard live validation | WIRED | `collect_dashboard_audit` discovers dashboards per audited board and runs `validate_dashboard` read-back, recording ok/mismatch/error rather than skipping. |
| Structured setup evidence output | WIRED | `build_setup_evidence` returns a structured bundle: project/workflow_family, readiness, permission_preflight, board_audit, canonical_filter_candidates, dashboard_audit, and `blocked_or_unsupported_outcomes` produced by `classify_setup_states` using the spec's status taxonomy (`implemented-and-supported`, `supported-but-unvalidated-here`, `unsupported-by-current-api-surface`, `permission-blocked`, `validation-incomplete`). The legacy `manual_follow_up` field has been fully removed. |

Remaining hardening (not blockers): guarded classic apply orchestration is still PARTIAL; the team-managed layered-diagnosis and supported-write-surface rows above remain PARTIAL/UNVALIDATED pending a first-class diagnosis slice and end-to-end remediation proof. `board/setup_evidence.py` now has dedicated unit tests (`tests/test_setup_evidence.py`, passing alongside the `setup-project`/`estimation-parity` CLI tests; ruff + mypy clean as of 2026-06-09). A scratch `tests/_debug_setup_evidence.py` exists in the working tree and SHOULD be removed before archive. These are follow-up items, not spec defects. The requirements remain the target standard and SHALL NOT be downgraded.

## Migration Plan

1. Add a new OpenSpec capability `jira-space-setup-standard` that defines the standardized setup workflow and outputs.
2. Add a delta spec for `ticket-intelligence-core` clarifying that filter metadata captured during setup is a supported upstream input contract.
3. Create tasks that map the capability into concrete documentation and implementation follow-ups for `jira-skill` and `.agents` Jira workflows.
4. Future implementation changes can then reference this capability when adding preflight commands, setup runbooks, or automation wrappers.

## Rollback / safety posture

- The currently shipped execution slice is additive and read-mostly by default: `estimation-parity` is read-only, and `setup-project` defaults to preflight mode. The wired evidence collection (board audit, filter discovery, dashboard validation, permission preflight) performs only GET/read-back calls. For `team-managed / modern` projects, the current `--apply` path performs no unsupported field-write remediation.
- Remaining hardening — guarded classic apply orchestration and dedicated `setup_evidence` unit tests — stays additive. Rollback posture is trivial: do not enable guarded classic apply until validated.
- Future implementation tasks derived from this design SHOULD remain additive and SHOULD preserve existing Jira operator workflows until validated.

## Open Questions

- ~~Should the first implementation surface be a dedicated `jira-skill` command group for setup preflight/evidence capture, or an agent skill/runbook that orchestrates existing commands?~~ **Resolved (apply):** dedicated `jira-skill` CLI commands. `setup-project` (preflight + guarded `--apply`) and `estimation-parity` are the first implementation surface, backed by `FieldConfig.get_estimation_support_by_issue_type` / `check_project_fields`. Agent runbooks orchestrate these commands rather than reimplementing the logic.
- Should canonical filter sets be globally standardized across project families, or should the standard define a minimum required filter taxonomy plus optional project-family extensions? Current design assumes the latter.
- Should setup evidence be persisted only in OpenSpec/change artifacts, or also in a structured registry/sheet for operational discoverability? This remains optional and can be evaluated in implementation.
