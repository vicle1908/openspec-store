# Tasks: Agent Config Rationalization

## P1: Pre-mutation Backup

### 1. Create pre-mutation snapshot
- [ ] Run `hermes backup --quick --label pre-rationalization`
- [ ] Verify snapshot contains pre-mutation values: `delegation.child_timeout_seconds=0`, `tool_output.max_bytes=100000`, `tool_output.max_lines=5000`, `compression.idle_compact_after_seconds=300`, `skills.creation_nudge_interval=15`, `agent.api_max_retries=1`
- [ ] Record snapshot ID for rollback

## P2: Config Mutations (6 total)

### 2. delegation.child_timeout_seconds
- [ ] Apply: `hermes config set delegation.child_timeout_seconds 600`
- [ ] Verify: `hermes config get delegation.child_timeout_seconds` returns `600`
- [ ] **Note:** Takes effect on new subagent sessions only; existing running subagents retain their prior timeout

### 3. compression.idle_compact_after_seconds
- [ ] Apply: `hermes config set compression.idle_compact_after_seconds 900`
- [ ] Verify: `hermes config get compression.idle_compact_after_seconds` returns `900`
- [ ] **Note:** Takes effect on new sessions only; existing long-lived sessions retain the old value

### 4. tool_output.max_bytes
- [ ] Apply: `hermes config set tool_output.max_bytes 50000`
- [ ] Verify: `hermes config get tool_output.max_bytes` returns `50000`
- [ ] **Note:** May truncate large tool outputs (test suites, broad grep). If issues arise, raise to 75000

### 5. tool_output.max_lines
- [ ] Apply: `hermes config set tool_output.max_lines 2000`
- [ ] Verify: `hermes config get tool_output.max_lines` returns `2000`
- [ ] **Note:** Same truncation risk as max_bytes

### 6. skills.creation_nudge_interval
- [ ] Apply: `hermes config set skills.creation_nudge_interval 50`
- [ ] Verify: `hermes config get skills.creation_nudge_interval` returns `50`

### 7. agent.api_max_retries
- [ ] Apply: `hermes config set agent.api_max_retries 3`
- [ ] Verify: `hermes config get agent.api_max_retries` returns `3`

## P3: Verification

### 8. Config check
- [ ] Run `hermes config check` — no errors
- [ ] Run `hermes config get` on all 6 keys — confirm new values
- [ ] Run `hermes doctor` — no new issues introduced

### 9. Smoke test
- [ ] Gateway health: `curl http://127.0.0.1:8787/health` returns `status: ok`
- [ ] Telegram round-trip: send test message, receive response

## P4: Evidence & Archive

### 10. Implementation evidence
- [ ] Write implementation-evidence.md with backup ID, mutation log, verification results

### 11. Archive
- [ ] Update main specs if delta specs were written
- [ ] Run `openspec archive agent-config-rationalization --yes`

## Rollback

If any setting causes issues:
1. Revert via `hermes config set <key> <old_value>`
2. Or restore from snapshot: `launchctl stop ai.hermes.gateway && sleep 3 && /snapshot restore <id> && launchctl start ai.hermes.gateway`
