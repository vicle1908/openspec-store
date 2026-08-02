# workflow-crud Specification

## Purpose

Provides full CRUD operations for Jira workflows, workflow schemes, and global statuses via the Jira REST API v3. Covers creation, validation, scheme management, and async task polling.

## Requirements

### Requirement: Create workflow with statuses and transitions
The system SHALL create a new workflow with full status and transition definitions in a single API call.

#### Scenario: Create workflow via new endpoint
- **WHEN** the system calls `create_workflow_with_transitions(payload)`
- **THEN** it sends `POST /rest/api/3/workflows/create` with the full payload
- **AND** the payload includes statuses (with statusReference UUIDs), transitions, and scope
- **AND** retries up to 3 times on 409 version conflicts with 5-second delay

#### Scenario: Create workflow via legacy endpoint
- **WHEN** the system calls `create_workflow_with_status_ids(name, status_ids)`
- **THEN** it sends `POST /rest/api/3/workflow` with status IDs (no transitions)
- **AND** returns the created workflow entity

### Requirement: Validate workflow creation payload
The system SHALL validate a workflow creation payload before committing it.

#### Scenario: Pre-flight validation
- **WHEN** the system calls `validate_workflow_create(payload)`
- **THEN** it sends `POST /rest/api/3/workflows/create/validation`
- **AND** returns the validation response body from Jira
- **AND** callers can inspect errors before proceeding with creation

### Requirement: Create and manage workflow schemes
The system SHALL create workflow schemes and manage their lifecycle.

#### Scenario: Create workflow scheme
- **WHEN** the system calls `create_workflow_scheme(name, workflow_name, description=...)`
- **THEN** it sends `POST /rest/api/3/workflowscheme` with the scheme definition
- **AND** sets the specified workflow as the `defaultWorkflow`
- **AND** returns the created scheme payload

#### Scenario: Get workflow scheme version
- **WHEN** the system calls `get_workflow_scheme_version(project_key, workflow_name)`
- **THEN** it fetches the project with `expand=workflowScheme`
- **AND** returns the scheme's version dict with `id` and `versionNumber`
- **AND** falls back to searching all schemes if the project scheme is not found

### Requirement: Switch project workflow scheme
The system SHALL switch a company-managed project to a different workflow scheme.

#### Scenario: Switch scheme with status mappings
- **WHEN** the system calls `switch_project_scheme(project_id, target_scheme_id, status_mappings=...)`
- **THEN** it sends `POST /rest/api/3/workflowscheme/project/switch`
- **AND** includes `mappingsByIssueTypeOverride` when status mappings are provided
- **AND** returns a task payload for async processing

#### Scenario: Get required status mappings
- **WHEN** the system calls `get_required_status_mappings(scheme_id, target_scheme_config)`
- **THEN** it sends `POST /rest/api/3/workflowscheme/update/mappings`
- **AND** returns the mapping payload from Jira

### Requirement: Wait for async Jira tasks
The system SHALL poll Jira task URLs until they reach a terminal state.

#### Scenario: Task completes successfully
- **WHEN** the system calls `wait_for_task(task_url)`
- **THEN** it polls the task URL at 2-second intervals
- **AND** returns the final task payload when status is COMPLETE
- **AND** handles 404 on poll as successful completion (task cleaned up)

#### Scenario: Task fails or times out
- **WHEN** the task status is FAILED, CANCELLED, or DEAD
- **THEN** the system raises `JiraWorkflowError` with the failure message
- **AND** when the poll deadline (120s default) is exceeded, raises timeout error
