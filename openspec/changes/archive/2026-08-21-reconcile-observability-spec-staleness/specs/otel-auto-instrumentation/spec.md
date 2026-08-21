## REMOVED Requirements

### Requirement: AgentRuntime SHALL include Instrumentation capability

**Reason:** Unconditional explicit instrumentation conflicts with global `Agent.instrument_all()` ownership and can produce duplicate spans.

**Migration:** Global `Agent.instrument_all()` is canonical. An explicit `Instrumentation()` capability is used only when global instrumentation is unavailable or a per-agent override is intentionally supplied.

## ADDED Requirements

### Requirement: Pydantic AI instrumentation SHALL have one owner per logical operation

The system SHALL use `Agent.instrument_all()` as the canonical global instrumentation owner. AgentRuntime SHALL add explicit `Instrumentation()` only when required for fallback or per-agent override. Each logical operation SHALL emit exactly one span.

#### Scenario: Agent run emits OTel span

- **WHEN** an agent run completes via AgentRuntime.run()
- **THEN** an OTel span with name `invoke_agent {agent_name}` SHALL be created with attributes `gen_ai.agent.name`, `gen_ai.aggregated_usage.input_tokens`, and `gen_ai.aggregated_usage.output_tokens`

#### Scenario: Model request emits OTel span

- **WHEN** the agent makes an LLM API call
- **THEN** an OTel CLIENT span with name `chat {model_name}` SHALL be created with attributes `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, and `gen_ai.usage.output_tokens`

#### Scenario: Tool execution emits OTel span

- **WHEN** the agent executes a tool
- **THEN** an OTel INTERNAL span with name `execute_tool {tool_name}` SHALL be created with attribute `gen_ai.tool.name`

#### Scenario: Instrumentation composes with existing capabilities

- **WHEN** AgentRuntime has both Instrumentation and ApprovalGate capabilities
- **THEN** the Instrumentation span SHALL wrap the ApprovalGate hook execution (Instrumentation is outermost)

#### Scenario: Global instrumentation prevents duplicate spans

- **WHEN** global instrumentation is active
- **THEN** AgentRuntime SHALL NOT add a redundant default `Instrumentation()` capability
- **AND** each logical operation SHALL emit exactly one span

#### Scenario: Explicit instrumentation overrides per-agent settings

- **WHEN** a caller supplies an explicit `Instrumentation()` capability
- **THEN** the explicit settings SHALL apply to that agent
- **AND** no duplicate spans SHALL be emitted

## MODIFIED Requirements

### Requirement: InstrumentationSettings SHALL be configurable via settings

The system SHALL support configuring `InstrumentationSettings` parameters (`include_content`, `include_binary_content`, `include_model_request_parameters`) via `ObservabilitySettings` in `foundation/settings.py`.

#### Scenario: Privacy mode disables content capture

- **WHEN** `OTEL_INCLUDE_CONTENT=false` is set in environment
- **THEN** InstrumentationSettings SHALL be created with `include_content=False`, excluding prompts and completions from span attributes

#### Scenario: Binary content excluded by default

- **WHEN** no `OTEL_INCLUDE_BINARY_CONTENT` is set
- **THEN** InstrumentationSettings SHALL default to `include_binary_content=False`

#### Scenario: Model request parameters included by default

- **WHEN** no `OTEL_INCLUDE_MODEL_REQUEST_PARAMETERS` is set
- **THEN** InstrumentationSettings SHALL default to `include_model_request_parameters=True`

#### Scenario: Settings flow through to InstrumentationSettings

- **WHEN** `OTEL_INCLUDE_CONTENT=false` and `OTEL_INCLUDE_BINARY_CONTENT=false` are set
- **THEN** `configure_tracing()` SHALL pass these values directly to `InstrumentationSettings`, not derive them from `capture_sensitive_payloads`

### Requirement: Agent instrument_all SHALL be called at startup

The system SHALL call `Agent.instrument_all(InstrumentationSettings(...))` once during observability initialization so that any Agent constructed without an explicit Instrumentation capability still emits OTel spans.

#### Scenario: Global instrumentation activates for all agents

- **WHEN** `init_observability()` is called with a configured OTel endpoint
- **THEN** `Agent.instrument_all()` SHALL be invoked with settings derived from `ObservabilitySettings`
