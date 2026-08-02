## ADDED Requirements

### Requirement: AgentRuntime SHALL include Instrumentation capability
AgentRuntime.__init__() SHALL add `Instrumentation()` from `pydantic_ai.capabilities` to the capabilities list passed to the pydantic-ai Agent constructor. This capability SHALL be placed before other capabilities in the list so it acts as the outermost middleware (tracing wraps everything).

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
