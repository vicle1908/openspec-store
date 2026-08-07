# Tasks: MCP Router Watchdog

## Phase 1: Health Check Script

- [x] 1.1 Create `~/.hermes/scripts/mcp-router-health.sh` with process audit
  - Query mcp-router SQLite for registered local servers
  - Find mcp-router PID and its child processes
  - Match each registered server against running children
  - Output: JSON with status per server
  - Exit codes: 0=healthy, 1=degraded, 2=critical

- [x] 1.2 Add `--restart` flag for auto-recovery
  - Kill MCP Router if any local server is missing
  - Wait 35s for re-initialization
  - Re-verify all servers are running
  - Log to `~/.hermes/logs/mcp-router-watchdog.log`

- [x] 1.3 Add `--full` flag for MCP connectivity test
  - Test tool count via `mcpr connect` + tools/list
  - Compare against expected count
  - Report missing tool prefixes

## Phase 2: Cron Integration

- [x] 2.1 Create Hermes cron job (every 10 minutes)
  - Run health check script
  - State file at `/tmp/mcp-router-watchdog-state.json`
  - Only alert on state transition (healthy → degraded)
  - Silent when healthy

- [x] 2.2 Add alert delivery
  - Deliver: local (cron saves output, no chat spam)
  - On degradation: report which servers missing
  - Manual recovery: `~/.hermes/scripts/mcp-router-health.sh --restart`

## Phase 3: Verification

- [x] 3.1 Test health check against current running state
  - Reports all 7 servers healthy ✓
  - JSON output correct ✓

- [x] 3.2 Simulate server death
  - Killed agentmemory MCP shim
  - Health check detected missing server (exit code 1) ✓
  - --restart flag restarted MCP Router ✓
  - All 7 servers restored ✓

- [x] 3.3 Verify cron delivery
  - Cron created: mcp-router-watchdog (every 10m)
  - Deliver: local (saves to ~/.hermes/cron/output/)
  - State tracking via /tmp/mcp-router-watchdog-state.json
