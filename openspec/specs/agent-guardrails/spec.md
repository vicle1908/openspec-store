## Purpose

Defines how MCP tool annotations (readOnlyHint, destructiveHint, openWorldHint, idempotentHint) are discovered, mapped to the existing guardrail authority classes, and enforced through input guards for authorized agent sessions.

## Requirements

### Requirement: MCP tool annotation mapping to guardrails
MCP tool annotations (readOnlyHint, destructiveHint, openWorldHint, idempotentHint) discovered via pydantic-ai's `ToolDefinition.metadata['annotations']` SHALL be mapped to the existing `InputGuardrail`/`OutputGuardrail` framework and `AuthorityClass` enum.

#### Scenario: Read-only MCP tool
- WHEN an MCP tool has `ToolDefinition.metadata['annotations']['readOnlyHint'] == true`
- THEN the tool SHALL be mapped to `AuthorityClass.READ`
- AND no high-authority approval SHALL be required for invocation

#### Scenario: Destructive MCP tool
- WHEN an MCP tool has `ToolDefinition.metadata['annotations']['destructiveHint'] == true`
- THEN the tool SHALL be mapped to `AuthorityClass.SHELL` or `AuthorityClass.FILESYSTEM_WRITE` based on the tool's input schema
- AND the standard high-authority approval flow SHALL apply

#### Scenario: Open-world MCP tool
- WHEN an MCP tool has `ToolDefinition.metadata['annotations']['openWorldHint'] == true`
- THEN the tool SHALL be mapped to `AuthorityClass.NETWORK`

#### Scenario: Non-idempotent MCP tool
- WHEN an MCP tool has `ToolDefinition.metadata['annotations']['idempotentHint'] == false`
- THEN the tool invocation SHALL be logged as non-idempotent
- AND a warning SHALL be emitted to structlog

#### Scenario: Unknown or absent annotations
- WHEN an MCP tool has no `annotations` in its `ToolDefinition.metadata`
- OR `ToolDefinition.metadata` is `None` (non-MCP tool)
- THEN the tool SHALL default to `AuthorityClass.READ` (conservative)
- AND the conservative default SHALL be logged at debug level

### Requirement: MCP annotations flow into InputGuardrail
MCP tool annotations SHALL be used to enhance input guardrail decisions.

#### Scenario: Guard reads MCP annotations
- WHEN an `InputGuardrail` evaluates a tool call
- THEN the guard SHALL have access to `ToolDefinition.metadata['annotations']` for MCP tools
- AND the guard MAY use annotation hints to inform its allow/block decision

#### Scenario: Guard blocks destructive MCP tool without approval
- WHEN a destructive MCP tool is called AND no approval has been granted
- THEN the `InputGuardrail` SHALL return `GuardrailResult.block(message="Destructive MCP tool requires approval")`

### Requirement: Docs-sync write-capable agents install bounded tool guardrails

Write-capable documentation generation and full-sync agents SHALL install
bounded tool-argument, shell-command, and result-redaction guardrails in
addition to existing containment hooks and approval gates. These guardrails
SHALL be derived from the supplied production tool registry and SHALL use the
exact registered tool selectors and argument keys. The write guard SHALL cover
`write_doc.path` and `sync_spec.main_path`; `sync_spec.delta_path` remains a
read input governed by read authority rather than a write target. The shell
guard SHALL cover `shell_execute.command` whenever that tool is visible to the
mode.

#### Scenario: Generation mode composition

- **WHEN** docs-sync constructs a generation or full-sync agent with a supplied registry and bounded documentation root
- **THEN** the capability set SHALL include write-path, shell-command, and result-redaction tool guardrails
- **AND** the configured selectors and argument keys SHALL match the supplied production registry exactly
- **AND** the existing write-containment and approval hooks SHALL remain installed

#### Scenario: Registry replacement is respected

- **WHEN** a caller supplies a registry with a custom or reduced visible tool set
- **THEN** guardrail registration SHALL use that registry's canonical tool identities
- **AND** the builder SHALL not construct or silently substitute a second registry

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

### Requirement: Explicit workspace-root policy for write-capable docs-sync

Write-capable docs-sync construction SHALL require a concrete workspace root
and at least one bounded documentation root expressed relative to that
workspace. The policy SHALL reject missing, ambiguous, absolute, escaping, or
unbounded documentation roots before model or write-capable tool execution.

#### Scenario: Concrete workspace and bounded root are accepted

- **WHEN** generation is constructed with an existing workspace root and a documentation root such as `docs/`
- **THEN** the workspace root SHALL anchor canonical path resolution
- **AND** writes SHALL remain confined to the configured workspace-relative documentation root

#### Scenario: Workspace root is missing

- **WHEN** a write-capable mode is constructed without a concrete workspace root
- **THEN** construction SHALL fail with an actionable configuration error
- **AND** no model or write-capable tool SHALL execute

#### Scenario: Documentation root escapes the workspace

- **WHEN** a configured documentation root is absolute, traverses outside the workspace, or cannot be bounded after canonical and symlink checks
- **THEN** construction SHALL fail closed
- **AND** the diagnostic SHALL not expose credentials, secrets, or raw sensitive path data
