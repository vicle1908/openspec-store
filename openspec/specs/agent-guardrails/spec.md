## Purpose

Defines how MCP tool annotations (readOnlyHint, destructiveHint, openWorldHint, idempotentHint) are discovered, mapped to the existing guardrail authority classes, and enforced through input guards for authorized agent sessions.

## Requirements

### Requirement: MCP tool annotation mapping to guardrails
MCP tool annotations (readOnlyHint, destructiveHint, openWorldHint, idempotentHint) discovered via pydantic-ai's `ToolDefinition.metadata['annotations']` SHALL be mapped to the existing `InputGuard`/`OutputGuard` framework and `AuthorityClass` enum.

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

### Requirement: MCP annotations flow into InputGuard
MCP tool annotations SHALL be used to enhance input guardrail decisions.

#### Scenario: Guard reads MCP annotations
- WHEN an `InputGuard` evaluates a tool call
- THEN the guard SHALL have access to `ToolDefinition.metadata['annotations']` for MCP tools
- AND the guard MAY use annotation hints to inform its allow/block decision

#### Scenario: Guard blocks destructive MCP tool without approval
- WHEN a destructive MCP tool is called AND no approval has been granted
- THEN the `InputGuard` SHALL return `GuardResult.block(message="Destructive MCP tool requires approval")`
