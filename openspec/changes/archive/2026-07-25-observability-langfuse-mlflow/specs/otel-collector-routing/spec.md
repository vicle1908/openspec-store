## ADDED Requirements

### Requirement: OTel Collector receives agent-core telemetry
The system SHALL deploy an OpenTelemetry Collector (v0.157.0, image `otel/opentelemetry-collector-contrib:0.157.0`) that receives OTLP traces, metrics, and logs from agent-core via gRPC (port 4317) and HTTP (port 4318).

#### Scenario: Agent spans reach Collector
- **WHEN** agent-core emits an OTel span with `service.name=agent-core`
- **THEN** the Collector receives the span via OTLP gRPC on port 4317

### Requirement: Collector routes traces to Langfuse
The system SHALL configure the Collector to export traces, metrics, and logs to the Langfuse OTLP endpoint (`http://langfuse-web:4317` via gRPC or `http://langfuse-web:4318` via HTTP). Export SHALL use the `batch` processor with `timeout: 10s` and `send_batch_size: 500` for efficiency. The validated config structure:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
processors:
  batch:
    timeout: 10s
    send_batch_size: 500
exporters:
  otlp/langfuse:
    endpoint: langfuse-web:4317
    tls:
      insecure: true
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/langfuse]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/langfuse]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/langfuse]
```

#### Scenario: Traces routed to Langfuse
- **WHEN** the Collector receives a batch of traces
- **THEN** traces are exported to Langfuse's OTLP endpoint and appear in Langfuse UI within 30 seconds

### Requirement: Collector is extensible for future backends
The Collector configuration SHALL support adding additional OTLP exporters (e.g., Logfire Cloud, SigNoz) by appending exporter entries to the pipeline — no code changes required.

#### Scenario: Add Logfire Cloud exporter
- **WHEN** a new `otlp/logfire` exporter is added to the Collector config with endpoint `ingest.pydantic.dev:443`
- **THEN** traces are exported to both Langfuse AND Logfire Cloud simultaneously

### Requirement: Collector handles failures gracefully
The Collector SHALL implement retry logic with exponential backoff for failed exports. The OTel Collector's built-in retry mechanism handles this via the exporter's `retry_on_failure` setting (enabled by default). If a backend is unreachable, the Collector SHALL queue spans locally and retry without losing data.

#### Scenario: Backend temporarily unreachable
- **WHEN** Langfuse endpoint returns 503 for 60 seconds
- **THEN** the Collector queues spans locally and retries with backoff, exporting successfully once Langfuse recovers

### Requirement: Collector config managed via Docker Compose
The Collector configuration file (`otel-collector-config.yaml`) SHALL be mounted into the Collector container at `/etc/otelcol-contrib/config.yaml` via Docker Compose volumes. Changes to the config SHALL be applied by restarting the Collector container (`docker compose restart otel-collector`).

#### Scenario: Config update via compose
- **WHEN** `otel-collector-config.yaml` is modified and `docker compose restart otel-collector` is run
- **THEN** the Collector reloads with the new configuration
