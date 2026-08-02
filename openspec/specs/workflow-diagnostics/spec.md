# workflow-diagnostics Specification

## Purpose

Provides CLI commands for operational troubleshooting of Jira workflows: preview, validation, history, broken-rule detection, and fixing stuck issues.

## Requirements

### Requirement: Preview workflow document
The system SHALL provide a CLI command to preview a workflow's current state.

#### Scenario: Preview workflow by ID
- **WHEN** the user runs `jira workflow preview --workflow-id <id>`
- **THEN** the system calls `POST /rest/api/3/workflows/preview` with the workflow ID
- **AND** displays the workflow name, ID, version, status count, and transition count
- **AND** supports optional `--project` and `--issue-type` filters

#### Scenario: Preview nonexistent workflow
- **WHEN** the user previews a workflow that does not exist
- **THEN** the system displays "Workflow not found" with the workflow ID
- **AND** exits with code 1

### Requirement: Validate transition validator payload
The system SHALL provide a CLI command to validate a field-required validator payload before applying it.

#### Scenario: Validate with required/optional fields
- **WHEN** the user runs `jira workflow validate --project PROJ --required "Developer" --optional "Reviewer"`
- **THEN** the system calls the validator with the specified field requirements
- **AND** displays "Payload valid" with warning count on success
- **AND** displays "Payload invalid" with error details on failure

#### Scenario: Validate with legacy --fields flag
- **WHEN** the user runs `jira workflow validate --project PROJ --fields "Developer,Reviewer"`
- **THEN** all fields are treated as required
- **AND** `--fields` is mutually exclusive with `--required`/`--optional`

### Requirement: Add transition to workflow
The system SHALL provide a CLI command to add a transition to an existing workflow.

#### Scenario: Add transition with status references
- **WHEN** the user runs `jira workflow add-transition --workflow-id <id> --from <status> --to <status> --name "Start Review"`
- **THEN** the system calls `POST /rest/api/3/workflows/update` with the transition definition
- **AND** preserves all existing transitions in the workflow
- **AND** handles version conflicts by re-fetching and retrying

### Requirement: Validate workflow create payload
The system SHALL provide a CLI command to validate a workflow creation payload.

#### Scenario: Validate payload before creation
- **WHEN** the user runs `jira workflow validate-payload` with a JSON payload file
- **THEN** the system calls `POST /rest/api/3/workflows/create/validation`
- **AND** reports validation errors or confirms the payload is valid

### Requirement: View and revert workflow history
The system SHALL provide CLI commands to view and revert workflow changes.

#### Scenario: View workflow change history
- **WHEN** the user runs `jira workflow history --workflow-id <id>`
- **THEN** the system displays the change history for the workflow
- **AND** shows version numbers, timestamps, and change descriptions

#### Scenario: Revert workflow to previous version
- **WHEN** the user runs `jira workflow revert-history --workflow-id <id> --version <n>`
- **THEN** the system reverts the workflow to the specified version
- **AND** displays the revert result

### Requirement: Check for broken workflow rules
The system SHALL provide a CLI command to detect broken workflow rules.

#### Scenario: Check rules for a workflow
- **WHEN** the user runs `jira workflow check-broken-rules --workflow-id <id>`
- **THEN** the system inspects the workflow for broken validators, conditions, or post-functions
- **AND** reports any broken rules with their transition and rule type

### Requirement: Fix stuck issues
The system SHALL provide a CLI command to fix issues stuck in a status with no available transitions.

#### Scenario: Fix stuck issue with available transition
- **WHEN** the user runs `jira workflow fix-stuck --issue PUB-79 --target Done`
- **THEN** the system fetches the issue's current status and available transitions
- **AND** if a transition to the target status exists, executes it
- **AND** displays "Success!" with the target status name

#### Scenario: Fix stuck issue with no transitions
- **WHEN** the user runs the fix-stuck command and no transitions are available
- **THEN** the system displays "No transitions available - need to update workflow"
- **AND** suggests using the Jira Web UI to add the transition

#### Scenario: Dry-run fix-stuck
- **WHEN** the user runs `jira workflow fix-stuck --issue PUB-79 --dry-run`
- **THEN** the system displays what changes would be made without applying them
