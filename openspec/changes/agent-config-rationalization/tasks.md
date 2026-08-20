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
- [ ] Fresh session activation needed: copied into agent state at construction; existing sessions retain 300 until gateway restart or fresh CLI session

### 3. tool_output.max_bytes
- [x] Apply: `hermes config set tool_output.max_bytes 50000`
- [x] Verify: returns `50000`
- [ ] Truncation smoke test: NOT RUN

### 4. tool_output.max_lines
- [x] Apply: `hermes config set tool_output.max_lines 3000`
- [x] Verify: returns `3000`
- [ ] read_file pagination smoke test: NOT RUN

### 5. agent.api_max_retries
- [x] Apply: `hermes config set agent.api_max_retries 3`
- [x] Verify: returns `3`
- [ ] Fresh session activation needed: copied into agent state at construction; gateway still uses `api_max_retries=1` until restart

## P3: Verification

### 6. Config validation
- [x] `hermes config check` — version 37, no errors
- [x] `hermes config get` on all 4 keys — confirmed new values
- [ ] `hermes doctor` — pending fresh run

### 7. Smoke tests
- [x] Gateway health: `status: ok`
- [x] Telegram round-trip: this conversation is proof
- [ ] Truncation: large output commands produce clean truncated output — NOT RUN

### 8. Regression check
- [x] `agent.max_turns` remains `500`
- [x] `display.show_reasoning` remains `true`
- [x] `display.reasoning_full` remains `true`

## P4: Evidence & Archive

### 9. Implementation evidence
- [x] Write implementation-evidence.md with backup ID, mutation log, verification results

### 10. Gateway restart for full activation
- [ ] User runs from separate terminal: `launchctl stop ai.hermes.gateway && sleep 3 && launchctl start ai.hermes.gateway`
- [ ] Verify: `curl -s http://127.0.0.1:8787/health` returns `status: ok`
- [ ] Verify: `hermes config get agent.api_max_retries` returns `3`
- [ ] Verify: `hermes config get compression.idle_compact_after_seconds` returns `900`

### 11. Truncation smoke tests (after restart)
- [ ] Generate output >50KB, verify clean truncation marker
- [ ] Use read_file on file >3000 lines, verify pagination
- [ ] Update evidence with observed results

### 12. Archive
- [ ] `openspec change validate agent-config-rationalization` — valid
- [ ] `openspec validate --all` — 377/377
- [ ] Update implementation-evidence.md with final observed results
- [ ] Run `openspec archive agent-config-rationalization --yes`

## Omitted (not implemented)

### delegation.child_timeout_seconds
- Research: `delegate_tool.py:2803` — `_child_future.result(timeout=child_timeout)` — wall-clock cap
- Decision: omit — 600s would kill productive long-running subagents, conflicts with `agent.max_turns=500`
- Recommendation if user wants later: 3600s, not 600s

## Rollback

If any setting causes issues:
1. Revert individual: `hermes config set <key> <old_value>`
2. Or full rollback: `launchctl stop ai.hermes.gateway && sleep 3 && /snapshot restore 20260820-035818-pre-rationalization-v2 && launchctl start ai.hermes.gateway`
