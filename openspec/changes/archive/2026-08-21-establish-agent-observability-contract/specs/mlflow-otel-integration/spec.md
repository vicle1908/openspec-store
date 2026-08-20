## MODIFIED Requirements

### Requirement: MLflow OTLP exporter SHALL be added to OTel Collector

MLflow trace ingestion SHALL use exactly one configured route mode: `autolog` (MLflow pydantic-ai autolog), `collector` (OTel Collector exporter via `otlp/mlflow`), or `disabled`. The default mode SHALL be determined by Phase 0 deployment evidence, not assumed. Collector mode SHALL be implemented only after deployment validation confirms the OTel Collector and MLflow backend support OTLP trace ingestion. Autolog and Collector trace ingestion SHALL NOT be active simultaneously. The selected mode SHALL be determined at configuration time and SHALL NOT change at runtime.

#### Scenario: Traces reach MLflow via OTel Collector

- **WHEN** an agent run completes and the OTel Collector is configured with the MLflow exporter
- **THEN** the trace SHALL appear in the MLflow tracing UI with spans for agent run, model requests, and tool executions
- **AND** this route is conditional on Phase 0 deployment validation

#### Scenario: MLflow not in Docker Compose — collector degrades gracefully

- **WHEN** the `mlflow-server` container is not running
- **THEN** the OTel Collector SHALL retry exports and log warnings but SHALL NOT drop traces destined for Langfuse

#### Scenario: Autolog mode active

- **WHEN** MLflow is configured with mode `autolog`
- **THEN** traces SHALL reach MLflow via `mlflow.pydantic_ai.autolog()` SDK integration
- **AND** no Collector MLflow exporter SHALL be registered for the same pipeline

#### Scenario: Collector mode active (deferred)

- **WHEN** MLflow is configured with mode `collector`
- **THEN** the OTel Collector SHALL include an `otlp/mlflow` exporter
- **AND** traces SHALL reach MLflow exclusively through the Collector
- **AND** `mlflow.pydantic_ai.autolog()` SHALL NOT be called

#### Scenario: Disabled mode

- **WHEN** MLflow is configured with mode `disabled`
- **THEN** no MLflow trace export SHALL occur
- **AND** the application SHALL function normally

### Requirement: MLflow pydantic-ai autolog SHALL be best-effort

`configure_tracing()` SHALL attempt to call `mlflow.pydantic_ai.autolog()` if MLflow is configured with mode `autolog`. Failure (e.g., compatibility mismatch with pydantic-ai v2) SHALL be logged as a debug message and SHALL NOT block observability initialization. On failure, the MLflow mode SHALL be treated as `disabled`.

#### Scenario: Autolog succeeds

- **WHEN** MLflow is configured and `mlflow.pydantic_ai.autolog()` succeeds
- **THEN** MLflow SHALL capture additional trace data via its native SDK alongside the OTel pipeline

#### Scenario: Autolog fails — OTel pipeline still works

- **WHEN** `mlflow.pydantic_ai.autolog()` raises an ImportError or compatibility error
- **THEN** a debug message SHALL be logged
- **AND** traces SHALL still reach other configured backends via the OTel pipeline

### Requirement: MLflow experiment logging SHALL be preserved

The existing `MLflowClient` wrapper SHALL continue to work for experiment logging (params, metrics, tags) independent of trace capture mode. The `MLflowClient` wrapper SHALL isolate exceptions from callers.

#### Scenario: Hook-based experiment logging still works

- **WHEN** `mlflow_hooks` in `builtins.py` calls `start_run()`/`log_params()`/`log_metrics()`/`end_run()`
- **THEN** the experiment data SHALL be recorded in MLflow experiment tracking

#### Scenario: MLflow logging failure does not crash caller

- **WHEN** `MLflowClient.log_metrics()` raises an exception
- **THEN** the exception SHALL be caught
- **AND** a warning SHALL be logged
- **AND** the calling code SHALL continue normally
