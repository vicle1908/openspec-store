# Design: MCP Router Watchdog

## Architecture

```
Hermes cron (every 10m)
  └─ mcp-router-health.sh
       ├─ Phase 1: Process audit
       │   sqlite3 → list registered local servers
       │   pgrep → find mcp-router PID
       │   pstree/pgrep -P → list child processes
       │   Match: for each registered server, find matching child
       │
       ├─ Phase 2: MCP connectivity test (optional, slower)
       │   echo init+tools/list | mcpr connect → verify tool count
       │   Compare against expected count (132 from last known good)
       │
       └─ Phase 3: Recovery (if --restart flag)
           killall "MCP Router" → open -a "MCP Router"
           sleep 30 → re-verify
           Log result
```

## Server Detection Strategy

Each registered server has a `command` + `args` in the SQLite DB. We match
against running process command lines:

| Server | Expected Process Pattern |
|--------|------------------------|
| agentmemory | `agentmemory/mcp` |
| brave | `brave-search-mcp` |
| desktop-commander | `desktop-commander` |
| gitnexus | `gitnexus` |
| medium-search | `medium-mcp-server` |
| node_repl | `node_repl` |
| wiki | `wiki_mcp_server` or `wiki-mcp-server` |

The matching is fuzzy (substring) since npm/npx wraps commands differently.

## State Tracking

Last known state stored in `/tmp/mcp-router-watchdog-state.json`:
```json
{
  "last_check": "2026-08-07T07:30:00",
  "healthy": true,
  "missing_servers": [],
  "tool_count": 132,
  "last_restart": null
}
```

State file is in `/tmp/` (ephemeral) — if the machine reboots, the cron
re-discovers state from scratch. This is intentional: a reboot also
restarts mcp-router.

## Recovery Behavior

- **Degraded** (1-2 servers missing but mcp-router running): Restart MCP Router
- **Critical** (mcp-router not running): Start MCP Router
- **Healthy**: No action, no alert

Alert delivery: via Hermes cron `deliver` to Telegram home channel.
Only alert on state transitions (healthy→degraded), not every check.

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Process tree audit (chosen) | Fast (<1s), no network, no tool calls | Can't detect zombie processes that are alive but unresponsive |
| MCP tool count test | Catches all failure modes | Slower (~7s for mcpr connect), depends on npx cache |
| Both (chosen) | Fast first pass, thorough second pass | Slightly more complex script |

We use process audit as the fast path and skip the MCP connectivity test
in the cron (too slow for 10-minute intervals). The MCP test is available
as an `--full` flag for manual diagnostics.

## Risks

1. **Restart disrupts active sessions**: Killing MCP Router kills all MCP
   connections. Any in-flight tool calls will fail. Mitigation: only restart
   when no active Hermes sessions are processing (cron runs during idle).
   Actually, this is unavoidable — better to restart promptly than leave
   tools broken for hours.

2. **False positives**: A server might take time to start (npx download).
   Mitigation: the script only checks servers that should be running
   (mcp-router has been up for >60s).

3. **npx cache misses**: First `npx -y @agentmemory/mcp` after cache clear
   takes 30+ seconds. Mitigation: global installs exist for most servers.
