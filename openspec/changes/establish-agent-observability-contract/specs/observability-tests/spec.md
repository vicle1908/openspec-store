## MODIFIED Requirements

### Requirement: LangfuseClient unit tests

The system SHALL have unit tests for `LangfuseClient` covering: initialization with config, no-op fallback when unconfigured, score_trace() method, and context manager behavior.

#### Scenario: Client initializes with config

- **WHEN** `LangfuseClient.create({"host": "http://localhost:3000", "public_key": "pk", "secret_key": "sk"})` is called
- **THEN** a client instance is returned (or no-op if SDK not installed)

#### Scenario: No-op fallback

- **WHEN** `LangfuseClient.create({})` is called with empty config
- **THEN** a no-op client is returned that silently discards operations

### Requirement: MLflowClient unit tests

The system SHALL have unit tests for `MLflowClient` covering: initialization, no-op fallback, start_run(), log_params(), log_metrics(), log_tags(), and exception isolation.

#### Scenario: Client initializes with URI

- **WHEN** `MLflowClient.create("http://localhost:5000")` is called
- **THEN** a client instance is returned (or no-op if SDK not installed)

#### Scenario: Exception isolation

- **WHEN** `MLflowClient.log_metrics()` raises an exception
- **THEN** the exception SHALL be caught
- **AND** a warning SHALL be logged
- **AND** the calling code SHALL continue normally

### Requirement: Scorer unit tests

The system SHALL have unit tests for CostScorer and RegressionScorer covering: evaluate() return type, threshold behavior, edge cases.

#### Scenario: CostScorer thresholds

- **WHEN** `CostScorer().evaluate()` is called with cost_usd/tokens_total combinations
- **THEN** scores are 1.0 (excellent), 0.8 (good), 0.5 (acceptable), 0.2 (expensive), 0.0 (zero tokens)

#### Scenario: RegressionScorer detection

- **WHEN** `RegressionScorer(baseline_latency_ms=5000).evaluate()` is called with latency_ms=3000 and success=True
- **THEN** result is `{"passed": True, "rationale": "within baseline"}`

### Requirement: Integration test

The system SHALL have an integration test that runs the full evaluation pipeline using pydantic-evals Dataset: create Dataset with cases and evaluators → run evaluate_sync() → verify EvaluationReport returned with correct case count.

#### Scenario: End-to-end evaluation

- **WHEN** `run_evaluation(dataset=my_dataset, task_function=my_agent, targets=[])` is called
- **THEN** pydantic-evals Dataset evaluation runs and EvaluationReport is returned

#### Scenario: MLflow logging

- **WHEN** `run_evaluation(dataset=my_dataset, task_function=my_agent, targets=["mlflow"])` is called with mocked MLflow
- **THEN** `_log_to_mlflow()` is called with the report

## ADDED Requirements

### Requirement: Startup activation conformance test

Every supported process entry point SHALL have a test proving that observability is initialized before any agent construction.

#### Scenario: agent-core CLI initializes observability

- **WHEN** an agent-core CLI command executes
- **THEN** `init_observability()` SHALL be called before the first agent is built
- **AND** an OTel span SHALL be emitted proving activation

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

### Requirement: Short-lived process flush test

Tests SHALL verify that CLI commands flush all pending spans before process exit.

#### Scenario: CLI exit flushes spans

- **WHEN** an agent-core CLI command completes
- **THEN** all pending OTel spans SHALL be exported before process exit

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

### Requirement: Backend failure isolation test

Tests SHALL verify that an unavailable Langfuse or MLflow backend does not prevent span export to other backends.

#### Scenario: Langfuse unavailable does not block OTel export

- **WHEN** Langfuse endpoint is unreachable
- **THEN** spans SHALL still be exported via the OTel Collector
- **AND** the process SHALL exit without error

### Requirement: Evaluation numeric score reporting test

Tests SHALL prove that numeric evaluator scores are reported as measurements, not as pass/fail assertions.

#### Scenario: Numeric scores reported as measurements

- **WHEN** an evaluation produces `{scores: {accuracy: 0.8}}`
- **THEN** the accuracy score SHALL be reported as a measurement
- **AND** the pass rate SHALL be `null` (no assertions)

### Requirement: Evaluation trace linkage test

Tests SHALL verify that `EvalRecord` stores nullable `trace_id` and `span_id` populated from `EvaluationReport`.

#### Scenario: Evaluation with active trace records trace IDs

- **WHEN** an evaluation runs inside an active OTel span
- **THEN** the `EvalRecord` SHALL have non-null `trace_id` and `span_id`

#### Scenario: Evaluation without trace records null IDs

- **WHEN** an evaluation runs outside any OTel span context
- **THEN** the `EvalRecord` SHALL have `trace_id=None` and `span_id=None`
