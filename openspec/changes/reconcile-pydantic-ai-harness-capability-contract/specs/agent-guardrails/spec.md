## ADDED Requirements

### Requirement: Docs-sync write-capable agents install bounded tool guardrails

Write-capable documentation generation and full-sync agents SHALL install bounded tool-argument, shell-command, and result-redaction guardrails in addition to existing containment hooks and approval gates.

#### Scenario: Generation mode composition

- **WHEN** docs-sync constructs a generation or full-sync agent with a bounded documentation root
- **THEN** the capability set SHALL include write-path, shell-command, and result-redaction tool guardrails
- **AND** the existing write-containment and approval hooks SHALL remain installed

#### Scenario: Read-only mode composition

- **WHEN** docs-sync constructs check or discovery-only behavior
- **THEN** write-capable tool guardrails SHALL not grant write authority
- **AND** read-only tool visibility and authority policy SHALL remain unchanged

### Requirement: Tool guardrails fail closed without replacing containment authority

ToolGuardrail evaluation SHALL block unsafe arguments and redact sensitive results, while the authoritative path-containment, approval, and exactly-once ledger boundaries SHALL remain independently enforced.

#### Scenario: Unsafe write path

- **WHEN** a write tool receives an absolute path, traversal path, or path outside the approved documentation roots
- **THEN** the tool call SHALL be blocked with a stable redacted diagnostic
- **AND** no write-capable tool SHALL execute

#### Scenario: Dangerous shell command

- **WHEN** a shell tool receives a blocked command pattern
- **THEN** the tool call SHALL be blocked before execution
- **AND** the blocked attempt SHALL be available to the existing audit path

#### Scenario: Sensitive result

- **WHEN** a tool result contains a recognized secret or personal-data pattern
- **THEN** the result SHALL be replaced or blocked according to the configured detector
- **AND** the raw sensitive value SHALL not be exposed to the model or generated documentation
