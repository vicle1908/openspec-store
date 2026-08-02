## Why

The original `jira-code-review-field-validation` change shipped the `jira-skill` `WorkflowClient` and `TransitionValidator` against the *legacy* Jira Cloud Workflow REST API. Since then, Atlassian has made two breaking changes that the implementation already encountered and partially patched in code, but the spec was never updated:

1. **Default Workflow Editor** — Since 30 March 2026, Atlassian directs all customers to the new unified workflow editor. The legacy editor is being removed in June 2026. The new editor uses a different payload shape for `POST /rest/api/3/workflows/update` that requires a fully-materialized workflow document (statuses with `statusReference` UUIDs, transitions with `fromStatusReference`/`toStatusReference`/`links`, layout coordinates, and `version.{id,versionNumber}`).
2. **Team-managed project workflow editing** — Team-managed (next-gen, "Software Simplified Workflow for Project X") workflows are editable via the same `/rest/api/3/workflows/update` endpoint provided the new payload shape is used. The implementation already detects this case via `is_team_managed_project()` and currently refuses with `TeamManagedProjectError` — but that refusal is a regression because programmatic editing *is* supported, just with a stricter payload.

In addition, the implementation gained two new entry points — `WorkflowClient.add_transition()` and `WorkflowClient.add_transition_with_validator()` — that are not in the original spec at all. They are necessary because the most common reason for a "transition not found" error is that the project workflow is the simplified 3-status one (To Do / In Progress / Done) and the user needs a "Code Review" transition created before a validator can be attached.

A second gap surfaced after the first version was live: callers wanted to declare that some fields are *required* and others are *optional* on the same transition (e.g., "Dev in Charge required, Developer optional"). Jira's `system:validate-field-value` validator with `ruleType: fieldRequired` only expresses "these fields MUST be filled", so we need a per-field `required` flag in the SDK and idempotency that only compares the required subset.

The new spec must:

- Treat the new unified-editor payload shape as the canonical contract.
- Allow — and properly implement — team-managed project workflow updates.
- Cover the transition-creation entry points.
- Add a `validate` step using `POST /rest/api/3/workflows/update` with `validationOptions.levels=[ERROR,WARNING]` to dry-run payload shape before commit.
- Use `POST /rest/api/3/workflows/preview` as the read-side counterpart (per the new editor's design), not the deprecated `GET /rest/api/3/workflows/{id}`.
- Distinguish required and optional fields per call, with a `FieldRequirement` model and `field_requirements` parameter.

## What Changes

- Update the canonical spec `openspec/specs/jira-workflow-validator/spec.md` to declare support for both company-managed and team-managed project workflows, to require the new-editor payload shape for all updates, to cover `add_transition` + `add_transition_with_validator`, and to support a per-field `required` flag (with `field_requirements=[{"name", "required"}]`).
- Add four new requirements to the spec: **Team-managed project support**, **Transition creation**, **Preview-then-validate workflow**, and **Required vs. optional fields**.
- Replace the blanket `TeamManagedProjectError` with two more specific errors:
  - `UnsupportedWorkflowEditorError` (replaces `TeamManagedProjectError`) — raised when the workflow is still on the legacy editor, with a remediation hint to use the Jira UI for the duration of the editor migration. A backward-compat alias `TeamManagedProjectError` will be retained with a `DeprecationWarning`.
  - `TeamManagedEditNotPermittedError` — new, raised when the calling identity has `Administer projects` but the workflow is on a shared global scheme that would require `Administer Jira`.
- Document the `statusReference` UUID + layout + `version` semantics that the implementation already uses, so the spec is the single source of truth.
- Archive the previous `jira-code-review-field-validation` change as the historical reference and supersede its spec content with the updated one.

## Capabilities

### New Capabilities

- `jira-workflow-validator` (extended) — same surface as the original change, but with the broader contract:
  - Adds new-editor payload shape to `add_validator` and `add_transition`.
  - Adds `add_transition_with_validator` (combined entry point).
  - Adds `preview_workflow(workflow_id_or_project)` using `POST /rest/api/3/workflows/preview` to read the new-editor workflow document.
  - Adds `validate_update_payload(payload)` using `POST /rest/api/3/workflows/update` with `validationOptions.levels` to surface server-side payload errors before commit.
  - Adds `is_team_managed_project()` and `can_edit_team_managed_workflow()` capability checks.

  **Specification:** `openspec/specs/jira-workflow-validator/spec.md` (updated).

### Modified Capabilities

- None.

## Supersedes

- `openspec/changes/jira-code-review-field-validation` (Complete) — historical. The new spec file replaces its requirements; the implementation was already updated in code to match the new behavior, but the spec was lagging. The old change will be archived with a `superseded-by: jira-workflow-validator-team-managed` note in its README.

## Impact

- `jira-skill`:
  - `src/jira_skill/workflow/client.py` — `add_validator`, `add_transition`, `add_transition_with_validator`, `get_workflow_full` are already coded against the new editor. The spec just formalizes the contract.
  - `src/jira_skill/workflow/validator.py` — `preview`, `apply`, `apply_add_transition_with_validator` already call `is_team_managed_project()`. The spec formally extends them to support team-managed projects instead of rejecting them.
  - `src/jira_skill/workflow/exceptions.py` — add `TeamManagedEditNotPermittedError` (permission-gated), demote `TeamManagedProjectError` to "unsupported editor variant" (e.g., the site has not been migrated to the new editor, or the workflow is on an unsupported scheme).
  - `tests/test_workflow_client.py` and `tests/test_transition_validator.py` — already updated for the current behavior; add a test fixture for team-managed happy path.
- `tdt-core` — unchanged. Auth and transport stay in `tdt_core`.
- `jira-daily-reports` — no impact, but may want to reuse the same `is_team_managed_project` helper in the future.
- `jira-skill/QUICK-REFERENCE.md` — needs an updated "Team-managed project workflow editing" section that documents the new editor payload and the supported transition-creation flow.
- `openspec/specs/jira-workflow-validator/spec.md` — the canonical spec file at the top level (not just the change's spec delta) will be re-written at archive time to match the merged delta.

## Non-Goals

- Modifying Jira field configurations globally (only transition-level validation).
- Creating Jira Automation rules.
- Supporting Jira Server / Data Center (v2 endpoint differences out of scope).
- Removing the legacy `WorkflowClient.add_validator` legacy code path; the implementation already handles both editor payloads, and the spec formalizes the new-editor path.
- Bulk editing 100+ workflows in one shot (the existing orchestrator does this with a Python loop, but a streaming batch API is out of scope).

## Additional Capabilities (added during implementation)

After the original proposal, the implementation gained additional
capabilities driven by the Sprint 16 deployment:

### History-based workflow repair

A new class of methods on `WorkflowClient` and matching CLI commands
to programmatically repair workflows blocked by pre-existing broken
rules (e.g. `system:restrict-issue-transition` with empty parameters
introduced by Jira's editor migration). The strategy was discovered
during deep research: the Jira Workflow History API retains clean
historical versions of workflows (typically v0), and reverting to that
version via the new editor's `workflows/update` endpoint clears the
corruption.

- `list_workflow_history(workflow_id)`, `get_workflow_history(workflow_id, version)`
- `has_clean_history(workflow_id, version=0)`, `is_recoverable_via_history(project_key, ...)`
- `revert_to_history(workflow_id, project_key=None, history_version=0, dry_run=True)`
- `has_broken_rules(project_key, field_ids=None, error_message=...)`
- CLI: `jira workflow revert-history`, `jira workflow history`, `jira workflow check-broken-rules`
- Auto-repair opt-in via `JIRA_SKILL_AUTO_REPAIR_HISTORY=1` env var

### Diagnostic integration

`scripts/sprint16_diagnose.py` was updated to use the new helpers
and surface a `recoverable_via_history` verdict alongside the
existing verdicts. This makes the Sprint 16 deployment self-documenting
in CI/dashboards.

**Specification:** see sections 22-23 of `tasks.md`, Decision 13 of `design.md`,
and section 10 of `LIVE-VERIFICATION.md`.
