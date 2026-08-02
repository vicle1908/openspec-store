# Standardize Jira Space Setup Tasks

## 1. Formalize the shared standard in OpenSpec

- [x] 1.1 Review `tdt-meta/openspec/changes/standardize-jira-space-setup/proposal.md`, `design.md`, and both spec files to confirm the capability boundaries match existing Jira automation surfaces
- [x] 1.2 Validate that `specs/jira-space-setup-standard/spec.md` covers project-style preflight, canonical filters, board/dashboard validation, captured identifiers, and blocked/unsupported outcomes
- [x] 1.3 Validate that `specs/ticket-intelligence-core/spec.md` only adds the intended filter-metadata reuse delta and does not redefine unrelated ticket-intelligence behavior

## 2. Map the standard into implementation surfaces

- [x] 2.1 In `jira-skill`, identify the existing commands/modules that already satisfy parts of the standard (`field_config.py`, `board/*`, `analysis/filter_registry.py`, `user_roles.py`, dashboard workflows) and note the gaps for a future apply phase
- [x] 2.2 In `.agents` Jira/OpenSpec skills, identify where setup guidance should reference the new standard so future agent runs follow the same preflight/evidence workflow
- [x] 2.3 Decide whether the first implementation entry point should be a dedicated `jira-skill` preflight/setup command group or an agent-runbook wrapper over existing commands, and capture that decision during apply

## 3. Prepare verification and rollout expectations

- [x] 3.1 Verify the change reaches apply-ready state with `openspec status --change "standardize-jira-space-setup"`
- [x] 3.2 During implementation, require repo-specific verification in `jira-skill` (`uv run pytest`, `ruff`, `mypy` on touched files) plus a live Jira dry-run/readback check for at least one target project
- [x] 3.3 Preserve rollback as additive-only: if future setup automation proves unsafe, keep the OpenSpec standard and disable the new command/runbook entry point until validation is complete

## 4. Align EW guidance to evidence from other spaces

- [x] 4.1 Classify candidate reference spaces by live Jira project style and setup-detection surface before using them as parity baselines — implemented via `FieldConfig.get_estimation_support_by_issue_type` (records `project_style` + `detection_source` of `createmeta`/`project_issue_types`/`project_issue_types_fallback` per issue type)
- [x] 4.2 Record the strongest observed live baseline from team-managed spaces separately from the stricter target standard so EW guidance does not overclaim current consistency — `estimation-parity` CLI emits the observed Story Points + Time Tracking baseline distinctly from the "Story Points + Original Estimate + Time Tracking" target standard
- [x] 4.3 Update setup outputs, docs, and skills so EW remediation guidance says whether the next step is "match best observed baseline" or "reach target standard" for each missing capability — `setup-project` preflight/guarded-apply reports per-issue-type capability gaps, the EW board `953` estimation-field readback, and the blocked/unsupported boundary for team-managed write paths; covered by `tests/analysis/test_cli.py` (4 passing)

## 5. Split the setup contract into explicit workflow families

- [x] 5.1 Update the OpenSpec design to define `team-managed / modern` and `classic / legacy` setup as separate workflow families under a shared preflight
- [x] 5.2 Update `jira-space-setup-standard` so project style explicitly selects the workflow family before any apply/remediation step
- [x] 5.3 Add requirements that team-managed setup is detection-first and API-surface-bound because issue-layout / project field-association control remains outside or only partially covered by supported public write APIs
- [x] 5.4 Add requirements that classic setup uses explicit screen/tab/scheme alignment semantics and only performs guarded apply steps with read-back validation
- [x] 5.5 Update implementation follow-up expectations so future `jira-skill setup-project` execution reports the selected workflow family and does not present a single generic apply contract across both Jira project styles

## 6. Validate the spec against current implementation and add execution guidance

- [x] 6.1 Compare the spec against the shipped `jira-skill` surfaces (`setup-project`, `estimation-parity`, `FieldConfig`, board and dashboard commands) and record which requirements are already satisfied versus still planning-only
- [x] 6.2 Add an implementation-status section to the design so execution can distinguish current coverage from future apply work without weakening the target requirements
- [x] 6.3 Add rollout guidance that the current shipped slice is read-mostly and safe by default, while unwired requirements remain planning targets for future apply work
- [x] 6.4 During implementation, translate the spec into concrete execution slices for `jira-skill setup-project`. The required primitives already exist and are NOT blockers; the gap is wiring them into the setup workflow. DONE: `SetupEvidenceCollector` (`board/setup_evidence.py`) is wired into `setup-project` (`cli.py` `build_setup_evidence`). REMAINING TEST GAP: no dedicated unit tests for `setup_evidence.py` yet — add coverage for board audit, filter candidates, dashboard audit, and readiness aggregation in a future apply step.
  - [x] 6.4.1 Replace the hard-coded board readback (`cli.py:1152` — `jira.get("rest/agile/1.0/board/953/configuration") if project == "EW"`) with a general board audit driven by `BoardOperations.list_boards(project_key=...)` + `get_board(..., include_configuration=True)` / `get_board_configuration`, so any project's boards are discovered and their resolved filter wiring validated (satisfies "Existing boards SHALL be audited").
  - [x] 6.4.2 Emit the selected workflow family (`team-managed / modern` vs `classic / legacy`) in `setup-project` output and evidence (satisfies task 5.5).
  - [x] 6.4.3 Wire canonical filter capture/validation (`board/filter_creator.py`, `list_filters`, `analysis/filter_registry.py`) into the setup workflow so filter IDs + JQL + sharing state are captured (satisfies "canonical filter outputs").
  - [x] 6.4.4 Wire dashboard read-back validation (existing `dashboard` / `dashboard-rollback` per `jira-dashboard-automation`) into setup so board+dashboard live validation is recorded rather than skipped — `SetupEvidenceCollector.collect_dashboard_audit` calls `validate_dashboard` for each board-resolved filter and records `ok`/`mismatch`/`error`/`skipped` status with gadget-binding issues; invoked from `build_setup_evidence` (`setup_evidence.py:222`).
  - [x] 6.4.5 Wire a permission preflight (`user_roles.has_permission`, currently unused by the setup path) so insufficient capability is reported as an actionable blocker.
  - [x] 6.4.6 Emit structured evidence (project key, board IDs, filter IDs, dashboard IDs when applicable, canonical names, JQL summaries, blocked/unsupported outcomes, explicit readiness outcome) instead of console-only text.
- [x] 6.4.7 Add a dedicated team-managed diagnostics slice to `jira-skill` that distinguishes `global field exists`, `instance capability enabled`, and `project exposure missing` using read-only Jira surfaces such as create-metadata, edit-metadata, field search, project properties, project features, and time-tracking configuration.
- [x] 6.4.8 Extend setup evidence and/or a dedicated diagnostics command so team-managed findings can state whether a missing capability is caused by unavailable fields, disabled global capability, unsupported current API write coverage, or project-level layout exposure gaps without implying non-programmatic remediation.
- [x] 6.4.9 Evaluate supported public write surfaces for TMP setup, including project feature APIs and `PUT /rest/api/3/field/association`, and record which setup gaps are `supported-but-unvalidated-here` versus which remain `unsupported-by-current-api-surface` after live validation.
- [x] 6.4.10 Rename or reshape `SetupEvidenceCollector.build_setup_evidence()` output so the current legacy `manual_follow_up` field becomes an explicit blocked/unsupported status structure aligned to the spec taxonomy (`implemented-and-supported`, `supported-but-unvalidated-here`, `unsupported-by-current-api-surface`, `permission-blocked`, `validation-incomplete`).
- [x] 6.4.11 Add SDK-first required-field verification for team-managed projects using Jira REST v3 create metadata (`required: true/false`), and surface it in `setup-project` as read-only evidence rather than unsupported apply behavior.
