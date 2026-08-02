# jira-workflow-validator — Delta Specification

This delta extends the canonical `jira-workflow-validator` spec with team-managed project support, transition creation, and server-side payload validation. The pre-existing requirements (field discovery, idempotency, CLI, error handling) are preserved verbatim from the canonical spec; this delta appends new requirements and documents the new-editor payload shape.

## ADDED Requirements

### Requirement: Read workflow documents via the new-editor API

The system SHALL retrieve workflow information using the new unified-editor read endpoints, not the deprecated `GET /rest/api/3/workflows/{id}`. The unified editor is the default editor for Jira Cloud as of March 2026; the legacy editor is being removed in June 2026.

#### Scenario: Search workflows
- **WHEN** the user requests a list of workflows
- **THEN** the system SHALL call `GET /rest/api/3/workflows/search?expand=values.transitions`
- **AND** return workflows with their entity IDs, names, scope, and version

#### Scenario: Bulk-get workflow by ID
- **WHEN** the user provides a workflow entity ID
- **THEN** the system SHALL call `POST /rest/api/3/workflows` with `{"workflowIds": [<id>]}`
- **AND** return the workflow with its transitions and rules

#### Scenario: Preview workflow document
- **WHEN** the user calls `preview_workflow(workflow_id)` (or with `project_key` + `issue_type_id`)
- **THEN** the system SHALL call `POST /rest/api/3/workflows/preview` with the workflow ID
- **AND** return a dict with `workflows[0]`, `statuses`, and `version` fields
- **AND** include the full layout coordinates, status reference UUIDs, and transition links

#### Scenario: GET fallback is graceful
- **WHEN** the deprecated `GET /rest/api/3/workflows/{id}` returns 404
- **THEN** the system SHALL NOT raise; it SHALL return the bulkGet result and treat the 404 as "no extra data"
- **AND** log a debug-level message identifying the workflow as new-editor-only

### Requirement: Detect project type and editor scope

The system SHALL expose helpers to detect whether a project is team-managed and whether its workflow is editable by the calling identity.

#### Scenario: Detect team-managed project
- **WHEN** the user calls `is_team_managed_project(project_key)`
- **THEN** the system SHALL call `GET /rest/api/3/project/{project_key}` with `expand=projectTypeKey` (or equivalent)
- **AND** return `True` if `style == "next-gen"` or `simplified == True`
- **AND** return `False` for company-managed projects
- **AND** return `False` on any error fetching project metadata (fail-soft)

#### Scenario: Capability check for team-managed workflow edits
- **WHEN** the user calls `can_edit_team_managed_workflow(project_key)`
- **THEN** the system SHALL call `GET /rest/api/3/workflows/capabilities` for the project + issue type
- **AND** return `True` if `editorScope == "PROJECT"` AND the calling identity has `Administer projects`
- **AND** return `False` if the workflow is on a shared global scheme (would require `Administer Jira`)
- **AND** return `False` if the workflow is still on the legacy editor

#### Scenario: Editor scope fallback
- **WHEN** the `/workflows/capabilities` endpoint is unavailable
- **THEN** the system SHALL fall back to `editorScope` returned in the preview/search response
- **AND** raise `UnsupportedWorkflowEditorError` only when a write is attempted against a legacy-editor workflow

### Requirement: Add a Field Required validator to an existing transition (extended)

The system SHALL add a `system:validate-field-value` validator with `ruleType: fieldRequired` to enforce required fields, using the new-editor payload shape. The implementation MUST support both company-managed and team-managed project workflows.

This requirement extends the existing "Add Field Required validator to transition" requirement. The original behavior (call `POST /rest/api/3/workflows/update`, idempotency, optimistic locking) is preserved; this delta adds the team-managed and new-editor support, and replaces the legacy `TeamManagedProjectError` with finer-grained errors.

#### Scenario: Add validator to company-managed transition
- **WHEN** the user calls `apply_validator(project_key, from_status, to_status, field_names)` against a company-managed project
- **THEN** the system SHALL build a full new-editor payload
- **AND** call `POST /rest/api/3/workflows/update` with the validator attached to the target transition
- **AND** include the current `version.id` and `versionNumber` for optimistic locking
- **AND** include all existing transitions in the payload (the new editor requires the full document)
- **AND** generate per-request `statusReference` UUIDs for each status

#### Scenario: Add validator to team-managed transition
- **WHEN** the user calls `apply_validator(project_key, ...)` against a team-managed project with `editorScope == "PROJECT"`
- **THEN** the system SHALL build the same new-editor payload
- **AND** call `POST /rest/api/3/workflows/update` with the same payload shape
- **AND** succeed (the new editor supports both project types)

#### Scenario: Validator already exists (idempotency)
- **WHEN** a validator with the same `ruleKey` and `fieldsRequired` already exists on the transition
- **THEN** the system SHALL skip adding a duplicate validator
- **AND** return a dict with `already_configured: True` and the matched validator

#### Scenario: Permission denied on team-managed workflow
- **WHEN** the user calls `apply_validator(...)` against a team-managed project whose workflow is on a shared global scheme
- **THEN** the system SHALL raise `TeamManagedEditNotPermittedError` with a remediation hint ("ask a Jira admin to grant Administer Jira, or edit the workflow in the Jira UI for this project")
- **AND** NOT call the update endpoint

#### Scenario: Legacy editor payload rejection
- **WHEN** the user calls `apply_validator(...)` against a workflow still on the legacy editor
- **THEN** the system SHALL raise `UnsupportedWorkflowEditorError`
- **AND** recommend using the Jira UI for the duration of the editor migration

#### Scenario: Validation fails (version conflict)
- **WHEN** the workflow `version.versionNumber` has changed since retrieval
- **THEN** the system SHALL return `VersionConflictError` with the conflict details
- **AND** suggest re-running `preview_workflow()` to refresh the state

### Requirement: Create a new transition

The system SHALL add a new transition to a workflow via the new-editor `workflows/update` endpoint.

#### Scenario: Add DIRECTED transition
- **WHEN** the user calls `add_transition(workflow_id, from_status, to_status, transition_name)`
- **THEN** the system SHALL resolve the status names to numeric IDs via `GET /rest/api/3/status`
- **AND** detect duplicate transitions via `find_transition()` and raise `TransitionAlreadyExistsError` if a match exists
- **AND** build a new-editor payload with the new transition (`type: DIRECTED`)
- **AND** call `POST /rest/api/3/workflows/update`
- **AND** include all existing transitions in the payload

#### Scenario: Add GLOBAL transition
- **WHEN** the user calls `add_transition(..., transition_type="GLOBAL")`
- **THEN** the system SHALL build a transition with `type: GLOBAL` (no `fromStatusReference`)
- **AND** use the numeric `toStatusReference` directly (no `fromStatusReference`)

#### Scenario: Discover new transition ID after creation
- **WHEN** the create call succeeds
- **THEN** the system SHALL re-fetch the workflow via `preview_workflow()`
- **AND** find the new transition by name match (fallback: highest numeric ID)
- **AND** return the discovered ID

### Requirement: Add a transition with a validator in one call

The system SHALL provide a combined entry point that creates a transition and attaches a field-required validator in a single logical call.

#### Scenario: Combined create + attach on company-managed project
- **WHEN** the user calls `apply_add_transition_with_validator(project_key, from_status, to_status, transition_name, field_names)`
- **THEN** the system SHALL resolve all IDs and run a duplicate check
- **AND** call `add_transition()` to create the transition
- **AND** re-fetch the workflow to discover the new transition ID
- **AND** call `add_validator()` to attach the field-required validator
- **AND** return a unified result dict with `transition_id`, `add_transition_response`, `add_validator_response`

#### Scenario: Combined create + attach on team-managed project
- **WHEN** the user calls the same method against a team-managed project
- **THEN** the system SHALL execute the same flow (the new editor supports it)
- **AND** raise `TeamManagedEditNotPermittedError` only if the workflow is on a shared global scheme

#### Scenario: Dry-run combined create + attach
- **WHEN** the user passes `dry_run=True`
- **THEN** the system SHALL resolve all IDs and check duplicates
- **AND** return a `status: "dry_run"` result dict without making any write calls

### Requirement: Validate payload shape before commit

The system SHALL expose a helper that uses the server-side `validationOptions` to dry-run the payload shape before committing the update.

#### Scenario: Validate a well-formed payload
- **WHEN** the user calls `validate_update_payload(payload)`
- **THEN** the system SHALL call `POST /rest/api/3/workflows/update?validationOptions=ERROR,WARNING`
- **AND** return `{"valid": True, "errors": [], "warnings": []}` if the payload is accepted

#### Scenario: Validate a malformed payload
- **WHEN** the user calls `validate_update_payload(payload)` with a payload missing a required field
- **THEN** the system SHALL call the same endpoint
- **AND** return `{"valid": False, "errors": [...], "warnings": [...]}` listing the server-side validation errors
- **AND** raise `ValidationError` if `raise_on_error=True` is set

#### Scenario: `apply()` automatically validates
- **WHEN** the user calls `apply()` (or `apply_add_transition_with_validator()`)
- **THEN** the system SHALL call `validate_update_payload()` automatically before the real `update` call
- **AND** raise `ValidationError` on any ERROR-level finding, so the user does not commit a broken payload

### Requirement: CLI exposes team-managed and transition-creation commands

The system SHALL provide CLI commands for the new entry points.

#### Scenario: Preview workflow command
- **WHEN** user runs `jira workflow preview --workflow-id <id>`
- **THEN** the system SHALL call `preview_workflow()` and output the full new-editor workflow document

#### Scenario: Add transition command
- **WHEN** user runs `jira workflow add-transition --project PROJ --from "In Progress" --to "Code Review" --name "Code Review"`
- **THEN** the system SHALL create the transition and output the discovered transition ID

#### Scenario: Add transition with validator command
- **WHEN** user runs `jira workflow add-transition-with-validator --project PROJ --from "In Progress" --to "Code Review" --name "Code Review" --fields "Developer,Dev in Charge"`
- **THEN** the system SHALL execute the combined create + attach flow and output the result

#### Scenario: Validate payload command
- **WHEN** user runs `jira workflow validate-payload --file payload.json`
- **THEN** the system SHALL call `validate_update_payload()` and exit 0 on valid, non-zero on invalid (with errors printed)

#### Scenario: Add-validator --dry-run now server-validates
- **WHEN** user runs `jira workflow add-validator --project PROJ --from "In Progress" --to "Code Review" --fields "Developer,Dev in Charge" --dry-run`
- **THEN** the system SHALL call `validate_update_payload()` against the server
- **AND** output the validation result and the would-be payload diff

### Requirement: Detect pre-existing broken rules in a workflow

The system SHALL provide a diagnostic helper that identifies pre-existing broken rules in a project's workflow without applying any change.

#### Scenario: Detect broken rules via structured validation

- **WHEN** the user calls `has_broken_rules(project_key)`
- **THEN** the system SHALL build a would-be validator payload
- **AND** call `POST /rest/api/3/workflows/update/validation` (the structured validation endpoint)
- **AND** parse the response into `server_only_rule_ids` (codes `MISSING_RULE_PARAMETER`) and `invalid_config_rule_ids` (codes `INVALID_RULE_CONFIGURATION`)
- **AND** return a dict with `valid`, `errors`, `warnings`, `server_only_rule_ids`, `invalid_config_rule_ids`, and `has_broken_rules` (bool)

#### Scenario: No workflow found

- **WHEN** the user calls `has_broken_rules(project_key)` for a project with no workflow
- **THEN** the system SHALL return `has_broken_rules: True` with `errors: ["No workflow found for project {key}"]`

#### Scenario: Workflow has no transitions

- **WHEN** the user calls `has_broken_rules(project_key)` and the project's workflow has no transitions
- **THEN** the system SHALL return `has_broken_rules: False` (no rules to break)

### Requirement: History-based workflow repair

The system SHALL provide helpers to read and restore past versions of a workflow via the Jira Workflow History API (`/rest/api/3/workflow/history` and `/rest/api/3/workflow/history/list`).

#### Scenario: List available history versions

- **WHEN** the user calls `list_workflow_history(workflow_id)`
- **THEN** the system SHALL call `POST /rest/api/3/workflow/history/list` with `{"workflowId": <id>}`
- **AND** return a list of versioned entries (newest first)

#### Scenario: Read a specific history version

- **WHEN** the user calls `get_workflow_history(workflow_id, version=0)`
- **THEN** the system SHALL call `POST /rest/api/3/workflow/history` with `{"workflowId": <id>, "version": 0}`
- **AND** return the workflow document at that version (in the legacy `rules.conditionsTree` format)
- **AND** return `None` if the version is not available

#### Scenario: Detect a clean history version

- **WHEN** the user calls `has_clean_history(workflow_id, version=0)`
- **THEN** the system SHALL return `True` if the version is retrievable AND every transition has no conditions/validators with empty required parameters
- **AND** return `False` if the version is not available OR contains any broken rule

#### Scenario: Identify a project as recoverable

- **WHEN** the user calls `is_recoverable_via_history(project_key, history_version=0)`
- **THEN** the system SHALL return `True` when the project is team-managed, has a workflow, and the specified history version is clean
- **AND** return `False` otherwise

#### Scenario: Revert a workflow to a history version (dry-run)

- **WHEN** the user calls `revert_to_history(workflow_id, project_key, history_version=0, dry_run=True)`
- **THEN** the system SHALL read the history version, convert the legacy `rules.conditionsTree` format to the new editor's `conditions` block, and submit via `POST /rest/api/3/workflows/update?validationOptions=ERROR,WARNING`
- **AND** return a result dict with `status: "dry_run"`, `valid`, `errors`, `warnings`, and `from_version`
- **AND** NOT commit any change

#### Scenario: Revert a workflow to a history version (apply)

- **WHEN** the user calls `revert_to_history(workflow_id, project_key, history_version=0, dry_run=False)`
- **AND** the dry-run passed validation
- **THEN** the system SHALL submit the converted payload to `POST /rest/api/3/workflows/update`
- **AND** return a result dict with `status: "applied"`, `from_version`, `to_version`, and the API response

#### Scenario: Revert fails when history has fewer statuses

- **WHEN** the user calls `revert_to_history()` for a workflow whose current version has more statuses than the history version
- **THEN** the server SHALL reject the update with a "statusMappings" error
- **AND** the SDK SHALL surface this in `result["valid"] == False` with the error message in `result["errors"]`
- **AND** the caller SHALL treat this as a permanent limitation (manual UI cleanup required)

#### Scenario: Revert fails when history version is missing

- **WHEN** the user calls `revert_to_history()` with a `history_version` that is not available
- **THEN** the system SHALL raise `WorkflowNotFoundError`

### Requirement: Auto-repair broken workflows on apply

The system SHALL provide an opt-in mode where `apply()` automatically attempts a history-based repair when the server rejects a validator payload with `MISSING_RULE_PARAMETER` errors.

#### Scenario: Auto-repair enabled via environment

- **WHEN** the user sets `JIRA_SKILL_AUTO_REPAIR_HISTORY=1`
- **AND** the project has a clean v0 history
- **THEN** the system SHALL pre-flight validate the would-be payload
- **AND** on `MISSING_RULE_PARAMETER` errors, call `revert_to_history(dry_run=False)` first
- **AND** retry the original `add_validator()` after the revert succeeds

#### Scenario: Auto-repair is opt-in

- **WHEN** the user does NOT set `JIRA_SKILL_AUTO_REPAIR_HISTORY=1`
- **THEN** the system SHALL NOT attempt any history-based repair
- **AND** the original `MISSING_RULE_PARAMETER` errors SHALL propagate to the caller

#### Scenario: Auto-repair fails gracefully

- **WHEN** the auto-repair revert does not validate
- **THEN** the system SHALL log a warning with the dry-run errors
- **AND** let the original `add_validator()` call fail with its server-side error
- **AND** NOT raise a new exception

### Requirement: CLI exposes history-repair commands

The system SHALL provide CLI commands for the history-based repair entry points.

#### Scenario: Revert-history command

- **WHEN** user runs `jira workflow revert-history --project PROJ`
- **THEN** the system SHALL run `revert_to_history(dry_run=True)` and print the validation result
- **AND** exit 0 if the dry-run validates, non-zero otherwise

#### Scenario: Revert-history --apply

- **WHEN** user runs `jira workflow revert-history --project PROJ --apply`
- **THEN** the system SHALL run `revert_to_history(dry_run=False)` and print the before/after version numbers

#### Scenario: Revert-history --version N

- **WHEN** user runs `jira workflow revert-history --project PROJ --version 2`
- **THEN** the system SHALL use history version 2 (instead of default 0)

#### Scenario: Workflow history command

- **WHEN** user runs `jira workflow history --project PROJ`
- **THEN** the system SHALL print the v0 history summary (status count, transition count, broken rules count, clean bool)

#### Scenario: Check-broken-rules command

- **WHEN** user runs `jira workflow check-broken-rules --project PROJ`
- **THEN** the system SHALL call `has_broken_rules()` and print the structured error report
- **AND** if the project is recoverable, print the recommended `workflow revert-history` command
