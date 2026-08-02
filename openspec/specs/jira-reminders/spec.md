# jira-reminders Specification

## Purpose

Automatically post @mention reminders on Jira tickets with missing required fields. Supports escalation policies, suppression rules (grace period, off-hours, weekend, label-based), deduplication, and audit logging.

## Requirements

### Requirement: Policy-driven reminder rules

The system SHALL load reminder policies from a YAML config file (`reminder-policies.yaml`) defining which fields are required per issue type, who to @mention (role-based resolution), and escalation rules.

#### Scenario: Valid policy loaded
- **WHEN** the policy YAML contains valid required-field rules
- **THEN** the system loads the policies without error

#### Scenario: Malformed policy YAML
- **WHEN** the policy YAML has syntax errors
- **THEN** the system rejects the config with an actionable error

### Requirement: JQL-based ticket search

The system SHALL search for tickets with missing required fields using JQL queries constructed from the loaded policies. Searches are chunked at 150 display names per query.

#### Scenario: Build JQL from policy
- **WHEN** a policy requires "Developer" field on Bug issues
- **THEN** the system builds JQL: `issuetype = Bug AND "Developer" is EMPTY AND ...`

### Requirement: Escalation state persistence

The system SHALL persist escalation state across runs using SQLite. Each ticket's escalation level, last reminder timestamp, and resolution status are tracked.

#### Scenario: Escalation state persists
- **WHEN** a ticket is reminded at level 1
- **THEN** the next run detects the prior reminder and escalates to level 2 if unresolved

### Requirement: Suppression rules

The system SHALL suppress reminders based on: grace period (don't remind again within N hours), off-hours (suppress during non-business hours), weekend (suppress on weekends), and label-based suppression (skip tickets with specific labels).

#### Scenario: Grace period suppression
- **WHEN** a ticket was reminded 2 hours ago and grace period is 24 hours
- **THEN** the system skips the reminder

#### Scenario: Off-hours suppression
- **WHEN** the current time is outside business hours and off-hours suppression is enabled
- **THEN** the system suppresses all reminders

### Requirement: Dry-run and explain modes

The system SHALL support `--dry-run` (show actions without posting) and `--explain <KEY>` (show suppression/escalation reasoning for a specific ticket).

#### Scenario: Dry-run mode
- **WHEN** `--dry-run` is set
- **THEN** the system logs what it would do without posting any Jira comments

#### Scenario: Explain mode
- **WHEN** `--explain POEMS2-1234` is passed
- **THEN** the system shows the ticket's escalation state, suppression rules, and why a reminder would or would not be sent

### Requirement: ADF @mention comments

The system SHALL post reminders as Atlassian Document Format (ADF) comments with @mention syntax targeting the resolved assignee or role-based recipient.

#### Scenario: Post mention with account ID
- **WHEN** the recipient has a known Jira account ID
- **THEN** the comment uses `<at account-id>` ADF syntax

#### Scenario: Post mention without account ID
- **WHEN** the recipient's account ID is unknown
- **THEN** the comment falls back to `<at>displayname</at>` syntax

### Requirement: Audit log

The system SHALL log every reminder action (sent, suppressed, escalated) with structured fields for downstream analysis. The `--show-history` command displays recent audit entries.

#### Scenario: Audit log entries
- **WHEN** a reminder is sent
- **THEN** an audit entry records: ticket key, action, escalation level, timestamp, recipient
