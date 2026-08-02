# observability-otel-instrumentation

## ADDED Requirements

### Requirement: OTel TracerProvider Initialized Before structlog Configuration
When `OTEL_ENABLED=true`, the TracerProvider SHALL be initialized before the structlog processor chain is configured. The provider SHALL be configured with a Resource containing at minimum: `service.name`, `service.version=1.0.0`, and `deployment.environment=local`.

#### Scenario: TracerProvider set before FastAPIInstrumentor
- **WHEN** `OTEL_ENABLED=true` in webhook-receiver or ai-review
- **THEN** `setup_otel()` SHALL call `TracerProvider(resource=...)` and `trace.set_tracer_provider(provider)` before any structlog processor is configured

### Requirement: Trace Context Injected into structlog via Prepended Processor
When `OTEL_ENABLED=true`, structlog SHALL include a processor that reads the current OTel span and injects `trace_id` and `span_id` into the event's extra dict. The processor SHALL be prepended to the processor chain (evaluated before other processors) and SHALL only inject context when `span.is_recording()` is `True`.

The injected fields SHALL be:
- `trace_id` — 32 lowercase hex characters, formatted from `ctx.trace_id`
- `span_id` — 16 lowercase hex characters, formatted from `ctx.span_id`

#### Scenario: Log event within a request span carries trace context
- **WHEN** webhook-receiver handles a POST to `/gitlab-webhook` with an active OTel span
- **THEN** every structlog call in that request SHALL include `extra["trace_id"]` and `extra["span_id"]` in the JSON output

#### Scenario: Background tasks without spans omit trace fields
- **WHEN** a structlog call occurs outside of any OTel span (no active span)
- **THEN** `span.is_recording()` returns `False` and the processor SHALL return the event dict unchanged

### Requirement: FastAPI Auto-Instrumentation with Excluded Health Routes
When `OTEL_ENABLED=true`, webhook-receiver and ai-review SHALL call `FastAPIInstrumentor.instrument_app(app)` after app creation. Health endpoints (`/health`, `/health/full`, `/healthz`, `/health/ingress`) SHALL be excluded from automatic span creation to avoid noise.

The instrumentation SHALL create spans for all other routes with attributes: `http.method`, `http.url`, `http.status_code`, and `http.route`.

#### Scenario: Webhook request creates a span
- **WHEN** webhook-receiver receives POST to `/gitlab-webhook` with `OTEL_ENABLED=true`
- **THEN** a span SHALL be created with `span.name = "POST /gitlab-webhook"` and standard HTTP attributes

#### Scenario: Health endpoint is excluded from tracing
- **WHEN** `GET /health` is called
- **THEN** FastAPIInstrumentor SHALL NOT create a span for that request

### Requirement: HTTPX Client Instrumented with traceparent Propagation
When `OTEL_ENABLED=true`, outbound HTTP calls made via `httpx.AsyncClient` SHALL be instrumented via `HTTPXClientInstrumentor().instrument()`. This propagates the active trace context via the W3C `traceparent` header on every outbound request.

The legacy `X-Trace-Id` header (format: `trace-{uuid.hex[:12]}`) SHALL be preserved alongside the new `traceparent` header.

#### Scenario: Dispatch to ai-review carries both trace headers
- **WHEN** webhook-receiver dispatches to `POST http://127.0.0.1:8090/reviews/gitlab-mr` with an active trace
- **THEN** the request SHALL include both:
  - `traceparent: 00-<32-hex-trace-id>-<16-hex-span-id>-01`
  - `X-Trace-Id: trace-{uuid.hex[:12]}` (legacy header, unchanged)

### Requirement: OTLP Exporter Configured for Local Collector
When `OTEL_ENABLED=true`, the SDK SHALL export spans via OTLP HTTP/protobuf. The endpoint SHALL be constructed as: `{OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces`, defaulting to `http://localhost:4318/v1/traces` when the env var is unset.

The SDK SHALL use `BatchSpanProcessor` with default settings (max queue size 2048, max batch size 512, schedule delay 5s).

#### Scenario: Exports to local LGTM collector
- **WHEN** `OTEL_ENABLED=true` and `OTEL_EXPORTER_OTLP_ENDPOINT` is unset
- **THEN** spans SHALL be exported to `http://localhost:4318/v1/traces`

#### Scenario: Uses custom endpoint when set
- **WHEN** `OTEL_EXPORTER_OTLP_ENDPOINT=http://collector.internal:4318`
- **THEN** spans SHALL be exported to `http://collector.internal:4318/v1/traces`

### Requirement: OTel Disabled by Default — No Side Effects When Absent
When `OTEL_ENABLED` is absent or set to `false`, webhook-receiver and ai-review SHALL NOT initialize any OTel component. The `setup_otel()` function SHALL return immediately. The services SHALL behave identically to before — no TracerProvider, no structlog changes, no headers added.

#### Scenario: No OTel initialization without env var
- **WHEN** `OTEL_ENABLED` is not set
- **THEN** `setup_otel()` SHALL return immediately; `FastAPIInstrumentor` SHALL NOT be called; structlog SHALL NOT be modified

### Requirement: Grafana LGTM Auto-Provisioned with Dashboards
The `tdt-observability/` repository SHALL include Grafana provisioning files and dashboard JSON in `grafana/provisioning/` and `grafana/dashboards/`. When the LGTM container starts with the provided volume mount, Grafana SHALL auto-import datasources and dashboards.

The provisioning SHALL include:
- Datasources: Tempo (`:3200`), Loki (`:3100`), Mimir (`:9009`)
- Dashboards: TDT Service Health, TDT Distributed Traces

#### Scenario: LGTM starts with auto-provisioned datasources
- **WHEN** the operator runs `deploy/lgtm/run-lgtm.sh`
- **THEN** Grafana at `http://localhost:3000` SHALL have Tempo, Loki, and Mimir pre-configured as datasources

#### Scenario: Service health dashboard is available
- **WHEN** the operator navigates to Grafana → Dashboards → TDT Observability
- **THEN** the TDT Service Health dashboard SHALL display spans, error rates, and trace counts

#### Scenario: Trace-to-Log correlation link works
- **WHEN** an operator clicks a span in Grafana Tempo
- **THEN** Grafana SHALL offer a "View Logs in Loki" link filtered by the span's `trace_id`
