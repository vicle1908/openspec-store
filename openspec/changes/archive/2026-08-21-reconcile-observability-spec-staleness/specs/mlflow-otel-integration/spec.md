## REMOVED Requirements

### Requirement: MLflow OTLP exporter SHALL be added to OTel Collector

**Reason:** Unconditional Collector routing conflicts with the implemented exclusive route-mode model.

**Migration:** Configure exactly one MLflow route: `autolog`, `collector`, or `disabled`. `autolog` is the default; `collector` remains explicitly configured and deployment-gated.

## ADDED Requirements

### Requirement: MLflow trace ingestion SHALL use an exclusive route mode

MLflow tracing SHALL use exactly one of `autolog`, `collector`, or `disabled`. The selected mode SHALL be determined at configuration time and SHALL NOT change at runtime.

#### Scenario: Autolog mode is the default

- **WHEN** no explicit MLflow route mode is configured
- **THEN** the system SHALL use `autolog`
- **AND** it SHALL NOT configure Collector export to MLflow

#### Scenario: Collector mode is explicitly selected

- **WHEN** `mlflow_mode=collector`
- **THEN** autolog SHALL NOT be enabled
- **AND** Collector export SHALL remain subject to deployment validation

#### Scenario: MLflow tracing is disabled

- **WHEN** `mlflow_mode=disabled`
- **THEN** neither autolog nor Collector trace export SHALL be enabled

## MODIFIED Requirements

### Requirement: MLflow pydantic-ai autolog SHALL be best-effort

`configure_tracing()` SHALL attempt to call `mlflow.pydantic_ai.autolog()` if MLflow is configured with mode `autolog`. Failure (e.g., compatibility mismatch with pydantic-ai v2) SHALL be logged as a debug message and SHALL NOT block observability initialization.

#### Scenario: Autolog succeeds

- **WHEN** MLflow is configured and `mlflow.pydantic_ai.autolog()` succeeds
- **THEN** MLflow SHALL capture additional trace data via its native SDK alongside the OTel pipeline

#### Scenario: Autolog fails — OTel pipeline still works

- **WHEN** autolog raises an import or compatibility error
- **THEN** the failure SHALL be logged without blocking observability initialization
- **AND** other configured OTel backends SHALL continue operating
- **AND** MLflow tracing SHALL be treated as disabled unless another route was explicitly selected

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
