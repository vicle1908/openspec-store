# Proposal: Agent Config Rationalization

## Why

The current Hermes Agent v0.20.4 installation has 5 configuration settings that should be tuned for better safety, resilience, and reduced noise. These are all operational guardrails and output budget settings — no provider, MoA, or approval posture changes.

The `agent.max_turns=500` setting is **intentionally retained** at its current value per user instruction. This is not an oversight.

## What Changes

### Config Mutations (5 total)

| # | Key | Current → New | Rationale |
|---|-----|---------------|-----------|
| 1 | `delegation.child_timeout_seconds` | `0` → `600` | Prevents hung subagents blocking orchestrator indefinitely. 10 min is generous — most subagents finish in <5 min. |
| 2 | `compression.idle_compact_after_seconds` | `300` → `900` | 5 min idle compresses mid-task when user steps away briefly. 15 min preserves context for natural breaks. |
| 3 | `tool_output.max_bytes` | `100000` → `50000` | Large tool outputs (full test suites, large grep results) bloat context and trigger premature compression. 50KB is still generous. |
| 4 | `tool_output.max_lines` | `5000` → `2000` | Same rationale — 2000 lines is still ample for terminal output. |
| 6 | `agent.api_max_retries` | `1` → `3` | Self-hosted gateways have transient network issues. 1 retry = immediate failure. 3 retries with backoff handles flaky connections. |

### NOT Changing (explicit)

- `agent.max_turns=500` — retained per user instruction
- MoA presets — production-tested, high-risk
- Approvals posture — correct for autonomous operation
- MCP Router definition — preserved per spec
- Provider configs — all working
- Display settings — just updated (show_reasoning=true, reasoning_full=true)

## Impact

- **Primary target:** `~/.hermes/config.yaml` — 6 key-value changes
- **Behavioral impact:** Subagents get a 10-minute timeout, tool outputs are capped more aggressively, idle compression is deferred, skill nudges are less frequent, API retries handle transient failures
- **Risk:** Low — all changes are guardrail/budget adjustments, not behavioral changes
- **Rollback:** Revert 6 keys via `hermes config set` or restore from `~/.hermes/state-snapshots/`
- **Repositories:** No application source changes
