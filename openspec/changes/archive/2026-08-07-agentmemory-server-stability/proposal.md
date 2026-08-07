# Proposal: agentmemory Server Stability

## Why

The agentmemory server (v0.9.28) suffered from WebSocket connection degradation
between the Node.js server and the iii engine (v0.11.2). After startup, the
WebSocket connection would break (1650+ reconnect attempts), causing the HTTP
routes on port 3111 to be unregistered. This made all REST API endpoints
(`/agentmemory/health`, `/agentmemory/remember`, `/agentmemory/smart-search`,
`/agentmemory/session/start`) return empty responses.

**Impact:** The Hermes plugin's 6 lifecycle hooks (prefetch, sync_turn,
on_session_end, on_pre_compress, on_memory_write, system_prompt_block) were
silently failing as no-ops. The plugin's 3 tools (`memory_recall`, `memory_save`,
`memory_search`) also relied on the REST API and returned empty results.

The server had no auto-restart mechanism — manual intervention was required
every time the WebSocket connection degraded.

## What Changes

1. **Kill and restart** the broken agentmemory process, establishing fresh
   WebSocket connections to the iii engine.

2. **launchd service** (`com.agentmemory.server.plist`) with:
   - Absolute paths to `node` and `agentmemory` CLI (launchd has no shell PATH)
   - `RunAtLoad` + `KeepAlive.SuccessfulExit=false` for auto-start on boot
     and auto-restart on crash
   - Proper environment variables (CI=1, HOME, PATH)

3. **Health watchdog** (`com.agentmemory.watchdog.plist`) running every 5 minutes:
   - Checks REST API health endpoint
   - If empty response or unhealthy status, kills and restarts server
   - Logs to `~/.agentmemory/log/watchdog.log`

4. **Health check script** (`~/.hermes/scripts/agentmemory-healthcheck.sh`):
   - Checks process existence, REST API health, response parsing
   - Auto-restart on failure with logging

## Risks

- **Low:** launchd duplicate-load error (code 5) when service is already loaded.
  Harmless — the existing service continues running.
- **Low:** Watchdog kills server during active WebSocket operations.
  Acceptable tradeoff for guaranteed recovery.

## Verification

- `curl http://localhost:3111/agentmemory/health` returns `{"status":"healthy"}`
- `launchctl list | grep agentmemory` shows both services registered
- Remember/search roundtrip returns results
- Embedding API returns 768-dim vectors (nomic-embed-text)
