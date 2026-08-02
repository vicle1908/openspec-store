# jira-workflow-client-extensions Specification

## Purpose

Define `tdt_core.clients.jira_workflow`: the Jira REST API v3 extensions for managing workflow statuses across both team-managed and company-managed project styles.

## ADDED Requirements

### Requirement: Module location and imports

The `jira_workflow` module SHALL live at `tdt-core/src/tdt_core/clients/jira_workflow.py`. It SHALL be importable as `from tdt_core.clients.jira_workflow import TeamManagedWorkflowHandler, CompanyManagedWorkflowHandler`. It SHALL NOT import CLI dependencies (no `typer`, no `click`).

#### Scenario: Pure library import
- **WHEN** `from tdt_core.clients.jira_workflow import TeamManagedWorkflowHandler` is called
- **THEN** the import SHALL succeed with no CLI dependencies loaded

### Requirement: TeamManagedWorkflowHandler — get_statuses

`TeamManagedWorkflowHandler.get_statuses(project_key: str) -> list[Status]` SHALL call `GET /rest/api/3/project/{project_key}/statuses` and return a list of unique `Status` objects with `id`, `name`, and `statusCategory`.

The response is a list of issue-type blocks, each containing a `statuses` array. The same status record MAY appear under multiple issue types; the handler SHALL deduplicate by `id`.

#### Scenario: Fetch project statuses
- **WHEN** `TeamManagedWorkflowHandler.get_statuses("PDS")` is called
- **THEN** it SHALL call `GET /rest/api/3/project/PDS/statuses`
- **AND** return a list of `Status` objects with `id`, `name`, `statusCategory`
- **AND** the list SHALL contain each status ID at most once even if it appears under multiple issue types

### Requirement: TeamManagedWorkflowHandler — bulk_transition

`TeamManagedWorkflowHandler.bulk_transition(project_key: str, from_id: int, to_id: int) -> int` SHALL transition all issues in the given project from `from_id` to `to_id` and return the count of transitioned issues.

The implementation SHALL:

1. Call `POST /rest/api/3/search/jql` with `jql=project = "{key}" AND status = "{from_id}"` and paginate with `nextPageToken` to collect all matching issue keys.
2. For each issue, call `GET /rest/api/3/issue/{key}/transitions` to find the `transition.id` whose `to.id` equals `to_id`.
3. Group issue keys by transition ID; for each group, call `POST /rest/api/3/bulk/issues/transition` with `bulkTransitionInputs` (max 5 inputs per call).
4. Return the sum of `totalTransitions` across bulk responses.
5. If no issue has a transition path to `to_id`, raise `PartialTransitionError(failed_issue_keys=[...])` listing those keys.

`TeamManagedWorkflowHandler.bulk_transition_for_dedupe(project_key: str, loser_id: int, winner_id: int) -> int` SHALL call `bulk_transition` first, then call `DELETE /rest/api/3/statuses/{loser_id}`.

#### Scenario: Bulk transition with retry
- **WHEN** `bulk_transition("PDS", 10282, 10000)` is called
- **AND** any underlying HTTP call returns 429 (rate limit)
- **THEN** the handler SHALL back off 60 seconds and retry up to 3 times
- **AND** return the count of successfully transitioned issues

#### Scenario: Dedupe bulk transition
- **WHEN** `bulk_transition_for_dedupe("PDS", 10282, 10000)` is called
- **THEN** it SHALL call `bulk_transition("PDS", 10282, 10000)` first
- **AND** after successful transition, it SHALL call `DELETE /rest/api/3/statuses/10282`
- **AND** return the count of transitioned issues

#### Scenario: Partial success
- **WHEN** `bulk_transition` partially succeeds (some issues transitioned, some failed due to a missing transition path)
- **THEN** the handler SHALL return the count of successfully transitioned issues
- **AND** raise `PartialTransitionError` with the list of failed issue keys

### Requirement: TeamManagedWorkflowHandler — find_issues_in_status_grouped_by_project

`TeamManagedWorkflowHandler.find_issues_in_status_grouped_by_project(status_id: int) -> dict[str, list[str]]` SHALL run a JQL `status = {status_id}` search instance-wide, paginate via `nextPageToken`, and return a mapping of `project_key -> [issue_key, ...]` for every project that holds issues in the given status.

This is the primitive for instance-wide duplicate detection: a status record `X` may exist as a project-private record in many team-managed projects; collapsing all of them requires finding which projects actually use `X` so the dedupe command can fan out per-project transitions.

#### Scenario: Discover projects using a status
- **WHEN** `find_issues_in_status_grouped_by_project(10000)` is called and 3 projects (SR, PWM, WD) have issues currently in status `10000`
- **THEN** it SHALL return `{"SR": ["SR-1", "SR-2"], "PWM": ["PWM-5"], "WD": ["WD-9"]}`
- **AND** it SHALL NOT call any Jira write API

### Requirement: CompanyManagedWorkflowHandler — create_workflow

`CompanyManagedWorkflowHandler.create_workflow(name: str, statuses: list[int]) -> str` SHALL create a new Jira workflow in the company-managed style, referencing the supplied status record IDs, and return the workflow entity ID.

The `statuses` parameter is a list of Jira status record IDs (not `Status` objects) because the company-managed workflow API takes IDs, not full status payloads.

#### Scenario: Create workflow with canonical statuses
- **WHEN** `create_workflow("PDS-clean", [10000, 3, 10014])` is called
- **THEN** it SHALL call `POST /rest/api/3/workflow` with a workflow payload referencing IDs `10000`, `3`, `10014`
- **AND** return the `entityId` of the created workflow

### Requirement: CompanyManagedWorkflowHandler — bulk_transition (project-scoped)

`CompanyManagedWorkflowHandler.bulk_transition(project_key: str, from_id: int, to_id: int) -> int` SHALL transition all issues in a single company-managed project from `from_id` to `to_id`. It delegates to the same per-project JQL and bulk transition flow as the team-managed handler.

#### Scenario: Global dedupe affects all company-managed projects
- **WHEN** the company-managed "Done" cluster has 3 records: ids 10538, 10014, 10610
- **AND** projects CFD, CFDAHP, and CFDBO all reference some of these
- **THEN** the dedupe command SHALL iterate projects CFD, CFDAHP, CFDBO via `find_issues_in_status_grouped_by_project`
- **AND** call `bulk_transition(project_key="CFD", from_id=10538, to_id=10014)` for each (project, loser) pair
- **AND** the loser's `/rest/api/3/statuses/{id}` delete is performed once at the cluster level (global)

### Requirement: CompanyManagedWorkflowHandler — assign_workflow_scheme

`CompanyManagedWorkflowHandler.assign_workflow_scheme(project_key: str, workflow_entity_id: str, issue_type_ids: list[str]) -> None` SHALL assign the created workflow to the project via a workflow scheme.

#### Scenario: Assign workflow scheme
- **WHEN** `assign_workflow_scheme("CFD", "workflow-entity-123", ["10001", "10002"])` is called
- **THEN** it SHALL call `PUT /rest/api/3/workflowscheme/{scheme_id}/draft` with the mapping
- **AND** raise `WorkflowSchemeAssignmentError` if the scheme assignment fails

### Requirement: Error types

The module SHALL define the following exception classes:

- `WorkflowAPIError`: base class for all workflow API errors
- `PartialTransitionError(WorkflowAPIError)`: raised when some issues fail to transition; exposes `failed_issue_keys: list[str]`
- `RateLimitError(WorkflowAPIError)`: raised when all retries are exhausted
- `WorkflowSchemeAssignmentError(WorkflowAPIError)`: raised when scheme assignment fails

#### Scenario: PartialTransitionError carries failed keys
- **WHEN** `bulk_transition` partially succeeds with failed keys `["PDS-42", "PDS-99"]`
- **THEN** `PartialTransitionError.failed_issue_keys` SHALL be `["PDS-42", "PDS-99"]`

### Requirement: Session injection

Both handlers SHALL accept a `PatchedJira` client in their constructor and use it for all HTTP calls. The handler SHALL read `client._session` for HTTP transport and `client.url` for the base URL. No handler SHALL create its own `requests.Session`.

#### Scenario: Session sharing
- **WHEN** `TeamManagedWorkflowHandler(client=jira_client)` is instantiated
- **THEN** it SHALL use `jira_client._session` for all HTTP calls
- **AND** no new session shall be created internally

### Requirement: Status endpoint note (delete)

`TeamManagedWorkflowHandler.delete_status(project_key: str, status_id: int)` SHALL call `DELETE /rest/api/3/statuses/{status_id}` — the modern global endpoint that replaced the legacy `DELETE /rest/api/3/project/{key}/workflow/statuses/{id}`. The `project_key` argument is reserved for future per-project routing and is currently unused (Atlassian's modern delete is global).

#### Scenario: Modern delete endpoint
- **WHEN** `delete_status("PDS", 10282)` is called
- **THEN** it SHALL call `DELETE /rest/api/3/statuses/10282`
- **AND** the `PDS` argument SHALL be ignored for routing
