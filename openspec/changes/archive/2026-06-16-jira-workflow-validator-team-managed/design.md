## Context

The TDT ecosystem has multiple Jira-aware tools (`jira-skill`, `webhook-receiver` jira_guard, `jira-daily-reports`) that historically treated the workflow API as a black box and warned users to use the Jira UI for any non-trivial workflow edit. The original `jira-code-review-field-validation` change in May 2026 broke that stance by adding programmatic field-required validators, but it was implemented against the *legacy* editor payload shape. Atlassian has since promoted the unified workflow editor as the only supported editor (full migration in March 2026; legacy editor being removed in June 2026). Two facts have changed:

1. **Payload shape** — The new unified editor requires the entire workflow document to be re-uploaded on every update, with statuses, layouts, transitions, validators, triggers, and version. `statusReference` is a per-request UUID that links top-level status definitions to workflow layouts. A subset-update (only the changed transition) is no longer accepted for new-editor workflows.
2. **Project type support** — Team-managed project workflows (e.g. `Software Simplified Workflow for Project TJ`) are editable via the same `POST /rest/api/3/workflows/update` endpoint provided the new payload shape is used and the calling identity has `Administer projects` on the target project. They are *not* editable via the legacy `PUT /rest/api/3/workflow/{id}` endpoint.

The current `jira-skill` implementation already partially accounts for both — it builds a full new-editor payload, generates per-request `statusReference` UUIDs, copies all existing transitions to preserve them, and uses `is_team_managed_project()` to detect team-managed projects. The gap is the *spec* does not document any of this, the implementation *rejects* team-managed projects via `TeamManagedProjectError`, and there is no documented path for `add_transition` / `add_transition_with_validator` (which were added to the code in May 2026 but never specced).

## Goals / Non-Goals

**Goals**

- One canonical spec for the `jira-workflow-validator` capability that covers:
  - Field discovery (custom field ID resolution).
  - Workflow read (search, bulkGet, preview).
  - Validator attachment to an existing transition.
  - New transition creation.
  - Combined transition+validator creation.
  - Team-managed project support.
  - Idempotency, dry-run, and validate-then-commit semantics.
- Keep the existing public API (`WorkflowClient`, `TransitionValidator`, `FieldDiscovery`) intact, and document the per-method contracts.
- Make `is_team_managed_project()` a public, documented helper.
- Replace the blanket `TeamManagedProjectError` with two more specific errors:
  - `TeamManagedEditNotPermittedError` — the user has `Administer projects` on the project but the workflow is on a shared scheme that requires `Administer Jira`.
  - `UnsupportedWorkflowEditorError` — the workflow is still on the legacy editor and the new payload shape is rejected by the server.
- Ensure the `validate_update_payload()` helper is exposed so the CLI and SDK users can dry-run payload shape before commit.

**Non-Goals**

- Removing the legacy editor payload code path. (Some workflows may still be on it; the helper should detect and report, not silently fall back.)
- Adding a Forge-style "save workflow as draft then publish" two-phase commit. The current `workflows/update` is atomic; that is good enough.
- Implementing bulk-edit streams (batch 100+ workflows in a single HTTP request).
- Supporting Jira Server / Data Center v2 differences.

## Decisions

### Decision 1: New-editor payload shape is canonical

The spec mandates the new unified-editor payload shape for *all* `POST /rest/api/3/workflows/update` calls. The implementation already builds this payload in `add_validator`, `add_transition`, and `add_transition_with_validator`. The spec formalizes the structure:

```json
{
  "statuses": [
    {
      "id": "<numeric status id or omit for new>",
      "name": "<status name>",
      "statusCategory": "TODO|IN_PROGRESS|DONE",
      "statusReference": "<uuid>"
    }
  ],
  "workflows": [
    {
      "id": "<workflow entity id>",
      "version": { "id": "<version uuid>", "versionNumber": <int> },
      "statuses": [
        { "statusReference": "<uuid>", "layout": {"x": 0, "y": 0}, "properties": {} }
      ],
      "transitions": [
        {
          "id": "<numeric transition id>",
          "name": "<transition name>",
          "type": "INITIAL|GLOBAL|DIRECTED",
          "toStatusReference": "<uuid>",
          "fromStatusReference": "<uuid or omit for DIRECTED>",
          "links": [{"fromStatusReference": "<uuid>", "fromPort": 0, "toPort": 1}],
          "validators": [
            {
              "ruleKey": "system:validate-field-value",
              "parameters": {
                "ruleType": "fieldRequired",
                "fieldsRequired": "customfield_10020,customfield_10021",
                "ignoreContext": "true",
                "errorMessage": "..."
              }
            }
          ],
          "actions": [],
          "triggers": [],
          "properties": {}
        }
      ]
    }
  ]
}
```

**Rationale**

- Atlassian's new editor is the only supported editor as of March 2026.
- The implementation already builds this shape. The spec just documents it.
- Smaller "diff" updates are no longer accepted for new-editor workflows; full re-upload is required.

**Alternatives considered**

- *Per-transition PUT endpoint* (`PUT /rest/api/3/workflow/{workflowId}/transitions/{transitionId}/validators`) — does not exist in v3. Rejected.
- *Forge-style PUT /rest/api/3/workflow/rule/config* — restricted to Connect/Forge apps for *their own* rules; cannot be used for `system:validate-field-value`. Rejected.

### Decision 2: Team-managed project support is *enabled*, with a guard

`TeamManagedProjectError` currently blocks all team-managed project edits. The new spec enables them. The guard changes from "is it team-managed?" to "do we have the right permission?". The helper `can_edit_team_managed_workflow(project_key)` returns False if:

- The project is team-managed *and* the workflow is on a shared global scheme (edit would require `Administer Jira`, not `Administer projects`).
- The workflow is still on the legacy editor (server rejects the new payload shape).

In the failure case, `TeamManagedEditNotPermittedError` is raised, and the SDK/CLI prints a remediation hint: "ask a Jira admin to grant Administer Jira, or edit the workflow in the Jira UI for this project."

**Rationale**

- The blocker was based on outdated knowledge (pre-new-editor). The new editor has unified the API for both project types.
- The `is_team_managed_project()` detection is still valuable for routing decisions (e.g., picking a different default workflow), but it should not block edits.
- Distinguishing *permission* from *editor-version* failures gives users a more actionable error.

**Alternatives considered**

- *Keep blocking team-managed projects* — would force users back to the UI for any project that uses the simplified workflow, which is most team-managed projects. Rejected.
- *Auto-grant Administer Jira via OAuth* — out of scope and unsafe.

### Decision 3: `add_transition` and `add_transition_with_validator` are part of the public API

The implementation already exposes these. The spec formally documents them and adds the orchestrator `apply_add_transition_with_validator()` on `TransitionValidator`.

**Rationale**

- The original change's "ready to deploy" checklist noted that the simplified workflow has only To Do / In Progress / Done; adding a "Code Review" status + transition is a prerequisite for the validator to be meaningful.
- Splitting "create transition" from "attach validator" into two API calls lets users see intermediate state, but in practice both calls share a workflow version and need to be atomic from the user's perspective. The combined entry point is the common case.

### Decision 4: `validate_update_payload()` as a dry-run helper

The Jira API supports a `validationOptions` query parameter on `POST /rest/api/3/workflows/update` that runs the update through the same payload-shape validators as the real endpoint, but does not commit. The spec adds `WorkflowClient.validate_update_payload(payload) -> dict[str, Any]` that returns the validation result (errors, warnings). The `TransitionValidator.apply()` method shall call this automatically before the real `update` and raise `ValidationError` on any ERROR-level finding.

**Rationale**

- Cheap pre-flight check that catches malformed payloads before they fail with confusing 400 errors.
- Same code path that the server uses, so the result is authoritative.
- Saves a round-trip when iterating on the payload shape.

**Alternatives considered**

- *Local-only payload validation in Python* — duplicates server logic and will drift.
- *Try-and-rollback* — risky; workflow updates may be partially applied.

### Decision 5: `preview_workflow` uses `POST /rest/api/3/workflows/preview`

The deprecated `GET /rest/api/3/workflows/{id}` returns 404 for most real workflows. The new-editor-correct way to read a workflow document is `POST /rest/api/3/workflows/preview` with `{"workflowIds": [...]}` and `{"projectAndIssueTypes": [{"projectId": ..., "issueTypeId": ...}]}` as alternative inputs. The spec adds `WorkflowClient.preview_workflow(workflow_id, project_key=None, issue_type_id=None)`.

**Rationale**

- `preview` is the read counterpart to `update`. Same response shape.
- Returns statuses, transitions, and version — the inputs needed to build a safe update payload.
- `GET /workflows/{id}` is being removed.

### Decision 6: Required vs. optional fields per field, with `FieldRequirement`

A `system:validate-field-value` validator with `ruleType: fieldRequired` can only
express "these fields MUST be filled". To support use cases like "Dev in
Charge is required, but Developer is optional" we cannot encode that as a
single validator — Jira's `fieldsRequired` is a positive list of fields that
must have a value.

The new spec introduces a `FieldRequirement` model that callers pass to
`preview()`, `apply()`, and `apply_add_transition_with_validator()`:

```python
class FieldRequirement:
    name: str       # Field display name
    required: bool  # True = included in fieldsRequired; False = recorded but not enforced
```

The legacy `field_names: list[str]` form is preserved and treated as
`field_requirements=[{"name": n, "required": True} for n in field_names]`
— fully backward-compatible.

The `has_validator()` idempotency check now compares the existing
`fieldsRequired` set against the *required* subset of the caller's fields
only. Optional fields are ignored for matching.

When the caller passes **no required fields** (all optional), the SDK
short-circuits: it prints a clear warning and returns
`{"action": "noop", "reason": "no_required_fields"}` without making an API
call. This avoids a no-op round-trip to Jira.

**Rationale**

- Most expressive of the user's intent without adding new Jira validator types.
- Backward-compatible: every existing call site continues to work.
- The new CLI surface (`--required` / `--optional`) is more discoverable than
  a single comma-separated list for users who care about the distinction.
- Idempotency semantics line up with what users expect: "if my required
  fields are already enforced, don't re-apply".

**Alternatives considered**

- *Two validators per field (one for required, one for "may-be-present")* —
  Jira does not have a "may-be-present" rule type; rejected.
- *Always emit a validator with the union of all fields, and toggle the
  `errorMessage` between modes* — semantically wrong; rejected.
- *Two separate transitions (one for required, one for optional) per field* —
  duplicates transitions; rejected.

### Decision 7: `find_transition()` matches by `toStatusReference` too

The legacy `find_transition()` only matched transitions by their display
name (either equal to the target status, or `"from -> to"`). This
fails for workflows where the transition's display name is an action
verb (e.g., `Submit`, `Complete`) that doesn't include the target
status name — which is common in real Jira workflows.

The spec adds a third matching strategy: resolve the transition's
`toStatusReference` against a `statusReference → name` map and match
against the target status. The map is sourced from the workflow's
own `statuses` array when present, or built from `list_all_statuses()`
when not.

A new optional `status_by_ref: dict[str, str] | None` argument lets
callers pre-build the map (e.g., from the rich `preview_workflow()`
document) and pass it in for efficiency.

**Rationale**

- Real-world workflows use action-verb transition names. Without this
  matching strategy, the SDK can't find the `Submit` transition in AM
  (which goes to `PM Review`) or the `Complete` transition in TJ
  (which goes to `Code Review`).
- The new strategy is purely additive: legacy matching still runs
  first; the new strategy is a fallback.

### Decision 8: Use the rich `preview_workflow()` document for payload build

The bulkGet response from `find_workflow_for_project()` can have an
**incomplete `statuses` list** for some team-managed workflows (notably
when the workflow has statuses that aren't actively used by any
transition in the response). When the SDK uses this incomplete list
to build a new-editor payload, the server-side validator rejects the
update with "Transition refers to a status that does not exist within
this workflow."

The fix: in `apply()` and `validate()`, fetch the rich
`preview_workflow()` document (which includes all statuses in full)
and use it as the `workflow_data` argument to
`_build_validator_payload()`. The fetch happens **only on the
actual-apply path** so idempotent / already-configured callers don't
pay the extra round-trip.

A helper `_safe_full_workflow(workflow, project_key)` returns the
rich document when available, falling back to the bulkGet data on
error. The bulkGet path is still used as the source of truth for
`find_transition()` because it's faster and gives the same result
when the workflow is well-formed.

**Rationale**

- The rich document is the source of truth for "all statuses in the
  workflow" — anything that references a status not in this document
  will fail server validation.
- Lazy fetch keeps the idempotent / already-configured path
  round-trip-free, preserving the original performance characteristic.

### Decision 9: Defensive `fromStatusReference` resolution

Jira's new editor does NOT always include `fromStatusReference` at
the transition level for `DIRECTED` transitions. It may only encode
the from-status in `links[].fromStatusReference`. When the SDK reads
the transition and copies it into the payload, it gets `fromStatusReference:
None` and the server rejects the update with "Transition refers to a
status that does not exist."

The fix: in `_build_validator_payload()`, fall back to
`links[0].fromStatusReference` for both the target transition and
all copied transitions. This is a defensive read; it only fires when
the transition-level `fromStatusReference` is missing.

**Rationale**

- Avoids server-side rejections for legitimate workflow shapes.
- The fallback is a no-op when `fromStatusReference` is already set.

### Decision 10: Pre-existing broken rules require manual UI fix

Some team-managed project workflows in this Jira instance have
**pre-existing conditions/validators with missing required
parameters** (e.g., `system:restrict-issue-transition` with
`params: {}`). The new editor refuses to propagate ANY update to
these workflows because doing so would propagate the broken rules.

Projects confirmed affected: **AM** (11 broken rules), **TJ** (2
conditions + 4 server-only rules). Projects confirmed clean: **DT**
(after manual cleanup), **AO**, **ACO**, **AIG**, **AO**, **AOP**,
**AP**, **AU**.

The spec documents this as a **known limitation** that requires
manual UI cleanup before the SDK can update the workflow. The
`_strip_broken_rules_inplace()` helper is provided as an **opt-in**
cleanup (env var `JIRA_SKILL_REPAIR_BROKEN_RULES=1`) for users who
want the SDK to attempt the repair automatically, but it is not
guaranteed to succeed: in some Jira instances, the server
regenerates broken rules on each update, in which case the strip is
a no-op.

**Rationale**

- We can't fix pre-existing server-side corruption from the client.
  The Jira UI is the only authoritative way to repair these workflows.
- Opt-in behavior avoids surprising users whose workflows are clean.
- The `find_clean_projects_for_verification` script
  (`scripts/probe_tj_rules.py`) is a useful diagnostic for users
  facing this issue.

### Decision 11: Remap `links[].fromStatusReference` and `links[].toStatusReference` for DIRECTED transitions

Jira's new-editor workflow document encodes status references in
**two** places on a transition:

- The transition-level `fromStatusReference` and `toStatusReference`
  fields (top of the transition dict).
- The `links[]` array (each link has its own `fromStatusReference`
  and `toStatusReference`).

For **GLOBAL** transitions, only the top-level `toStatusReference` is
set; `fromStatusReference` is `null` and `links` is empty. For
**DIRECTED** transitions, the top-level `fromStatusReference` is
often `null`, and the actual from-status is encoded in
`links[0].fromStatusReference`.

`_build_validator_payload()` regenerates every declared status's
`statusReference` to a fresh UUID before submission (per
`/workflows/update` requirements). The previous fix remapped the
top-level transition fields, but **not** the values inside `links[]`.
When the link still held the old integer status ID while the rest
of the payload used fresh UUIDs, the server rejected the update
with:

```
Transition refers to a status that does not exist within this workflow.
Transition references an unknown status.
```

The fix is to apply the same `status_ref_map` remap inside the
`links[]` array, for both the target transition and the "copy all
other transitions" loop. Non-reference fields like `fromPort` and
`toPort` are preserved verbatim.

**Rationale**

- DIRECTED transitions are common in team-managed workflows with
  multi-status cycles (e.g., AU's "Complete development on Feature
  Branch → CODE REVIEW" → "deploy in dev environment" → ... cycle).
- The fix is defensive and silent: when the link doesn't reference
  a known status, the remap is a no-op.
- The original apply code never failed for GLOBAL transitions, so
  this fix is targeted at the DIRECTED case.

**Alternatives considered**

- *Skip the links[] remap and rely on the server to be lenient*:
  rejected, the server is not lenient.
- *Always rebuild the entire workflow document server-side*:
  rejected, the new editor requires the full document.
- *Drop `links[]` from the payload entirely*:
  rejected, the editor needs it to render the workflow diagram.

**Tests added**

- `test_build_validator_payload_remaps_links_status_references`
- `test_build_validator_payload_links_remap_preserves_other_fields`

### Decision 12: History-Based Workflow Repair

Some team-managed project workflows have **pre-existing broken rules**
(conditions/validators with missing required parameters) that prevent
any programmatic update via the new editor's `workflows/update` API.
Previously this was a hard block requiring manual UI cleanup.

A new programmatic repair strategy uses Jira's **workflow history API**:

- `POST /rest/api/3/workflow/history/list` returns all available versions
  for a workflow (retained 60 days, data from October 30, 2025 onwards)
- `POST /rest/api/3/workflow/history` with `{"workflowId": "...", "version": N}`
  returns the full workflow at that version

For AM/RMD/SR, history v0 (written 2026-04-14) contains the
**original, clean workflow** with zero broken conditions and all
transitions intact. The broken rules were introduced in subsequent
versions.

**The repair strategy**: read v0, convert its legacy format
(`rules.conditionsTree`) to the new editor format (top-level
`conditions` field), and submit as a `workflows/update` payload.

**Correct payload structure**:

```json
{
  "statuses": [rich_doc_root_statuses],
  "workflows": [{
    "id": "<current_workflow_id>",
    "version": {"id": "<current_version_id>", "versionNumber": N},
    "statuses": [v0_workflow_statuses],
    "transitions": [v0_transitions_in_new_format]
  }]
}
```

Key conversion rules:
- `toStatusReference`, `links[].fromStatusReference` — copied directly
  (numeric IDs, not UUIDs)
- `rules.conditionsTree` → new format `conditions` with
  `{operation, conditionGroups, conditions}` (only when present)
- `rules.validators` → new format `validators` with
  `ruleKey/id/parameters`
- `rules.validators[].type` → `ruleKey`, empty `configuration` →
  empty `parameters`
- `actions`, `triggers` → empty arrays

**TJ limitation**: TJ's current workflow has 9 statuses but history v0
has only 8. The server requires `statusMappings` for the removed status,
but Jira only provides 8 of the 9 expected entries. This structural
mismatch cannot be resolved without manual intervention.

**SDK enhancement**: Add `workflow revert-history` CLI command and
`WorkflowClient.revert_to_history()` method to automate this repair.

**Rationale**

- Uses an existing Jira API endpoint (history) that is already documented
  and supported
- The v0 history is authoritative — it's the original workflow before the
  corruption
- The conversion from legacy to new format is deterministic and safe
- The approach is opt-in: `workflow revert-history` is a separate command
  that runs before `workflow_add_validator`

## Architecture

```
TransitionValidator (orchestrator)
├── is_team_managed_project()             # NEW: public helper
├── can_edit_team_managed_workflow()      # NEW: permission check
├── list_project_workflows()              # existing
├── preview()                             # existing (was raising TeamManagedProjectError; now allows)
├── apply()                               # existing (now allows team-managed)
├── apply_add_transition_with_validator() # NEW (was raising TeamManagedProjectError; now allows)
└── validate_update_payload()             # NEW

WorkflowClient (REST adapter)
├── list_workflows()                      # existing
├── get_workflow()                        # existing (bulkGet)
├── get_workflow_full()                   # existing (bulkGet + optional GET fallback)
├── preview_workflow()                    # NEW: POST /workflows/preview
├── find_workflow_for_project()           # existing
├── find_transition()                     # existing
├── has_validator()                       # existing
├── add_transition()                      # existing
├── add_validator()                       # existing (new-editor payload)
├── add_transition_with_validator()       # existing (orchestrator)
├── validate_update_payload()             # NEW: POST /workflows/update?validationOptions
├── resolve_status_name_to_id()           # existing
├── list_all_statuses()                   # existing
└── is_team_managed_project()             # existing (now exposed publicly)

FieldDiscovery
├── list_all_fields()                     # existing
├── list_custom_fields()                  # existing
├── find_field_by_name()                  # existing
└── resolve_field_ids()                   # existing

Exceptions (workflow/exceptions.py)
├── JiraWorkflowError                     # existing base
├── WorkflowNotFoundError                 # existing
├── TransitionNotFoundError               # existing
├── FieldNotFoundError                    # existing
├── PermissionDeniedError                 # existing
├── VersionConflictError                  # existing
├── RateLimitError                        # existing
├── StatusNotFoundError                   # existing
├── TransitionAlreadyExistsError          # existing
├── TeamManagedProjectError               # MODIFIED → "UnsupportedWorkflowEditorError" (legacy editor only)
├── TeamManagedEditNotPermittedError      # NEW
└── ValidationError                       # NEW (from validate_update_payload)
```

## API Payload Reference (new editor, both project types)

`POST /rest/api/3/workflows/update` with `validationOptions` query parameter for dry-run.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `statuses[].id` | string | optional | Numeric status ID. Omit when creating a new status. |
| `statuses[].name` | string | required | Status display name. |
| `statuses[].statusCategory` | string | required | `TODO`, `IN_PROGRESS`, or `DONE` (uppercase). |
| `statuses[].description` | string | optional | Status description. |
| `statuses[].statusReference` | string (UUID) | required | Self-defined per request. Maps to `workflows[].statuses[].statusReference`. |
| `workflows[].id` | string (UUID) | required | Workflow entity ID. |
| `workflows[].version.id` | string (UUID) | required | Current version UUID (for optimistic locking). |
| `workflows[].version.versionNumber` | int | required | Current version number. |
| `workflows[].statuses[].statusReference` | string (UUID) | required | Must match a top-level `statuses[].statusReference`. |
| `workflows[].statuses[].layout` | object | required | `{x: float, y: float}` layout coordinates. |
| `workflows[].transitions[].id` | string | required | Numeric transition ID. |
| `workflows[].transitions[].type` | string | required | `INITIAL`, `GLOBAL`, or `DIRECTED`. |
| `workflows[].transitions[].name` | string | required | Transition display name. |
| `workflows[].transitions[].toStatusReference` | string (UUID) | required | Must match a top-level `statuses[].statusReference`. |
| `workflows[].transitions[].fromStatusReference` | string (UUID) | optional | Omit for `DIRECTED` transitions that target the same status. |
| `workflows[].transitions[].links` | array | required | `[{fromStatusReference, fromPort, toPort}]`. |
| `workflows[].transitions[].validators` | array | optional | Validator list. |
| `workflows[].transitions[].actions` | array | optional | Post-function list. |
| `workflows[].transitions[].triggers` | array | optional | Trigger list. |
| `workflows[].transitions[].properties` | object | optional | Transition properties. |

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| New-editor payload shape is verbose; easy to omit a field | Silent server errors, hard to debug | Use `validate_update_payload()` as a pre-flight check. |
| `version.id` UUID is required alongside `versionNumber`; missing the UUID causes 400 | Validator attachment fails | Read `version.id` from `preview_workflow()` before building the payload. |
| Team-managed workflow on a shared global scheme | Permission error 403 | Detect via `can_edit_team_managed_workflow()` and raise `TeamManagedEditNotPermittedError` with remediation hint. |
| Status reference UUID collision in same request | Subtle 400 error | Generate a new `uuid.uuid4()` per status per request; never reuse. |
| Layout coordinates of `0,0` for new statuses | Jira may move the layout, but it does not reject | Use the same `x,y` as the source status, or place at `0,0` for new statuses (acceptable). |
| Per-workflow version conflict under concurrent updates | `VersionConflictError` | Re-fetch the workflow, re-apply, retry once. |
| Editor migration in progress (some workflows still legacy) | Mixed payload acceptance | Detect via `editorScope` from `/workflows/capabilities`; raise `UnsupportedWorkflowEditorError` for legacy. |

## Test Plan

1. **Unit tests** (existing, plus additions):
   - `test_add_validator_new_editor_payload` — assert the payload structure is exactly the new-editor shape.
   - `test_add_transition_team_managed` — verify the payload includes all required fields for a team-managed workflow.
   - `test_validate_update_payload_dry_run` — assert that `validationOptions` query param is set and that errors are propagated.
   - `test_can_edit_team_managed_workflow_shared_scheme` — assert `False` for a workflow on a shared scheme.
   - `test_can_edit_team_managed_workflow_dedicated_scheme` — assert `True` for a project-scoped workflow.
   - `test_team_managed_edit_not_permitted_error` — assert the right exception is raised with a useful hint.
2. **Integration tests** against a real Jira Cloud instance:
   - Apply a `system:validate-field-value` validator to a `Software Simplified Workflow for Project GWM` (GWM is team-managed, dedicated scheme).
   - Apply a `system:validate-field-value` validator to a global workflow used by an AM project.
   - Add a new transition (To Do → In Review) to the GWM workflow, then attach a validator to it.
3. **CLI tests**:
   - `jira-skill workflow add-validator --project GWM --from "In Progress" --to "In Review" --fields "Developer,Dev in Charge"` should succeed.
   - Same command against a workflow on a shared global scheme should exit with a clear `TeamManagedEditNotPermittedError` message and non-zero exit code.

## Verification Evidence (already collected)

- **GWM (team-managed, dedicated scheme)** — validator applied via the new-editor payload shape in May 2026.
- **AM (company-managed)** — validator applied via the same payload shape.
- **11 Software Simplified Workflows** — validator applied across projects (ATUP, BMMQ, DEMO, GFOQAT, GQ, GWM, JA, M2QAT, MQ, MW, TES).
- **CFD workflows** — known limitation: orphaned status references prevent programmatic editing. Documented in QUICK-REFERENCE.


## Decision 13: SDK exposes history-repair entry points

After proving the history-revert strategy manually for AM, RMD, and SR
in the previous session, the SDK now provides first-class support for
this repair pattern.

**New methods on `WorkflowClient`:**

| Method | Purpose |
|--------|---------|
| `list_workflow_history(workflow_id)` | List available versioned history entries via `POST /rest/api/3/workflow/history/list` |
| `get_workflow_history(workflow_id, version)` | Read a specific history version via `POST /rest/api/3/workflow/history`. Returns the workflow in legacy `rules.conditionsTree` format. |
| `has_clean_history(workflow_id, version=0)` | Check whether a history version has zero broken rules. Used as a pre-flight check. |
| `is_recoverable_via_history(project_key, history_version=0)` | Check whether a project is a candidate for history-based repair (team-managed, has workflow, has clean v0). |
| `revert_to_history(workflow_id, project_key=None, history_version=0, dry_run=True)` | The main repair method. Reads clean history, converts to new editor format, dry-runs or applies via `workflows/update`. |
| `has_broken_rules(project_key, field_ids=None, error_message=...)` | Diagnostic helper. Builds a would-be validator payload, runs the structured `workflows/update/validation` endpoint, parses the response into `server_only_rule_ids` (codes `MISSING_RULE_PARAMETER`) and `invalid_config_rule_ids` (codes `INVALID_RULE_CONFIGURATION`). |

**New helper on `TransitionValidator`:**

`_maybe_repair_and_apply(...)` — wraps the existing `add_validator()` call
with an opt-in pre-flight check. When `JIRA_SKILL_AUTO_REPAIR_HISTORY=1`
is set AND the structured validation reports `MISSING_RULE_PARAMETER`
errors, calls `revert_to_history()` first, then proceeds with the
normal `add_validator()` flow.

**New CLI commands:**

| Command | Purpose |
|---------|---------|
| `jira workflow revert-history --project PROJ [--version N] [--apply]` | Run `revert_to_history()` (dry-run by default; `--apply` to commit). |
| `jira workflow history --project PROJ [--version N]` | Show summary of a history version. |
| `jira workflow check-broken-rules --project PROJ` | Run `has_broken_rules()` and print structured report with `server-only` / `invalid-config` rule IDs and recovery recommendation. |

**Diagnostic integration:**

`scripts/sprint16_diagnose.py` was updated to:
1. Use the new `has_broken_rules()` and `is_recoverable_via_history()` helpers.
2. Add a new verdict: `recoverable_via_history` (printed as REC=Y in the table).
3. The exit code now treats `recoverable_via_history` as non-blocking, so CI can distinguish "blocked" from "recoverable".

**Rationale:**

- *Reuses existing endpoints* (the Workflow History API was already documented and supported).
- *Deterministic conversion* — the legacy `rules.conditionsTree` to new `conditions` mapping is straightforward and well-tested.
- *Opt-in auto-repair* — `JIRA_SKILL_AUTO_REPAIR_HISTORY=1` is off by default to avoid surprising callers with workflow reverts. Callers who want auto-repair can set the env var; others use the explicit `workflow revert-history` command.
- *Dry-run by default* — `revert_to_history()` defaults to `dry_run=True`; the caller must pass `dry_run=False` (or `--apply` on the CLI) to commit. This mirrors `add-validator --dry-run`.
- *Honest about limitations* — the dry-run will fail for projects with status-count mismatches (e.g., TJ). The SDK surfaces the error rather than papering over it; the recommendation message names the manual cleanup path.

**Live verification (Sprint 16, 2026-06-16):**

| Project | Verdict | BROKEN | SRV-ONLY | RECOVER | Notes |
|---------|---------|--------|----------|---------|-------|
| AM | ready_for_apply | Y | 0 | Y | Validator already applied; 1 visible broken rule remains (not blocking). |
| AU | ready_for_apply | Y | 0 | Y | Validator already applied. |
| FUN | ready_for_apply | Y | 0 | Y | Validator already applied. |
| PDS | ready_for_apply | Y | 0 | Y | Validator already applied. |
| RMD | ready_for_apply | Y | 0 | Y | Validator already applied. |
| SR | ready_for_apply | Y | 0 | Y | Validator already applied. |
| TJ | recoverable_via_history | Y | 4 | Y | Clean v0 exists (8 statuses, 14 transitions) but revert fails with `statusMappings` error (current 14 vs v0 8). Manual UI cleanup required. |
