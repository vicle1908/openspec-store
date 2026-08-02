# Agent Streaming

## Purpose

Streaming support for agent-core via `run_stream()` on `AgentRuntime`, wrapping pydantic-ai's `Agent.run_stream()`.

## Requirements

### Requirement: AgentRuntime streaming API

`AgentRuntime` SHALL expose `run_stream(user_content, deps, output_type)` as an async generator function that yields `StreamChunk` instances.

#### Scenario: Stream text output
- **WHEN** `async for chunk in agent_runtime.run_stream("query", deps):` is used
- **THEN** chunks with `text=<delta>` SHALL be yielded incrementally as the model generates output

#### Scenario: Stream structured output
- **WHEN** `run_stream("query", deps, output_type=MyModel)` is called
- **THEN** the final chunk SHALL have `output=<validated_model_instance>` and `done=True`

#### Scenario: Stream completion
- **WHEN** the model finishes generating
- **THEN** a final `StreamChunk` with `done=True` SHALL be yielded

#### Scenario: Usage limit exceeded
- **WHEN** `UsageLimitExceeded` is raised during streaming
- **THEN** a `StreamChunk` with `done=True` SHALL be yielded (graceful degradation)

### Requirement: StreamChunk type

`StreamChunk` SHALL be a dataclass in `_ai/types.py` with fields:
- `text: str | None` — incremental text delta
- `output: Any | None` — final structured output
- `tool_call: dict[str, Any] | None` — tool call info (for approval requests)
- `done: bool` — True on final chunk

#### Scenario: Text chunk construction
- **WHEN** `StreamChunk(text="hello")` is created
- **THEN** `chunk.text` SHALL be `"hello"` and `chunk.done` SHALL be `False`

#### Scenario: Output chunk construction
- **WHEN** `StreamChunk(output={"key": "value"}, done=True)` is created
- **THEN** `chunk.output` SHALL be the dict and `chunk.done` SHALL be `True`

#### Scenario: Tool call chunk construction
- **WHEN** `StreamChunk(tool_call={"tool_name": "read_file", "args": {...}})` is created
- **THEN** `chunk.tool_call` SHALL contain the tool call info

### Requirement: ApprovalGate streaming integration

The streaming path SHALL support approval gate interruption via pydantic-ai's `HandleDeferredToolCalls` capability.

#### Scenario: Approval needed during streaming
- **WHEN** a tool call with `requires_approval=True` is invoked during streaming
- **THEN** `run_stream()` SHALL catch `_ApprovalResolutionError` and yield a `StreamChunk` with `tool_call` containing approval request info

#### Scenario: Streaming continues after approval
- **WHEN** the approval gate interrupts streaming
- **THEN** the stream SHALL terminate gracefully with `done=True`

### Requirement: Backward compatibility

The existing `AgentRuntime.run()` method SHALL remain unchanged.

#### Scenario: Non-streaming still works
- **WHEN** `AgentRuntime.run("query", deps)` is called
- **THEN** it SHALL return `AgentResult` exactly as before with no behavioral changes

### Requirement: LangGraph workflow streaming

> **Status: NOT YET IMPLEMENTED** — `WorkflowEngine.run()` uses `invoke` only. Streaming via `stream_mode` parameter is planned for a future change.

`WorkflowEngine` SHALL support streaming modes for real-time workflow execution monitoring.

#### Scenario: Token-by-token LLM streaming
- **WHEN** `WorkflowEngine.run()` is called with `stream_mode="messages"`
- **THEN** the engine SHALL yield `(message_chunk, metadata)` tuples for each LLM token
