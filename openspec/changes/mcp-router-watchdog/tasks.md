# Tasks: MCP Router Watchdog

## Phase 1: Health Check Script

- [x] 1.1 Create `~/.hermes/scripts/mcp-router-health.sh` with process audit
  - Query mcp-router SQLite for registered local servers
  - Find mcp-router PID and its child processes
  - Match each registered server against running children
  - Output: JSON with status per server
  - Exit codes: 0=healthy, 1=degraded, 2=critical

- [ ] 1.2 Add `--restart` flag for auto-recovery
  - Kill MCP Router if any local server is missing
  - Wait 30s for re-initialization
  - Re-verify all servers are running
  - Log to `~/.hermes/logs/mcp-router-watchdog.log`

- [ ] 1.3 Add `--full` flag for MCP connectivity test
  - Test tool count via `mcpr connect` + tools/list
  - Compare against expected count
  - Report missing tool prefixes

## Phase 2: Cron Integration

- [ ] 2.1 Create Hermes cron job (every 10 minutes)
  - Run health check script
  - State file at `/tmp/mcp-router-watchdog-state.json`
  - Only alert on state transition (healthy → degraded)
  - Silent when healthy

- [ ] 2.2 Add alert delivery
  - Send alert to Telegram home when servers are dead
  - Include: which servers missing, when last healthy, restart attempted

## Phase 3: Verification

- [ ] 3.1 Test health check against current running state
  - Should report all 7 servers healthy
  - Tool count should match 132

- [ ] 3.2 Simulate server death
  - Kill agentmemory MCP shim process
  - Run health check → should detect missing server
  - Run with --restart → should restart MCP Router
  - Verify all servers restored

- [ ] 3.3 Verify cron delivery
  - Trigger cron manually
  - Confirm no alert when healthy
  - Confirm alert when degraded
