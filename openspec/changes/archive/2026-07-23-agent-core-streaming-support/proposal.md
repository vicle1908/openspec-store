## Why

`AgentRuntime` spec (AR-5) requires `run_stream()` that returns an `AsyncIterator[StreamChunk]`. The `StreamChunk` and `ApprovalRequestChunk` types are referenced in `stream_approval.py` but never defined in `_ai/types.py` — causing import errors. The streaming method itself doesn't exist on `AgentRuntime`.

## What Changes

- **Define missing types**: `StreamChunk` and `ApprovalRequestChunk` dataclasses in `_ai/types.py`
- **Implement `run_stream()`**: Wrap pydantic-ai's `Agent.run_stream()` to yield `StreamChunk` instances
- **Fix `stream_approval.py`**: Remove broken imports, use the newly defined types
- **Update agent-runtime spec**: Remove DEFERRED status from AR-5
- **Update docs**: Reflect streaming as implemented

## Capabilities

### New Capabilities
- `agent-streaming`: Streaming support via `run_stream()` on `AgentRuntime`

### Modified Capabilities
- `agent-runtime` (existing): `AgentRuntime` gains `run_stream()` method

## Impact

- **Code**: `_ai/types.py`, `_ai/agent.py`, `_ai/stream_approval.py`
- **Tests**: New tests in `tests/test_streaming.py`
- **Dependencies**: None — uses existing pydantic-ai `run_stream()`
- **Backward compat**: Fully backward-compatible — `run_stream()` is additive
