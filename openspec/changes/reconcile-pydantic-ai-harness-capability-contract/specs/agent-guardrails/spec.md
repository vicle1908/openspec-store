## ADDED Requirements

### Requirement: Docs-sync write-capable agents install bounded tool guardrails

Write-capable documentation generation and full-sync agents SHALL install bounded tool-argument, shell-command, and result-redaction guardrails in addition to existing containment hooks and approval gates. The write guard SHALL cover `write_doc.path` and `sync_spec.main_path`; `sync_spec.delta_path` remains a read input governed by read authority rather than a write target. The shell guard SHALL cover `shell_execute.command` whenever that tool is visible to the mode.

#### Scenario: Generation mode composition

- **WHEN** docs-sync constructs a generation or full-sync agent with a bounded documentation root
- **THEN** the capability set SHALL include write-path, shell-command, and result-redaction tool guardrails
- **AND** the configured tool selectors and argument keys SHALL match the production tool registry exactly
- **AND** the existing write-containment and approval hooks SHALL remain installed

#### Scenario: Read-only mode composition

- **WHEN** docs-sync constructs check or discovery-only behavior
- **THEN** write-capable tool guardrails SHALL not grant write authority
- **AND** read-only tool visibility and authority policy SHALL remain unchanged

### Requirement: Tool guardrails fail closed without replacing containment authority

ToolGuardrail evaluation SHALL block unsafe arguments and redact sensitive results, while the authoritative path-containment, approval, and exactly-once ledger boundaries SHALL remain independently enforced. The write guard SHALL call the existing `agent_docs_sync.tools.path_policy.resolve_allowed_write_path` and SHALL not reproduce path normalization. Guardrail and containment rejections SHALL emit exactly one bounded audit event through the existing audit sink with a stable decision code and without raw path, command, secret, personal-data, or document-content values.

#### Scenario: Unsafe write path

- **WHEN** `write_doc.path` or `sync_spec.main_path` receives an absolute path, traversal path, or path outside the approved documentation roots
- **THEN** the tool call SHALL be blocked with a stable redacted diagnostic
- **AND** no write-capable tool SHALL execute

#### Scenario: Valid write path

- **WHEN** a write tool receives a path that resolves within an approved documentation root after canonical path and symlink checks
- **THEN** the ToolGuardrail MAY allow the call to continue to approval and containment enforcement
- **AND** the ToolGuardrail SHALL NOT create a second weaker path-normalization policy

#### Scenario: Dangerous shell command

- **WHEN** a shell tool receives a blocked command pattern
- **THEN** the tool call SHALL be blocked before execution
- **AND** the blocked attempt SHALL be available to the existing audit sink through a stable redacted decision that does not expose the raw command

#### Scenario: Sensitive result

- **WHEN** a tool result contains a recognized secret or personal-data pattern
- **THEN** the result SHALL be replaced or blocked according to the configured detector
- **AND** the raw sensitive value SHALL not be exposed to the model or generated documentation

#### Scenario: Layered rejection attribution

- **WHEN** an outer authoritative containment hook rejects an unsafe write before the innermost ToolGuardrail evaluates it
- **THEN** public-boundary evidence SHALL attribute the rejection to containment and SHALL not claim that ToolGuardrail executed
- **AND** separate exact-selector tests SHALL prove the write ToolGuardrail blocks the same unsafe `ToolCallInfo`, while a bounded valid call SHALL reach the ToolGuardrail and continue only to approval and containment
- **AND** the combined path SHALL emit one redacted audit event rather than duplicate records
