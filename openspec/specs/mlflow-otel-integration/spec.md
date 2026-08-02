## Purpose

This specification defines requirements for Mlflow Otel Integration.

## Requirements

### Requirement: MLflow OTLP exporter SHALL be added to OTel Collector
`otel-collector-config.yaml` SHALL include an `otlp/mlflow` exporter pointing at `mlflow-server:5000` and the traces pipeline SHALL route to both `otlp/langfuse` and `otlp/mlflow`.

#### Scenario: Traces reach MLflow via OTel Collector
- **WHEN** an agent run completes and the OTel Collector is configured with the MLflow exporter
- **THEN** the trace SHALL appear in the MLflow tracing UI with spans for agent run, model requests, and tool executions

#### Scenario: MLflow not in Docker Compose — collector degrades gracefully
- **WHEN** the `mlflow-server` container is not running
- **THEN** the OTel Collector SHALL retry exports and log warnings but SHALL NOT drop traces destined for Langfuse

### Requirement: MLflow pydantic-ai autolog SHALL be best-effort
`configure_tracing()` SHALL attempt to call `mlflow.pydantic_ai.autolog()` if MLflow is configured. Failure (e.g., compatibility mismatch with pydantic-ai v2) SHALL be logged as a debug message and SHALL NOT block observability initialization.

#### Scenario: Autolog succeeds
- **WHEN** MLflow is configured and `mlflow.pydantic_ai.autolog()` succeeds
- **THEN** MLflow SHALL capture additional trace data via its native SDK alongside the OTel pipeline

#### Scenario: Autolog fails — OTel pipeline still works
- **WHEN** `mlflow.pydantic_ai.autolog()` raises an ImportError or compatibility error
- **THEN** a debug message SHALL be logged and traces SHALL still reach MLflow via the OTel Collector

### Requirement: MLflow experiment logging SHALL be preserved
The existing `MLflowClient` wrapper and `mlflow_hooks` in `builtins.py` SHALL continue to work for experiment logging (params, metrics, tags). This is independent of trace capture.

#### Scenario: Hook-based experiment logging still works
- **WHEN** `mlflow_hooks` in `builtins.py` calls `start_run()`/`log_params()`/`log_metrics()`/`end_run()`
- **THEN** the experiment data SHALL be recorded in MLflow experiment tracking
