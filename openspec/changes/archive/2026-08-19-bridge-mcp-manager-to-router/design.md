# Design: Standards-Compliant MCP Plug-and-Play

## Problem

The current `MCPManager` wraps pydantic-ai's `MCPToolset` but ignores MCP tool annotations, requires manual server config, and doesn't reference the official standard.

pydantic-ai's `MCPToolset` already implements the full MCP protocol per the 2026-07-28 specification. The value-add is the **mapping layer** — translating server-declared annotations into agent-core's authority policy — not a custom transport bridge.

## Official MCP Standard (2026-07-28) — Key Facts

- **Stateless protocol** — no initialize handshake; every request carries protocol version in `_meta`
- **Transports**: stdio (newline-delimited JSON-RPC), Streamable HTTP (POST + optional SSE)
- **Tool annotations**: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` — declared by server, consumed by client
- **Security**: "Clients MUST consider tool annotations to be untrusted unless they come from trusted servers"
- **Disambiguation**: "Clients SHOULD implement a disambiguation strategy such as prefixing tool names with a server identifier"

## Architecture

```
AgentConfig.mcp_servers
    |
    v
MCPManager.configure_from_config(config)
    |
    +--> for each URL in config.mcp_servers:
    |    MCPToolset(url) --> pydantic-ai handles MCP protocol
    |    tools/list --> discover tools with annotations
    |
    +--> ToolAnnotationMapper:
    |    readOnlyHint:true  --> AuthorityClass.READ
    |    destructiveHint:true --> AuthorityClass.SHELL or FILESYSTEM_WRITE
    |    openWorldHint:true --> AuthorityClass.NETWORK
    |    (no annotations)   --> AuthorityClass.READ (conservative default)
    |
    +--> register tools with mapped authority classes into ToolRegistry
    |
    v
Agent has MCP tools with proper authority classes
```

## Tool Annotation → AuthorityClass Mapping

| MCP Annotation | AuthorityClass | Reasoning |
|---------------|---------------|-----------|
| `readOnlyHint: true` | `READ` | No host state change |
| `destructiveHint: true` | `SHELL` or `FILESYSTEM_WRITE` | Modifies external state |
| `openWorldHint: true` | `NETWORK` | Touches external systems |
| `idempotentHint: false` | Logged, no downgrade | Non-idempotent = risk signal |
| No annotations | `READ` (conservative) | Unknown tools get least-privilege |

Conservative default follows MCP spec security: "Clients MUST consider tool annotations to be untrusted unless they come from trusted servers."

## Tool Name Disambiguation

Per MCP spec: "Clients SHOULD implement a disambiguation strategy such as prefixing tool names with a server identifier."

The `MCPManager` prefixes each tool name with the server's identity to avoid cross-server collisions:
- `mcp-router:read_file` (from mcp-router)
- `gitnexus:query` (from gitnexus server)
- `tavily:search` (from tavily server)

## Files Changed

| File | Change |
|------|--------|
| `agent_core/_ai/mcp.py` | Add `ToolAnnotationMapper` class, `configure_from_config()` method |
| `agent_core/_ai/config.py` | Add `mcp_servers: list[str]` field to `AgentConfig` |
| `openspec/specs/mcp-integration/spec.md` | MODIFIED: standards compliance, annotation mapping, auto-registration |

## Testing

- Test: readOnlyHint tool → READ authority class
- Test: destructiveHint tool → appropriate high-authority class
- Test: unknown annotations → conservative READ default
- Test: tool name disambiguation (no collisions)
- Test: configure_from_config reads URLs and creates MCPToolset instances
- Existing tests pass unchanged
