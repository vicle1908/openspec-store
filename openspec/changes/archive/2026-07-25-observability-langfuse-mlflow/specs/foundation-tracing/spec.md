## MODIFIED Requirements

### Requirement: OTel tracing endpoint configuration
The system SHALL configure the OTel tracer provider to export spans to the OTel Collector endpoint (default: `http://otel-collector:4317`) instead of directly to a backend. The `ObservabilitySettings.otel_endpoint` field (currently at `foundation/settings.py:146`, env prefix `OTEL_`) SHALL be deprecated in favor of a new `otel_collector_endpoint` field. The `configure_tracing()` function (currently at `foundation/tracing.py:39`) SHALL accept both parameters for backward compatibility.

#### Scenario: Traces route through Collector
- **WHEN** `configure_tracing(otel_collector_endpoint="http://otel-collector:4317")` is called
- **THEN** spans are exported to the Collector, which routes them to configured backends

#### Scenario: Backward-compatible direct endpoint
- **WHEN** `configure_tracing(otel_endpoint="http://backend:4317")` is called (legacy parameter)
- **THEN** spans are exported directly to the specified endpoint (backward compatible)

#### Scenario: No Collector configured
- **WHEN** both `otel_collector_endpoint` and `otel_endpoint` are empty
- **THEN** a no-op tracer is used (existing behavior unchanged, as defined at `tracing.py:59-61`)

### Requirement: Tracer provider initialization
The system SHALL initialize the OTel TracerProvider with GenAI semantic conventions (v1.37+) and batch span processor. The `configure_tracing()` function SHALL accept both `otel_endpoint` (deprecated) and `otel_collector_endpoint` (new) parameters. The existing `ObservabilitySettings` class SHALL be extended with the new field while preserving backward compatibility with the `OTEL_` env prefix.

#### Scenario: New config key used
- **WHEN** `configure_tracing(otel_collector_endpoint="http://otel-collector:4317", service_name="agent-core")` is called
- **THEN** a TracerProvider is configured with batch export to the Collector

#### Scenario: Deprecated key still works
- **WHEN** `configure_tracing(otel_endpoint="http://old-backend:4317")` is called
- **THEN** a TracerProvider is configured with export to the old backend (deprecated path)

### Requirement: ObservabilitySettings extension
The `ObservabilitySettings` class in `foundation/settings.py` SHALL be extended with new fields for Langfuse and MLflow configuration. The existing `OTEL_*` env prefix SHALL be preserved. New settings SHALL use separate env prefixes: `LANGFUSE_*` for Langfuse and `MLFLOW_*` for MLflow. The new fields SHALL have sensible defaults (empty strings for endpoints, false for disabled features).

#### Scenario: New settings loaded from config.yaml
- **WHEN** `config.yaml` contains `observability.langfuse_host: "http://localhost:3000"`
- **THEN** the `ObservabilitySettings` instance has `langfuse_host="http://localhost:3000"`

#### Scenario: Env vars override yaml
- **WHEN** `LANGFUSE_HOST=http://prod:3000` is set and `config.yaml` has `observability.langfuse_host: "http://localhost:3000"`
- **THEN** `ObservabilitySettings.langfuse_host="http://prod:3000"` (env takes precedence)
