# Tasks: Agent Config Rationalization

## P1: Pre-mutation Backup

### 1. Create pre-mutation snapshot
- [x] Run `hermes backup --quick --label pre-rationalization-v2`
- [x] Verify snapshot contains pre-mutation values for all 4 keys (idle_compact=300, max_bytes=100000, max_lines=5000, api_max_retries=1)
- [x] Record snapshot ID: `20260820-035818-pre-rationalization-v2`

## P2: Config Mutations (4 total)

### 2. compression.idle_compact_after_seconds
- [x] Apply: `hermes config set compression.idle_compact_after_seconds 900`
- [x] Verify: returns `900`
- [x] Fresh session activation confirmed after gateway restart (PID 1885)

### 3. tool_output.max_bytes
- [x] Apply: `hermes config set tool_output.max_bytes 50000`
- [x] Verify: returns `50000`
- [x] Truncation smoke test: 60KB terminal output cleanly truncated

### 4. tool_output.max_lines
- [x] Apply: `hermes config set tool_output.max_lines 3000`
- [x] Verify: returns `3000`
- [x] read_file pagination smoke test: 4797-line file paginated at 3000-line cap

### 5. agent.api_max_retries
- [x] Apply: `hermes config set agent.api_max_retries 3`
- [x] Verify: returns `3`
- [x] Fresh session activation confirmed after gateway restart (PID 1885)

## P3: Verification

### 6. Config validation
- [x] `hermes config check` — version 37, no errors
- [x] `hermes config get` on all 4 keys — confirmed new values post-restart
- [x] `hermes doctor` — clean (2 npm advisories only, pre-existing)

### 7. Smoke tests
- [x] Gateway health: `status: ok`
- [x] Telegram round-trip: this conversation is proof
- [x] Truncation: terminal output truncated cleanly at ~50KB

### 8. Regression check
- [x] `agent.max_turns` remains `500`
- [x] `display.show_reasoning` remains `true`
- [x] `display.reasoning_full` remains `true`
- [x] MoA presets unchanged

## P4: Evidence & Archive

### 9. Implementation evidence
- [x] Write implementation-evidence.md with backup ID, mutation log, verification results

### 10. Gateway restart for full activation
- [x] Gateway restarted via external terminal (PID 1885, server_started_at: 1787202743)
- [x] Verify: `curl -s http://127.0.0.1:8787/health` returns `status: ok`
- [x] Verify: `hermes config get agent.api_max_retries` returns `3`
- [x] Verify: `hermes config get compression.idle_compact_after_seconds` returns `900`

### 11. Archive
- [x] `openspec change validate agent-config-rationalization` — valid (skip_specs: true)
- [x] Run `openspec archive agent-config-rationalization --yes`

## Omitted (not implemented)

### delegation.child_timeout_seconds
- Research: `delegate_tool.py:2803` — `_child_future.result(timeout=child_timeout)` — wall-clock cap
- Decision: omit — 600s would kill productive long-running subagents, conflicts with `agent.max_turns=500`
- Recommendation if user wants later: 3600s, not 600s

## Rollback

If any setting causes issues:
1. Revert individual: `hermes config set <key> <old_value>`
2. Or full rollback: `launchctl stop ai.hermes.gateway && sleep 3 && /snapshot restore 20260820-035818-pre-rationalization-v2 && launchctl start ai.hermes.gateway`
