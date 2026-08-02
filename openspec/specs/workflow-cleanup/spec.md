# workflow-cleanup Specification

## Purpose

Provides bulk-delete operations for inactive Jira workflows, orphaned workflow schemes, and duplicate global statuses. Enables operational cleanup of workflow artifacts that are no longer in use.

## Requirements

### Requirement: List all workflows across all pages
The system SHALL provide a method to list all workflows with full pagination support.

#### Scenario: Paginated workflow listing
- **WHEN** the system calls `list_workflows_all()`
- **THEN** it fetches all workflows using `GET /rest/api/3/workflows/search` with pagination (maxResults=50)
- **AND** returns a complete list of workflow dicts with `id` and `name`
- **AND** handles multi-page responses by iterating until `isLast` is true

### Requirement: Delete inactive workflows
The system SHALL delete workflows that are inactive (not associated with any workflow scheme).

#### Scenario: Delete a single inactive workflow
- **WHEN** the system calls `delete_workflow(entity_id)`
- **THEN** it sends `DELETE /rest/api/3/workflow/{entityId}`
- **AND** raises `JiraWorkflowError` if the workflow is active or system-owned

#### Scenario: Find inactive workflows
- **WHEN** the system calls `find_inactive_workflows()`
- **THEN** it attempts `DELETE` on each workflow and catches failure
- **AND** returns only workflows where the delete succeeds (status 204)
- **AND** reverses the delete for workflows that were successfully deleted during probe

#### Scenario: Bulk delete inactive workflows
- **WHEN** the system calls `delete_inactive_workflows()`
- **THEN** it iterates all workflows and attempts `DELETE` on each
- **AND** returns a list of successfully deleted workflow names

### Requirement: List and delete workflow schemes
The system SHALL provide CRUD operations for workflow schemes.

#### Scenario: Paginated scheme listing
- **WHEN** the system calls `list_workflow_schemes_all()`
- **THEN** it fetches all schemes using `GET /rest/api/3/workflowscheme` with pagination
- **AND** returns a complete list of scheme dicts with `id` and `name`

#### Scenario: Delete a workflow scheme
- **WHEN** the system calls `delete_workflow_scheme(scheme_id)`
- **THEN** it sends `DELETE /rest/api/3/workflowscheme/{id}`
- **AND** raises `JiraWorkflowError` on failure

#### Scenario: Find orphaned workflow schemes
- **WHEN** the system calls `find_inactive_workflow_schemes()`
- **THEN** it fetches all schemes and checks each for `projectAssociations`
- **AND** returns only schemes with no project associations

#### Scenario: Bulk delete orphaned schemes
- **WHEN** the system calls `delete_inactive_workflow_schemes()`
- **THEN** it iterates all schemes, checks project associations, and deletes orphaned ones
- **AND** returns a list of deleted scheme names

### Requirement: Delete global statuses
The system SHALL delete global Jira statuses by ID or name.

#### Scenario: Delete statuses by ID
- **WHEN** the system calls `delete_statuses(status_ids)`
- **THEN** it sends `DELETE /rest/api/3/statuses?id=...&id=...` in chunks of 50
- **AND** returns a list of successfully deleted status IDs
- **AND** silently skips statuses that are in use

#### Scenario: Find statuses by name
- **WHEN** the system calls `find_deletable_statuses(name)`
- **THEN** it sends `GET /rest/api/3/status?search={name}`
- **AND** returns all statuses with an exact name match

#### Scenario: Delete all statuses with a given name
- **WHEN** the system calls `delete_all_statuses_by_name(name)`
- **THEN** it finds all matching statuses and deletes them by ID
- **AND** returns a list of deleted status IDs
