# shb-mcp-servers Specification Delta

## MODIFIED Requirements

### Requirement: Standardized MCP Server Transports
The `shb-mcp-servers` package SHALL implement Model Context Protocol compliant servers using the official FastMCP SDK (`from mcp.server.fastmcp import FastMCP`), exposing asynchronous stdio and Server-Sent Events (SSE) transports with automatic Pydantic schema validation.

#### Scenario: Agent connects via stdio transport
- **WHEN** an autonomous agent initializes a subprocess transport pointing to an SHB MCP server executable
- **THEN** the server performs protocol handshake, returns server capabilities, and lists registered tools

#### Scenario: Agent connects via FastMCP stdio transport
- **WHEN** an autonomous agent initializes an MCP client pointing to the `shb-mcp` server
- **THEN** FastMCP SHALL perform protocol handshake, declare server capabilities, and expose registered tools, resources, and prompts

### Requirement: Banking Context and Engineering Tool Providers
The system SHALL provide dedicated MCP tool modules, resource templates (`shb://accounts/{account_number}/summary`), and compliance prompt templates (`audit-ticket-compliance`) for consuming agent runtimes.

#### Scenario: MCP tool discovery and execution
- **WHEN** an agent sends a `tools/call` JSON-RPC request for a registered banking tool
- **THEN** the MCP server executes the corresponding provider method and returns structured content with status 200

#### Scenario: MCP resource read for account summary
- **WHEN** an agent reads a URI matching `shb://accounts/{account_number}/summary`
- **THEN** the MCP server SHALL resolve account details and return a structured text resource payload

#### Scenario: Compliance audit prompt invocation
- **WHEN** an agent requests the `audit-ticket-compliance` prompt template
- **THEN** the MCP server SHALL return the standardized banking compliance audit prompt instructions
