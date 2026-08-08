# platform-extensibility Specification

## Purpose
The platform implements Services own data and deployment Each service SHALL be the sole writer of its authoritative data and SHALL have independent credentials, migrations, configuration validation, health endpoints, and deployment lifecycle.
## Requirements
### Requirement: Services own data and deployment

> **Status**: IMPLEMENTED. Each service owns its data; independent credentials, migrations, health endpoints enforced.

Each service SHALL be the sole writer of its authoritative data and SHALL have independent credentials, migrations, configuration validation, health endpoints, and deployment lifecycle.

#### Scenario: Shared local PostgreSQL instance
- **WHEN** multiple services use one PostgreSQL container in local development
- **THEN** each service still uses a distinct database or schema owner and cannot write another service's tables

### Requirement: Shared libraries remain infrastructure neutral

> **Status**: IMPLEMENTED. Platform module contains only contracts, telemetry, test utilities; no domain models.

Cross-service libraries SHALL be limited to generated contracts, telemetry setup, and test utilities. They MUST NOT contain domain models, repositories, global configuration, or database clients.

#### Scenario: New Payment service
- **WHEN** developers create the Payment service
- **THEN** it defines its own domain and persistence model while reusing only approved contract and platform utilities

### Requirement: Extraction follows operational need

> **Status**: IMPLEMENTED. Services extracted based on operational need; payment, inventory, shipping services created.

A module SHALL be extracted into a service only when independent ownership, scaling, availability, security, retention, or release cadence justifies the distributed-system cost.

#### Scenario: Notification growth
- **WHEN** notification volume and retry behavior need independent scaling
- **THEN** the Notification module can become a Kafka consumer service without changing Order table ownership

### Requirement: Optional infrastructure is capability driven

> **Status**: IMPLEMENTED. Capability-driven admission enforced via ADR; optional infrastructure requires documented rationale.

Redis, search stores, schema registries, and other optional infrastructure SHALL be introduced only with an owned capability, failure model, operational metric, and removal strategy. The same rule SHALL apply to optional inspection tooling such as a Kafka broker UI.

#### Scenario: Cache proposal
- **WHEN** a read cache is proposed
- **THEN** the design identifies the authority, invalidation policy, stale-read tolerance, observability, and fallback behavior before adding Redis

#### Scenario: Broker UI proposal
- **WHEN** the broker-UI tools profile is proposed
- **THEN** the design identifies the authority (developer inspection only), the failure model (container stop has zero runtime impact), the operational metric (none — non-runtime dependency), and the removal strategy (drop the overlay and remove the `verify-images` entry) before adding the image

### Requirement: Observability is consistent across services

> **Status**: IMPLEMENTED. Structured logs, traces, metrics emitted with service identity and correlation context.

Every service SHALL emit structured logs, traces, and metrics with service identity, environment, request/correlation context, and dependency outcomes while excluding secrets and sensitive payment data.

#### Scenario: Cross-service failure
- **WHEN** fulfillment fails across Order and Inventory boundaries
- **THEN** operators can correlate the API request, workflow, activity, and integration event using shared identifiers

### Requirement: Local Compose is not production topology

> **Status**: IMPLEMENTED. Docker Compose provides local development; not represented as production HA.

The Docker Compose stack SHALL provide reproducible local development with pinned images, health checks, internal/external listener separation, persistent volumes where useful, and optional tools profiles. It SHALL NOT be represented as a production HA deployment.

#### Scenario: Fresh local startup
- **WHEN** a developer starts the stack with empty volumes
- **THEN** migrations, topics, publication, and Debezium connector initialize idempotently before dependent runtimes start, without manual database or broker steps

### Requirement: Broker UI tools profile is opt-in and arm64-validated

> **Status**: IMPLEMENTED. Tools overlay with Kafka UI exists; arm64 validation via verify-images enforced.

The Kafka broker UI SHALL be exposed only via a separate `deploy/docker-compose.tools.yaml` overlay activated by `--profile tools`. The pinned image MUST advertise a native `linux/arm64` manifest entry and SHALL be checked by `make verify-images` on every PR.

#### Scenario: Broker UI starts with the tools profile
- **WHEN** a developer runs `docker compose --profile tools -f deploy/docker-compose.yaml -f deploy/docker-compose.tools.yaml up`
- **THEN** the broker UI container starts on a documented `localhost` port and connects to the runtime Kafka broker over the internal listener

#### Scenario: Broker UI does not start without the tools profile
- **WHEN** a developer runs `docker compose -f deploy/docker-compose.yaml up` without `--profile tools`
- **THEN** the broker UI container does not start, no optional image is downloaded, and the runtime stack's readiness is unaffected

#### Scenario: Broker UI image lacks arm64 manifest
- **WHEN** `make verify-images` runs and the pinned `KAFKA_UI_VERSION` image lacks a `linux/arm64` manifest entry
- **THEN** `verify-images` exits non-zero, the broker-UI overlay is rejected, and `verify-traceability` records the gap as an unmapped scenario

### Requirement: Broker UI is a non-runtime dependency

> **Status**: IMPLEMENTED. Kafka UI isolated from runtime; does not affect health checks or write topics.

The broker UI SHALL NOT participate in any Order Service readiness check, SHALL NOT receive traffic on behalf of the API, orchestrator, or worker roles, and SHALL NOT write to any Kafka topic.

#### Scenario: Broker UI stops during a developer session
- **WHEN** a developer stops the broker-UI container while the runtime stack is healthy
- **THEN** the runtime stack's `/health/ready` continues to return 200 and no Order Service log line attributes the UI's state to readiness

#### Scenario: Broker UI attempts to write to a Kafka topic
- **WHEN** a developer misconfigures the broker UI with write permissions
- **THEN** the design records this as a forbidden scenario, `verify-traceability` flags the misconfiguration, and the overlay MUST be configured read-only by default

### Requirement: Cross-service REST call conventions

> **Status**: IMPLEMENTED. OTel-instrumented HTTP client used; correlation headers propagated; per-peer timeouts enforced.

Every cross-service REST call in the platform SHALL use the platform's `platform/http.Client` (OTel-instrumented), SHALL propagate `traceparent`, `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id` headers, SHALL declare a per-peer timeout, and SHALL emit a Prometheus counter labelled by peer name, method, and status code.

#### Scenario: Cross-service call carries the OTel propagator headers
- **WHEN** a service issues a `GET /api/v1/products/<id>/quote` call to `catalog-service`
- **THEN** the outbound request contains the `traceparent`, `tracestate`, `X-Correlation-Id`, `X-Request-Id`, and `X-Causation-Id` headers extracted from the inbound request context, allowing the peer service to continue the trace

#### Scenario: Cross-service call timeout aborts the order
- **WHEN** the catalog-service does not respond within `ORDER_CATALOG_CALL_TIMEOUT_MS` (default 1500ms)
- **THEN** the platform client returns a wrapped `ErrPeerUnavailable` with `peer=catalog-service`, the orchestrator records a 503 in the call counter, and the order creation command fails fast with a 503 response — no infinite retry, no in-band timeout

### Requirement: Capability-gated dependency admission

> **Status**: IMPLEMENTED. ADR-gated dependency admission enforced; architecture tests verify ADR existence.
A service SHALL import a vendor SDK (cache SDK, email SDK, SMS SDK, payment SDK) into its own module only after authoring an ADR that satisfies the five-point test in `order-service/docs/adr/0004-optional-infrastructure.md`: (1) name the problem in one sentence, (2) name the platform-native alternative that was considered and why it was rejected, (3) name the owner service, (4) name the integration boundary, (5) name the failure mode and the compensating control.

#### Scenario: Architecture test enforces ADR existence
- **WHEN** the cross-service architecture test runs against a service that imports a vendor SDK
- **THEN** the test confirms `docs/adr/<NNNN>-<purpose>-sdk.md` exists with the five required sections, otherwise the build fails

#### Scenario: Architecture test fails when ADR has empty failure-mode section
- **WHEN** a service ADR's "Failure Mode" section is empty
- **THEN** the architecture test fails the build with the error `adr <NNNN>-<purpose>-sdk.md: section "Failure Mode" is empty`

### Requirement: Platform module imports no vendor SDK

> **Status**: IMPLEMENTED. Platform module imports zero vendor SDKs; CI gate enforces via go list -m all.

The `platform/` module SHALL import zero vendor SDKs (cache, email, SMS, payment, push, etc.). The platform exposes interfaces only; per-service admission is gated by ADR. The CI gate SHALL run `go list -m all` against the platform module and fail the PR if any vendor SDK appears in the dependency closure.

#### Scenario: Platform module's go.sum contains no cache client
- **WHEN** `go list -m all` runs against the `platform/` module
- **THEN** no module path matches `redis|valkey|bigcache|ristretto|freecache|twilio|aws-sdk-go-v2/service/ses`

#### Scenario: Platform module's go.sum contains no observability vendor
- **WHEN** `go list -m all` runs against the `platform/` module
- **THEN** the only OTel packages present are the cross-cutting `go.opentelemetry.io/otel*` modules — no `datadog`, `honeycomb`, `newrelic`, `signoz`, or `lightstep` packages are present

### Requirement: Cross-service REST path namespace convention

> **Status**: IMPLEMENTED. Cross-service paths follow /api/v1/<peer>/<resource> convention; enforced by test.

Cross-service REST paths SHALL live under `/api/v1/<peer>/<resource>`. The namespace is per-peer (e.g., `/api/v1/catalog/products/<id>/quote`); peer names match the directory name under `services/`. The convention is enforced by the architecture test `test/architecture/cross_service_path_test.go`.

#### Scenario: Cross-service paths match the per-peer namespace
- **WHEN** the architecture test scans every route registered on every HTTP server across every service
- **THEN** every cross-service path matches the regex `^/api/v1/(customer|catalog|notification|reporting)/[a-z][a-z0-9-/]+$`

### Requirement: Optional infrastructure is capability driven (Phase 2 extensions)

> **Status**: IMPLEMENTED. Phase 2 extensions enforced; OTel-instrumented HTTP client used for cross-service calls.

The capability-driven admission rule for optional infrastructure (Redis, schema registries, search, broker UI) SHALL be extended by the Phase 2 requirements below. Cross-service HTTP calls SHALL use the OTel-instrumented `platform/http.Client`, SHALL surface peer-unavailable failures as the typed `ErrPeerUnavailable` sentinel, SHALL require a capability-cache ADR before admitting any cache SDK into a service module, and SHALL route all telemetry exclusively through the platform OTel Collector.

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

### Requirement: New business domain services are first-class platform capabilities

> **Status**: IMPLEMENTED. Payment, inventory, shipping services exist with extraction ADRs documenting rationale.

The three new services introduced by the `extract-business-domains-and-dedicated-workflow-orchestration` change (`payment-service`, `inventory-service`, `shipping-service`) are first-class platform capabilities and SHALL each have an ADR at `services/<name>/docs/adr/0001-service-extraction.md` documenting the extraction rationale, the alternatives considered, and the data ownership boundary. The ADR SHALL follow the 5-point admission format (Problem / Considered Alternative / Owner / Integration Boundary / Failure Mode) used by `order-service/docs/adr/0004-optional-infrastructure.md`. The architecture test in each new service's `test/architecture/` SHALL assert the ADR file exists and contains the five required sections.

#### Scenario: All three new services have extraction ADRs

- **WHEN** the architecture test scans for `services/<name>/docs/adr/0001-service-extraction.md`
- **THEN** the test verifies that the file exists for `payment-service`, `inventory-service`, and `shipping-service`
- **AND** the test verifies that each file contains the `## Problem`, `## Considered Alternative`, `## Owner`, `## Integration Boundary`, `## Failure Mode` sections
- **AND** the test fails if any section is missing or empty

### Requirement: Cross-service contract package layout is a contract surface

> **Status**: IMPLEMENTED. Contract package layout enforced; proto and contracts directories exist for all services.

The `services/<name>/proto/<domain>/v1/` (source `.proto` files) and `services/<name>/contracts/<domain>/v1/` (generated `.pb.go` files) package layout is a contract surface, matching the existing `services/order-service/proto/order/v1/` and `services/order-service/contracts/order/v1/` directory layout. A change to the package layout (renaming a directory, removing a `.proto` file, regenerating with a different `buf` configuration) SHALL require a new OpenSpec change. The `cross-service-workflow-contracts` capability is the canonical place to document any contract-layout change.

#### Scenario: Contract package layout is enforced by the architecture test

- **WHEN** the architecture test scans `services/<name>/proto/` and `services/<name>/contracts/`
- **THEN** the test verifies that each service has both `proto/<domain>/v1/` and `contracts/<domain>/v1/` subdirectories
- **AND** the test verifies each contains a `<domain>.proto` file and a `<domain>.pb.go` file respectively
- **AND** the test fails if the directory structure deviates from the convention

### Requirement: Docker-compose overlay pattern is a contract surface

> **Status**: IMPLEMENTED. Docker Compose overlay pattern established; all services have overlay files.

The `deploy/docker-compose.<service>.yaml` overlay pattern (one file per service, merged with the top-level `docker-compose.yaml` via `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.<service>.yaml up -d`) is a contract surface. A new service SHALL add a new overlay file; the overlay SHALL include `<service>-migrate`, `<service>-api`, `<service>-worker`, `<service>-infrastructure-init`, and `<service>-topics-init` containers (the last is omitted for read-only services like `reporting-service` and `catalog-service`). The overlay SHALL set `<SERVICE>_TEMPORAL_ADDRESS=temporal:7233` and `<SERVICE>_TEMPORAL_TASK_QUEUE=<service-task-queue>`.

#### Scenario: All eight services have a docker-compose overlay

- **WHEN** the architecture test lists `deploy/docker-compose.*.yaml` files
- **THEN** the list contains overlays for `order-service`, `payment-service`, `inventory-service`, `shipping-service`, `notification-service`, `customer-service`, `reporting-service`, `catalog-service`
- **AND** each overlay's worker container has `depends_on: temporal: condition: service_healthy`

### Requirement: Makefile target pattern is a contract surface

> **Status**: PARTIAL. Makefile targets exist for some services; comprehensive coverage may be partial.

The Makefile target pattern for each service (`<service>-build`, `<service>-compose-up`, `<service>-smoke-test`) is a contract surface. A new service SHALL add three Makefile targets: a build target that runs `go build -o bin/<service>-service ./services/<service>/cmd/<service>/`; a compose-up target that runs `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.<service>.yaml up -d`; a smoke-test target that runs the service's contract test in `tests/cross-service-smoke/`. The `make help` target SHALL list the new targets.

#### Scenario: All eight services have Makefile targets

- **WHEN** the architecture test scans the `Makefile` for `<service>-build`, `<service>-compose-up`, `<service>-smoke-test` patterns
- **THEN** the test verifies that all eight services have all three targets
- **AND** the test fails if any target is missing

### Requirement: Service module path convention is a contract surface

> **Status**: IMPLEMENTED. All services use github.com/victory1908/<name> module path convention.

The Go module path for each new service SHALL be `github.com/victory1908/<name>` (matching `notification-service`, `customer-service`, `reporting-service`, `catalog-service`). The `go.mod` in `services/<name>/go.mod` SHALL declare this module path. A change to the module path (e.g., adding a new top-level segment) SHALL require a new OpenSpec change. The `order-service` is the historical exception (`github.com/victory1908/services/order-service`) and SHALL NOT be changed by this delta; new services SHALL use the `github.com/victory1908/<name>` form so the reserved-prefix test in `services/order-service/test/architecture/layering_test.go::TestHypotheticalPeerServiceCannotImportOrderInternals` (which lists `github.com/victory1908/payment-service/`, `github.com/victory1908/inventory-service/`, `github.com/victory1908/shipping-service/`) continues to work as-is.

#### Scenario: All eight service modules have the correct module path

- **WHEN** the architecture test scans `services/<name>/go.mod` for the `module` directive
- **THEN** the test verifies that `services/order-service/go.mod` declares `module github.com/victory1908/services/order-service` (the historical exception)
- **AND** the test verifies that the other seven service modules declare `module github.com/victory1908/<name>`

