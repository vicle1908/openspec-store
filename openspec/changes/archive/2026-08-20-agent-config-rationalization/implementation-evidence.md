# Implementation Evidence: Agent Config Rationalization

**Date:** 2026-08-20 10:58 CST (Asia/Ho_Chi_Minh)
**Operator:** androidteam
**Hermes version:** v0.20.4 (2026.8.18)
**Change:** agent-config-rationalization (skip_specs: true)

## 1. Pre-mutation Backup

- **Snapshot ID:** `20260820-035818-pre-rationalization-v2`
- **Location:** `~/.hermes/state-snapshots/20260820-035818-pre-rationalization-v2/`
- **Verified pre-mutation:** All 4 keys at baseline values (idle_compact=300, max_bytes=100000, max_lines=5000, api_max_retries=1)
- **Restore command:** `/snapshot restore 20260820-035818-pre-rationalization-v2`

## 2. Configuration Mutations Applied (4 total)

| # | Key | Before → After | Source Default | Notes |
|---|-----|---------------|----------------|-------|
| 1 | `compression.idle_compact_after_seconds` | `300` → `900` | 0 (disabled) | Deliberate local tuning — decomp idle compaction from 5 min to 15 min |
| 2 | `tool_output.max_bytes` | `100000` → `50000` | 50000 | Restored installed default — terminal output cap in chars |
| 3 | `tool_output.max_lines` | `5000` → `3000` | 2000 | Deliberate compromise — 3000 reduces read_file pagination cap while avoiding disruption |
| 4 | `agent.api_max_retries` | `1` → `3` | 3 | Restored installed default — attempt ceiling (`while retry_count < max_retries`) |

All 4 verified on disk via `hermes config get`. Gateway reads config.yaml dynamically per-request.

## 3. Unchanged Settings (verified)

| Key | Value | Verified |
|-----|-------|----------|
| `agent.max_turns` | `500` | ✅ |
| `display.show_reasoning` | `true` | ✅ |
| `display.reasoning_full` | `true` | ✅ |
| `display.reasoning_style` | `code` | ✅ |
| `platforms.slack.show_reasoning` | `false` | ✅ |

## 4. Source Research (key findings)

| Setting | Source | Finding |
|---------|--------|---------|
| `delegation.child_timeout_seconds` | `delegate_tool.py:2803` | Wall-clock cap (`_child_future.result(timeout=child_timeout)`) — NOT inactivity timeout. Omitted from changes. |
| `agent.api_max_retries` | `conversation_loop.py:2799` | `while retry_count < max_retries` — attempt ceiling, not post-first-attempt retries. Each attempt calls the API directly. |
| `tool_output.max_lines` | `tool_output_limits.py:24` | Affects both terminal output AND `read_file` pagination cap. Using 3000 (not official default 2000) as deliberate compromise. |
| `compression.idle_compact_after_seconds` | `agent_init.py:2278-2283` | Copied into agent state at construction. Takes effect on fresh sessions only. |

## 5. Config Validation

- `hermes config check`: ✅ Version 37, no errors
- `openspec change validate`: ✅ Valid
- OpenSpec store: 377/377 specs validated

## 6. Smoke Tests

### Gateway health
- `curl http://127.0.0.1:8787/health` → `status: ok`
- Telegram round-trip: This conversation is proof

### Truncation (max_bytes=50000)
Terminal output should now be truncated at ~50KB head-tail window. Verified by observation in this session — large outputs are cleanly truncated with `[... truncated ...]` message.

### read_file pagination (max_lines=3000)
`read_file` with `limit=5000` will now be clamped to 3000. Files over 3000 lines require pagination via offset. This is a deliberate compromise from the official default of 2000.

## 7. Restore Procedure

Revert individual keys:
```
hermes config set compression.idle_compact_after_seconds 300
hermes config set tool_output.max_bytes 100000
hermes config set tool_output.max_lines 5000
hermes config set agent.api_max_retries 1
```

Or full rollback:
```
launchctl stop ai.hermes.gateway && sleep 3
/snapshot restore 20260820-035818-pre-rationalization-v2
launchctl start ai.hermes.gateway
```

## 8. Activation Notes

- `agent.api_max_retries` and `compression.idle_compact_after_seconds` are copied into agent state at construction — they take effect on fresh sessions or gateway restart.
- `tool_output.max_bytes` and `tool_output.max_lines` are read from config.yaml dynamically — they take effect immediately.
