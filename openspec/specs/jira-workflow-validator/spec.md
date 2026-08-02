# jira-workflow-validator Specification

## Purpose

Define the jira-workflow-validator capability: a CLI tool that programmatically adds Jira Workflow transition validators via REST API v3 to enforce required fields before specific status transitions.

## Requirements

### Requirement: Discover field IDs programmatically
The system SHALL provide a way to map field names to their Jira custom field IDs without manual lookup.

#### Scenario: Get all fields
- **WHEN** the user requests field discovery for a project
- **THEN** the system SHALL call `GET /rest/api/3/field` and return a list of all fields
- **AND** filter results to show only custom fields (fields where `custom: true`)

#### Scenario: Find specific field by name
- **WHEN** the user searches for a field by name (e.g., "Developer")
- **THEN** the system SHALL return the field ID (e.g., `customfield_10020`)
- **AND** return `None` if no matching field is found

#### Scenario: Resolve multiple field names to IDs
- **WHEN** the user provides a list of field names to resolve
- **THEN** the system SHALL return a dict mapping each name to its ID
- **AND** report any fields that could not be found

### Requirement: Discover workflows and transitions
The system SHALL retrieve workflow information including transitions to identify target transitions.

#### Scenario: List available workflows
- **WHEN** the user requests a list of workflows
- **THEN** the system SHALL call `GET /rest/api/3/workflows/search?expand=transitions.rules`
- **AND** return workflows with their entity IDs, names, and version numbers

#### Scenario: Find transition by status names
- **WHEN** the user specifies `from_status="In Progress"` and `to_status="Code Review"`
- **THEN** the system SHALL find the matching transition in the workflow
- **AND** return the transition ID, name, and current validators

#### Scenario: Get workflow by ID
- **WHEN** the user provides a workflow entity ID
- **THEN** the system SHALL call `POST /rest/api/3/workflows` with the workflow ID
- **AND** expand transitions with their rules

#### Scenario: Preview workflow document (new editor)
- **WHEN** the user requests a workflow document for inspection
- **THEN** the system SHALL call `POST /rest/api/3/workflows/preview` with `{"workflowIds": [workflow_id]}`
- **AND** return the full new-editor document (statuses, layouts, transitions, links, version)
- **AND** for project-scoped reads, accept `{"projectAndIssueTypes": [{"projectId": "<id>", "issueTypeId": "<id>"}]}` instead of `workflowIds`

### Requirement: Check existing validators (idempotency)
The system SHALL check for existing validators before adding new ones to ensure idempotent execution.

#### Scenario: Validator already exists
- **WHEN** a validator with the same `ruleKey` and `fieldsRequired` already exists on the transition
- **THEN** the system SHALL skip adding a duplicate validator
- **AND** return a message indicating the validator already exists

#### Scenario: No matching validator
- **WHEN** no matching validator exists on the transition
- **THEN** the system SHALL proceed to add the new validator

### Requirement: Add Field Required validator to transition
The system SHALL add a `system:validate-field-value` validator with `ruleType: fieldRequired` to enforce required fields.

#### Scenario: Add validator successfully
- **WHEN** the transition does not have the required validator
- **THEN** the system SHALL call `POST /rest/api/3/workflows/update` with the validator payload
- **AND** include the current workflow version for optimistic locking

#### Scenario: Validation fails (version conflict)
- **WHEN** the workflow version has changed since retrieval
- **THEN** the system SHALL return an error with the conflict details
- **AND** suggest re-running to refresh the workflow state

### Requirement: Distinguish required and optional fields
The system SHALL allow callers to specify which fields are required and which are optional on a transition. Fields marked `required=true` are enforced via `system:validate-field-value` with `ruleType: fieldRequired`; fields marked `required=false` are recorded in the result metadata but are NOT included in the `fieldsRequired` validator parameter (i.e., they remain optional and are not enforced).

#### Scenario: All fields required (default)
- **WHEN** the caller passes `field_names=["Developer", "Dev in Charge"]` (legacy form, no per-field flag)
- **THEN** the system SHALL treat every field as required
- **AND** the resulting validator payload SHALL include both field IDs in `fieldsRequired`

#### Scenario: Mix of required and optional fields
- **WHEN** the caller passes `field_requirements=[{"name": "Developer", "required": False}, {"name": "Dev in Charge", "required": True}]`
- **THEN** the resulting validator payload SHALL include ONLY the `Dev in Charge` field ID in `fieldsRequired`
- **AND** the result metadata SHALL list BOTH fields with their required/optional flag
- **AND** the error message SHALL mention ONLY the required fields

#### Scenario: All fields optional
- **WHEN** the caller passes `field_requirements=[{"name": "Developer", "required": False}, {"name": "Dev in Charge", "required": False}]`
- **THEN** the system SHALL return a result with `no_required_fields: true` and a clear warning
- **AND** SHALL NOT submit any update to Jira
- **BECAUSE** a `fieldRequired` validator with zero required fields is a no-op and an unnecessary round-trip

#### Scenario: Backward compatibility
- **WHEN** existing callers use the legacy `field_names=[...]` form without the `required` flag
- **THEN** the system SHALL behave identically to v1.2 (every field treated as required)
- **AND** existing CLI invocations SHALL continue to work without changes

### Requirement: Idempotency checks the required subset only
The system SHALL compare the existing `fieldRequired` validator's `fieldsRequired` set against the *required* subset of the caller's fields. Optional fields SHALL be ignored for idempotency comparison.

#### Scenario: Validator already exists with the same required fields
- **WHEN** the transition has a `fieldRequired` validator whose `fieldsRequired` exactly matches the caller's required fields
- **THEN** the system SHALL skip adding a duplicate validator
- **AND** return a message indicating the validator already exists

#### Scenario: Validator exists with a different required subset
- **WHEN** the transition has a `fieldRequired` validator but the existing `fieldsRequired` differs from the caller's required subset
- **THEN** the system SHALL proceed to add a new validator with the caller's required fields
- **AND** the existing validator SHALL be left in place (the new one is added, not replaced)

### Requirement: Provide CLI interface
The system SHALL provide a CLI command for the workflow validator functionality.

#### Scenario: Discover fields command
- **WHEN** user runs `jira workflow discover --field "Developer"`
- **THEN** the system SHALL output the field ID and any matches

#### Scenario: List workflows command
- **WHEN** user runs `jira workflow list`
- **THEN** the system SHALL output a table of workflows with IDs and names

#### Scenario: Add validator command (dry-run)
- **WHEN** user runs `jira workflow add-validator --project PROJ --from "In Progress" --to "Code Review" --fields "Developer,Dev in Charge" --dry-run`
- **THEN** the system SHALL output the changes that WOULD be made without applying them

#### Scenario: Add validator command (apply)
- **WHEN** user runs `jira workflow add-validator --project PROJ --from "In Progress" --to "Code Review" --fields "Developer,Dev in Charge"`
- **THEN** the system SHALL apply the validator to the workflow
- **AND** output the result of the operation

### Requirement: Add a new transition with an attached validator
The system SHALL be able to add a brand-new transition to a workflow and attach a field-required validator in a single API call.

#### Scenario: Transition does not exist
- **WHEN** the user calls `add_transition` or `apply_add_transition_with_validator` for a transition that does not exist
- **THEN** the system SHALL construct a new transition with the specified `from` and `to` statuses
- **AND** attach a `system:validate-field-value` validator with `ruleType: fieldRequired` for the requested fields
- **AND** submit the full new-editor workflow document to `POST /rest/api/3/workflows/update`

#### Scenario: Transition already exists
- **WHEN** the user attempts to add a transition that is already present
- **THEN** the system SHALL raise `TransitionAlreadyExistsError` with a remediation hint

### Requirement: Server-side payload validation (dry-run)
The system SHALL provide a way to validate a would-be update payload against the server before applying it.

#### Scenario: Payload is valid
- **WHEN** the user calls `validate()` or `validate_update_payload(payload)` with a well-formed payload
- **THEN** the system SHALL call `POST /rest/api/3/workflows/update?validationOptions=ERROR,WARNING`
- **AND** return `{"valid": True, "errors": [], "warnings": []}`

#### Scenario: Payload is invalid
- **WHEN** the payload fails server-side validation
- **THEN** the system SHALL return `{"valid": False, "errors": [...], "warnings": [...]}`
- **AND** raise `ValidationError` if `raise_on_error=True`

### Requirement: Distinguish project and editor scope
The system SHALL distinguish between company-managed projects, team-managed projects with project-scoped schemes, team-managed projects with shared global schemes, and workflows still on the legacy editor.

#### Scenario: Company-managed project
- **WHEN** `is_team_managed_project(project_key)` returns `False`
- **THEN** the system SHALL allow the operation
- **AND** no additional editor-scope check is required

#### Scenario: Team-managed, project-scoped scheme
- **WHEN** `is_team_managed_project(project_key)` is `True`
- **AND** `can_edit_team_managed_workflow(project_key)` returns `True` (editorScope == "PROJECT")
- **THEN** the system SHALL allow the operation

#### Scenario: Team-managed, shared global scheme
- **WHEN** `is_team_managed_project(project_key)` is `True`
- **AND** `can_edit_team_managed_workflow(project_key)` returns `False` (editorScope == "GLOBAL")
- **THEN** the system SHALL raise `TeamManagedEditNotPermittedError`
- **AND** the error message SHALL include a remediation hint (use the Jira UI, or use a project-scoped scheme)

#### Scenario: Legacy editor
- **WHEN** the workflow metadata reports `editor == "legacy"`
- **THEN** the system SHALL raise `UnsupportedWorkflowEditorError`

### Requirement: Handle errors gracefully
The system SHALL provide clear error messages for common failure scenarios.

#### Scenario: Permission denied
- **WHEN** the user lacks admin permissions to modify workflows
- **THEN** the system SHALL return an error with a clear message about required permissions

#### Scenario: Rate limiting
- **WHEN** the API returns a 429 Too Many Requests
- **THEN** the system SHALL implement exponential backoff and retry
- **AND** log the retry attempts

#### Scenario: Network error
- **WHEN** a network error occurs during API call
- **THEN** the system SHALL return a clear error with the underlying cause

## API Reference

### Field Discovery Endpoint

```
GET /rest/api/3/field
```

Returns all fields. Filter for `custom: true` to get only custom fields.

### Field Requirement Model

The `field_requirements` parameter on `preview()`, `apply()`, and
`apply_add_transition_with_validator()` accepts a list of:

```python
class FieldRequirement:
    name: str       # Jira field display name
    required: bool  # True = field is required; False = optional
```

Callers may also pass the legacy `field_names: list[str]` form, which is
equivalent to passing `field_requirements=[{"name": n, "required": True} for n in field_names]`.

### Workflow Search Endpoint

```
GET /rest/api/3/workflows/search?expand=transitions.rules
```

Returns paginated list of workflows with their transitions and rules.

### Workflow Bulk Update Endpoint

```
POST /rest/api/3/workflows/update
```

The new unified-editor API requires a **full workflow document** (no partial PATCHes). The payload includes statuses with `statusReference` UUIDs, transitions with `fromStatusReference`/`toStatusReference`, and the current `version.id` for optimistic locking.

**Request Body (new editor shape):**
```json
{
  "workflows": [{
    "id": "<workflow-entity-id>",
    "version": {
      "id": "<version-uuid>",
      "versionNumber": <int>
    },
    "statuses": [
      {
        "statusReference": "10001",
        "name": "To Do",
        "layout": {"x": 0, "y": 0}
      }
    ],
    "transitions": [
      {
        "id": "11",
        "name": "Start Progress",
        "type": "global",
        "fromStatusReference": "10000",
        "toStatusReference": "10001",
        "validators": [
          {
            "ruleType": "fieldRequired",
            "type": "com.atlassian.jira.plugin.system.customfield:required",
            "configuration": {
              "fieldId": "customfield_10020",
              "errorMessage": "Developer is required"
            }
          }
        ]
      }
    ]
  }]
}
```

**Required Permissions:** `manage:jira-configuration` or `Administer Jira` global permission. For team-managed projects, the project must use a project-scoped workflow scheme (not a shared global scheme).

### Workflow Validation Endpoint (new editor)

```
POST /rest/api/3/workflows/update?validationOptions=ERROR,WARNING
```

Performs a server-side dry-run validation of a would-be update payload without applying it.

### Workflow Capabilities Endpoint

```
GET /rest/api/3/workflows/capabilities
```

Returns the `editorScope` for the current user/project. Values: `GLOBAL` (shared scheme, requires global admin), `PROJECT` (project-scoped, editable by project admin).

### Workflow Preview Endpoint (new editor)

```
POST /rest/api/3/workflows/preview
```

Reads the full new-editor workflow document. Accepts `{"workflowIds": [...]}` or `{"projectAndIssueTypes": [{"projectId": "...", "issueTypeId": "..."}]}`.

## CLI Command Structure

```
jira workflow [group] [command] [options]

Groups:
  workflow discover          Discover fields and workflows
  workflow list              List available workflows
  workflow status-list       List all Jira statuses with numeric IDs
  workflow transition-info   Show transitions and validators for a project's workflow
  workflow preview           Preview a workflow document via POST /workflows/preview
  workflow add-validator     Add validator to an existing transition
  workflow add-transition    Add a NEW transition (optionally with a validator)
  workflow validate          Server-side validate the would-be validator payload
  workflow validate-payload  Server-side validate a JSON payload from a file/stdin

Commands:
  jira workflow discover --field <name>                            Find field ID by name
  jira workflow list                                              List all workflows
  jira workflow status-list                                       List all Jira statuses
  jira workflow transition-info --project <key>                    Show transitions + validators
  jira workflow preview --workflow-id <id>                        Preview a workflow document
  jira workflow add-validator                                     Add required field validator
  jira workflow add-transition                                    Add a NEW transition + validator
  jira workflow validate --project <key> --from <s> --to <s>      Validate a would-be payload
  jira workflow validate-payload --input <file>                   Validate a JSON payload

Options:
  --project <key>          Target project key (required for project-scoped commands)
  --from <status>          Source status (default: "In Progress")
  --to <status>            Target status (default: "Code Review")
  --fields <names>         Comma-separated field names (legacy; treated as all-required)
  --required <names>       Comma-separated REQUIRED field names
  --optional <names>       Comma-separated OPTIONAL field names (recorded, not enforced)
  --dry-run                Preview without applying
  --error-message <msg>    Custom error message
  --workflow-id <id>       Workflow entity ID (for preview)
  --input <file>           Path to a JSON payload file (for validate-payload)

When mixing `--required` and `--optional`, the union of both sets is the full
set of field names. The `--required` subset is the one emitted in the
`fieldsRequired` validator parameter. If only `--optional` is given and no
required fields are present, the command prints a clear warning and exits
without making any API call.
```

## Implementation Notes

- Use `tdt_core.clients.jira.JiraClientFactory.from_env()` for authentication
- Field names are case-sensitive in Jira
- The new editor requires a full workflow document on every update — no partial PATCHes
- `statusReference` is a self-defined UUID (or numeric string) used to bind statuses to layout coordinates and transition endpoints
- Workflow `version.id` and `versionNumber` are required for optimistic locking
- `ignoreContext: true` is recommended for custom fields that may not be in all contexts
- The skill fails open on `editorScope == "GLOBAL"` for team-managed projects, and raises `TeamManagedEditNotPermittedError` (remediation: Jira UI or project-scoped scheme)
- `preview_workflow()` is the canonical way to read a workflow document for the new editor (not `GET /workflows/search` with expansion, which is the legacy shape)
