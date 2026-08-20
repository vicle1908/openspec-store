# Proposal: Agent Config Rationalization

## Why

The Hermes Agent v0.20.4 installation has explicit overrides that deviate from installed defaults and should be tuned for better resilience and output management. These are operational guardrails and output budget settings — no provider, MoA, approval posture, or display changes.

## What Changes

### Config Mutations (4 total)

| # | Key | Current | Installed Default | Candidate | Rationale |
|---|-----|---------|-------------------|-----------|-----------|
| 1 | `compression.idle_compact_after_seconds` | 300 | 0 (disabled) | 900 | Defer idle compaction from 5 min to 15 min. Deliberate local tuning — installed default is disabled. Takes effect on fresh sessions only. |
| 2 | `tool_output.max_bytes` | 100000 | 50000 | 50000 | Restore installed default. Large terminal outputs bloat context and trigger premature compression. 50KB ≈ 12-15K tokens. |
| 3 | `tool_output.max_lines` | 5000 | 2000 | 3000 | Deliberate local compromise — 3000 reduces read_file pagination cap while avoiding disruption to file-reading workflows. |
| 4 | `agent.api_max_retries` | 1 | 3 | 3 | Restore installed default. Loop is `while retry_count < max_retries` — this is an attempt ceiling, not post-first-attempt retries. |

### NOT Changing (explicit)

- `agent.max_turns=500` — retained per user instruction
- `delegation.child_timeout_seconds=0` — wall-clock cap semantics (`_child_future.result(timeout=child_timeout)`), keep unlimited
- `display.show_reasoning=true` — just updated
- `display.reasoning_full=true` — just updated
- MoA presets — production-tested
- Approvals posture — correct for autonomous operation
- MCP Router definition — preserved per spec

## Impact

- **Primary target:** `~/.hermes/config.yaml` — 4 key-value changes
- **Behavioral impact:** Idle compression deferred, tool outputs capped at 50KB, read_file pagination capped at 3000 lines, API retry ceiling restored to 3
- **Risk:** Medium — `tool_output.max_lines=3000` affects read_file pagination; truncation and pagination smoke tests required before archive
- **Rollback:** Revert 4 keys via `hermes config set` or restore from snapshot
- **Repositories:** No application source changes
