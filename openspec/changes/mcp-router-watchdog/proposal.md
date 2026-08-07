# Proposal: MCP Router Watchdog

## Why

MCP servers registered in mcp-router (Electron app) silently die without
auto-recovery. Discovery: agentmemory MCP shim crashed sometime after
Aug 6 17:10 and was not running by Aug 7 session start. 53 of 132 tools
were missing. Manual `killall "MCP Router" && open -a "MCP Router"` was
required to restore full tool surface.

Root cause: mcp-router does not monitor or restart its child MCP server
processes. When an `npx` or `python` subprocess exits (OOM, crash, timeout),
the tools silently disappear from the aggregated tool list. No alert, no
restart, no recovery.

Impact: Any Hermes session that starts while servers are down will never
see the missing tools for its entire lifetime (tools are cached at init).

## What Changes

1. **Health check script** (`~/.hermes/scripts/mcp-router-health.sh`)
   - Queries mcp-router SQLite DB for registered local servers
   - Compares against running child processes of mcp-router PID
   - Tests MCP tool availability via CLI bridge (`mcpr connect`)
   - Reports which servers are dead/missing
   - Exit code 0 = healthy, 1 = degraded, 2 = critical

2. **Auto-restart logic** (same script, `--restart` flag)
   - If any local server process is missing: restart MCP Router
   - Wait for re-initialization, then verify all servers came back
   - Log restart events to `~/.hermes/logs/mcp-router-watchdog.log`

3. **Hermes cron job** (every 10 minutes)
   - Runs the health check script
   - Only alerts if state changed (was healthy → now degraded)
   - Silent when healthy (no spam)

No changes to mcp-router code, MCP server registrations, or Hermes config.
