# Proposal: MCP Router Watchdog v2 — Multi-Agent Resilience

## Why

The v1 watchdog (`mcp-router-health.sh`) correctly detects dead MCP servers
and restarts MCP Router, but has three critical gaps discovered during research:

### Gap 1: Full Restart Disrupts All 20 Clients

MCP Router serves **20 client tokens** simultaneously: Hermes, Claude Code,
Codex, Pi, Kimi Code, OpenCode, Cursor, Cline, VS Code, Zed, JetBrains,
Kilocode, Warp, Lingma, fable-5-dev, Copilot, Antigravity, Droid, and more.

When the watchdog runs `killall "MCP Router"`, ALL 20 clients lose ALL
MCP tools at once. Each client must independently re-discover and
re-connect. Hermes handles this (exponential backoff, 5 retries, parked
retry at 300s), but other agents may not recover gracefully.

**Research finding:** MCP Router does NOT auto-restart dead child processes.
When a child dies, its tools vanish immediately (verified: killing
medium-search reduced tools from 132→126). The only current recovery is
killing the entire Electron app.

### Gap 2: No Per-Server Recovery

All 7 local servers are treated equally. A crash in `medium-search`
(low-criticality) triggers the same full restart as `gitnexus` (high-
criticality, affects code intelligence for all agents).

### Gap 3: No Crash Pattern Visibility

No tracking of which servers crash, how often, or whether crashes cluster
(e.g., agentmemory always crashes after gateway restart). Without this,
we can't predict or prevent failures.

## What Changes

1. **Per-server process restart** (`--restart-server <name>`)
   - Kill only the dead server's child process, then signal MCP Router
     to respawn it via IPC (`mcp:stop` + `mcp:start`)
   - Falls back to full restart if IPC fails

2. **Criticality tiers** (in health check output)
   - HIGH: gitnexus, wiki, agentmemory (affect code intelligence)
   - MEDIUM: brave, desktop-commander, node_repl, medium-search
   - LOW: remote servers (auto-reconnect, no action needed)

3. **Crash tracking** (`~/.hermes/logs/mcp-router-crashes.json`)
   - Log each server crash with timestamp, context, recovery action
   - Detect patterns (e.g., "agentmemory crashes 3x/day after gateway restart")
   - Surface crash frequency in health check output

4. **Escalation logic**
   - Level 1: Restart individual dead server (if IPC available)
   - Level 2: Full MCP Router restart (if IPC fails or multiple servers dead)
   - Level 3: Alert user with crash report (if restart fails)

5. **Multi-agent awareness**
   - Document which agents are affected by each server
   - Include agent impact in crash alerts
   - Verify recovery works across agents (not just Hermes)

No changes to mcp-router code, MCP server registrations, or agent configs.
