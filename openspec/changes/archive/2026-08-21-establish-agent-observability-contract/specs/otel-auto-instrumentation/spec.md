## MODIFIED Requirements

### Requirement: AgentRuntime SHALL include Instrumentation capability

AgentRuntime.__init__() SHALL add `Instrumentation()` from `pydantic_ai.capabilities` to the capabilities list passed to the pydantic-ai Agent constructor. When both global `Agent.instrument_all()` and an explicit `Instrumentation()` capability are active, the system SHALL NOT emit duplicate spans for the same logical operation. The explicit capability MAY override per-agent settings (e.g., `include_content`) when it differs from global defaults.

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

#### Scenario: No duplicate spans from global and explicit instrumentation

- **WHEN** `Agent.instrument_all()` was called at startup and an agent runs with an explicit `Instrumentation()` capability
- **THEN** each logical operation SHALL produce exactly one span
- **AND** the explicit capability's settings SHALL apply to that agent when they differ from global defaults

## ADDED Requirements

### Requirement: Explicit and global instrumentation coordination

The system SHALL define a single canonical instrumentation path. `Agent.instrument_all()` SHALL be the primary mechanism. An explicit `Instrumentation()` capability on an `AgentRuntime` SHALL be reserved for per-agent setting overrides (e.g., different `include_content` value for a specific agent). The system SHALL prevent duplicate spans from both paths operating on the same logical operation.

#### Scenario: Global instrumentation active, explicit capability absent

- **WHEN** `Agent.instrument_all()` was called at startup and an agent runs without an explicit `Instrumentation()` capability
- **THEN** OTel spans SHALL be emitted by the global instrumentation

#### Scenario: Global instrumentation active, explicit capability present with different settings

- **WHEN** `Agent.instrument_all()` was called and an agent runs with an explicit `Instrumentation()` capability providing different settings (e.g., `include_content=True` vs global `False`)
- **THEN** the explicit capability's settings SHALL apply to that agent
- **AND** no duplicate spans SHALL be emitted
