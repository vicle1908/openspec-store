## ADDED Requirements

### Requirement: Langfuse SDK client initialization
The system SHALL provide a `LangfuseClient` class in `agent_core.observability.langfuse_client` that initializes the Langfuse SDK v4 (latest: 4.14.1) with configuration from `~/.tdt/config.yaml` (section `observability.langfuse_*`). The client SHALL use `langfuse.get_client()` (v4 API) for initialization. The client SHALL support both direct SDK initialization and OTel OTLP ingest mode.

#### Scenario: Client initializes with config
- **WHEN** `LangfuseClient.create()` is called with valid config (host, public_key, secret_key)
- **THEN** a Langfuse v4 client instance is returned via `get_client()` and the connection is verified

#### Scenario: Client initializes with missing config
- **WHEN** `LangfuseClient.create()` is called with empty host
- **THEN** a no-op client is returned that silently discards all operations (graceful degradation)

### Requirement: LLM call OTel instrumentation
The system SHALL add OTel spans to `BifrostGateway.complete()` and `LiteLLMGateway.complete()` (currently at `llm_gateway/gateway.py:243` and `gateway.py:437`) so that individual LLM calls appear as nested spans under the agent trace. Each LLM span SHALL capture: model name, prompt tokens, completion tokens, cost_usd, latency_ms, and finish_reason.

#### Scenario: LLM call produces OTel span
- **WHEN** `BifrostGateway.complete()` makes an HTTP call to the LLM provider
- **THEN** an OTel span `llm.complete` is created with attributes `gen_ai.system=openai`, `gen_ai.request.model=<model>`, `gen_ai.response.usage.prompt_tokens=<n>`, `gen_ai.response.usage.completion_tokens=<n>`, `gen_ai.usage.cost_usd=<cost>`

#### Scenario: LLM call with no OTel configured
- **WHEN** OTel is not configured (no-op tracer)
- **THEN** `BifrostGateway.complete()` functions normally with no tracing overhead

### Requirement: Tool execution OTel instrumentation
The system SHALL add an OTel span to `ToolRegistry.execute()` (currently at `tool_registry/registry.py:123`) so that each tool invocation appears as a nested span under the agent trace. Each tool span SHALL capture: tool name, input args (redacted), output length, duration_ms, and success status.

#### Scenario: Tool execution produces OTel span
- **WHEN** `ToolRegistry.execute("shell_execute", {"command": "ls"})` is called
- **THEN** an OTel span `tool.execute` is created with attributes `agent_core.tool.name=shell_execute`, `agent_core.tool.success=true`, `agent_core.tool.duration_ms=<ms>`

#### Scenario: Tool execution with no OTel configured
- **WHEN** OTel is not configured (no-op tracer)
- **THEN** `ToolRegistry.execute()` functions normally with no tracing overhead

### Requirement: Agent runs traced to Langfuse via OTel Collector
The system SHALL route OTel spans from `BaseAgent.run()` (which already emits spans via `tracer.start_as_current_span(OP_INVOKE_AGENT)` at `agent.py:210`) AND the new LLM/tool spans through the OTel Collector to Langfuse. The Collector handles batching and export. Langfuse will receive a complete trace tree: agent → LLM calls → tool executions.

#### Scenario: Full trace tree appears in Langfuse
- **WHEN** `BaseAgent.run("Summarize the README")` completes with 2 LLM calls and 3 tool calls
- **THEN** a Langfuse trace appears with: root span (agent run), 2 child spans (LLM calls with token/cost data), 3 child spans (tool executions with args/results)

#### Scenario: Agent run with no Collector configured
- **WHEN** `otel_collector_endpoint` is empty
- **THEN** `BaseAgent.run()` uses the existing no-op tracer (current behavior unchanged)

### Requirement: Langfuse @observe() decorator for enhanced tracing
The system SHALL optionally wrap `BaseAgent.run()` with Langfuse `@observe()` decorator when `observability.langfuse_inline_tracing` is enabled. This provides richer Langfuse-native features (session tracking, prompt/playground integration) beyond what OTel spans provide. When disabled, only OTel-routed spans are used.

#### Scenario: Inline tracing enabled
- **WHEN** `observability.langfuse_inline_tracing=true` and Langfuse is configured
- **THEN** `BaseAgent.run()` produces a Langfuse-native trace with nested spans for tool calls, PLUS the OTel span via Collector

#### Scenario: Inline tracing disabled (default)
- **WHEN** `observability.langfuse_inline_tracing=false` (default)
- **THEN** only OTel Collector-routed spans appear in Langfuse (no @observe() decorator)

### Requirement: Score recording on traces
The system SHALL record evaluation scores on Langfuse traces after each agent run. Scores SHALL include at minimum: `success` (boolean), `accuracy` (numeric 0-1), `tool_success_rate` (numeric 0-1), and `cost_usd` (numeric).

#### Scenario: Successful run records scores
- **WHEN** an agent run completes with `success=True` and `accuracy_score=0.95`
- **THEN** Langfuse scores `success=1.0`, `accuracy=0.95`, `tool_success_rate=<calculated>`, `cost_usd=<tracked>` are attached to the trace

#### Scenario: Failed run records scores
- **WHEN** an agent run completes with `success=False`
- **THEN** Langfuse score `success=0.0` is attached to the trace

### Requirement: Cost tracking via Langfuse
The system SHALL track per-run cost data in Langfuse using the model pricing information from the LLM gateway response. Cost data SHALL be visible in Langfuse's cost dashboard.

#### Scenario: LLM call cost tracked
- **WHEN** an agent run makes 3 LLM calls with costs $0.01, $0.02, $0.01
- **THEN** the Langfuse trace shows total cost $0.04 and per-model breakdown

### Requirement: Session-based multi-turn tracing
The system SHALL group traces from the same conversation/session under a Langfuse session using the `session_id` attribute. This enables multi-turn conversation analysis.

#### Scenario: Multi-turn conversation grouped
- **WHEN** 3 agent runs share `session_id="session-123"`
- **THEN** all 3 traces appear under the same Langfuse session, ordered by timestamp

### Requirement: Skill effectiveness tracking
The system SHALL record which skill was used for each agent run as a Langfuse trace tag (`skill=<name>`). This enables filtering and comparison by skill in the Langfuse UI.

#### Scenario: Skill tag recorded
- **WHEN** an agent run resolves to skill `jira-comprehensive-management`
- **THEN** the Langfuse trace has tag `skill=jira-comprehensive-management`

### Requirement: Tool call detail capture
The system SHALL capture each tool invocation as a nested Langfuse span with tool name, input arguments, output, duration, and success status.

#### Scenario: Tool call captured
- **WHEN** agent calls `shell_execute` with args `{"command": "ls -la"}`
- **THEN** a nested span appears under the agent trace with name `shell_execute`, input `{"command": "ls -la"}`, output `<ls output>`, duration `<ms>`, and status `success`
