## Purpose

This specification defines requirements for Mcp Integration.

## Requirements

### Requirement: MCPToolset integration
The system SHALL support Pydantic AI's `MCPToolset` for native MCP server integration.

#### Scenario: Connect to MCP server via URL
- **WHEN** `AgentRuntime` is configured with `mcp_servers=["http://localhost:3000"]`
- **THEN** the agent SHALL connect to the MCP server using `MCPToolset` and discover available tools
- **NOTE:** `MCPToolset` wraps FastMCP Client and supports local (stdio) and remote (Streamable HTTP, SSE) servers

#### Scenario: Connect via MCPToolset directly
- **WHEN** `AgentRuntime` is configured with `toolsets=[MCPToolset("http://localhost:3000")]`
- **THEN** the agent SHALL have access to all tools exposed by the MCP server
- **NOTE:** Use `toolsets=[...]` for lower-level access, lifecycle management, or sharing one MCP server across multiple agents

#### Scenario: MCP tools available to agent
- **WHEN** an MCP server provides tools
- **THEN** those tools SHALL be available to the agent via the normal tool calling interface
- **AND** MCP tools SHALL be validated and executed through the same ToolRegistry path

#### Scenario: MCP server disconnection
- **WHEN** an MCP server becomes unavailable
- **THEN** the agent SHALL gracefully handle the disconnection
- **AND** previously discovered tools SHALL remain available (cached)

### Requirement: MCP configuration
The system SHALL support MCP server configuration via agent runtime settings.

#### Scenario: Configure MCP servers via capability
- **WHEN** `AgentRuntime(mcp_servers=["http://localhost:3000"])` is constructed
- **THEN** the `MCP` capability SHALL be added to the agent's capabilities automatically
- **NOTE:** `MCP("url")` is the capability-level API; `MCPToolset` is the toolset-level API

#### Scenario: Configure MCP servers via toolsets
- **WHEN** `AgentRuntime(toolsets=[MCPToolset("http://localhost:3000")])` is constructed
- **THEN** the MCPToolset SHALL be registered with the agent's tool collection

#### Scenario: MCP server authentication
- **WHEN** an MCP server requires authentication
- **THEN** the system SHALL support bearer token or API key authentication via configuration

### Requirement: MCP tool governance
MCP tools SHALL be subject to the same governance as built-in tools.

#### Scenario: MCP tool allowlist
- **WHEN** a skill specifies `allowed-tools` that includes MCP tool names
- **THEN** only those MCP tools SHALL be available to the agent

#### Scenario: MCP tool metrics
- **WHEN** an MCP tool is invoked
- **THEN** the ToolRegistry SHALL track its execution metrics (invocations, failures, duration)

### Requirement: MCP with native provider support
The system SHALL support provider-native MCP execution when available.

#### Scenario: Native MCP on nhà cung cấp dịch vụ AI/nhà cung cấp dịch vụ AI
- **WHEN** the model provider supports native MCP (nhà cung cấp dịch vụ AI, nhà cung cấp dịch vụ AI Responses)
- **THEN** MCP tools SHALL be executed server-side when `native=True`
- **AND** local fallback SHALL be used when native execution is not available
- **NOTE:** Pydantic AI auto-switches between native and local execution
