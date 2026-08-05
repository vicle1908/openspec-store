# Erratum: Prior Pi MCP Verification

Date: 2026-08-05

## What was claimed

The archived Pi verification (`2026-08-04-add-pi-coding-agent-skill/verification.md`) stated:

> "Using `--tools <mcp-name>` did NOT work for MCP tools (Pi's --tools only filters built-in tools)."
>
> "MCP tools are available by default when pi-mcp-adapter is installed and the model chooses to use them."

The Pi v1.0.0 and v1.1.0 skill also stated:

> `--tools` filtering: `--tools` does NOT filter MCP tools; it only filters Pi core/extension tools

## What actually happened

The prior verification used the Hermes-style name `mcp__mcp_router__brave_web_search` in the `--tools` flag. That name is not how pi-mcp-adapter generates direct tool names.

With the adapter's default `toolPrefix: "server"` and server name `mcp-router`, tool `brave_web_search` becomes:

```
mcp_router_brave_web_search
```

## Corrected behavior

1. **Direct MCP tools are registered as Pi tools** and therefore ARE filterable by `--tools` / `--exclude-tools` using their generated names.
2. The prior test failed only because the wrong tool name was used.
3. Proxy-mode MCP access (the `mcp` tool) is governed by whether `mcp` itself is in the tool set, plus adapter config.
4. The adapter's own documentation recommends targeted direct sets of 5-20 tools and warns about 75+ direct tools adding prompt overhead.

## Evidence

- `--tools mcp_router_brave_web_search` → tool call succeeded
- `--tools read` → model reported MCP tool unavailable
- `--tools mcp` → proxy discovery worked, reported exact direct-tool name

## Corrected Pi skill

The Pi skill v1.2.0 reflects this corrected behavior. The MCP section was rewritten to distinguish direct-tool filtering from proxy-mode filtering and to document adapter-generated naming.
