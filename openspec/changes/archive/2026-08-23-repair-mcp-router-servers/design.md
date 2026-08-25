## Context

The mcp-router (v0.6.3) aggregates multiple MCP servers into a single endpoint at `localhost:3282/mcp`. Two registered servers — wiki and graphify — are not functioning for Claude Code clients despite showing as "healthy" in the Hermes health state.

**Current architecture:**
```
Claude Code → CLI connect (stdio) → mcp-router HTTP (port 3282) → Individual MCP servers
                                         ↓
                                  AggregatorServer
                                         ↓
                              RequestHandlers.handleListTools()
                                         ↓
                              getAllToolsInternal() → client.listTools() per server
```

**Investigation findings (verified 2026-08-22):**

1. **Wiki server** (id: `d4a303da-c523-4834-a0fe-8cdd13c3edaf`):
   - Command: `/Users/androidteam/Developer/wiki-mcp-server/.venv/bin/python`
   - Args: `["/Users/androidteam/Developer/wiki-mcp-server/src/wiki_mcp_server/server.py"]`
   - **MCP version fix**: Was using MCP 2.0 `MCPServer` (FastMCP) → ported to MCP 1.29.0 low-level `Server` API (matching graphify's pattern)
   - **Blank-line filter**: Added `_filter_blank_stdin()` (matching graphify's implementation)
   - Server responds correctly to MCP protocol (verified standalone + Node.js MCP client)
   - Server process starts as child of mcp-router (confirmed via process tree)
   - **But**: Tools don't appear in mcp-router's aggregated tool list despite process running
   - **Root cause hypothesis**: The mcp-router Electron app (v0.6.3, built Jul 22 2026) bundles an older MCP SDK. The wiki server's process starts but the SDK client handshake may fail silently. Graphify (same pattern) works because its tools were added before the app was built.
   - **Investigation evidence**:
     - `connectToServerWithResult()` error is caught and logged to `console.error` (invisible in Electron production mode)
     - No wiki-related errors appear in captured stderr/stdout
     - The process IS a child of mcp-router but client is never added to `this.clients` map
     - Tested with exact same Node.js MCP client → works perfectly (6 tools)

2. **Graphify server** (id: `graphify-microservices`):
   - Command: `graphify`
   - Args: `["~/Developer/go-microservices", "--mcp", "--code-only"]`
   - graphify v0.9.46 has NO `--mcp` flag — the server silently exits with code 0
   - **Root cause**: Invalid command configuration. However, **graphifyy 0.9.48 HAS MCP server support** via `python -m graphify.serve` (stdio and HTTP transports).
   - **Correct command**: `~/.local/share/uv/tools/graphifyy/bin/python -m graphify.serve ~/Developer/go-microservices/graphify-out/graph.json`
   - **Dependency**: Requires `mcp` package installed in the graphifyy environment
   - **Impact**: Server registered with wrong command, produces zero tools. Fix: update command to use correct MCP server entry point.

## Goals / Non-Goals

**Goals:**
- Make wiki tools callable from Claude Code via mcp-router
- Fix or replace graphify MCP server registration
- Ensure both servers survive mcp-router restarts

**Non-Goals:**
- Modify mcp-router source code (unless necessary for wiki tool exposure)
- Create new MCP server implementations from scratch
- Change wiki or graphify CLI tool behavior
- Modify Claude Code's permission rules (already correct: `mcp__mcp-router__*`)

## Decisions

### Decision 1: Wiki tool exposure fix

**Chosen approach**: Split wiki into a separate MCP server entry in mcp-router.

The mcp-router HTTP server serves all 132 tools (verified via direct HTTP POST including session initialization). The CLI bridge (`connect.ts`) forwards all tools without filtering — `this.client.listTools()` returns everything. Tool catalog mode is not enabled (no projectId sent by Claude Code).

The root cause is a **Claude Code MCP client tool visibility limit** (~57 tools per server). With 12 servers registered and 132 total tools, many tools are invisible. Splitting wiki into a separate MCP server entry would give it its own tool namespace, bypassing the per-server limit.

**Options evaluated:**

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Separate MCP entry** | Register wiki as independent MCP server in mcp-router | Wiki tools get own namespace, bypasses limit | Requires wiki server to run standalone |
| B. Reduce server count | Disable unused servers (brightdata, grep-mcp, etc.) | More tool slots for wiki | Removes functionality |
| C. Wait for Claude Code fix | Client-side limit may be lifted in future | No changes needed | Wiki remains broken now |
| D. Use wiki CLI directly | Call wiki tools via bash/python | Works immediately | Not integrated into MCP |

**Recommendation**: Option A — Register wiki as a separate MCP server. The wiki server already runs as a standalone Python process. Adding it as a second entry (or replacing the current entry with a standalone config) gives it its own tool namespace.

### Decision 2: Graphify server approach

**Chosen approach**: Fix graphify server configuration to use correct MCP entry point.

Graphifyy 0.9.48 includes `python -m graphify.serve` — a full MCP stdio server. The current config uses `graphify ~/Developer/go-microservices --mcp --code-only` which is invalid. The correct command is:

```bash
~/.local/share/uv/tools/graphifyy/bin/python -m graphify.serve ~/Developer/go-microservices/graphify-out/graph.json
```

**Options evaluated:**

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Fix command** | Update mcp-router DB to use correct `python -m graphify.serve` | Full MCP integration, graph query tools exposed | Requires `mcp` package in graphifyy env |
| B. Remove from registry | Disable graphify in mcp-router | Clean, no false health status | Loses MCP integration |
| C. Keep as CLI only | Use graphify CLI directly | Simple | Not integrated into MCP |

**Recommendation**: Option A — Fix the command. Graphifyy 0.9.48 has proper MCP support. The current config just uses the wrong entry point.

### Decision 3: uv preference

All Python dependencies managed with `uv` (not pip). Wiki MCP server already uses `uv sync`. Any new Python scripts must use `uv run`.

## Risks / Trade-offs

- **[Risk] Claude Code tool limit is client-side** → Mitigation: Split wiki into separate MCP server entry to bypass per-server limit. If Claude Code lifts limit in future, can re-aggregate.
- **[Risk] Wiki server standalone stability** → Mitigation: Wiki server already runs as standalone Python process with `uv sync`. Adding as separate MCP entry doesn't change its runtime.
- **[Risk] Graphify removal breaks Hermes expectations** → Mitigation: Check Hermes health state config, update if needed. Graphify CLI still works independently.
- **[Trade-off] Removing graphify from MCP** → Users lose potential MCP integration, but graphify has no MCP mode anyway. CLI tools are already documented and working.
- **[Finding] 75 tools invisible to Claude Code** → Not just wiki. Tavily (5 tools), brightdata (5 tools), node_repl (3 tools), and others are also affected. Splitting high-priority servers (wiki, tavily) into separate entries is the pragmatic fix.
