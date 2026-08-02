## Purpose

Programmatically add missing status transitions to Jira workflows when issues are stuck at statuses not included in the current workflow configuration.

## Requirements

### Requirement: Add missing status to workflow

The system SHALL add a status to a Jira workflow when the status exists as a global status but is not included in the workflow configuration.

#### Scenario: Status exists globally but not in workflow
- **WHEN** an issue is at a status that exists in Jira but is not in the project's workflow
- **THEN** the system SHALL identify the missing status and add it to the workflow

### Requirement: Add transition from missing status

The system SHALL add a transition from the missing status to a target status (e.g., Done) to allow issues to progress.

#### Scenario: Add transition to Done status
- **WHEN** a status is added to a workflow
- **THEN** the system SHALL create a transition from that status to the Done status (status category: done)

### Requirement: Handle workflow version correctly

The system SHALL handle workflow versioning to avoid conflicts when updating workflows.

#### Scenario: Update workflow with valid version
- **WHEN** updating a workflow via Jira REST API v3
- **THEN** the system SHALL use the correct workflow version ID to avoid version conflict errors

### Requirement: Preserve existing transitions

The system SHALL preserve all existing transitions when adding new statuses or transitions to a workflow.

#### Scenario: Add status without breaking existing transitions
- **WHEN** adding a new status and transition to a workflow
- **THEN** all existing statuses and transitions SHALL remain unchanged

### Requirement: CLI command for stuck issues

The system SHALL provide a CLI command to diagnose and fix stuck issues.

#### Scenario: Fix stuck issue via CLI
- **WHEN** user runs the fix command with an issue key
- **THEN** the system SHALL identify the stuck status, add it to the workflow if needed, and transition the issue to Done

### Requirement: Dry-run mode

The system SHALL support dry-run mode to preview changes before applying them.

#### Scenario: Preview workflow changes
- **WHEN** user runs the fix command with --dry-run flag
- **THEN** the system SHALL show what changes would be made without actually modifying the workflow
