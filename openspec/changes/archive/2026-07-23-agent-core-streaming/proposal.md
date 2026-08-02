## Why

`AgentRuntime.run()` returns a complete `AgentResult` after the entire generation finishes. For long-running agents (multi-tool workflows, complex reasoning), users see nothing until completion. Pydantic AI V2 provides `run_stream()` with incremental validated output — text chunks arrive as they're generated, and structured output is validated incrementally against the schema. The LLM gateway already supports raw HTTP streaming (`LLMDelta`), but this isn't wired through to the agent runtime layer.

## What Changes

- New `run_stream()` method on `AgentRuntime` wrapping Pydantic AI's `run_stream()` API
- New `StreamChunk` type with `text`, `output`, `tool_call`, `usage`, and `done` fields
- `BaseAgent` exposes `run_stream()` as public async API
- ApprovalGate integration: stream interrupts for approval requests, resumes after approval
- Existing `run()` method unchanged — no breaking changes

## Capabilities

### New Capabilities
- `agent-streaming`: Incremental streaming of agent output with Pydantic AI validated structured output streaming, approval gate interruption, and `AsyncIterator[StreamChunk]` public API

### Modified Capabilities
<!-- No existing capabilities are modified — run() is unchanged -->

## Impact

- **Code:** `agent_core/_ai/agent.py` (run_stream), `agent_core/_ai/types.py` (StreamChunk), `agent_core/agent_base/agent.py` (public API)
- **Tests:** New `tests/agent_base/test_streaming.py`
- **Dependencies:** None new (uses existing Pydantic AI V2 streaming API)
- **Backward compatibility:** Fully backward compatible — new method, existing `run()` unchanged
