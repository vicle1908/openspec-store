# pub-reject-transitions Specification

## Purpose

Add reject/duplicate ticket support to the PUB project workflow, matching TJ's `Rejected/Duplicated` status pattern. Enables clean ticket lifecycle management when tickets are invalid, duplicate, or out of scope.

## Requirements

### Requirement: Rejected/Duplicated status in PUB workflow
The system SHALL have a `Rejected/Duplicated` status with `Done` category in the PUB project workflow.

#### Scenario: Status exists in workflow
- **WHEN** the PUB workflow is queried
- **THEN** it includes a status named `Rejected/Duplicated` with status category `Done`
- **AND** the status is accessible from `To Do`, `In Progress`, and `Code Review` statuses

### Requirement: Reject transitions from active statuses
The system SHALL provide `Reject` transitions from `To Do`, `In Progress`, and `Code Review` to `Rejected/Duplicated`.

#### Scenario: Reject from To Do
- **WHEN** a ticket in `To Do` status is rejected
- **THEN** the system transitions it to `Rejected/Duplicated`
- **AND** sets the resolution to `Duplicate` or `Won't Fix` as appropriate
- **AND** clears the assignee

#### Scenario: Reject from In Progress
- **WHEN** a ticket in `In Progress` status is rejected
- **THEN** the system transitions it to `Rejected/Duplicated`
- **AND** sets the resolution field
- **AND** logs the rejection reason in a comment

#### Scenario: Reject from Code Review
- **WHEN** a ticket in `Code Review` status is rejected
- **THEN** the system transitions it to `Rejected/Duplicated`
- **AND** sets the resolution field

### Requirement: Reopen transition from Rejected/Duplicated
The system SHALL provide a `Reopen` transition from `Rejected/Duplicated` back to `To Do`.

#### Scenario: Reopen rejected ticket
- **WHEN** a ticket in `Rejected/Duplicated` status is reopened
- **THEN** the system transitions it to `To Do`
- **AND** clears the resolution field
- **AND** the ticket re-enters the normal workflow

### Requirement: Reject CLI command
The system SHALL provide a CLI command to reject a ticket.

#### Scenario: Reject with reason
- **WHEN** the user runs `jira workflow reject --issue PUB-XX --reason "duplicate"`
- **THEN** the system transitions the ticket to `Rejected/Duplicated`
- **AND** adds a comment with the rejection reason
- **AND** displays confirmation with the ticket's new status

#### Scenario: Reject without reason
- **WHEN** the user runs `jira workflow reject --issue PUB-XX`
- **THEN** the system transitions the ticket to `Rejected/Duplicated`
- **AND** adds a default comment "Ticket rejected"

#### Scenario: Reject already rejected ticket
- **WHEN** the user tries to reject a ticket already in `Rejected/Duplicated`
- **THEN** the system displays "Ticket is already rejected"
- **AND** exits with code 0

### Requirement: Reject API method on WorkflowClient
The system SHALL provide a `reject_issue()` method on `WorkflowClient`.

#### Scenario: Reject via API
- **WHEN** the system calls `reject_issue(issue_key, reason=None)`
- **THEN** it fetches the issue's current status
- **AND** verifies the status supports a reject transition
- **AND** executes the transition to `Rejected/Duplicated`
- **AND** sets resolution to `Duplicate` and clears assignee
- **AND** adds a comment with the reason (or default "Ticket rejected")
- **AND** returns the updated issue status

#### Scenario: Reject with invalid transition
- **WHEN** the issue's current status does not have a reject transition
- **THEN** the system raises `JiraWorkflowError` with message "Cannot reject from status {status}"

### Requirement: Workflow migration for reject transitions
The system SHALL create a new workflow with reject transitions and switch the project scheme.

#### Scenario: Create workflow with reject transitions
- **WHEN** the system creates a new workflow via `POST /rest/api/3/workflows/create`
- **THEN** it includes all existing transitions plus 3 new Reject transitions
- **AND** each Reject transition links from To Do, In Progress, or Code Review to Rejected/Duplicated
- **AND** references existing statuses by numeric ID for reuse

#### Scenario: Switch project scheme
- **WHEN** the system creates a new scheme and switches the project
- **THEN** it creates a scheme with the new workflow as default
- **AND** switches the project to use the new scheme
- **AND** all existing tickets gain the new Reject transition options
