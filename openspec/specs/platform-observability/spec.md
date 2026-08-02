# platform-observability Specification

## Purpose

This spec defines the observability stack: OpenTelemetry trace and metric exporters with two-tier sampling, structured slog-based logging with OTel correlation, Prometheus scrape endpoint, and the DaemonSet-agent + Deployment-gateway OTel Collector topology. Trace context MUST propagate across HTTP and Kafka boundaries.
## Requirements

> **Deployment-readiness status:** PARTIAL / UNVERIFIED. Source-level SDK and logging features may be implemented as annotated below, but Collector configuration, pipeline readiness, and required cross-service telemetry have not passed clean-environment acceptance together.
>
> **Acceptance evidence:** validate the exact pinned Collector image/configurations through `make validate-deployment`, then run `make dev-smoke` or `make kind-smoke`. Retain the `microservices.deployment-validation/v1` manifest at `artifacts/deployment-validation/<run-id>/manifest.json` (or the configured artifact root) and its referenced telemetry report.

### Requirement: Structured logger with OpenTelemetry trace correlation via log/slog + otelslog

> **Status**: IMPLEMENTED. Structured logger built on log/slog with OTel correlation via otelslog bridge.

The platform SHALL provide a structured logger built on `log/slog` (NOT a vendored logger), wrapped by the `go.opentelemetry.io/contrib/instrumentation/log/slog/otelslog` bridge so `trace.id`, `span.id`, and OTel `trace_flags` are automatically injected into every record whenever a sampled span is on the supplied `context.Context`. The platform MUST use `slog.InfoContext(ctx, ...)`, `slog.WarnContext(ctx, ...)`, `slog.ErrorContext(ctx, ...)` — NEVER `slog.Info(...)` without a context — so OTel correlation works. The logger SHALL emit JSON to stdout in non-development environments, ISO-8601 timestamps, the standard fields `service.name`, `service.version`, and `deployment.environment` on every record, and the request-scoped fields `request.id`, `correlation.id`, `trace.id`, and `span.id` whenever those values are present on the supplied `context.Context`. The logger MUST inject `trace.id` and `span.id` only when a sampled span exists on the context so the platform's log records correlate with traces without requiring every call site to set them.

#### Scenario: Logger injects trace identifiers when a sampled span is present via the otelslog bridge
- **WHEN** a log record is emitted via `slog.InfoContext(ctx, ...)` with a context carrying a sampled OTel span
- **THEN** the record's JSON output contains `trace_id` and `span_id` fields (NOT `trace.id` and `span.id` — `otelslog` uses underscore names) equal to the span's trace and span identifiers, AND Loki receives these as structured fields so log-trace correlation in Grafana works

#### Scenario: Logger omits trace identifiers when no span is present
- **WHEN** a log record is emitted with a `context.Context` that does not carry an OTel span
- **THEN** the record's JSON output does not contain `trace.id` or `span.id` fields

#### Scenario: Logger redacts sensitive field names
- **WHEN** a log record carries a field whose key matches the platform's redact list (case-insensitive)
- **THEN** the field's value is replaced with the placeholder `[REDACTED]` in the JSON output

### Requirement: Prometheus metric endpoint

> **Status**: IMPLEMENTED. Prometheus /metrics endpoint exposed with process and service-scoped metrics.

The platform SHALL provide a Prometheus-format `/metrics` HTTP endpoint, exposed on a configurable port, that exposes process metrics (CPU, memory, GC, file descriptors, goroutines) and a service-scoped metric registry where every metric name uses the `<service_scope>_` prefix. The endpoint MUST NOT require authentication in local development and MUST require authentication or network policy in production; the auth posture is configurable per service.

#### Scenario: Metrics endpoint exposes process metrics
- **WHEN** the platform's HTTP server receives a GET request on `/metrics`
- **THEN** the response is Prometheus exposition format and includes `process_cpu_seconds_total`, `process_resident_memory_bytes`, and `go_goroutines`

#### Scenario: Metrics names are scoped to the owning service
- **WHEN** a service registers a counter with the name `commands_total`
- **THEN** the exposed metric name is `<service_scope>_commands_total`

### Requirement: OpenTelemetry trace and metric exporters with two-tier sampling

> **Status**: IMPLEMENTED. OTel SDK configured with two-tier sampling; OTLP gRPC export to collector.

The platform SHALL configure an OTel tracer provider and meter provider that export over OTLP gRPC to the endpoint named by `OTEL_EXPORTER_OTLP_ENDPOINT` (default `http://localhost:4317`) when set, or no-op otherwise. The platform SHALL expose resource attributes `service.name` (the short service identifier, e.g., `order-service`), `service.version` (the git SHA at build time, populated from the Dockerfile's build-arg injection), `deployment.environment` (one of `local`, `staging`, `production`, set from `DEPLOYMENT_ENV`), `service.namespace` (the logical platform namespace, set to `victory1908/microservices` for every Phase-2 service — this is what Mimir uses to scope queries across the fleet), and `service.instance.id` (the Kubernetes pod name, or pod UUID in dev) for every exported span and metric sample. Sampling SHALL be a two-tier configuration: **(1) SDK head sampler**: `sdktrace.ParentBased(sdktrace.TraceIDRatioBased(0.10))` in production so root spans are sampled at 10% with child spans respecting the parent's decision (override `OTEL_TRACES_SAMPLER_ARG` to change the ratio); **(2) OTel Collector tail sampler**: a `tail_sampling` processor with three policies evaluated in order — `errors` (always sample errors), `latency` (sample p99 > 1s), `probabilistic` (10% fallback for healthy traffic). Local development SHALL configure `ParentBased(AlwaysOn)` via `OTEL_TRACES_SAMPLER=always_on` so the full request timeline is recorded. The SDK MUST NOT mute spans the tail sampler would have captured: head sampling's job is to reduce SDK-side load, NOT to make tail-sampling decisions the collector can't reverse.

#### Scenario: SDK exports a span over OTLP
- **WHEN** the service starts a sampled span and exits its scope
- **THEN** the OTel Collector (or test collector) receives the span with the service's resource attributes attached

#### Scenario: SDK exports a metric sample over OTLP
- **WHEN** the service records a histogram observation through the platform's meter
- **THEN** the OTel Collector receives the metric sample with the service's resource attributes attached

#### Scenario: ParentBased sampling honours the parent's sampled flag
- **WHEN** a child span is created from a parent context whose sampled flag is false
- **THEN** the child span is not exported

#### Scenario: Resource attributes include service.instance.id for trace de-duplication
- **WHEN** the OTel SDK initializes
- **THEN** every span and metric sample carries `service.instance.id` set to the Kubernetes pod name (or pod UUID in dev), preventing double-counting in Mimir/Tempo when a service scales up/down

#### Scenario: Collector tail sampler captures errors that head sampler dropped
- **WHEN** a 5xx response with a sampled-false root span arrives at the OTel Collector
- **THEN** the `errors` policy in `tail_sampling` retains the trace so errors are fully observable despite the head sampler dropping most roots

### Requirement: Propagation across HTTP and Kafka boundaries

> **Status**: IMPLEMENTED. W3C Trace Context and correlation headers propagated across HTTP and Kafka.

The platform SHALL propagate W3C Trace Context, the correlation ID, the request ID, and the causation ID across outbound HTTP requests via the headers `traceparent`, `tracestate`, `X-Correlation-Id`, `X-Request-Id`, and `X-Causation-Id`. The platform SHALL propagate the same identifiers across Kafka record headers in the order `traceparent`, `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id`. Inbound HTTP and Kafka record handlers SHALL extract the identifiers and attach them to the handler's `context.Context` so downstream code observes them transparently.

#### Scenario: Outbound HTTP request carries propagation headers
- **WHEN** an outbound HTTP request is made through the platform's instrumented client
- **THEN** the request includes `traceparent`, `X-Correlation-Id`, `X-Request-Id`, and `X-Causation-Id` matching the current context

#### Scenario: Inbound HTTP request extracts propagation headers
- **WHEN** an inbound HTTP request arrives with `traceparent` and `X-Correlation-Id`
- **THEN** the handler's `context.Context` carries the extracted trace ID and correlation ID

#### Scenario: Kafka record carries propagation headers
- **WHEN** a service publishes a Kafka record through the platform's instrumented producer
- **THEN** the record's headers include `traceparent`, `X-Correlation-Id`, `X-Request-Id`, and `X-Causation-Id`

#### Scenario: Inbound Kafka record attaches propagation headers to the OTel span
- **WHEN** a consumer reads a Kafka record whose headers include `traceparent`
- **THEN** the consumer's processing context carries the extracted trace ID

### Requirement: HTTP server instrumentation

> **Status**: IMPLEMENTED. Chi-router middleware creates server spans with metrics and panic recovery.

The platform SHALL provide a chi-router middleware that creates a server span for every incoming HTTP request, attaches the propagation headers from the request, records request duration and active-request count metrics, and propagates panics into the structured log as a 500 response without leaking the panic message to the client.

#### Scenario: Inbound HTTP request creates a server span
- **WHEN** an HTTP request reaches the platform's router
- **THEN** a server span is created, the span status is set to `Error` on non-2xx responses, and the span name is `HTTP <method> <route>`

#### Scenario: Panic in handler becomes 500 response
- **WHEN** an HTTP handler panics
- **THEN** the response is `500 Internal Server Error`, the panic is logged at ERROR level with the trace ID, and the panic message is NOT included in the response body

### Requirement: Context-scoped logging helpers

> **Status**: IMPLEMENTED. LoggerFromContext, WithLogger helpers exist for context-scoped logging.

The platform SHALL provide helpers `LoggerFromContext`, `WithLogger`, and `Logger` that store a `*zap.Logger` on `context.Context` so handlers retrieve a logger pre-populated with the request-scoped fields. The platform MUST NOT introduce a global logger; every logger instance is constructed during process startup and passed via dependency injection.

#### Scenario: Logger retrieved from context carries request-scoped fields
- **WHEN** a handler retrieves the logger via `LoggerFromContext(ctx)`
- **THEN** every record emitted through that logger includes `request.id`, `correlation.id`, `trace.id`, and `span.id` matching the context

### Requirement: Baggage policy — control flags only, PII/secrets forbidden

> **Status**: PARTIAL. Baggage propagation exists; PII/secrets enforcement may be partial.

The platform SHALL expose baggage propagation via the OTel `TextMapPropagator` composite, but enforce that baggage contains ONLY cross-service control flags (e.g., `experiment.arm`, `request.priority`). The platform MUST enforce the Go SDK's 64-entry / 8 KB baggage size limit at the ingress boundary (via a custom `TextMapPropagator` that rejects oversized bags). The platform SHALL publish a documented allow-list of baggage keys; the linter (`platform/contracts/lint`) rejects commits adding new baggage keys outside the allow-list without an ADR. Secrets, PII, authentication tokens, and personal data MUST NEVER appear in baggage; the redact list applies to baggage headers as well.

#### Scenario: Oversized baggage is rejected at ingress
- **WHEN** an inbound HTTP request carries a `baggage` header larger than 8 KB
- **THEN** the platform rejects the request with `400 Bad Request` and logs a structured warning naming the offending header (NOT its content)

#### Scenario: PII in baggage is rejected by redact list
- **WHEN** an outbound HTTP request is about to send a baggage key whose value matches the redact list pattern
- **THEN** the propagator drops the key (does not send it) and logs a WARN

### Requirement: OTel Collector topology — DaemonSet agent + Deployment gateway

> **Status**: PARTIAL. OTel Collector config exists; DaemonSet/Deployment topology may be partial.

The platform SHALL deploy the OTel Collector with a two-tier topology in production:

- **DaemonSet agent (`otelcol-agent`)** — one pod per Kubernetes node. Receives OTLP gRPC and OTLP HTTP from local apps on `0.0.0.0:4317`/`0.0.0.0:4318`. Processors in order: `memory_limiter` (FIRST, with hard `gc_limit` and `spike_limit`), `k8sattributes`, `attributes`/`transform` (cardinality control), `batch`. **Does NOT perform tail sampling** (tail sampling latency per-node would corrupt cluster-wide trace decisions). Exports OTLP via the `loadbalancing` exporter (routing-key = trace ID) to the gateway.
- **Deployment gateway (`otelcol-gateway`)** — horizontally scaled behind a `Service`. Receives OTLP from agents. Processors in order: `memory_limiter`, `tail_sampling` (with policies `errors`, `latency` > 1s, `probabilistic` 10%), final `batch`. Exporters: `otlp/tempo` (gRPC), `otlphttp/mimir`, `otlphttp/loki`, `debug` (dev only). HPA scales on `otelcol_exporter_queue_size` and `otelcol_processor_tail_sampling_sampled_traces` metrics.

The HPA SHALL trigger on `otelcol_*` queue size metrics (not just CPU) so the gateway scales before its queues overflow. The OTel Collector's own Prometheus endpoint SHALL be scraped by the platform's Prometheus; an alert fires when `otelcol_exporter_queue_size > 80% of max` for 5 minutes.

#### Scenario: Agent forwards traces to the gateway via load-balancing exporter
- **WHEN** an app emits a span to the per-node agent
- **THEN** the agent routes it to the gateway using trace-ID-routed load balancing, ensuring all spans of the same trace land on the same gateway instance (required for tail sampling)

#### Scenario: Gateway tail sampler retains errors despite head sampler dropping
- **WHEN** the gateway receives a complete trace where the root span was not sampled by the SDK but the trace contains a 5xx response
- **THEN** the `errors` policy of `tail_sampling` retains the trace and the exporter forwards it to Tempo

### Requirement: Double-instrumentation guard (mesh + app)

> **Status**: DEFERRED. Double-instrumentation guard not yet implemented for service mesh deployments.

When the platform is deployed with a service mesh (Istio or Linkerd), BOTH the sidecar AND the application emit telemetry for every request. The platform SHALL detect this condition and disable the application's HTTP-server-side instrumentation when a mesh sidecar is present. Detection mechanism: an environment variable `OTEL_INSTRUMENTATION_DOUBLE_TRACE_GUARD=true` is set by the mesh admission controller via a `Pod` annotation; the platform's `observability.Init()` reads the env var and skips adding the server-side middleware for the relevant HTTP path (the sidecar handles server-side tracing). For client-side and out-of-process spans (Kafka, Temporal, PostgreSQL) the application STILL emits — those are not duplicated by the sidecar.

#### Scenario: App-side HTTP server middleware is disabled when sidecar is present
- **WHEN** the platform starts in a pod where `OTEL_INSTRUMENTATION_DOUBLE_TRACE_GUARD=true`
- **THEN** the platform's HTTP middleware does NOT create server spans for inbound requests (the sidecar handles them), but DOES create client spans for outbound HTTP calls and tracer spans for out-of-process work (Kafka, Temporal, PostgreSQL)

### Requirement: Span naming, status, and attribute conventions

> **Status**: IMPLEMENTED. Span naming and attribute conventions follow OTel semantic conventions.

The platform SHALL enforce span-naming and attribute conventions derived from the OpenTelemetry semantic conventions, with platform-specific conventions for cross-service call paths and saga compensation. Span names SHALL be `<protocol> <method> <route>` (HTTP client and server), `<messaging.system> <destination> <operation>` (Kafka, Temporal), `<db.system> <operation>` (PostgreSQL). Spans SHALL set their status to `Error` on non-2xx HTTP responses, `Temporal` activity failures, and Kafka processing errors. Spans SHALL attach the standard resource attributes (`service.name`, `service.version`, `service.namespace`, `service.instance.id`, `deployment.environment`) and the per-spankind attributes (`http.method`, `http.route`, `http.status_code`, `messaging.destination`, `db.statement`).

#### Scenario: Server span follows naming convention
- **WHEN** the platform's HTTP middleware handles a `POST` to `/api/v1/orders`
- **THEN** the server span is named `HTTP POST /api/v1/orders`, attributes `http.method=POST`, `http.route=/api/v1/orders`, and `http.status_code` matches the response

#### Scenario: Activity span sets status to Error on failure
- **WHEN** a Temporal activity returns a non-retryable error
- **THEN** the activity span status is `Error`, attributes `error.type` (the typed error), `error.message`, and the status description carries `activity=<name>`

### Requirement: Collector configuration matches the pinned binary

Every OpenTelemetry Collector configuration used by local, CI, staging, or production deployment SHALL validate with the exact pinned Collector image before the deployment can start or be promoted.

#### Scenario: Supported Collector configuration validates

- **WHEN** CI runs the pinned Collector image's configuration validation command against every tracked Collector configuration
- **THEN** each configuration exits zero and all referenced receivers, processors, exporters, extensions, and internal-telemetry fields are supported by that image

#### Scenario: Removed configuration field blocks promotion

- **WHEN** a Collector configuration contains a field or component rejected by the pinned image
- **THEN** validation exits non-zero, identifies the configuration path, and prevents local acceptance and deployment promotion

### Requirement: Collector readiness reflects pipeline availability

Collector health SHALL be determined through an enabled health endpoint or supported internal-telemetry endpoint and SHALL remain false when configuration loading or required pipeline startup fails.

#### Scenario: Valid pipelines become ready

- **WHEN** the Collector loads all required pipelines and starts its configured health endpoint
- **THEN** the container or Pod readiness check succeeds and OTLP clients can connect to the documented receiver ports

#### Scenario: Collector process exits during startup

- **WHEN** configuration decoding or pipeline initialization causes the Collector process to exit
- **THEN** dependent acceptance tests fail readiness and retain the Collector startup logs

### Requirement: Required telemetry assertions fail closed

Cross-service acceptance and post-deployment verification SHALL require telemetry from every service named by the acceptance profile and MUST NOT convert a missing trace, metric, or log assertion into a passing result.

#### Scenario: Expected service traces are present

- **WHEN** the acceptance workflow completes successfully
- **THEN** the verifier finds correlated traces for every required service and records their trace identifiers in evidence

#### Scenario: Required telemetry is absent

- **WHEN** a required service produces no matching telemetry within the bounded observation window
- **THEN** the verifier exits non-zero and identifies the missing service and signal

