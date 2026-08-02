## ADDED Requirements

### Requirement: AgentRuntime streaming API
The system SHALL provide `run_stream()` on `AgentRuntime` that wraps Pydantic AI's `run_stream()` and returns an async context manager yielding `StreamChunk` instances.

#### Scenario: Stream text output
- **WHEN** `async with agent_runtime.run_stream("query", deps) as stream:` is used
- **THEN** `async for chunk in stream.stream_text():` SHALL yield incremental text tokens as the model generates output

#### Scenario: Stream structured output
- **WHEN** `async with agent_runtime.run_stream("query", deps, output_type=MyModel) as stream:` is used
- **THEN** `async for chunk in stream.stream_output():` SHALL yield validated Pydantic model instances as they become available

#### Scenario: Stream completes
- **WHEN** the model finishes generating
- **THEN** the async context manager SHALL exit cleanly and `StreamedRunResult.output` SHALL contain the final result

### Requirement: LangGraph workflow streaming
The system SHALL support LangGraph's streaming modes for real-time workflow execution monitoring.

#### Scenario: Token-by-token LLM streaming
- **WHEN** `WorkflowEngine.run()` is called with `stream_mode="messages"`
- **THEN** the engine SHALL yield `(message_chunk, metadata)` tuples for each LLM token
- **AND** metadata SHALL include `langgraph_node` identifying which node produced the token

#### Scenario: Unified StreamPart format
- **WHEN** streaming with `version="v2"`
- **THEN** all stream chunks SHALL use the unified `StreamPart` format with `type` and `data` fields

#### Scenario: Custom data emission from nodes
- **WHEN** a node uses `get_stream_writer()` to emit custom data
- **THEN** the data SHALL be yielded as `stream_mode="custom"` chunks
- **AND** consumers SHALL receive the custom data in real-time
- **NOTE:** Use `from langgraph.config import get_stream_writer` inside node functions

#### Scenario: Checkpoint events during streaming
- **WHEN** streaming with `stream_mode="checkpoints"`
- **THEN** checkpoint events SHALL be yielded after each state transition
- **AND** events SHALL include the full state snapshot

### Requirement: StreamChunk type
The system SHALL define `StreamChunk` as a dataclass wrapping Pydantic AI's streaming output.

#### Scenario: Text chunk
- **WHEN** `stream.stream_text()` yields a text delta
- **THEN** a `StreamChunk` with `text=<delta>` SHALL be yielded

#### Scenario: Structured output chunk
- **WHEN** `stream.stream_output()` yields a validated model instance
- **THEN** a `StreamChunk` with `output=<model_instance>` SHALL be yielded

#### Scenario: Final result
- **WHEN** streaming completes
- **THEN** a `StreamChunk` with `done=True` and `output=<final_result>` SHALL be yielded

### Requirement: BaseAgent public streaming API
The `BaseAgent` class SHALL expose `run_stream()` as a public async context manager.

#### Scenario: Consumer calls run_stream
- **WHEN** `async with agent.run_stream("query") as stream:` is called
- **THEN** an async context manager yielding `StreamedRunResult` SHALL be returned

#### Scenario: Streaming preserves dependencies
- **WHEN** `agent.run_stream("query")` is called
- **THEN** the agent's configured dependencies SHALL be used automatically via `deps_type`

### Requirement: ApprovalGate streaming integration
The streaming path SHALL support approval gate interruption via Pydantic AI's `HandleDeferredToolCalls` capability.

#### Scenario: Approval needed during streaming
- **WHEN** a tool call with `requires_approval=True` is invoked during streaming
- **THEN** the `HandleDeferredToolCalls` capability SHALL intercept the deferred call
- **NOTE:** The existing `ApprovalGate` in `agent_core/_ai/capability.py` already handles this

#### Scenario: Streaming with approval
- **WHEN** `run_stream()` is used with tools requiring approval
- **THEN** the stream SHALL yield approval requests and pause until resolved

### Requirement: Thinking capability integration
The system SHALL support Pydantic AI's `Thinking` capability for provider-adaptive extended thinking.

#### Scenario: Enable thinking with default effort
- **WHEN** `AgentRuntime(capabilities=[Thinking()])` is constructed
- **THEN** the agent SHALL use the model provider's default thinking behavior

#### Scenario: Enable thinking with specific effort
- **WHEN** `AgentRuntime(capabilities=[Thinking(effort="high")])` is constructed
- **THEN** the agent SHALL use extended thinking at the specified effort level
- **NOTE:** Supported levels: "minimal", "low", "medium", "high", "xhigh" (xhigh only on nhà cung cấp dịch vụ AI claude-opus-4.8+)

#### Scenario: Provider-adaptive thinking
- **WHEN** thinking is enabled on a supporting model (nhà cung cấp dịch vụ AI, nhà cung cấp dịch vụ AI, Google)
- **THEN** the system SHALL use provider-native thinking APIs automatically
- **AND** non-supporting models SHALL gracefully fall back to no thinking

### Requirement: ToolSearch capability integration
The system SHALL support Pydantic AI's `ToolSearch` capability for progressive tool discovery.

#### Scenario: Enable tool search
- **WHEN** `AgentRuntime(capabilities=[ToolSearch()])` is constructed
- **THEN** tools marked with `defer_loading=True` SHALL be discovered on-demand

#### Scenario: Tool search strategy
- **WHEN** `ToolSearch(strategy='keywords')` is configured
- **THEN** the system SHALL use the specified strategy for tool discovery
- **NOTE:** Strategies: 'keywords', 'bm25', 'regex', or custom callable

### Requirement: Backward compatibility
The existing `AgentRuntime.run()` method SHALL remain unchanged.

#### Scenario: Non-streaming still works
- **WHEN** `AgentRuntime.run("query", deps)` is called
- **THEN** it SHALL return `AgentResult` exactly as before with no behavioral changes

### Requirement: Usage tracking in streaming
The system SHALL track token usage and cost during streaming runs.

#### Scenario: Usage captured
- **WHEN** a streaming run completes
- **THEN** `StreamedRunResult.usage()` SHALL return accurate token counts and cost data
