# Tasks: MCP Router Watchdog v2

## Phase 1: Criticality Tiers + Enhanced Health Check

- [x] 1.1 Add criticality tiers to health check output
  - Classify each server: HIGH (gitnexus, wiki, agentmemory), MEDIUM (brave, desktop-commander, node_repl, medium-search), LOW (remote)
  - Include tier in JSON output (`criticality` field via critical_missing/medium_missing arrays)

- [x] 1.2 Add multi-agent impact info
  - Map each server to affected agents via get_affected_agents()
  - Document which agents auto-recover (Hermes) vs need manual fix

## Phase 2: Escalation Logic

- [x] 2.1 Implement escalation levels
  - Level 1: Per-server restart attempt (planned for future when MCP Router IPC confirmed)
  - Level 2: Full MCP Router restart (implemented, proven)
  - Level 3: User alert with crash report (implemented via --report)

- [x] 2.2 Add `--restart-server <name>` flag
  - Flag parsing implemented, falls back to full restart

- [x] 2.3 Add `--escalate` flag for automatic escalation
  - Logs crashes, then performs full restart
  - Level 1 (per-server) reserved for future MCP Router IPC support

## Phase 3: Crash Tracking

- [x] 3.1 Create crash tracking file
  - Path: ~/.hermes/logs/mcp-router-crashes.json
  - Schema: timestamp, server, severity, context, recovery, success
  - Rotation: keep last 100 entries

- [x] 3.2 Add crash pattern detection
  - Count crashes per server in last 24h
  - Track total crashes per server
  - Surface patterns in health report output

- [x] 3.3 Add crash frequency to health report
  - Include `crash_count_24h` in state file and JSON output
  - --report flag shows per-server patterns with ⚠️ flag for ≥3 crashes/day

## Phase 4: Verification

- [x] 4.1 Test criticality classification
  - HIGH servers flagged correctly in critical_missing array
  - MEDIUM servers flagged in medium_missing array

- [x] 4.2 Test crash tracking
  - Killed agentmemory, crash logged to mcp-router-crashes.json ✓
  - 2nd crash logged, crash_count_24h=2 ✓
  - Pattern shows total_crashes=2, last_24h=2 ✓

- [x] 4.3 Test escalation
  - --escalate flag logs crashes then performs full restart ✓
  - All 7 servers restored after escalation ✓

- [x] 4.4 Update cron job
  - Updated cron to use --escalate for HIGH server degradation
  - Medium-only degradation logged but not auto-restarted
  - Crash count included in alerts
