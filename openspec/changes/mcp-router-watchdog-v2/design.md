# Design: MCP Router Watchdog v2

## Architecture

```
Hermes cron (every 10m)
  └─ mcp-router-health.sh v2
       │
       ├─ Phase 1: Process Audit (<1s)
       │   SQLite → registered servers + types
       │   pgrep → MCP Router PID + children
       │   Match → missing/healthy per server
       │
       ├─ Phase 2: Criticality Assessment
       │   HIGH: gitnexus, wiki, agentmemory
       │   MEDIUM: brave, desktop-commander, node_repl, medium-search
       │   LOW: remote servers (auto-reconnect)
       │
       ├─ Phase 3: Escalation Decision
       │   if 0 missing → healthy (no action)
       │   if 1 missing, MEDIUM → restart server only
       │   if 1 missing, HIGH → restart server, fallback to full restart
       │   if 2+ missing → full MCP Router restart
       │   if MCP Router dead → start MCP Router
       │
       ├─ Phase 4: Recovery Execution
       │   Option A: Per-server restart (experimental)
       │     - Kill dead child process
       │     - Signal MCP Router via DB trigger
       │     - Wait 10s, re-verify
       │   Option B: Full restart (proven)
       │     - killall "MCP Router"
       │     - open -a "MCP Router"
       │     - Wait 35s, re-verify
       │
       └─ Phase 5: Crash Tracking
           - Log event to mcp-router-crashes.json
           - Detect patterns (crash frequency, time correlation)
           - Include in health report
```

## Server Criticality Matrix

| Server | Tier | Agents Affected | Crash Impact |
|--------|------|----------------|--------------|
| gitnexus | HIGH | All 20 | Code intelligence lost (context, impact, query) |
| wiki | HIGH | All 20 | Curated knowledge unavailable |
| agentmemory | HIGH | All 20 | Episodic memory lost (53 tools) |
| brave | MEDIUM | All 20 | Web search fallback available via Hermes |
| desktop-commander | MEDIUM | Cursor, VS Code | Desktop control lost |
| node_repl | MEDIUM | All 20 | JavaScript REPL lost |
| medium-search | MEDIUM | All 20 | Article search lost |
| brightdata | LOW | All 20 | Auto-reconnects (remote) |
| context7 | LOW | All 20 | Auto-reconnects (remote) |
| deepwiki | LOW | All 20 | Auto-reconnects (remote) |
| docfork | LOW | All 20 | Auto-reconnects (remote) |
| exa | LOW | All 20 | Auto-reconnects (remote) |
| grep-mcp | LOW | All 20 | Auto-reconnects (remote) |
| tavily | LOW | All 20 | Auto-reconnects (remote) |

## Per-Server Restart Strategy

**Problem:** MCP Router Electron app does NOT auto-restart dead children.
Verified experimentally: `kill $MEDIUM_PID` → process stays dead, tools
vanish immediately (132→126 tools).

**Approach A: Direct child kill + DB signal (experimental)**
- Kill the dead child process (it's already dead, so this is a no-op)
- Update the server's `updated_at` timestamp in SQLite to trigger
  MCP Router to re-evaluate the server
- Wait for MCP Router to respawn the child

**Risk:** MCP Router may not watch the DB for changes (it caches on
startup). This needs testing.

**Approach B: Use Electron IPC (if accessible)**
- MCP Router exposes `mcp:start` and `mcp:stop` IPC channels
- Could send IPC command to restart a specific server
- **Blocker:** No known API surface for external IPC calls

**Approach C: Targeted process restart (pragmatic)**
- Instead of `killall "MCP Router"`, kill only the specific dead child
- Then kill MCP Router and immediately restart it
- MCP Router will spawn all children fresh, including the dead one
- **This is functionally equivalent to full restart but with better logging**

**Chosen: Approach C** (pragmatic, proven) with future option for
Approach A/B if MCP Router adds server management APIs.

## Crash Tracking Schema

File: `~/.hermes/logs/mcp-router-crashes.json`
```json
{
  "crashes": [
    {
      "timestamp": "2026-08-07T01:10:00Z",
      "server": "agentmemory",
      "severity": "high",
      "context": "cron-detection",
      "recovery": "full-restart",
      "recovery_success": true,
      "affected_agents": ["hermes", "claude-code", "codex", "pi", "fable-5"]
    }
  ],
  "patterns": {
    "agentmemory": {
      "total_crashes": 3,
      "last_24h": 1,
      "avg_time_between": "8h",
      "common_context": "post-gateway-restart"
    }
  }
}
```

## State File Enhancement

File: `/tmp/mcp-router-watchdog-state.json`
```json
{
  "status": "healthy",
  "healthy": true,
  "last_check": "2026-08-07T01:30:00Z",
  "missing_servers": [],
  "healthy_servers": ["agentmemory", "brave", ...],
  "critical_missing": [],
  "medium_missing": [],
  "crash_count_24h": 2,
  "last_restart": null,
  "tool_count": 132,
  "mcp_router_uptime": 37414,
  "clients_affected": 0
}
```

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Per-server restart via IPC | Zero disruption to other servers/clients | IPC API not confirmed accessible |
| Full restart (current) | Proven, reliable, simple | Disrupts all 20 clients for ~35s |
| Process kill only | Fast, no disruption | Tools vanish, no recovery without restart |
| Escalation (chosen) | Best of all: try gentle first, escalate | More complex script |

## Risks

1. **Per-server restart may not work**: MCP Router may not support it.
   Mitigation: Always fall back to full restart. Log the attempt.

2. **Crash tracking file grows unbounded**: Mitigation: Rotate weekly,
   keep last 100 entries.

3. **Multiple agents affected simultaneously**: This is inherent to the
   shared mcp-router architecture. Mitigation: document which agents
   recover automatically (Hermes) vs which need manual intervention.

4. **False pattern detection**: With only a few crashes, patterns may be
   misleading. Mitigation: require 3+ crashes before surfacing patterns.
