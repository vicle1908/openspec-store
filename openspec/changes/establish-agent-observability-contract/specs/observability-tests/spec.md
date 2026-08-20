## ADDED Requirements

### Requirement: Startup activation conformance test

Every supported process entry point SHALL have a test proving that observability is initialized before any agent construction.

#### Scenario: agent-core CLI initializes observability

- **WHEN** `agent-core review`, `agent-core propose`, or any agent-core CLI subcommand is invoked
- **THEN** `init_observability()` SHALL be called before the first agent is built
- **AND** an OTel span SHALL be emitted proving activation

#### Scenario: agent-docs-sync CLI initializes observability

- **WHEN** the `docs-sync` CLI is invoked
- **THEN** `init_observability(service_name="agent-docs-sync")` SHALL be called exactly once

#### Scenario: No import-time initialization

- **WHEN** any `agent_core` subpackage is imported without calling `init_observability()`
- **THEN** no OTel tracer provider SHALL be configured as a side effect

### Requirement: Initialization idempotency test

Tests SHALL prove that calling `init_observability()` twice does not add duplicate processors or emit duplicate spans.

#### Scenario: Duplicate call does not produce duplicate spans

- **WHEN** `init_observability()` is called twice with the same service name
- **THEN** a single logical operation SHALL produce exactly one root span

### Requirement: Span hierarchy assertion test

Tests SHALL verify the expected parent-child span tree for a complete agent run with tool calls.

#### Scenario: Agent run produces expected span tree

- **WHEN** an agent runs a single tool call
- **THEN** the exported span tree SHALL contain: root `invoke_agent` span with one child `execute_tool` span
- **AND** both spans SHALL carry the same `trace_id`
- **AND** the root span SHALL carry `gen_ai.agent.name` and `agent_core.run.id`

### Requirement: Duplicate-span detection test

Tests SHALL prove that `Agent.instrument_all()` and an explicit `Instrumentation()` capability do not produce duplicate spans for the same logical operation.

#### Scenario: Global and explicit instrumentation produce one span each

- **WHEN** `Agent.instrument_all()` is active and an agent runs with an explicit `Instrumentation()` capability
- **THEN** each logical operation SHALL produce exactly one span
- **AND** no span SHALL appear twice in the exported trace

### Requirement: Short-lived process flush test

Tests SHALL verify that CLI commands flush all pending spans before process exit.

#### Scenario: CLI exit flushes spans

- **WHEN** an agent-core CLI command completes
- **THEN** all pending OTel spans SHALL be exported before process exit
- **AND** the test SHALL verify spans were received by a test collector

### Requirement: Trace-log correlation test

Tests SHALL verify that structlog entries produced during an active span include `trace_id` and `span_id`.

#### Scenario: Structured log includes trace context

- **WHEN** `structlog.info("tool_executed")` is called inside an active OTel span
- **THEN** the JSON log output SHALL contain `trace_id` and `span_id` fields matching the active span

### Requirement: Content-off and redaction tests

Tests SHALL prove that prompts and tool payloads are NOT included in exported spans when `include_content=False`.

#### Scenario: Default privacy settings exclude content

- **WHEN** `init_observability()` is called with default settings
- **THEN** exported spans SHALL NOT contain prompt text or completion text
- **AND** tool arguments SHALL NOT appear in span attributes

### Requirement: Backend failure isolation test

Tests SHALL verify that an unavailable Langfuse or MLflow backend does not prevent span export to other backends.

#### Scenario: Langfuse unavailable does not block OTel export

- **WHEN** Langfuse endpoint is unreachable
- **THEN** spans SHALL still be exported via the OTel Collector
- **AND** the process SHALL exit without error

### Requirement: Evaluation trace-linkage test

Tests SHALL verify that `EvalRecord` stores nullable `trace_id` and `span_id`.

#### Scenario: Evaluation with active trace records trace IDs

- **WHEN** an evaluation runs inside an active OTel span
- **THEN** the `EvalRecord` SHALL have non-null `trace_id` and `span_id`

#### Scenario: Evaluation without trace records null IDs

- **WHEN** an evaluation runs outside any OTel span context
- **THEN** the `EvalRecord` SHALL have `trace_id=None` and `span_id=None`

### Requirement: Numeric evaluator aggregation test

Tests SHALL prove that numeric evaluation scores (e.g., `0.8`) are correctly aggregated, not excluded by identity comparison.

#### Scenario: Numeric score pass-rate is correct

- **WHEN** an evaluation produces scores `{accuracy: 0.8, cost: 1.0}` with threshold 0.5
- **THEN** the pass-rate SHALL reflect that both scores pass
- **AND** the aggregation SHALL not use `result.value is True`

### Requirement: MLflow exception isolation test

Tests SHALL verify that MLflow client exceptions are caught and logged, not propagated to callers.

#### Scenario: MLflow logging failure does not crash caller

- **WHEN** `MLflowClient.log_metrics()` raises an exception
- **THEN** the exception SHALL be caught
- **AND** a warning SHALL be logged
- **AND** the calling code SHALL continue normally

### Requirement: Conformance evidence levels

Each observability capability test SHALL declare its evidence level: specified, implemented, unit-tested, integration-tested, runtime-validated, or deployment-validated.

#### Scenario: Capability evidence is accurately classified

- **WHEN** an observability capability is tested
- **THEN** its evidence level SHALL be recorded
- **AND** runtime-validated SHALL only be claimed when verified against a running backend
