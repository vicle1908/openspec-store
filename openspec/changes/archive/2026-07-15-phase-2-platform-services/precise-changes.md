# Phase 2 — Precise Changes to Existing Order Service Code

This document enumerates every existing-order-service code change required by Phase 2, with the correct file paths (the actual layout is `cmd/order-service/<role>.go` and `internal/runtime/<role>.go` — there are NO per-role subdirectories like `cmd/order-service/api/main.go`). Every change listed here is required for the existing order-service to comply with the new `platform-*` capabilities introduced in Phase 2.

## 0. Layout — what's actually in the repo

```
order-service/
├── cmd/order-service/
│   ├── main.go                  # role dispatcher, signal handling, app.Run()
│   ├── roles.go                 # one function per role (api, worker, orchestrator, migrate, infrastructure init, healthcheck)
│   ├── adapter.go               # adapter for Fx DI
│   ├── adapter_test.go
│   ├── main_test.go
│   ├── wiring.go                # typed config wiring for Fx
│   └── worker_activities.go     # Temporal activity implementations
├── internal/runtime/
│   ├── runtime.go               # Fx lifecycle, signal handler, health server
│   ├── api.go                   # HTTP server wiring
│   ├── api_test.go
│   ├── worker.go                # Temporal worker wiring
│   ├── orchestrator.go          # Kafka consumer + Temporal starter wiring
│   ├── migrate.go               # one-shot migrations
│   ├── infrastructure.go        # one-shot topic + Debezium connector provisioning
│   └── healthcheck.go           # one-shot readiness probe
├── internal/observability/
│   ├── logging.go               # Zap factory (will be replaced by platform/observability)
│   ├── logging_test.go
│   ├── redact.go                # redact list + propagation context (will be replaced by platform/observability)
│   └── redact_test.go
├── internal/adapters/temporal/
│   ├── activities.go            # ValidateInventory, ProcessPayment, ReserveInventory, MarkOrderShipped, RefundPayment, ReleaseInventory
│   ├── workflows.go             # OrderFulfillmentWorkflow
│   └── ...                      # workflow tests
├── internal/adapters/kafka/     # current consumer (to be replaced by platform/kafka)
├── internal/adapters/postgres/repository.go
├── internal/adapters/http/handlers.go
├── internal/application/commands/create_order.go
├── internal/application/orchestration/processor.go
├── internal/config/config.go
├── internal/domain/order/order.go
├── test/architecture/layering_test.go
├── deploy/docker-compose.yaml
├── deploy/debezium-connector.json
├── verification/traceability.yaml
└── Makefile
```

This layout is consistent with `service-template/service-go-module-layout.md` ("`cmd/<service>/main.go` subcommands: `version`, `migrate`, `infrastructure init`, `api`, `orchestrator` (or equivalent), `worker`, `healthcheck`"). Phase 2's `platform-runtime` preserves this layout; per-role Fx apps are constructed inside `internal/runtime/<role>.go`.

---

## 1. Temporal activities — explicit timeouts and versioning

### File: `order-service/internal/adapters/temporal/workflow.go` (and `activities.go`)

**Current state (verified 2026-07-15 against the working tree)**:

- `workflow.go` lines 12-19 declare `workflowRunTimeout=24h`, `activityStartToClose=5min`, `activityHeartbeat=30s`, plus retry-policy constants.
- `workflow.go` line 191-196 (in `awaitActivity`) and lines 293-296 (compensation path) construct `workflow.ActivityOptions{ StartToCloseTimeout, ScheduleToCloseTimeout, HeartbeatTimeout, WaitForCancellation, RetryPolicy }` — the timeouts are **already set** for every activity in the saga. The SDK cannot retry "for its default 10-year horizon"; `ScheduleToCloseTimeout=activityStartToClose*2 = 10m` bounds the cumulative retry window.
- `OrderFulfillmentWorkflow` derives `workflowRunTimeout` from the `workflowRunTimeout` constant; `WorkflowExecutionTimeout` is therefore already bounded at 24h.

**Net of the above**: the original proposal's claim that "Today the activities use only `StartToCloseTimeout`" is **factually wrong**. The migration surface is small.

**Required changes**:

1. **No timeout changes are required.** The existing constants and `awaitActivity` already satisfy `platform-temporal-versioning` Requirements 3 (Explicit activity timeouts). The Phase 2 PR SHALL NOT add `StartToCloseTimeout`/`ScheduleToCloseTimeout`/`HeartbeatTimeout` as new fields; instead it SHALL move the constants into `platform/temporal/options.go::NewValidatedActivityOptions` and have `workflow.go` reference them, so that any future service that adopts the platform harness gets the same bounds by default.
2. The `OrderFulfillmentWorkflow` registration SHALL declare a `WorkflowID = "order/<order-id>"` reuse policy via `client.StartWorkflowOptions{ WorkflowIDReusePolicy: enums.WORKFLOW_ID_REUSE_POLICY_USE_EXISTING }` so duplicate `StartWorkflow` calls short-circuit. (The orchestrator side of this lives in `internal/application/orchestration/processor.go::startWorkflow`.)
3. Every activity's input struct already carries `Version` (`ContractVersionV1`) and `OperationID` (`OperationIDFor(orderID, op)`). The Phase 2 PR SHALL add an explicit call to `validateVersionedOperation(input)` (provided by `platform/temporal/contract_version.go`) at the top of each activity body, replacing the implicit version check currently scattered across the saga.
4. Add an explicit `TemporalWorkerLifecycle` `fx.StartStopHook` that the platform module re-exports. The order-service SHALL adopt the platform hook to align with the new convention, replacing the current `fx.Hook` in `internal/runtime/worker.go::registerWorkerHooks` (see Section 2 for the lifecycle review).

**Rationale**: `platform-temporal-versioning` Requirements 3 (Explicit activity timeouts — already satisfied), 4 (Idempotent activities with stable operation_id — already satisfied), 5 (Typed activity errors), 7 (Workflow ID reuse policy), 13 (Temporal activity version validation).

## 2. Temporal worker registration — Worker Versioning v2

### File: `order-service/internal/runtime/worker.go`

**Current state (verified 2026-07-15 against the working tree)**:

- `worker.go::registerWorkerHooks` uses `fx.Hook{ OnStart: ... opts.Worker.Start(ctx) ... OnStop: ... opts.Worker.Stop(ctx) ... }`. The current code already uses `Worker.Start(ctx)` (non-blocking, returns error) and `Worker.Stop(ctx)` (non-blocking). It does **not** use the blocking `Worker.Run()`. The original proposal's claim that "Temporal blocks on `Run()` which is incompatible with Fx's `OnStart` semantics" is **factually wrong** for the order-service.
- The workers register without `WorkerDeploymentOptions`. With only one worker deployment today this is harmless, but Phase 2 introduces peer services that depend on workflow versioning.
- The lifecycle uses `fx.Hook` (not `fx.StartStopHook`). `fx.Hook` works but the platform convention is `fx.StartStopHook` for clean start/stop timeouts; this is the small migration.

**Required changes**:

1. The `worker.New(client, taskQueue, worker.Options{...})` construction SHALL include `WorkerDeploymentOptions: worker.WorkerDeploymentOptions{DeploymentSeriesName: "order-fulfillment.v1", BuildID: <from runtime.DeploymentVersion()>}`. The platform's `runtime.DeploymentVersion()` helper returns the build ID derived from the git SHA at build time.

2. The orchestrator's `client.StartWorkflow` calls SHALL pass `client.StartWorkflowOptions{... UseVersioning: true}` so new workflow starts route to the configured deployment.

3. Replace the existing `fx.Hook` with the platform-provided `fx.StartStopHook` (see `platform/temporal/lifecycle.go` per `platform-temporal-versioning` Requirement 6). The migration preserves the current `Start(ctx)` / `Stop(ctx)` semantics — the platform hook adds a typed lifecycle logger and a 30s stop-timeout, but does not switch to `Run()`.

4. CI SHALL add a grep-based architecture test (`test/architecture/worker_no_blocking_run_test.go`) that fails the build if `worker.Run(` appears inside any `OnStart` hook body. The current code passes this test; the test is added so future contributors don't regress the convention.

**Rationale**: `platform-temporal-versioning` Requirement 1 (Worker Versioning v2 adoption) and Requirement 6 (Lifecycle Fx hook contract).

## 3. Temporal worker OTel propagator

### File: `order-service/internal/runtime/worker.go` and `orchestrator.go`

**Current state**: workers register without an OpenTelemetry propagator. Spans from inbound HTTP requests do not propagate into workflow executions.

**Required changes**:

1. Add the dependency `go.temporal.io/sdk/contrib/opentelemetry v0.7.0` to `order-service/go.mod`.

2. The worker SHALL be constructed with `worker.Options{Interceptors: []interceptor.WorkerInterceptor{temporal.NewTelemetryInterceptor(...)}}`.

3. The platform's `temporal.NewTelemetryInterceptor(...)` helper returns the OTel propagator + tracer.

**Rationale**: `platform-temporal-versioning` Requirement 9 (OpenTelemetry context propagation across Temporal).

## 4. Debezium connector — heartbeat and outbox identity

### File: `order-service/deploy/debezium-connector.json`

**Current state**: the connector config is missing `heartbeat.interval.ms`, the publication autocreate mode is documented but not enforced in some compose overlays, and the outbox table is `REPLICA IDENTITY FULL`.

**Required changes**:

1. Add `"heartbeat.interval.ms": "10000"` and `"heartbeat.topics.prefix": "order-debezium-heartbeat"` to the connector JSON. This proves the slot is alive when the outbox is empty.

2. Migrate the `outbox` table to `REPLICA IDENTITY DEFAULT` (the table is INSERT-only; `FULL` doubles WAL volume). Migration: `ALTER TABLE outbox REPLICA IDENTITY DEFAULT;` in a new migration file.

3. Confirm `"publication.autocreate.mode": "disabled"` is present in every environment-specific overlay (`docker-compose.yaml`, `docker-compose.tools.yaml`, `docker-compose.lgtm.yaml` once added). The platform's `make verify-images` and `make verify-static` SHALL reject a connector config that allows Debezium to autocreate the publication.

4. Add Debezium internal producer settings (`producer.override.*` per `platform-kafka-harness` Requirement 11): idempotence, lz4, linger.ms=10, batch.size=131072, acks=all.

**Rationale**: `platform-kafka-harness` Requirements 7 (Burrow-based consumer lag alerting — heartbeats feed lag visibility), 11 (Producer-side idempotence and batching), and 2026 best practices for INSERT-only outbox.

## 5. Kafka harness migration

### File: `order-service/internal/adapters/kafka/` (entire package) and `internal/runtime/orchestrator.go`

**Current state**: the order-service implements its own consumer with hand-rolled durable-receipt logic (mirrored in the existing `service-template/consumer-group.md`).

**Required changes**:

1. Delete the hand-rolled consumer code and replace it with imports of `github.com/victory1908/platform/kafka.Consumer`. The platform's consumer implements the same receipt semantics plus retry topics and DLQ.

2. Add the retry topics to `deploy/docker-compose.yaml`'s Kafka init script: `orders.events.v1.retry.1000`, `.retry.8000`, `.retry.60000`, `.retry.300000`, `.retry.1800000`, `orders.events.v1.dlq`.

3. Update the existing orchestration_receipts table migration to add the columns `retry_attempt`, `retry_dispatched_at`, `dlq_reason` (the platform's consumer reads these columns).

4. Add a Burrow sidecar (or rely on the platform's `otel-collector` Burrow receiver) and configure the platform's alert rules.

5. Use the platform's `RetryConsumer` (in `internal/runtime/orchestrator.go`) to read from retry topics, sleep, and re-publish to the source topic.

**Rationale**: `platform-kafka-harness` Requirements 1, 2 (Retry topic pattern), 7 (Burrow-based consumer lag alerting).

## 6. OTel SDK wiring

### Files: `order-service/internal/observability/logging.go`, `redact.go`, plus `internal/runtime/{api.go, worker.go, orchestrator.go}`

**Current state**: the existing `internal/observability/logging.go` provides structured logging via Zap but does NOT configure the OTel SDK. There is no OTel tracer/meter provider, no `/metrics` endpoint, no OTel propagator wiring.

**Required changes**:

1. **Replace `internal/observability/`** with imports of `github.com/victory1908/platform/observability`. Delete the existing `logging.go`, `logging_test.go`, `redact.go`, `redact_test.go` files; replace with thin re-exports of `platform/observability`.

2. **`internal/runtime/api.go`** SHALL call `observability.Init(ctx, observability.Config{ServiceName: "order-service", ServiceVersion: <git SHA>, DeploymentEnvironment: <env>, OTLPEndpoint: os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT")})` at startup. The OTel SDK SHALL be configured with `sdktrace.WithSampler(sdktrace.ParentBased(sdktrace.TraceIDRatioBased(0.10)))` (10% head sampling + parent-based). Tail sampling is configured in the collector.

3. **The Chi router** SHALL use `observability.HTTPMiddleware(router)` to create server spans. Server span naming: `HTTP <method> <route>`.

4. **The platform's `observability.Meter()`** provides a Prometheus exporter; the API role SHALL expose `/metrics` on a separate port (default `:9090`). The metric names SHALL use the `order_service_` scope prefix per `platform-observability` Requirement 2.

5. **The Kafka producer and consumer** SHALL use `observability.Propagator()` to inject/extract trace context. The OTel HTTP client middleware (`go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp`) SHALL wrap outbound HTTP calls so trace context propagates to the customer and catalog services.

6. **Logs**: switch to `log/slog` with the `otelslog` bridge (`go.opentelemetry.io/contrib/instrumentation/log/slog/otelslog`) so `trace_id` and `span_id` are injected automatically. Use `slog.InfoContext(ctx, ...)` (NOT `slog.Info(...)`) so the context is propagated.

7. **Resource attributes** (per `platform-observability` Requirement 4): `service.name=order-service`, `service.version=<git SHA>`, `deployment.environment=<env>`, `service.namespace=<orchestration|notification|customer|catalog|reporting>`, `service.instance.id=<K8s pod name>`.

8. **Baggage**: enforce the 64-entry / 8 KB limit (now enforced in Go SDK). Validate baggage at ingress; never put PII or secrets. Use baggage ONLY for cross-service control flags (e.g., `experiment.arm=variant-A`); propagate via `otel.GetTextMapPropagator().Inject(ctx, carrier)`.

**Rationale**: `platform-observability` Requirements 1, 2, 3, 4, 5, 6, and the 2026 best practices for SDK configuration, sampling, resource attributes, baggage, and log correlation.

## 7. Cross-service call paths

### File: `order-service/internal/application/commands/create_order.go`

**Current state**: the create-order command validates the customer ID via a bare ULID check and snapshots the product ID without consulting the catalog.

**Required changes**:

1. Before persisting the order, the command SHALL call `GET /customer-service/api/v1/customers/{id}/reference` via the OTel-instrumented HTTP client (`otelhttp.NewTransport(http.DefaultTransport)`). The call has a 2-second timeout. On `404 Not Found` the command returns `ErrCustomerReferenceUnavailable` mapped to `404 Not Found`. On timeout the command returns `503 Service Unavailable` with code `customer_reference_unavailable`.

2. For each line item, the command SHALL call `GET /catalog-service/api/v1/products/{id}/quote` via the OTel-instrumented HTTP client. The call has a 2-second timeout. The quote response includes `snapshot_id` which the command stores on the line item.

3. The HTTP client SHALL use the platform's `observability.HTTPClient(...)` wrapper so trace context propagates to the peer service.

4. **Customer causation ID handoff**: when the customer profile changes mid-order (e.g., a GDPR purge fires between the reference check and the order persist), the order service SHALL detect the divergence on `Order.customer_snapshot.version` mismatch and abort the order with `ErrCustomerReferenceStale`. This prevents the order from referencing a customer the platform has purged. The causation ID `X-Causation-Id` from the catalog/customer response SHALL be stored on the order for audit.

**Rationale**: `customer-profile` Requirement 6 (Customer reference snapshot in Order), `catalog-pricing-snapshot` Requirements 2 (Price quote endpoint) and 7 (Synchronous price quote from Order).

## 8. Idempotency-key posture

### File: `order-service/internal/adapters/http/handlers.go`

**Current state**: the `Idempotency-Key` header is validated by the HTTP handler and stored in the `idempotency_keys` PostgreSQL table.

**Required changes**: None today — the PostgreSQL-backed idempotency store is correct for the order-service. The platform's `platform-cache` spec offers a Redis-backed cache as an OPTIONAL accelerator; the order-service does not need it. The cache is admitted by the catalog service (for the 5-second quote cache) and the notification service (for per-channel rate limiting); the order-service does not gain a cache dependency.

**Rationale**: `platform-cache` Requirements 1 (Capability-gated admission) and 6 (Idempotency-via-cache contract — the contract explicitly notes PostgreSQL is the fallback when the cache is unavailable).

## 9. Architecture test refresh

### File: `order-service/test/architecture/`

**Current state**: the order-service has `layering_test.go` enforcing the strict layering. The other architecture tests listed in `platform-hexagonal-enforcement` are not yet present.

**Required changes**:

1. Add `sole_writer_test.go`, `ports_are_interfaces_test.go`, `adapter_implements_exactly_one_port_test.go`, `build_tag_isolation_test.go`, `domain_invariants_are_enforced_test.go`, and `architecture_test_test.go` (the meta-test).

2. Update `Makefile`'s `verify-architecture` target to run all architecture tests before `test-unit`.

3. Add `TestDeterministicWorkflowCode` invoking `workflowaudit` against every workflow file (per `platform-temporal-versioning` Requirement 14).

4. Add `TestWorkerVersioningIsConfigured` asserting the worker's `WorkerDeploymentOptions` are non-empty (per `platform-temporal-versioning` Requirement 1).

**Rationale**: `platform-hexagonal-enforcement` Requirement 9 (Architecture test coverage).

## 10. Verification manifest additions

### File: `order-service/verification/traceability.yaml`

**Current state**: 43 verifications across 9 capabilities (43 implemented, 2 planned but the planned ones were marked stale per the MVP evaluation).

**Required changes**:

1. Promote `OC-005` (Connector stops) and `PV-003` (Orchestrator crashes after workflow start) from `status: planned` to `status: implemented` once the corresponding runbook exercises are integrated into CI.

2. Add the cross-service verifications introduced by Phase 2 (PV-100..PV-110):
   - PV-100: Order Service captures customer reference snapshot before persisting order
   - PV-101: Order Service aborts when customer reference is unavailable
   - PV-102: Order Service captures catalog price snapshot before persisting line item
   - PV-103: Order Service aborts when price quote is unavailable
   - PV-104: Order Service cross-service call propagates trace context
   - PV-105: Notification service consumes OrderShipped and dispatches email
   - PV-106: Customer service GDPR export returns the customer's data within 2 seconds
   - PV-107: Customer service purge workflow respects the retention timer
   - PV-108: Catalog service price change invalidates cached quotes within 100 ms
   - PV-109: Reporting service consumer keeps up with peak event rate
   - PV-110: Reporting service late-event replay reconciles the projection

3. Add platform verifications (PV-200..PV-260) for every requirement in `platform-observability`, `platform-kafka-harness`, `platform-temporal-versioning`, `platform-cache` (when admitted), and `platform-hexagonal-enforcement`.

**Rationale**: `platform-verification` delta requirement (in proposal) and the "every scenario has a verification ID" pattern in `verification/traceability.yaml`.

## 11. Documentation updates

### Files: `order-service/docs/local-vs-production.md`, `docs/compatibility.md`, `docs/adr/0003-temporal-only-orchestrator.md`

**Current state**: these documents describe the existing order-service posture without the Worker Versioning v2, retry topics, or OTel wiring.

**Required changes**:

1. Add a new section to `local-vs-production.md` titled "Observability — OpenTelemetry + Grafana LGTM" describing the local dev path (`grafana/otel-lgtm` single container) and the production path (OTel Collector DaemonSet + gateway + scaled LGTM services).

2. Add a new section to `compatibility.md` titled "Worker Versioning v2 — contract stability" describing the deployment-series contract and the migration path when workflow code changes.

3. Update `docs/adr/0003-temporal-only-orchestrator.md` to mention Worker Versioning v2, the deterministic-workflow audit tool (`workflowaudit`), and the Go 1.26 GODEBUG settings (`tlssecpmlkem=0` opt-out if needed, `asynctimerchan` removal in 1.27).

4. Add a new ADR `0005-go-1.26-runtime.md` documenting the platform's adoption of Go 1.26 features: Green Tea GC default, PGO via `default.pgo`, `t.ArtifactDir()` for test artifacts, `B.Loop` for benchmarks, `tools.go` → `tool` directive migration, and the plan to migrate `httputil.ReverseProxy{Director}` → `Rewrite` in 1.27.

**Rationale**: `service-template/checklist.md` Section 8 (Documentation) — every capability change updates the platform docs.

## 12. Hidden technical debt closed by Phase 2

The hardening review of the existing order-service identified the following items that Phase 2 will resolve:

### 12.1 Worker-activity stubs
The current `internal/adapters/temporal/worker_activities.go` may contain stub activities (ValidateInventory/ProcessPayment/etc.) that delegate to in-module stubs rather than calling the future Payment/Inventory/Shipping services. Phase 2 closes this by introducing the `customer.v1.reference` HTTP client (already in `create_order.go` per Section 7). The Payment/Inventory/Shipping extractions are explicitly out of Phase 2 scope (deferred to Phase 3 per the proposal's "non-goals"); the in-module stubs remain for now.

### 12.2 Envelope decode compensation path
The current `internal/adapters/kafka/...` consumer decodes the `EventEnvelope` payload with a hand-rolled helper. Phase 2's `platform-contracts` exposes `platform.contracts.DecodeEnvelope(bytes) (EventEnvelope, error)` which returns `ErrInvalidEnvelope` for malformed bytes; the platform's kafka-harness quarantines these records (per `platform-kafka-harness` Requirement 3). The order-service's hand-rolled decoder is replaced.

### 12.3 Payload extraction at the consumer layer
The current order-service consumer unmarshals the typed event from `payload bytes` using a per-event-type switch. Phase 2's `platform-contracts` exposes a typed `DecodeEnvelope(bytes) (EventEnvelope, error)` plus the typed event registry (each event type has a generated Go type under `contracts/<domain>/vN/`). The consumer's per-event-type switch is replaced with a typed registry lookup.

### 12.4 Customer causation ID handoff
When the customer service emits a `CustomerSoftDeleted` event mid-order, the order service currently has no mechanism to detect the divergence. Phase 2 introduces the `Order.customer_snapshot.version` check (Section 7.4 above) plus the `X-Causation-Id` propagation so the order service aborts with `ErrCustomerReferenceStale` when the snapshot is invalidated.

### 12.5 ULID generation derivation
The current order-service generates ULIDs at the application boundary. Phase 2 makes the ULID generation an explicit `ports.IDGenerator` interface with a default implementation backed by `oklog/ulid/v2`. The hexagonal architecture test enforces that all ULID generation flows through the port (not directly from the `oklog` package).

### 12.6 DeployableConfig validation
The current `internal/config/config.go` uses Viper with `UnmarshalExact`. Phase 2 adds explicit role-scoped validation (`config.ValidateForRole(role)`) so the API role rejects Kafka config that's only required by the orchestrator, and the worker role rejects HTTP listener config that's only required by the API. The validation runs at startup, before any resource is constructed.

### 12.7 Fx per-role apps (Section 2 reinforcement)
The current `internal/runtime/{api.go, worker.go, orchestrator.go, migrate.go, infrastructure.go, healthcheck.go}` files construct Fx apps. Phase 2 reinforces the pattern that each role constructs its own `fx.New(...)` with `fx.ValidateApp(opts...)` as a pre-flight check, `fx.StartTimeout(30s)` and `fx.StopTimeout(30s)` as the budget, and signal ownership unambiguous (Fx owns SIGINT/SIGTERM for long-lived roles; the runner does not use `signal.NotifyContext`). The platform's `runtime.WithFxApp(role)` helper enforces the pattern.

### 12.8 Outbox table index on `event_id`
The current `outbox` table has a primary key on `id` but no secondary index on `event_id`. Phase 2 adds a secondary index `idx_outbox_event_id` so the platform's idempotent-consumer dedupe path is index-backed. Migration: `CREATE INDEX CONCURRENTLY idx_outbox_event_id ON outbox (event_id);`.

---

## Summary

| # | Area | Files affected (corrected paths) | Effort |
|---|---|---|---|
| 1 | Temporal activity timeouts | `internal/adapters/temporal/activities.go` | S |
| 2 | Worker Versioning v2 registration | `internal/runtime/worker.go` | S |
| 3 | Temporal OTel propagator | `internal/runtime/worker.go`, `internal/runtime/orchestrator.go`, `go.mod` | S |
| 4 | Debezium heartbeat + REPLICA IDENTITY | `deploy/debezium-connector.json`, `migrations/order/` | S |
| 5 | Kafka harness migration | `internal/adapters/kafka/`, `internal/runtime/orchestrator.go`, `deploy/docker-compose.yaml`, `migrations/order/` | M |
| 6 | OTel SDK wiring | `internal/observability/` (replaced), `internal/runtime/{api.go, worker.go, orchestrator.go}` | M |
| 7 | Cross-service call paths | `internal/application/commands/create_order.go`, `internal/adapters/http/handlers.go` | M |
| 8 | Idempotency-key migration path | (no change — Postgres is sufficient) | — |
| 9 | Architecture test refresh | `test/architecture/` | M |
| 10 | Verification manifest additions | `verification/traceability.yaml` | S |
| 11 | Documentation updates | `docs/local-vs-production.md`, `docs/compatibility.md`, `docs/adr/0003-temporal-only-orchestrator.md`, new `0005-go-1.26-runtime.md` | S |
| 12 | Hidden technical debt | Sections 12.1–12.8 above | M |

The Phase 2a (platform foundation) deliverable does items 1–7 plus the platform module itself. Phase 2b–e delivers items 8–11 per service. Item 12 lands in parallel.