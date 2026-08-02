# Reminder Policies Path Resolution

## ADDED Requirements

### Requirement: Reminder Policies Path Resolution

The system SHALL resolve the reminder policies file path using `tdt_state_path()` to enable running from any working directory.

### `remind()` command

- SHALL resolve config_path via `tdt_state_path("jira-daily-reports", "reminder-policies.yaml")` when not explicitly provided
- SHALL enable scheduler to run reminders from any working directory

#### Scenario: Reminder run from project directory
- **Given** running `jira-daily-reports remind` from the project root
- **When** no `--config` is provided
- **Then** the policies file is resolved to `~/.tdt/state/jira-daily-reports/reminder-policies.yaml`

#### Scenario: Reminder run from scheduler container
- **Given** the scheduler runs `remind` from `/workspace/agent-core/src`
- **When** no `--config` is provided
- **Then** the policies file is still resolved to `/home/agent/.tdt/state/jira-daily-reports/reminder-policies.yaml`
- **So** the workflow completes without `FileNotFoundError`
