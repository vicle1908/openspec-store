# Tasks: agentmemory Server Stability

## Phase 1: Investigation

- [x] 1.1 Investigate agentmemory server status — 4 processes running, WebSocket degraded (1650+ reconnect attempts), REST API returning empty
- [x] 1.2 Check official agentmemory docs (rohitg00/agentmemory) — confirmed REST API format, launchd not documented
- [x] 1.3 Verify mcp-router adapter — agentmemory registered in mcp-router DB, auto_start=1, healthy
- [x] 1.4 Check plugin compatibility — plugin v0.8.0 with 6 lifecycle hooks, allow_tool_override=true, plugin tools override MCP same-named tools

## Phase 2: Fix

- [x] 2.1 Kill broken agentmemory (PID 50597) and iii (PID 50687) processes
- [x] 2.2 Clean stale PID files from ~/.agentmemory/run/
- [x] 2.3 Start fresh agentmemory instance — verify REST API endpoints work (health, remember, search, session/start)
- [x] 2.4 Clean up duplicate instance (old PID 80668 vs fresh PID 82762)

## Phase 3: Persistence (launchd)

- [x] 3.1 Fix launchd plist PATH issue — launchd has no shell PATH, node not found (`env: node: No such file or directory`)
- [x] 3.2 Rewrite com.agentmemory.server.plist with absolute paths (`/opt/homebrew/bin/node`, full cli.mjs path)
- [x] 3.3 Create com.agentmemory.watchdog.plist — health check every 5 minutes
- [x] 3.4 Create agentmemory-healthcheck.sh — checks process, REST API, restart on failure
- [x] 3.5 Load both launchd services — verify auto-start works

## Phase 4: Verification

- [x] 4.1 Full health check sequence: server health, iii engine, ports, embeddings, observe+search roundtrip
- [x] 4.2 REST API endpoints: /health (healthy), /remember (success), /smart-search (results), /session/start (session created)
- [x] 4.3 launchd services registered: com.agentmemory.server (PID 4748), com.agentmemory.watchdog
- [x] 4.4 Embedding API: nomic-embed-text returning 768-dim vectors via Ollama
