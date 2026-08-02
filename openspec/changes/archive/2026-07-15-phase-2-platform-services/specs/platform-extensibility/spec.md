## ADDED Requirements

### Requirement: Optional infrastructure is capability driven
Redis, search stores, schema registries, gateways, and other infrastructure SHALL be introduced only with an owned capability, failure model, operational metric, and removal strategy. The same rule SHALL apply to optional inspection tooling such as a Kafka broker UI.

#### Scenario: Cache proposal
- **WHEN** a read cache is proposed
- **THEN** the design identifies the authority, invalidation policy, stale-read tolerance, observability, and fallback behavior before adding Redis

#### Scenario: Broker UI proposal
- **WHEN** the broker-UI tools profile is proposed
- **THEN** the design identifies the authority (developer inspection only), the failure model (container stop has zero runtime impact), the operational metric (none — non-runtime dependency), and the removal strategy (drop the overlay and remove the `verify-images` entry) before adding the image

#### Scenario: Cross-service call uses the OTel-instrumented HTTP client
- **WHEN** the order-service calls `customer-service` or `catalog-service` from `internal/application/commands/create_order.go`
- **THEN** the call goes through the platform's `platform/http.Client` (OTel-instrumented via `otelhttp.NewTransport`), the trace context propagates to the peer service, and the caller's span records `peer.service`, `http.request.method`, `http.response.status_code`

#### Scenario: Cross-service call is wrapped in a typed `ErrPeerUnavailable` sentinel
- **WHEN** a peer service returns a 5xx or the call times out after `ORDER_PEER_CALL_TIMEOUT_MS` (default 2000ms)
- **THEN** the platform's HTTP client wraps the error as `ErrPeerUnavailable` carrying the peer's name and the upstream status code; the calling application aborts the order with a deterministic 503 response carrying `retry-after` and `correlation_id`

#### Scenario: New service admits a cache only after authoring an ADR
- **WHEN** the catalog-service or notification-service module imports `github.com/redis/go-redis/v9` or `github.com/valkey-io/valkey-glide/go`
- **THEN** `test/architecture/cache_admission_test.go` confirms that `docs/adr/<NNNN>-<capability>-cache.md` exists with the five-point test documented in `order-service/docs/adr/0004-optional-infrastructure.md`, otherwise the architecture test fails the PR gate

#### Scenario: OTel Collector is the single egress for telemetry
- **WHEN** any service starts in the `lgtm` Compose profile
- **THEN** the service's `OTEL_EXPORTER_OTLP_ENDPOINT` defaults to `otel-collector:4317` (Compose internal listener) and no service holds a direct OTLP endpoint to Tempo, Mimir, or Loki in its configuration — only the collector does

## ADDED Requirements

### Requirement: Cross-service REST call conventions
Every cross-service REST call in the platform SHALL use the platform's `platform/http.Client` (OTel-instrumented), SHALL propagate `traceparent`, `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id` headers, SHALL declare a per-peer timeout, and SHALL emit a Prometheus counter labelled by peer name, method, and status code.

#### Scenario: Cross-service call carries the OTel propagator headers
- **WHEN** a service issues a `GET /api/v1/products/<id>/quote` call to `catalog-service`
- **THEN** the outbound request contains the `traceparent`, `tracestate`, `X-Correlation-Id`, `X-Request-Id`, and `X-Causation-Id` headers extracted from the inbound request context, allowing the peer service to continue the trace

#### Scenario: Cross-service call timeout aborts the order
- **WHEN** the catalog-service does not respond within `ORDER_CATALOG_CALL_TIMEOUT_MS` (default 1500ms)
- **THEN** the platform client returns a wrapped `ErrPeerUnavailable` with `peer=catalog-service`, the orchestrator records a 503 in the call counter, and the order creation command fails fast with a 503 response — no infinite retry, no in-band timeout

### Requirement: Capability-gated dependency admission
A service SHALL import a vendor SDK (cache SDK, email SDK, SMS SDK, payment SDK) into its own module only after authoring an ADR that satisfies the five-point test in `order-service/docs/adr/0004-optional-infrastructure.md`: (1) name the problem in one sentence, (2) name the platform-native alternative that was considered and why it was rejected, (3) name the owner service, (4) name the integration boundary, (5) name the failure mode and the compensating control.

#### Scenario: Architecture test enforces ADR existence
- **WHEN** the cross-service architecture test runs against a service that imports a vendor SDK
- **THEN** the test confirms `docs/adr/<NNNN>-<purpose>-sdk.md` exists with the five required sections, otherwise the build fails

#### Scenario: Architecture test fails when ADR has empty failure-mode section
- **WHEN** a service ADR's "Failure Mode" section is empty
- **THEN** the architecture test fails the build with the error `adr <NNNN>-<purpose>-sdk.md: section "Failure Mode" is empty`

### Requirement: Platform module imports no vendor SDK
The `platform/` module SHALL import zero vendor SDKs (cache, email, SMS, payment, push, etc.). The platform exposes interfaces only; per-service admission is gated by ADR. The CI gate SHALL run `go list -m all` against the platform module and fail the PR if any vendor SDK appears in the dependency closure.

#### Scenario: Platform module's go.sum contains no cache client
- **WHEN** `go list -m all` runs against the `platform/` module
- **THEN** no module path matches `redis|valkey|bigcache|ristretto|freecache|twilio|aws-sdk-go-v2/service/ses`

#### Scenario: Platform module's go.sum contains no observability vendor
- **WHEN** `go list -m all` runs against the `platform/` module
- **THEN** the only OTel packages present are the cross-cutting `go.opentelemetry.io/otel*` modules — no `datadog`, `honeycomb`, `newrelic`, `signoz`, or `lightstep` packages are present

### Requirement: Cross-service REST path namespace convention
Cross-service REST paths SHALL live under `/api/v1/<peer>/<resource>`. The namespace is per-peer (e.g., `/api/v1/catalog/products/<id>/quote`); peer names match the directory name under `services/`. The convention is enforced by the architecture test `test/architecture/cross_service_path_test.go`.

#### Scenario: Cross-service paths match the per-peer namespace
- **WHEN** the architecture test scans every route registered on every HTTP server across every service
- **THEN** every cross-service path matches the regex `^/api/v1/(customer|catalog|notification|reporting)/[a-z][a-z0-9-/]+$`