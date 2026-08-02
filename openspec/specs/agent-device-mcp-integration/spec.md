# agent-device-mcp-integration Specification

## Purpose
Defines opt-in MCP wiring for `agent-device` tools and the requirement that the MCP server is a structured command contract, not a generic shell runner.

NOTE: Implementation lives in the separate agent-device repository, not in agent-core.
## Requirements
### Requirement: MCP wiring is opt-in; no committed MCP config
The TDT workspace SHALL NOT commit a `.cursor/mcp.json`, `.mcp.json`, or similar MCP server configuration file. MCP wiring is documented as an opt-in per-operator setup.

#### Scenario: Cursor operator wants MCP tools
- **WHEN** a Cursor user wants structured `agent-device` MCP tools in chat
- **THEN** the operator creates a local `.cursor/mcp.json` (not committed to the workspace) with `{"mcpServers":{"agent-device":{"command":"agent-device","args":["mcp"]}}}`
- **AND** if Cursor cannot find the global binary, the operator uses the absolute binary path

#### Scenario: Claude Code operator wants MCP tools
- **WHEN** a Claude Code user wants structured `agent-device` MCP tools
- **THEN** the operator runs `claude mcp add --transport stdio --scope user agent-device -- agent-device mcp` or the project-scoped variant

### Requirement: MCP server is not a generic shell runner
The agent SHALL treat the `agent-device` MCP server as structured command contracts backed by `AgentDeviceClient`. If the MCP tool returns `isError: true`, the agent SHALL inspect the tool result, not only the JSON-RPC envelope.

#### Scenario: MCP tool returns an error
- **WHEN** the agent receives an `isError: true` result from an `agent-device` MCP tool
- **THEN** the agent surfaces the failure to the user and does not assume the operation succeeded

#### Scenario: MCP server fails to start (binary not found)
- **WHEN** the MCP server fails to start because the binary is not on PATH
- **THEN** the agent asks the operator to install the CLI or configure the absolute binary path; the agent MUST NOT silently fall back to `npx -y agent-device@latest`

