## Purpose

Configuration-driven auto-approval for specific tools, bypassing manual approval while maintaining security constraints.

## Requirements

### Requirement: Auto-approve configuration

The system SHALL support an `auto_approve_tools` configuration field that lists tools which should bypass the manual approval flow.

#### Scenario: Configuration parsing
- **WHEN** `auto_approve_tools` is specified in config.yaml
- **THEN** the system parses it as a tuple of tool names

#### Scenario: Default value
- **WHEN** `auto_approve_tools` is not specified in config.yaml
- **THEN** the system uses an empty tuple (no auto-approval)

### Requirement: Tool approval bypass

Tools listed in `auto_approve_tools` SHALL bypass the manual approval flow while maintaining all other security constraints.

#### Scenario: Auto-approved tool execution
- **WHEN** a tool in `auto_approve_tools` is invoked
- **AND** the tool has `requires_approval=True` in metadata
- **THEN** the system skips the approval request
- **AND** the tool executes immediately

#### Scenario: Non-approved tool execution
- **WHEN** a tool NOT in `auto_approve_tools` is invoked
- **AND** the tool has `requires_approval=True` in metadata
- **THEN** the system follows the standard approval flow

### Requirement: Security constraint preservation

Auto-approval SHALL NOT bypass security constraints.

#### Scenario: Path containment enforced
- **WHEN** an auto-approved tool writes to a file
- **THEN** the path must be within `allowed_doc_roots`
- **AND** the write is logged in the audit trail

#### Scenario: Scope enforcement
- **WHEN** an auto-approved tool is invoked
- **THEN** the tool's scope is checked against the authority grant
- **AND** violations are rejected

#### Scenario: Limits enforcement
- **WHEN** an auto-approved tool is invoked
- **THEN** the tool's limits (max_calls, timeout, etc.) are checked
- **AND** violations are rejected

### Requirement: Audit trail

All auto-approved operations SHALL be logged for audit purposes.

#### Scenario: Write logging
- **WHEN** an auto-approved tool writes to a file
- **THEN** the write is recorded in `writes.sqlite3`
- **AND** the approval status is recorded as "auto-approved"

#### Scenario: Lifecycle audit
- **WHEN** an auto-approved tool is invoked
- **THEN** a lifecycle audit event is created
- **AND** the event includes the tool name, arguments, and result

### Requirement: Configuration validation

The system SHALL validate the `auto_approve_tools` configuration.

#### Scenario: Valid tool names
- **WHEN** `auto_approve_tools` contains valid tool names
- **THEN** the configuration is accepted

#### Scenario: Invalid tool names
- **WHEN** `auto_approve_tools` contains unknown tool names
- **THEN** the system logs a warning but continues
- **AND** unknown tools are ignored
