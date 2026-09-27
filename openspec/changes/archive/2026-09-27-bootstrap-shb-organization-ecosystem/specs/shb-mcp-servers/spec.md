# Spec Delta: SHB MCP Servers

## Purpose

Provides Model Context Protocol (MCP) server endpoints, transport adapters, and tool definitions for autonomous agents in the Saigon - Hanoi Bank (SHB) ecosystem.

## ADDED Requirements

### Requirement: Standardized MCP Server Transports
The `shb-mcp-servers` package SHALL implement Model Context Protocol compliant servers exposing JSON-RPC over standard input/output (stdio) and Server-Sent Events (SSE) transports for consuming agent runtimes.

#### Scenario: Agent connects via stdio transport
- **WHEN** an autonomous agent initializes a subprocess transport pointing to an SHB MCP server executable
- **THEN** the server performs protocol handshake, returns server capabilities, and lists registered tools

### Requirement: Banking Context and Engineering Tool Providers
The system SHALL provide dedicated MCP tool modules for Jira issue management, GitLab merge request operations, browser automation, and banking API inspection.

#### Scenario: MCP tool discovery and execution
- **WHEN** an agent sends a `tools/call` JSON-RPC request for a registered banking tool
- **THEN** the MCP server executes the corresponding provider method and returns structured content with status 200

### Requirement: Command-Line Interface and Server Daemon
The package SHALL provide an executable CLI entrypoint named `shb-mcp` allowing operators and agent configuration managers to inspect and launch MCP servers.

#### Scenario: Server inspection invocation
- **WHEN** an operator runs `shb-mcp list-tools`
- **THEN** the CLI outputs all available MCP tools, parameter schemas, and transport binding specifications
