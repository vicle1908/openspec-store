## MODIFIED Requirements

### Requirement: Standards-compliant MCP server connection
The system SHALL connect to any standard MCP server using pydantic-ai's MCP capability/toolset, implementing the MCP 2026-07-28 specification. No server-specific customization SHALL be required.

#### Scenario: Connect to any MCP server via URL
- WHEN `AgentRuntime` is configured with an MCP server URL (stdio, streamable-http, or sse)
- THEN the system SHALL connect using pydantic-ai's `MCP("url")` capability or `MCPToolset(url)`
- AND the MCP protocol lifecycle (tool discovery, capability negotiation) SHALL be handled by pydantic-ai
- AND NO server-specific HTTP client or REST bridge SHALL be created

#### Scenario: Auto-registration from config
- WHEN `AgentConfig.mcp_servers` contains a list of MCP server URLs
- THEN `MCPManager.configure_from_config()` SHALL create `MCPToolset` instances for each URL
- AND discovered tools SHALL be registered with the ToolRegistry

#### Scenario: Tool name disambiguation
- WHEN tools are discovered from multiple MCP servers
- THEN tool names SHALL be prefixed with the server identifier to prevent collisions
- AND the prefix format SHALL be `<server-host>:<tool-name>` per MCP spec recommendation

## ADDED Requirements

### Requirement: MCP tool annotation to authority class mapping
The system SHALL map MCP tool annotations to `AuthorityClass` values automatically.

#### Scenario: Read-only tool
- WHEN an MCP server declares a tool with `readOnlyHint: true`
- THEN the tool SHALL be mapped to `AuthorityClass.READ`
- AND no high-authority approval SHALL be required

#### Scenario: Destructive tool
- WHEN an MCP server declares a tool with `destructiveHint: true`
- THEN the tool SHALL be mapped to `AuthorityClass.SHELL` or `AuthorityClass.FILESYSTEM_WRITE` based on the tool's input schema
- AND the standard high-authority approval flow SHALL apply

#### Scenario: Open-world tool
- WHEN an MCP server declares a tool with `openWorldHint: true`
- THEN the tool SHALL be mapped to `AuthorityClass.NETWORK`

#### Scenario: Unknown annotations (conservative default)
- WHEN an MCP tool has no annotations or unrecognized annotation values
- THEN the tool SHALL default to `AuthorityClass.READ`
- AND the conservative default SHALL be logged

### Requirement: MCP specification compliance
The system's MCP integration SHALL comply with the MCP 2026-07-28 specification.

#### Scenario: Stateless protocol compliance
- WHEN connecting to an MCP server
- THEN every request SHALL carry the protocol version in `_meta` fields
- AND the system SHALL NOT assume connection-level session state

#### Scenario: Transport support
- WHEN configured with a URL
- THEN the system SHALL support stdio and Streamable HTTP transports
- AND transport selection SHALL be automatic based on the URL scheme

#### Scenario: Server capability discovery
- WHEN connected to an MCP server
- THEN the system SHALL read `server_capabilities` and respect `tools.listChanged` notifications
