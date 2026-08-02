## Context

`AgentRuntime.run()` returns a complete `AgentResult` after the entire generation finishes. For long-running agents (multi-tool workflows, complex reasoning), users see nothing until completion. The LLM gateway already supports raw HTTP streaming via `LLMGateway.stream()`, but this isn't wired through to the agent runtime layer. Pydantic AI V2 provides `run_stream()` with incremental validated output. LangGraph 1.2 provides streaming modes for real-time workflow monitoring.

## Goals / Non-Goals

**Goals:**
- `run_stream()` method on `AgentRuntime` wrapping Pydantic AI's streaming API
- `StreamChunk` type wrapping Pydantic AI's streaming output
- `BaseAgent.run_stream()` as public async context manager
- ApprovalGate integration: stream interrupts for approval requests
- LangGraph streaming mode="messages" for token-by-token LLM streaming
- StreamWriter support for custom node emissions
- Existing `run()` method unchanged

**Non-Goals:**
- WebSocket streaming for API servers (future enhancement)
- Streaming through LLM gateway's raw HTTP streaming (Pydantic AI handles this)
- Changing the LLM gateway's `stream()` method

## Decisions

### Decision 1: Wrap Pydantic AI's run_stream, not raw HTTP streaming

**Choice:** Use `pydantic_ai.Agent.run_stream()` as the streaming backbone

**Rationale:**
- Pydantic AI handles model-specific streaming differences
- Built-in structured output validation during streaming via `stream_output()`
- Tool call streaming is handled by the framework
- Raw HTTP streaming (LLMGateway.stream()) is for non-agent use cases

**Verified Pydantic AI V2 streaming API:**
```python
async with agent.run_stream("query") as response:
    async for text in response.stream_text():
        print(text)
    async for output in response.stream_output():
        print(output)
    print(response.output)
```

### Decision 2: Add LangGraph streaming for workflow-level monitoring

**Choice:** Support LangGraph's streaming modes in WorkflowEngine

**Rationale:**
- Enables real-time UI updates during agent execution
- Users see progress instead of waiting for completion
- StreamWriter allows nodes to emit custom progress data
- Version="v2" provides unified StreamPart format

**Verified LangGraph 1.2 streaming API:**
```python
for chunk in compiled.stream(
    state,
    config,
    stream_mode="messages",  # Token-by-token LLM streaming
    version="v2",            # Unified StreamPart format
):
    if chunk["type"] == "messages":
        msg, metadata = chunk["data"]
        # Yield to consumer for real-time updates
```

### Decision 3: StreamChunk as a simple dataclass

**Choice:** `StreamChunk` dataclass wrapping Pydantic AI's streaming output

**Rationale:**
- Simple, lightweight — chunks arrive frequently
- Wraps `StreamedRunResult` methods into a unified interface
- `done` flag signals stream completion
- No Pydantic model overhead for high-frequency objects

### Decision 4: ApprovalGate uses same capability for streaming and non-streaming

**Choice:** Reuse existing `HandleDeferredToolCalls` capability

**Rationale:**
- Pydantic AI's streaming integrates with deferred tool calls via the same Hooks/capabilities mechanism
- The existing `ApprovalGate` already handles this
- No new approval logic needed for streaming path

## Risks / Trade-offs

**[Risk] Pydantic AI streaming API stability** → `run_stream()` is V2 stable but may evolve. Mitigation: Wrap in adapter layer, isolate framework dependency.

**[Risk] LangGraph streaming version compatibility** → `version="v2"` requires LangGraph >= 1.2. Mitigation: Current dependency is `>=1.2.1` — already met.

**[Risk] Consumer complexity** → Streaming consumers must handle async iteration, error recovery, and context manager protocol. Mitigation: Provide example patterns in docs.

## Migration Plan

1. Add `StreamChunk` type to `agent_core/_ai/types.py`
2. Implement `run_stream()` in `AgentRuntime` wrapping `pydantic_ai.Agent.run_stream()`
3. Wire through `BaseAgent.run_stream()` public async context manager
4. Add `stream_mode` parameter to `WorkflowEngine.run()` for LangGraph streaming
5. Add `StreamWriter` support for custom node emissions
6. ApprovalGate works via existing `HandleDeferredToolCalls` capability — no changes needed
7. Add tests in `tests/agent_base/test_streaming.py` and `tests/orchestration/test_streaming.py`
8. Document streaming patterns in agent-core README
