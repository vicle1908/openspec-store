# Design: Agent Config Rationalization

## Architecture

This is a configuration-only change. No application code, no architecture decisions. The design is a flat list of 6 key-value mutations in `~/.hermes/config.yaml`.

## Decision: agent.max_turns stays at 500

User explicitly retains `agent.max_turns=500`. This is intentional for complex multi-repo orchestration workflows. The 6 proposed changes do NOT touch this setting.

## Decision: tool_output budget reduction

Reducing `tool_output.max_bytes` from 100KB to 50KB and `max_lines` from 5000 to 2000 is aggressive but justified:
- Large tool outputs (full test suites, broad grep) consume context budget, trigger premature compression, and push out earlier context that matters more
- 50KB/2000 lines is still generous for 95% of operations
- If truncation causes issues, the operator can raise to 75KB/3000 lines

## Decision: idle compression deferred to 15 min

The current 5-minute idle timeout compresses context when the user steps away briefly. This loses detail mid-task. 15 minutes is long enough to preserve context during natural breaks while still compacting during genuine idle periods.

## Decision: subagent timeout at 10 min

A `child_timeout_seconds=0` means unlimited — a hung subagent blocks the orchestrator forever. The tool loop guardrails catch repeated tool failures but not slow progress. 10 minutes is generous (most subagents finish in <5 min) while preventing indefinite blocking.

## Rollback

All 6 changes are individually reversible via `hermes config set`. A pre-mutation snapshot provides full rollback.
