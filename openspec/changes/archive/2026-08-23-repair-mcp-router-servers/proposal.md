## Why

The mcp-router registered wiki and graphify MCP servers are not functioning correctly for Claude Code clients. Wiki tools exist in the mcp-router schema cache (132 tools served, including 8 wiki tools) but are filtered out before reaching Claude Code's tool list. Graphify is registered as an MCP server with an invalid command (`graphify ~/Developer/go-microservices --mcp --code-only`) — the `--mcp` flag doesn't exist in graphify v0.9.46, so the server silently fails to start. Both servers show as "healthy" in the Hermes health state despite being non-functional.

## What Changes

- **Fix wiki tool exposure**: Investigate and repair the tool filtering chain between mcp-router HTTP server and Claude Code client. The mcp-router serves 132 tools including wiki tools, but Claude Code only receives ~84 mcp-router tools. Root cause is likely in the CLI `connect` bridge or Claude Code's MCP client tool negotiation.
- **Fix graphify server registration**: Replace the broken graphify MCP server config with a working implementation. Options: (a) use `graphify watch` as a file watcher that generates graph.json, (b) create a thin MCP wrapper script, or (c) remove graphify from MCP registry and use as CLI-only tool.
- **Verify both servers end-to-end**: Confirm wiki_search, wiki_read, wiki_index, wiki_ingest, wiki_links, wiki_stale, and graphify tools are callable from Claude Code.

## Capabilities

### New Capabilities

None — this is a repair/config change, not new functionality.

### Modified Capabilities

None — no spec-level behavior changes. This is tooling infrastructure repair.

**skip_specs: true** — Pure tooling repair. No API contracts, user-facing behavior, or spec-level requirements change.

## Impact

- **mcp-router database**: `~/Library/Application Support/MCP Router/mcprouter.db` — server configs for wiki and graphify
- **Wiki MCP server**: `~/Developer/wiki-mcp-server/` — Python package, needs `uv sync`
- **Graphify CLI**: `~/.local/bin/graphify` v0.9.46 — standalone CLI, no MCP support
- **Claude Code MCP connection**: CLI `connect` bridge processes, permission rules (`mcp__mcp-router__*`)
- **Hermes health state**: `~/.hermes/tmp/mcp-health-state-*.json` — may need refresh after repair
