# Proposal: Standards-Compliant MCP Plug-and-Play Integration

## Why

The current `MCPManager` in `agent_core/_ai/mcp.py` correctly wraps pydantic-ai's `MCPToolset`, which already implements the full MCP protocol (transport negotiation, tool discovery, capability handshake). However, there are three gaps:

1. **No tool annotation mapping** — MCP servers declare tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) but agent-core ignores them. A "delete file" MCP tool gets the same authority class as a "read file" MCP tool.

2. **No auto-registration from config** — consumers must manually create `MCPServerConfig` objects. The system should read MCP server URLs from `AgentConfig` and auto-register them via `MCPToolset`.

3. **Spec doesn't reference the official MCP standard** — the current `mcp-integration` spec describes pydantic-ai integration but doesn't cite the MCP 2026-07-28 specification or define standards compliance requirements.

## What Changes

1. **Add MCP tool annotation → AuthorityClass mapping** — automatically assign authority classes based on server-declared annotations
2. **Add auto-registration from AgentConfig** — read `mcp_servers` from config and create `MCPToolset` instances automatically
3. **Update spec to reference MCP 2026-07-28** — cite the official specification, define transport support (stdio, Streamable HTTP), and add tool annotation requirement

## Scope

- `agent_core/_ai/mcp.py` — add `ToolAnnotationMapper`, `configure_from_config()`
- `agent_core/_ai/config.py` — add `mcp_servers` config field
- `openspec/specs/mcp-integration/spec.md` — MODIFIED: standards compliance, annotation mapping

## Out of Scope

- Custom transport implementations (delegate to pydantic-ai)
- OAuth 2.1 full flow (bearer token auth already works; OAuth deferred)
- Server-specific endpoints or REST bridges
