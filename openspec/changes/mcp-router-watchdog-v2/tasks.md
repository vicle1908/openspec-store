# Tasks: MCP Router Watchdog v2

## Phase 1: Criticality Tiers + Enhanced Health Check

- [ ] 1.1 Add criticality tiers to health check output
  - Classify each server: HIGH/MEDIUM/LOW
  - Include tier in JSON output (`criticality` field)
  - Add `critical_missing` and `medium_missing` arrays

- [ ] 1.2 Add multi-agent impact info
  - Map each server to affected agents
  - Include `affected_agents` in crash/alert output
  - Document which agents auto-recover (Hermes) vs need manual fix

## Phase 2: Escalation Logic

- [ ] 2.1 Implement escalation levels
  - Level 1: Per-server restart attempt (kill child, signal DB)
  - Level 2: Full MCP Router restart (if Level 1 fails or 2+ servers dead)
  - Level 3: User alert with crash report (if restart fails)

- [ ] 2.2 Add `--restart-server <name>` flag
  - Attempt to restart individual server
  - Log attempt and result
  - Fall back to full restart on failure

- [ ] 2.3 Add `--escalate` flag for automatic escalation
  - Try Level 1 first, then Level 2, then Level 3
  - Log each escalation step

## Phase 3: Crash Tracking

- [ ] 3.1 Create crash tracking file
  - Path: `~/.hermes/logs/mcp-router-crashes.json`
  - Schema: timestamp, server, severity, context, recovery, success
  - Rotate: keep last 100 entries

- [ ] 3.2 Add crash pattern detection
  - Count crashes per server in last 24h
  - Detect clusters (3+ crashes in 1 hour)
  - Surface patterns in health check output

- [ ] 3.3 Add crash frequency to health report
  - Include `crash_count_24h` in state file
  - Include per-server crash counts in JSON output

## Phase 4: Verification

- [ ] 4.1 Test criticality classification
  - Verify HIGH servers flagged correctly
  - Verify escalation logic chooses right level

- [ ] 4.2 Test crash tracking
  - Kill a server, verify crash logged
  - Kill same server 3x, verify pattern detected

- [ ] 4.3 Test escalation
  - Kill one MEDIUM server → should attempt per-server restart
  - Kill one HIGH server → should attempt per-server then full restart
  - Kill 2+ servers → should go straight to full restart

- [ ] 4.4 Update cron job
  - Update existing cron to use enhanced script
  - Verify delivery still works
