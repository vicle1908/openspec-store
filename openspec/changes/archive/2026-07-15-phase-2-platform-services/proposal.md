## Why

The Order Service MVP proves the single-service patterns (DDD, transactional outbox via Debezium CDC, durable Temporal orchestration, REST contracts, architecture tests) and the smoke stack is green end-to-end. The platform's `docs/ownership.md`, `docs/extraction.md`, and the ten `service-template/` documents already define the rules of the road for multi-service evolution, but only the Order Service exists today. Three normative gaps block a real cross-service platform: (1) consumer-only and read-mostly services that round out the e-commerce loop (notification, customer profile, product catalog, reporting) are not implemented; (2) the observability surface stops at structured logging and propagation headers — there is no OpenTelemetry SDK, no Prometheus endpoint, no trace exporter, no central collector, and no Grafana LGTM backends; (3) the shared platform code that every new service will need (logger with trace-context injection, OTLP-aware metrics, Kafka consumer harness with durable receipts, health probe wiring, Fx composition helpers) does not exist outside the order-service module. Phase 2 lands all three so the platform can support a second, third, and fourth independently deployable service without re-deriving the same foundation.

## What Changes

- Create a new Go module `platform/` containing reusable, generic, dependency-free packages (`platform/observability`, `platform/contracts`, `platform/kafka`, `platform/health`, `platform/runtime`) that every service depends on.
- Implement four new services, each in its own Go module under `services/`:
  - **notification-service** — pure consumer of `orders.events.v1` and `payments.events.v1`; owns `notifications` PostgreSQL, `notifications.events.v1` Kafka topic, and `notifications.<role>.v1` consumer groups; dispatches templated notifications (email/SMS/push) through a pluggable provider interface with at-least-once delivery and durable receipts.
  - **customer-service** — owner of customer profile and address book; owns `customers` PostgreSQL, `customers.events.v1` Kafka topic, REST CRUD API for customer/address entities, and GDPR export/delete endpoints; Order stores a customer reference snapshot only.
  - **catalog-service** — owner of product master and pricing authority; owns `catalog` PostgreSQL, `catalog.events.v1` Kafka topic, REST API for product/price entities; provides a price-quote endpoint that the Order service calls synchronously when building an order.
  - **reporting-service** — read-only projection consumer of every domain event topic; owns `reporting` PostgreSQL (denormalized star schema) and the reporting REST query API; never participates in any command path.
- Add end-to-end OpenTelemetry instrumentation: OTel SDK with OTLP gRPC exporter in every service, OTel Collector deployed in `deploy/docker-compose.yaml` as the single egress, and the Grafana LGTM stack (Loki for logs, Tempo for traces, Mimir for metrics, Grafana for visualization) wired under a `lgtm` profile with `grafana/otel-lgtm` as the local single-image bootstrap.
- Update Order Service to call Customer and Catalog through their REST APIs and consume their events instead of holding customer_id and product_id as bare ULIDs with no source-of-truth.
- Extend `docker-compose.yaml` with one `*-migrate`, one or more runtime services, and one Kafka + Postgres + Debezium connector per new service; add `deploy/docker-compose.lgtm.yaml` overlay for the observability stack.
- Wire OTel-aware Zap logging (with `trace_id` / `span_id` injection), Prometheus-format `/metrics` endpoint on every service, and a shared `Makefile` template that each service copies with its own scope prefix.
- Add architecture tests in each service module that mirror `order-service/test/architecture/` (domain purity, no peer-service imports, sole-writer database rule) and add a cross-service architecture test that fails the PR gate if any service imports a peer's internal package.

No existing REST, Protobuf, or database contract is broken. The Order Service's public API and event payloads are unchanged; the new services only add new topics, new REST endpoints, and new database schemas.

## Capabilities

### New Capabilities

- `platform-observability`: shared OTel-aware Zap logger, Prometheus metric registry, OTLP exporter wiring, trace-context propagation helpers, `/metrics` and `/health/*` HTTP handlers.
- `platform-contracts`: shared Protobuf contract conventions, event envelope helpers, Buf lint/breaking configuration template, generated-Go base types shared across services.
- `platform-kafka-harness`: shared Kafka consumer with durable receipt store, gap detection, quarantine sink, automatic claim-and-start workflow integration, and a `processor.ProcessRecord` interface every consumer implements.
- `platform-health`: shared `/health/live`, `/health/ready`, `/health/startup` probe with dependency-specific checks, dependency-ready aggregation, and the role-probe HTTP server used by Docker Compose healthchecks.
- `platform-runtime`: shared Fx composition, graceful shutdown, signal handling, role-subcommand dispatch (`api`, `worker`, `orchestrator`, `migrate`, `infrastructure init`, `healthcheck`), and the typed configuration load path.
- `platform-cache`: capability-gated cache abstraction. The platform exposes a `Cache` interface (Get / Set / SetNX / Del / Incr) without importing any vendor SDK. Services admit a vendor SDK (Redis or Valkey) into their own module only after authoring an ADR per `order-service/docs/adr/0004-optional-infrastructure.md`. The capability spec covers idempotency-via-cache (two-phase state), rate limiting (Lua / INCREX), cache-aside patterns, keyspace declaration, TTL bands, observability, and the rejection of Redis-as-source-of-truth.
- `platform-kafka-harness`: shared Kafka consumer with durable receipt store, gap detection, quarantine sink, automatic claim-and-start workflow integration, and a `processor.ProcessRecord` interface every consumer implements. Built on franz-go `v1.21.5` with cooperative-sticky balancing, K8s-static membership, and a non-blocking retry-topic chain (`<topic>.retry.1000`, `.retry.8000`, `.retry.60000`, `.retry.300000`, `.retry.1800000`, `<topic>.dlq`). Includes idempotent producer settings, Burrow consumer-lag monitoring, and OTel context propagation across Kafka boundaries.
- `platform-temporal-versioning`: Temporal Worker Versioning v2 (build-ID based), explicit activity timeouts (`StartToCloseTimeout`, `ScheduleToCloseTimeout`, `ScheduleToStartTimeout`, `HeartbeatTimeout`), deterministic workflow code enforcement via `workflowaudit`, idempotent activities with stable `operation_id`, typed errors (Retryable / NonRetryable / Compensation), saga compensation in inverse order, Workflow ID reuse policy, Temporal Schedules (replaces Cron API), OTel propagator integration, and workflow replay tests.
- `platform-hexagonal-enforcement`: executable architecture tests enforcing the strict layering `cmd → adapters → ports → application → domain`, sole-writer database rule, no peer-service internal imports, ports expressed as interfaces, adapters implementing exactly one port, build tags for optional infrastructure, and the platform's no-domain-types-in-shared-libraries rule.
- `notification-aggregate`: notification template + delivery attempt aggregate with template versioning, recipient scoping, and provider-failure compensation.
- `notification-dispatcher`: outbox-driven dispatch of email/SMS/push notifications through pluggable provider interfaces (SMTP, SES, Twilio, FCM); durable receipts table; per-channel rate limiting.
- `customer-profile`: customer aggregate with addresses, default shipping/billing flags, email/phone validation, and soft-delete with retention timer.
- `customer-gdpr-export`: GDPR Article 15/17 endpoints — `GET /api/v1/customers/{id}/export` returns the customer's data; `DELETE /api/v1/customers/{id}` triggers a retention-bound purge workflow with cryptographic erasure proof.
- `catalog-product`: product aggregate with variants, attributes, status (draft/active/archived), and category assignment.
- `catalog-pricing-snapshot`: pricing authority — base price, currency, discount windows, tax class; publishes `ProductPriceChanged` events and exposes a synchronous `GET /api/v1/products/{id}/quote` endpoint that Order calls before persisting a snapshot.
- `reporting-projection`: read-only projection store updated by consuming every domain event topic; provides `GET /api/v1/reports/{...}` query endpoints and never participates in any command path.
- `platform-go-runtime`: Go 1.26.5 toolchain pin; Green Tea GC default-on; `GOMEMLIMIT=80%` of container memory; per-service `default.pgo` committed for PGO; `tool` directive replaces `tools.go` for reproducible tooling pins; `httputil.ReverseProxy{Director}` migrated to `Rewrite`; `t.ArtifactDir()` adopted for test artifacts; `B.Loop` adopted for benchmarks; modernizer batches via `go fix -diff`; GODEBUG settings documented in `docs/adr/0005-go-1.26-runtime.md`; goroutine leak profile enabled in staging canary; Go 1.27 migration tracked.

### Capabilities added during spec finalization

The following capabilities were added after deep research into the existing order-service architecture, the `service-template/` conventions, and 2026 best practices for Kafka, Temporal, and Redis/Valkey:

- `platform-cache` — capability-gated cache abstraction; replaces the platform's `InternalOnly-Redis` posture (per `order-service/docs/adr/0004-optional-infrastructure.md`) with an interface + per-service ADR admission policy. Closes the gap where the catalog service legitimately needs a 5-second quote cache that PostgreSQL cannot serve at p99 < 50ms.
- `platform-kafka-harness` — supersedes the original simpler draft with: retry-topic chain, idempotent consumer pattern, franz-go producer/consumer settings, Burrow lag monitoring, OTel propagation. Anchored on the existing order-service `service-template/consumer-group.md` and `docs/adr/0001-at-least-once-event-delivery.md` conventions.
- `platform-temporal-versioning` — adds Worker Versioning v2, deterministic-workflow audit, explicit activity timeouts, typed errors, saga compensation, OTel propagator, replay tests. Closes gaps in the existing order-service that the MVP deferred (e.g., retry-policy floor, OTel propagation).
- `platform-hexagonal-enforcement` — codifies the architecture tests the existing order-service already runs in `test/architecture/layering_test.go` plus new tests for sole-writer, ports-are-interfaces, adapter-implements-exactly-one-port, build-tag isolation, and the architecture-test-itself-is-tested discipline.

### Modified Capabilities

The existing order-service MVP did not formally archive its capabilities into `openspec/specs/`. Phase 2's archive step SHALL sync the following delta specs (added during spec finalization based on a precise review of the existing order-service code):

- `order-temporal-workflow`: delta requirement adding `WorkflowExecutionTimeout` and `ScheduleToCloseTimeout` to the existing `OrderFulfillmentWorkflow`; delta adding the OTel propagator wiring; delta adding Worker Versioning v2 registration. The current code at `order-service/internal/adapters/temporal/activities.go` uses `temporalsdk.NewNonRetryableApplicationError` correctly but does not declare `ScheduleToCloseTimeout`, `HeartbeatTimeout`, or `WorkflowExecutionTimeout`, which means a stuck activity could in principle retry for the SDK's default 10-year horizon.
- `order-outbox-cdc`: delta requirement adding the `heartbeat.interval.ms=10000` and `REPLICA IDENTITY DEFAULT` settings to the Debezium connector; the existing `deploy/debezium-connector.json` is missing both.
- `platform-extensibility`: delta requirement adding the precise order-service code paths that change under Phase 2 (see `docs/precise-changes.md` in this change). These are documented per file:line and per PR.
- `platform-verification`: delta requirement strengthening the existing `verification/traceability.yaml` with the new verification IDs the Phase 2 services introduce (PV-100..PV-110 for cross-service calls, plus PV-200..PV-260 for the new platform capabilities).

## Impact

### New code (per service)

- `services/<name>/cmd/<name>/main.go` — entrypoint with the role subcommand set (`api`, `worker`, `orchestrator`, `migrate`, `infrastructure init`, `healthcheck`).
- `services/<name>/internal/domain/<name>/` — aggregate, value objects, identity types, domain events, sentinel errors.
- `services/<name>/internal/application/commands|queries|orchestration/` — handlers, idempotency, fingerprinting, unit-of-work orchestration.
- `services/<name>/internal/ports/` — repository, unit-of-work, clock, ID generator, workflow-starter interfaces.
- `services/<name>/internal/adapters/{http,postgres,kafka,temporal}/` — boundary adapters, each behind a build tag where the SDK is optional.
- `services/<name>/contracts/<name>/v1/` — generated Protobuf; Buf-managed; `buf.yaml` + `buf.gen.yaml` mirroring the order-service layout.
- `services/<name>/migrations/<name>/` — embedded Goose SQL, one migration per schema version, additive-only by construction.
- `services/<name>/deploy/{docker-compose.<name>.yaml, debezium-<name>-connector.json, provision-<name>-topics.sh}` — per-service infrastructure overlay.
- `services/<name>/test/{architecture,integration,compatibility,faults,performance,fuzz}/` — full test surface, ≥90/90/80 coverage.
- `services/<name>/verification/{traceability.yaml, coverage-policy.yaml, reference-environment.yaml, tools.env}` — verification evidence contract.
- `services/<name>/docs/{README.md, adr/, runbooks/, sequences/}` — service documentation.

### New code (platform module)

- `platform/go.mod` — independent module, versioned, pinned to Go 1.26.5.
- `platform/observability/` — `logger.go`, `tracer.go`, `meter.go`, `propagation.go`, `redact.go`, `metrics.go`.
- `platform/contracts/` — `event_envelope.go` (Go-level helpers around the generated `platform.events.v1.EventEnvelope`), Buf configuration template.
- `platform/kafka/` — `consumer.go`, `receipt.go`, `processor.go`, `quarantine.go`, build-tag-gated franz-go backend.
- `platform/health/` — `probe.go`, `checks.go`, role-probe server.
- `platform/runtime/` — `fx.go` (Fx options), `shutdown.go`, `roles.go`, `config.go` (typed config loader).
- `platform/docs/` — module README, ADR for the shared-platform boundary, runbooks for cross-cutting incidents.
- `platform/test/` — unit + fuzz tests for every exported helper.

### New code (top-level)

- `deploy/docker-compose.lgtm.yaml` — Grafana LGTM stack overlay (`grafana/otel-lgtm` for local, real Loki/Tempo/Mimir in prod).
- `deploy/otel-collector-config.yaml` — receivers (OTLP gRPC/HTTP, prometheus), processors (batch, tail_sampling, memory_limiter, k8sattributes), exporters (logging for dev, otlp/tempo, otlphttp/mimir, otlphttp/loki for prod).
- `Makefile.platform` — canonical Makefile template each service copies with its own scope prefix.
- `scripts/wait-for-services.sh` — Compose healthcheck helper used by every service's migrate/infrastructure init role.

### Modified code

All paths below reflect the actual `order-service` layout: `cmd/order-service/{main.go, roles.go, adapter.go, wiring.go, worker_activities.go}` and `internal/runtime/{runtime.go, api.go, worker.go, orchestrator.go, migrate.go, infrastructure.go, healthcheck.go}`. There are no per-role subdirectories in this codebase.

- `order-service/internal/application/commands/create_order.go` — gains a pre-persistence call to `catalog-service` to capture a price snapshot, and a lookup of `customer-service` to verify customer existence (replacing the bare ULID check). Uses the OTel-instrumented HTTP client so trace context propagates to the peer service.
- `order-service/internal/application/orchestration/processor.go` — gains subscriptions to `customers.events.v1` and `catalog.events.v1` to update local denormalized views used for fast order validation; primary workflow path unchanged.
- `order-service/internal/runtime/api.go` — propagates incoming trace context to outbound HTTP calls via `otelhttp.NewTransport`; adds `/metrics` endpoint behind a separate port (default `:9090`) via the Prometheus exporter.
- `order-service/internal/runtime/worker.go` — adds Worker Versioning v2 build-ID configuration, adds Temporal OTel propagator via the SDK contrib package, registers `TemporalWorkerLifecycle` as `fx.StartStopHook` (NOT `fx.Hook` with `Run()`).
- `order-service/internal/runtime/orchestrator.go` — deletes the hand-rolled consumer and replaces it with `platform/kafka.Consumer`; adds subscriptions to retry topics; uses the platform's Burrow alert rules.
- `order-service/internal/observability/` — the entire directory is replaced by imports of `platform/observability`. The existing `logging.go` and `redact.go` are deleted.
- `order-service/internal/adapters/temporal/activities.go` — adds explicit `ScheduleToCloseTimeout`, `HeartbeatTimeout`, `WorkflowExecutionTimeout`; adds `contract_version` validation via `validateVersionedOperation`.
- `order-service/deploy/docker-compose.yaml` — gains `ORDER_CUSTOMER_SERVICE_URL` and `ORDER_CATALOG_SERVICE_URL` environment variables; gains `depends_on` references to `customer-api` and `catalog-api`; gains Debezium `heartbeat.interval.ms=10000`.
- `order-service/verification/traceability.yaml` — adds verification IDs for the cross-service call paths (PV-100..PV-110 series) and the platform capabilities (PV-200..PV-260).
- `order-service/docs/ownership.md` — promotes Notification, Customer, Catalog, Reporting rows from "planned" to "active in development".
- `order-service/docs/adr/0005-go-1.26-runtime.md` — new ADR documenting Green Tea GC default, PGO via `default.pgo`, `t.ArtifactDir()` adoption, `B.Loop` migration, `tool` directive migration, and the plan to migrate `httputil.ReverseProxy{Director}` → `Rewrite` in 1.27.
- Root `Makefile` — new targets `platform-verify`, `services-verify` that build and test the platform module and every service module in dependency order.

### Dependencies (new)

All Go module versions below were re-verified against `proxy.golang.org` and
the upstream GitHub release pages on **2026-07-15**. The OTel line has tight
minor-version coupling: `otelhttp` and the `otel/exporters/...` modules MUST
be at the minor version that matches the chosen `otel` core release, with
the contrib packages on their own (lagging) version line.

**OpenTelemetry core (`v1.44.0` line):**
- `go.opentelemetry.io/otel v1.44.0` — OpenTelemetry SDK core (tagged
  2026-05-27; latest stable on the proxy; the previous `v1.44.1` string in
  the proposal was a `pkg.go.dev` pseudo-version, not a real tag).
- `go.opentelemetry.io/otel/sdk v1.44.0` — tracer/metric/log SDK.
- `go.opentelemetry.io/otel/log v0.20.0` — log API (still Beta per the OTel
  spec; the `v0.x` line is expected even after graduation).
- `go.opentelemetry.io/otel/sdk/log v0.20.0` — log SDK.
- `go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc v1.44.0`
  — OTLP gRPC trace exporter.
- `go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc v1.44.0`
  — OTLP gRPC metric exporter.
- `go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc v0.20.0` — OTLP
  gRPC log exporter (now stable; previously experimental).
- `go.opentelemetry.io/otel/exporters/prometheus v0.66.0` — Prometheus scrape
  endpoint. **Correction**: this module is on the **core** (not contrib)
  version line; the correct pin is `v0.66.0`, NOT `v0.69.0` from the
  previous proposal (which would not resolve on the Go proxy).

**OpenTelemetry contrib (`v1.44.0` / `v0.69.0` line, tagged 2026-05-28):**
- `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.69.0` —
  HTTP client/server middleware. **Behavioral change since v0.65.0**:
  server span names now follow the OTel HTTP semconv
  (`<method> <route>` or `<method>`), and unknown methods report
  `_OTHER` instead of `GET`. Existing Grafana/Tempo dashboards that match
  on legacy span-name patterns MUST be updated.
- `go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.69.0`
  — gRPC instrumentation. Deprecated `WithSpanOptions` removed in v0.69.0.
- `go.opentelemetry.io/contrib/bridges/otelslog v0.19.0` — **corrected
  import path**: the bridge lives under `bridges/otelslog`, not
  `instrumentation/log/slog/otelslog` (that path does not exist on the
  contrib repo). v0.19.0 now uses `record.SetErr(err)` so `error`-typed
  fields surface as `exception.*` on OTLP logs.
- `go.opentelemetry.io/contrib/bridges/otelzap v0.19.0`, `otellogrus v0.19.0`,
  `otellogr v0.19.0` — same `SetErr` fix; adopt in tandem.
- `go.opentelemetry.io/contrib/otelconf v0.37.1` — declarative OTel config
  loader (replaces the previous `obsconfig` package path).
- `go.opentelemetry.io/contrib/samplers/jaegerremote v0.37.1` — gRPC remote
  sampler (alternative to `ParentBased(TraceIDRatioBased(0.10))` when
  per-service sampling strategy is required).

**PostgreSQL tracing (community-maintained, NOT in contrib):**
- `github.com/XSAM/otelsql v0.42.0` — `database/sql` wrapper. Use this for
  legacy `database/sql` code paths; v0.42.0 dropped the experimental
  `db.sql.latency` metric and the `db.statement` span attribute in favor
  of stable semconv.
- `github.com/exaring/otelpgx v0.11.1` — native `pgx/v5` tracer. **This is
  the platform's recommended pgx tracer**; set
  `config.ConnConfig.Tracer = otelpgx.NewTracer()` on every pgx connection
  and call `otelpgx.RecordStats(pool)` for the connection metrics.
- `github.com/pgx-contrib/pgxotel` — alternative maintained by the pgx
  community; considered for future use.

**Prometheus:**
- `github.com/prometheus/client_golang v1.23.2` — Prometheus metric
  primitives (current stable, 2025-09-05; no v1.24 released yet). Native
  histograms + exemplars supported since v1.22/v1.23.

**HTTP / sync / tools:**
- `golang.org/x/sync v0.22.0` — errgroup for parallel shutdown
  (latest stable, 2026-07-01).
- `golang.org/x/tools v0.48.0` — `go/packages` API for the
  hexagonal-enforcement architecture tests; also covers `go vet`,
  `staticcheck` integration, and `gopls` modernizers. The pre-release
  `v0.48.1-0.20260714...` is available for Go 1.27-aware analyzers; the
  platform tracks `v0.48.0` for reproducibility.
- `golang.org/x/crypto v0.54.0` — pinned at the module level (the bcrypt
  subpackage is part of this). The platform's config sets
  `bcrypt.DefaultCost = 12` (the stdlib default is 10, which is too low for
  2026 hardware).

**Kafka:**
- `github.com/twmb/franz-go v1.21.5` — Kafka client (tagged 2026-07-01;
  already current; a `v1.21.6` exists only as a pseudo-version). Includes
  full Kafka 4.2 support (added in `v1.21.0`). **Correction**: the order-
  service already pins `franz-go v1.21.5` (verified via `go.mod`); the
  previous proposal's framing of this as "replacing `segmentio/kafka-go`"
  was inaccurate — there is no segmentio dependency in the order-service
  to replace. The Phase 2 work promotes the kafka consumer logic to
  `platform/kafka` for re-use across services.
- `github.com/twmb/franz-go/pkg/kadm v1.18.0` — admin client for the
  `infrastructure init` role (topic + ACL + consumer group provisioning).
  Adds the KIP-1142/KIP-1152/KIP-860 admin APIs over the older `kmsg`
  direct calls.
- `github.com/twmb/franz-go/plugin/kotel v1.7.0` — drop-in OTel hook for
  produce/fetch spans. **Optional follow-up** for projection services that
  want per-record trace context in the broker.
- **Removed from proposal**: `PauseFetchTopics` / `ResumeFetchTopics` are
  NOT franz-go APIs. Consumer backpressure is achieved by
  `kgo.AutoCommitMarks()` + throttling the `cl.PollFetches(ctx)` loop.

**Temporal:**
- `go.temporal.io/sdk v1.46.0` — Go SDK (released 2026-07-07; includes OTel
  tracing for **standalone activities** via the contrib bridge).
- `go.temporal.io/api v1.63.3` — proto module (transitive; do not pin
  explicitly; the SDK's `go.mod` pulls the right version).
- `go.temporal.io/sdk/contrib/opentelemetry v0.7.0` — Temporal-OTel bridge
  (current stable, 2026-02-12). **Blocker resolved by using the
  pre-release pseudo-version**:
  `v0.7.1-0.20260430232007-8b9d2c2589cd` (April 30, 2026) pulls otel
  v1.41.0 transitively, which is compatible with the platform's otel
  v1.44.0 core pin (Go MVS picks the highest). When Temporal cuts a
  stable `v0.7.1` or `v0.8.0`, the platform switches to it.
- `go.temporal.io/sdk/contrib/envconfig v1.0.2` — env/TOML-driven
  `ClientConfigProfile` for service init (GA since 2026-02-26). The
  platform's `config.Load[ConfigType]` helper accepts `ClientConfigProfile`
  output as an alternative source.
- `go.temporal.io/sdk/contrib/tools/workflowcheck v0.5.0` — the actual
  static analyzer for deterministic workflow code. **Correction**: there
  is NO Temporal product called `workflowaudit` (it was a hallucinated
  name in the previous proposal). The real tool is `workflowcheck`,
  which is `go vet`-compatible (`go vet -vettool $(which workflowcheck)`).
  The platform's allowlist lives at
  `platform/workflows/.workflowcheck.yaml` and adds `os.Getenv`,
  `context.Background`, `net.LookupHost`, `os.Hostname` to the
  non-deterministic set.
- **Removed from proposal**: `temporal-proxy` is not a real Temporal
  product. The platform's OTel path is `apps → OTLP → OTel Collector →
  LGTM`; the official Temporal Cloud path uses the built-in mTLS endpoint
  and the `temporal` CLI's `temporal operator namespace` commands.
- **Worker Versioning v2 wording fix**: GA on **Temporal Server 1.31.0**
  (2026-04-29), not 1.30+ (where it was still public preview). The
  platform pins Temporal Server `v1.31.2` (released 2026-07-08) in
  compose. The SDK uses `worker.DeploymentOptions` (the public alias
  for the internal `WorkerDeploymentOptions`); the previous proposal's
  reference to `WorkerDeploymentOptions` directly is acceptable because
  it's the same type, but `worker.DeploymentOptions` is the canonical
  name.

**Cache (per-service admission, not platform module):**
- `github.com/redis/go-redis/v9 v9.21.0` — Redis 8.x client (the
  catalog service admission; platform module does NOT import this).
- `github.com/valkey-io/valkey-glide/go v2.5.0` — Valkey 9.x client
  (alternative admission; the catalog service may pick either).
- `redis:8.8-alpine` — Docker image for the cache. **Note**: Redis
  8.8 introduced vector + JSON v2 + new commands (ACLs v2, `CLUSTER
  MEET --bootstrap`); the platform's cache client MUST be Redis 8.8+ to
  support these.
- `valkey/valkey:9.1-alpine` — alternative Docker image.
- `oliver006/redis_exporter v1.86.0` — **Correction**: the previous
  proposal's pin of `v1.62.0` is too old to expose Redis 8.8 array
  metrics. Bump to `v1.86.0` to retain array-feature compatibility.

**Debezium (CDC, applied to the order-service compose):**
- `quay.io/debezium/connect:3.6.0.Final` — Debezium 3.6.0.Final (current
  stable; the `debezium/connect` Docker Hub mirror is stuck on
  `3.0.0.Final` and is therefore NOT used; `quay.io/debezium/connect` is
  the canonical registry).
- Debezium 3.6 introduces the new `IncrementalSnapshot` API and the
  enhanced `REPLICA IDENTITY DEFAULT` support (the order-service's
  outbox table uses this); the `heartbeat.interval.ms` and
  `publication.autocreate.mode` settings from D3.6 are unchanged.

**Protobuf / Buf:**
- `github.com/bufbuild/buf v1.71.0` — Buf CLI (current stable;
  2026-07-01). The previous proposal's pin of `v1.49.0` was months
  behind. Workspace v2 is the default mode in v1.71.0.
- `github.com/bufbuild/protovalidate v1.2.2` — runtime validator
  (replaces the deprecated `protoc-gen-validate`). `buf/validate/validate.proto`
  annotations are stable.

**Postgres driver:**
- `github.com/jackc/pgx/v5 v5.10.0` — `pgx/v5` (current stable,
  2026-06-15). Includes the `MaxConnLifetime` enforcement on `Acquire`
  (PR #2561), `OptionShouldPing`, `OpenDBFromPool`, `PrepareConn` hook,
  the `pgx.Identifier` safe SQL identifier helper, and the `pgx.Tracer`
  interface for the OTel bridge (used by `otelpgx`).

**ULID / identity:**
- `github.com/oklog/ulid/v2 v2.1.1` — ULID v2 (additive API over
  v2.0.0; new `Make(time.Time, *rand.Reader)`, `Bytes()`, `Timestamp()`
  helpers, `IsZero()` and `ulid.Nil`).

**Developer tooling (pinned via `go.mod`'s `tool` directive):**
- `go.uber.org/fx v1.24.0` — Fx (current stable; 2025-05-13). **Correction
  on phantom Fx APIs** the previous proposal referenced but which do NOT
  exist:
    - `fx.ValidateApp(opts...)` → **does not exist** as a public Fx API.
      The closest mechanism is `fxtest.New(t, opts...)` which auto-
      validates, OR `app.Err()` after `fx.New(...)` to read the
      initialization error. **Action**: rewrite the spec requirement to
      use `app.Err()` inspection in `cmd/<service>/main.go`.
    - `fx.WithTimeout(...)` → **does not exist**. The correct API is
      `fx.StartTimeout(d)` and `fx.StopTimeout(d)` (both real and
      stable).
    - `fxtest.WithRequireStartTimeout(...)` / `fxtest.WithRequireStopTimeout(...)`
      → **do not exist**. The correct helpers are `fxtest.WithTestLogger(t)`
      and `fxtest.EnforceTimeout` (added in v1.22.0).
  All four phantom API references appear in `specs/platform-runtime/spec.md`
  and MUST be corrected before the spec is applied. The platform adopts
  the real Fx API names.
- `github.com/prometheus/client_golang v1.23.2` — see above. **Note**:
  the previous proposal referenced `prometheus.NewPedanticRegistry`,
  which **does not exist**; the canonical mechanism for strict metric
  registration is `prometheus.NewRegistry()` + `prometheus.WrapRegistererWith*`.
- `github.com/golangci/golangci-lint/cmd/golangci-lint v2.12.2` — linter
  v2 line (GA; v1 is EOL). Requires the `.golangci.yml` v2 schema.
- `honnef.co/go/tools/cmd/staticcheck v0.7.0` (Staticcheck 2026.1) —
  pinned alongside golangci-lint (which already pulls it).
- `golang.org/x/vuln/cmd/govulncheck v1.1.4` — **Correction**: the
  previous proposal's pin of `v1.6.0` does not exist; the actual latest
  is `v1.1.4` (2026-01-13). Use as a CI step in the security workflow.
- `github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen v2.7.2` —
  **security-critical** (v2.7.0–v2.7.1 had code-injection CVEs fixed in
  v2.7.1 and v2.7.2). v2.8.0 will validate specs before codegen.
- `github.com/bufbuild/buf/cmd/buf v1.71.0` — see Protobuf / Buf.
- `github.com/golang/mock/mockgen v1.6.0` — **archived** upstream
  (2023-06-27). The platform tracks `v1.6.0` for existing tests but
  plans a follow-up to evaluate `mockery v3.x` (drop-in compatible) or
  `moq` (simpler API) for new code. This is a Phase 3+ follow-up, not
  blocking Phase 2.
- `golang.org/x/tools/cmd/stringer v0.48.0` — pinned with x/tools.

**SMTP catcher for local dev (replacement for `mailhog`):**
- `axllent/mailpit:v1.30` — **switch from `mailhog/mailhog`**: mailhog
  has not had a Docker image update since ~2019, lacks ARM64 support,
  and the project is effectively abandoned (issue #442
  "THIS PROJECT IS DEAD!" is still open). mailpit is a drop-in
  replacement (same default ports `1025` for SMTP and `8025` for the
  Web UI), actively maintained, ARM64-native, and offers a MailHog-
  compatible API. The `order-service/docs/adr/0006-mailhog-to-mailpit.md`
  records the switch.

### Dependencies (per-service additions)

- `notification-service`: `github.com/aws/aws-sdk-go-v2/service/ses` (provider interface, swappable), `github.com/twilio/twilio-go` (provider interface, swappable). The production provider credentials are not pinned in this change.
- `customer-service`: no new infra dependencies; `golang.org/x/crypto/bcrypt` for password-equivalent secret hashing if a future self-service signup is added (not in this change's scope).
- `catalog-service`: no new infra dependencies.
- `reporting-service`: `github.com/jackc/pgx/v5` (already pinned) for bulk projection loads.

### Dependencies (platform infrastructure, pinned in this change)

Image versions below were re-verified against Docker Hub, the OTel
Collector releases repo, and the Grafana releases repo on **2026-07-15**.
The previous proposal's pins were 1-21 minor versions behind.

- `grafana/otel-lgtm:v0.29.0` — local LGTM stack (pushed 2026-07-13).
  Bundles **OTel Collector v0.156.0** + **Grafana 13.1.0** +
  **Prometheus 3.13.1** + **Loki 3.7.3** + **Tempo 3.0.2** + **Mimir 3.1.2**.
  The previous proposal pinned `v0.11.0`; the actual image at the
  release index date was already `v0.29.0`.
- `otel/opentelemetry-collector-contrib:v0.156.0` — Collector with all
  receivers/exporters enabled (released 2026-07-07). The previous
  proposal pinned `v0.135.0` which is 21 minor versions behind. **Cluster
  name rename wave**: between `v0.149` and `v0.156`, many components
  renamed to snake_case (e.g. `kafkametrics` → `kafka_metrics`,
  `loadbalancingexporter` → `loadbalancing_exporter`,
  `k8sattributes` → `k8s_attributes`). Any collector config older than
  `v0.149` MUST be migrated before running on `v0.156.0`.
- `grafana/grafana:13.1.0` — visualization layer for the local stack
  (the previous `12.0.0` pin was 8 months old; v12 is no longer the
  current line).
- `prom/prometheus:v3.13.1` (or the LTS `v3.5.5`) — only when the
  platform runs without Mimir for cost reasons; the default is
  OTel Collector → Mimir. The previous `v3.5.0` pin is two patch
  releases behind.
- `quay.io/debezium/connect:3.6.0.Final` — Debezium 3.6.0.Final CDC
  connector image (NOT the Docker Hub `debezium/connect` mirror, which
  is stale on `3.0.0.Final`).

All image pins MUST clear `make verify-images` for `linux/arm64` before
this change can ship. Pinned versions are re-verified at `openspec sync`
and on every PR.

### Configuration

- Every service reads configuration from Viper under the `<SERVICE>_*` prefix (e.g., `CUSTOMER_DATABASE_URL`, `CATALOG_KAFKA_TOPIC`); the platform module's `config.go` provides the typed decoder used by every service.
- The OTel exporter endpoint is `OTEL_EXPORTER_OTLP_ENDPOINT` (default `http://localhost:4317`); each service sets its own resource attributes (`service.name`, `service.version`, `deployment.environment`) via the standard `OTEL_RESOURCE_ATTRIBUTES` env var.
- **Sampling strategy (head + tail combined)**:
  - **SDK (head)**: `sdktrace.ParentBased(sdktrace.TraceIDRatioBased(0.10))` — root spans sampled at 10%, child spans respect the parent's decision. Rationale: free heap/CPU savings on tracers that emit to the OTel Collector; production can scale the ratio via `OTEL_TRACES_SAMPLER_ARG=0.1`.
  - **Collector (tail)**: `tail_sampling` processor with three policies in this order: `errors` (always sample errors), `latency` (sample > 1s p99), `probabilistic` (10% fallback for healthy traffic). Tail sampling happens in the gateway collector AFTER the local `batch` processor and AFTER `memory_limiter`.
  - **Local dev**: `ParentBased(AlwaysOn)` for instant trace visibility; the `lgtm` Compose profile enables this via `OTEL_TRACES_SAMPLER=always_on`.
- **OTel Collector topology (production)**:
  - **DaemonSet agent** (`otelcol-agent`) per node — receives OTLP gRPC/HTTP from local apps; tail-samples on the gateway (not locally to avoid per-node tail sampling latency).
  - **Deployment gateway** (`otelcol-gateway`) behind a `Service` with HPA on `otelcol_*` queue size metrics — performs tail sampling, load-balanced export to Tempo/Mimir/Loki via `loadbalancing` exporter (trace-ID routing for Tempo).
  - Processors in order: `memory_limiter` (first, prevents OOM), `k8sattributes`, `attributes`/`transform`, `batch`, `tail_sampling`, `batch` (final). Receivers: OTLP gRPC + HTTP, Prometheus scrape, Kafka receiver (for backlog-without-trace data). Exporters: `otlp/tempo` (gRPC), `otlphttp/mimir` (Mimir), `otlphttp/loki` (Loki), `debug` for dev.
- **Baggage policy**: the platform enforces the 64-entry / 8 KB baggage limit (now enforced in Go SDK); services expose only cross-service control flags (`experiment.arm`, `request.priority`); secrets and PII are NEVER in baggage.
- Secrets (Kafka SASL, SMTP credentials, Twilio tokens, AWS keys) are read from environment variables only — never from disk, never from config files.
- **Go runtime knobs (1.26)**: `GOMEMLIMIT=<80% of container memory>` (Green Tea GC + slightly higher RSS), `GOEXPERIMENT=goroutineleakprofile` enabled in staging + one prod canary per service (for Temporal goroutine leak diagnostics). PGO is on by default via `-pgo=auto`; services commit a per-service `default.pgo` produced from a peak-load run.

### Go module hygiene (1.26)

- Every service `go.mod` pins **`go 1.26.5`** and uses the **`tool` directive** to pin `staticcheck`, `govulncheck@v1.6.0`, `golangci-lint`, `mockgen`, `stringer`, `oapi-codegen`. The `tools.go` blank-import hack is fully obsolete.
- Modernizer batch runs commit as PR reviewable diffs (`go fix -diff ./...`), not as automatic merges.

### CI surface

- Root CI matrix gains `platform`, `notification-service`, `customer-service`, `catalog-service`, `reporting-service` jobs alongside the existing `order-service` job.
- Each service's PR gate mirrors `order-service`'s `make verify-pr` adapted to its own scope prefix.
- Release gate (`make verify-release`) runs across all modules; the LGTM Compose overlay is brought up during `test-e2e` so every service's OTel-emitted data lands in Tempo/Mimir/Loki and the test verifies the data is present.
- The release-cadence job (added by `phase-1-follow-ups`) gates the Phase 2 release on the rollback-rehearsal target passing against the prior Phase 1 image.

### Operations

- New operational concerns: tail-sampling policy, OTel Collector cardinality control, Mimir retention, Tempo trace retention, Loki log retention — each documented in `platform/docs/runbooks/`.
- Production deltas per service follow the `order-service/docs/local-vs-production.md` template; each new service publishes its own `local-vs-production.md`.
- Rollback per service is forward-fix: production rollbacks rely on the same expand/contract pattern the Order Service uses. Each new service's first release must rehearse rollback in CI.

### Rollout

1. Land the `platform/` module with its tests, docs, and CI job first. No service depends on platform at this point.
2. Land `notification-service` end-to-end (proposal, specs, design, tasks, code, tests, deploy overlay, docs). It is the simplest peer service and validates the consumer-only pattern.
3. Land `customer-service` — REST-first, no Temporal needed, demonstrates the customer-ID as a real cross-service reference.
4. Land `catalog-service` — REST + events; Order Service starts calling it for price snapshots during this step.
5. Land `reporting-service` — depends on events from Order, Customer, Catalog; lands last because it accumulates.
6. Wire Order Service to call Customer and Catalog through their REST APIs and consume their events.
7. Deploy the LGTM overlay and verify every service's traces show up in Tempo, metrics in Mimir, logs in Loki.
8. Run the cross-service end-to-end smoke test: create customer → add product to catalog → create order (Order calls Catalog for price, Customer for reference) → process payment (in-module stub) → notification fires → reporting projection updates.

### Rollback

Per-service rollback is identical to the Order Service pattern: forward-fix migrations, expand/contract for breaking changes, prior image remains compatible with the current schema for one release. Cross-service rollback is harder: if Customer v2 removes a field the Order Service depends on, both services must roll together. The deployment runbook documents the dual-roll procedure and the release cadence ensures no two services cross-cut-release within 24 hours.

### Precise changes to existing order-service code

A companion document [`precise-changes.md`](./precise-changes.md) enumerates every existing-order-service code change required by Phase 2, with file:line citations and rationale tied to the corresponding OpenSpec requirement. The 12 areas of change are: (1) Temporal activity explicit timeouts (corrected path: `internal/adapters/temporal/activities.go`), (2) Worker Versioning v2 registration (corrected path: `internal/runtime/worker.go`), (3) Temporal OTel propagator (corrected paths: `internal/runtime/worker.go` + `orchestrator.go`), (4) Debezium connector heartbeat and outbox `REPLICA IDENTITY DEFAULT`, (5) Kafka harness migration to the platform's consumer with retry topics and DLQ (corrected path: `internal/adapters/kafka/` + `internal/runtime/orchestrator.go`), (6) Debezium producer settings, (7) OTel SDK wiring (corrected path: `internal/observability/` replaced by `platform/observability`, wired in `internal/runtime/{api.go, worker.go, orchestrator.go}`), (8) cross-service call paths in `create_order.go`, (9) idempotency-key migration path (no change required — PostgreSQL is sufficient), (10) architecture test refresh, (11) verification manifest additions (PV-100..PV-110 for cross-service calls, PV-200..PV-260 for new platform capabilities), (12) documentation updates, (13) hidden technical debt (12.1–12.8: worker-activity stubs, envelope decode compensation, payload extraction at consumer layer, customer causation ID handoff, ULID derivation, deployableConfig validation, Fx per-role apps, outbox `event_id` index).

### Ready-for-Execution Rubric

Before applying this change, the following MUST be true (counts reflect the
specs as finalised at the end of this research+spec finalization pass):

- [x] `openspec validate phase-2-platform-services --type change --strict` reports `valid`. (Last verified at the end of this research+spec finalization pass.)
- [x] `openspec validate --strict --all` reports 3 passed / 0 failed across `order-service-mvp`, `phase-1-follow-ups`, and `phase-2-platform-services`. (Last verified 2026-07-15.)
- [x] Every capability spec has at least one `#### Scenario` block. **393 scenarios across 21 capabilities** (the 21 capabilities live in 21 `spec.md` files; 4 of those files contain both a `## MODIFIED Requirements` block and a `## ADDED Requirements` block because the corresponding capability existed before Phase 2 — the OpenSpec convention counts the capability once but the `## … Requirements` heading twice; verified by `grep -c '^#### Scenario:' openspec/changes/phase-2-platform-services/specs/*/spec.md`).
- [x] Every capability spec has a verifiable `### Requirement` enumeration. **181 requirements** across the 21 capabilities.
- [x] `precise-changes.md` file paths match the actual order-service layout (Section 0 enumerates the layout; the 13 areas use the corrected paths). **Note**: this verification surfaced two factual errors in the original draft (Section 1's claim that activities "use only `StartToCloseTimeout`" and Section 2's claim that the worker uses `worker.Run`); see `precise-changes.md` lines 55-75 for the corrected wording.
- [x] `tests/platform/` (new) contains a smoke test (always-on `TestPlatformSmokeContractIsDefined`) plus a build-tagged disabled file (`smoke_test_disabled.go`) that activates once the platform module exists in PR-1.
- [x] `tools/templates/` (new) contains the canonical Makefile template (`Makefile.platform`), Dockerfile template (`Dockerfile.platform`), Compose overlay template (`docker-compose.service.yaml`), and a `README.md` documenting the substitution rules.
- [x] `docs/adr/0005-go-1.26-runtime.md` (new) documents the platform's Go 1.26 adoption choices (Green Tea GC, `GOMEMLIMIT=80%`, PGO default, `tool` directive, `B.Loop`, `t.ArtifactDir`).
- [x] `verify-traceability` reports zero unmapped scenarios. **473 verifications** across `order-service-mvp`, `phase-1-follow-ups`, and `phase-2-platform-services` (393 are `status: planned`, 80 are `status: implemented`). The validator walks every spec root and confirms every scenario has at least one entry.
- [ ] A dry-run of `openspec apply --change phase-2-platform-services --step platform-module-only` against an empty workspace succeeds without surfacing "unknown file" errors. This gate runs in PR-1's CI job, before the first Phase-2 code lands.

The implementation gate is met when the single remaining checkbox is
checked. **No code should be written before that gate is met.**

### Open decisions (resolved during this pass)

- **Sequence**: the proposal's Rollout Plan (lines 178-187) describes **8 sequential rollout stages**. The implementation `tasks.md` (334 tasks) maps onto those stages as follows (one PR per stage unless adjacent stages fit a single PR):
  1. PR-1 (platform module): tasks §1 (scaffolding) + §2 (observability) + §3 (contracts) + §4 (kafka harness) + §5 (health) + §6 (runtime) + §6a (cache) + §6b (temporal versioning) + §6c (hexagonal enforcement) + §6d (kafka harness enhancements) + §6e (debezium connector improvements) + §6f (Go runtime) + §7 (migrate order-service observability).
  2. PR-2 (LGTM overlay + notification-service): tasks §8 (OTel Collector and LGTM overlay) + §9 (notification scaffolding) + §10 (notification domain) + §11 (notification application) + §12 (notification HTTP/Kafka) + §13 (notification verification/docs).
  3. PR-3 (customer-service): tasks §14 (scaffolding) + §15 (domain) + §16 (application) + §17 (HTTP/Kafka) + §18 (verification/docs) + §18a (additional verification).
  4. PR-4 (catalog-service): tasks §19 (scaffolding) + §20 (domain) + §21 (application) + §22 (HTTP/Kafka) + §23 (verification/docs) + §23a (additional verification).
  5. PR-5 (reporting-service): tasks §25 (scaffolding) + §26 (projection store) + §27 (consumer) + §28 (query API) + §29 (replay/observability) + §30 (verification/docs) + §30a (additional verification).
  6. PR-6 (Order Service integration): tasks §24 (wire Order Service to Customer and Catalog).
  7. PR-7 (cross-service verification gates): tasks §31 (cross-service Compose) + §32 (end-to-end cross-service) + §34 (release verification).
  8. PR-8 (documentation + ADR finalization + technical debt): tasks §33 (documentation and ADRs) + §35 (hidden technical debt from order-service code review).
- **Cross-service rollback**: per-service rollback uses the expand/contract pattern (no change); cross-service rollback requires dual-roll for breaking Protobuf changes (already in the proposal).
- **Cache admission**: only catalog and notification services admit a cache in Phase 2; the platform module's `platform/cache` interface is exported without importing any vendor SDK. Order service does not gain a cache dependency.
- **Template placeholder syntax**: `tools/templates/` uses `__SERVICE_NAME__` / `__SERVICE_NAME_UPPER__` / `__SERVICE_PORT__` / `__SERVICE_METRICS_PORT__` (Python `__name__` style) instead of `{{...}}` because the latter is not a valid YAML scalar in all contexts. `tools/render-templates.sh <service>` substitutes the placeholders and writes `services/<service>/{Makefile,Dockerfile,deploy/docker-compose.yaml}`. The script is the documented per-service bootstrap entry point.