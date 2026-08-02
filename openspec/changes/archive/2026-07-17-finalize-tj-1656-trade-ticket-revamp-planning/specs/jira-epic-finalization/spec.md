# Specification: Jira Epic Finalization

## ADDED Requirements

### Requirement: Epic planning completeness tracking

The system SHALL track epic planning completeness including story breakdown, estimation, and resource allocation.

#### Scenario: Epic with complete planning

- **WHEN** an epic has all child issues broken down from Draft status
- **THEN** the epic planning completeness SHALL be 100%

#### Scenario: Epic with incomplete planning

- **WHEN** an epic has Draft stories remaining
- **THEN** the epic SHALL display planning completeness percentage
- **AND** SHALL flag HIGH risk for planning incomplete

#### Scenario: Epic with missing story points

- **WHEN** any task in an epic lacks story points
- **THEN** the epic SHALL display count of unestimated tasks

### Requirement: Story point estimation standards

The system SHALL support Fibonacci-based story point estimation (1, 2, 3, 5, 8, 13) for all tasks.

#### Scenario: Apply story points to tasks

- **WHEN** a task is being estimated
- **THEN** the system SHALL accept values from the Fibonacci sequence
- **AND** SHALL validate that points are positive integers

#### Scenario: Story point tier system

- **WHEN** applying tier-based estimation
- **THEN** Simple tasks SHALL receive 1-2 points
- **AND** Medium tasks SHALL receive 3-5 points
- **AND** Complex tasks SHALL receive 8-13 points

### Requirement: Resource workload balancing

The system SHALL track individual workload across tasks and flag overloaded resources.

#### Scenario: Normal workload

- **WHEN** an assignee has 5 or fewer active tasks
- **THEN** the resource SHALL be marked as OK capacity

#### Scenario: Overloaded resource

- **WHEN** an assignee has more than 5 active tasks
- **THEN** the resource SHALL be flagged as overloaded
- **AND** the system SHALL recommend redistribution

#### Scenario: Workload redistribution

- **WHEN** tasks are reassigned to balance workload
- **THEN** the system SHALL update both source and target assignee task counts
- **AND** SHALL reflect changes in real-time capacity reporting

### Requirement: Sprint allocation management

The system SHALL manage sprint assignments for all tasks within an epic.

#### Scenario: Sprint-assigned task

- **WHEN** a task is assigned to a sprint
- **THET** the task SHALL be visible in sprint planning
- **AND** SHALL contribute to sprint capacity calculations

#### Scenario: Task not in sprint

- **WHEN** a task exists but has no sprint assignment
- **THEN** the epic SHALL flag the task as unallocated
- **AND** SHALL recommend sprint assignment

### Requirement: Stale task identification

The system SHALL identify tasks that have been in non-terminal status for extended periods.

#### Scenario: Stale task threshold

- **WHEN** a task has been in To Do, In Progress, or SIT status for more than 30 days
- **THEN** the task SHALL be marked as stale
- **AND** SHALL appear in the staleness report

#### Scenario: Critical staleness

- **WHEN** a task has been in non-terminal status for more than 90 days
- **THEN** the task SHALL be flagged as critically stale
- **AND** SHALL require review action

### Requirement: Draft story breakdown

The system SHALL support breaking down Draft stories into platform-specific subtasks.

#### Scenario: Draft story with references

- **WHEN** a Draft story references external documentation (URS, Figma)
- **THEN** the subtasks SHALL inherit these references
- **AND** SHALL include acceptance criteria from documentation

#### Scenario: Platform-specific subtask creation

- **WHEN** breaking down a Draft story for mobile development
- **THEN** the system SHALL create iOS subtasks
- **AND** SHALL create Android subtasks
- **AND** SHALL maintain traceability to parent story

### Requirement: Epic status transition

The system SHALL support proper epic lifecycle management.

#### Scenario: Epic moves to In Progress

- **WHEN** an epic has no remaining Draft stories
- **AND** all tasks have at least one subtask or are properly scoped
- **THEN** the epic SHALL be eligible for In Progress status

#### Scenario: Epic completion tracking

- **WHEN** tasks move to Done status
- **THEN** the epic SHALL calculate completion percentage
- **AND** SHALL display progress in epic dashboard

### Requirement: Jira API integration

The system SHALL use tdt_core.clients for Jira operations to ensure consistent authentication and error handling.

#### Scenario: Fetch epic details

- **WHEN** retrieving epic information from Jira
- **THEN** the system SHALL use JiraClientFactory.from_env()
- **AND** SHALL use PatchedJira.jql() for queries

#### Scenario: Update task fields

- **WHEN** modifying task properties (status, assignee, story points)
- **THEN** the system SHALL use PatchedJira methods
- **AND** SHALL handle rate limiting gracefully

#### Scenario: Handle API errors

- **WHEN** Jira API returns an error
- **THEN** the system SHALL log the error with context
- **AND** SHALL provide actionable error messages
