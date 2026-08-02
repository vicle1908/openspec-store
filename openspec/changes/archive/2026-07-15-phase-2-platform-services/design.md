## Context

The Order Service MVP shipped with a single service module covering the order lifecycle (create → price → pay → fulfill → ship). The platform's `docs/ownership.md`, `docs/extraction.md`, and the ten `service-template/` documents define the rules of the road for multi-service evolution, but only the Order Service exists today. Phase 2 must:

1. Add four new services (Notification, Customer, Catalog, Reporting) that round out the e-commerce loop. Notification is a pure consumer; Customer and Catalog are REST+event services that the Order Service now calls synchronously and consumes asynchronously; Reporting is a read-only projection consumer.
2. Establish the cross-service platform that all future services will inherit: a shared Go `platform/` module with observability, Kafka harness, health, contracts, and runtime; a unified OpenTelemetry pipeline terminating in the Grafana LGTM stack via an OpenTelemetry Collector; a Protobuf contracts convention enforced by Buf.
3. Wire the Order Service into the new world without breaking its public API or existing Kafka contract: it gains cross-service calls to Customer and Catalog but keeps the same envelope schema, the same outbox topics, and the same Temporal workflow.

The Phase 1 follow-ups change (`phase-1-follow-ups`) is in apply mode and should land first — it adds the release-cadence CI, rollback rehearsal, and broker-UI tools profile that Phase 2 inherits unchanged. Phase 2 is the "next tier of the platform."

The design below covers the shared platform module, the cross-service observability stack, the contracts and event topology, the per-service architecture (one section per service), and the deployment and operations model.

## Goals / Non-Goals

**Goals:**

- Establish a single Go `platform/` module that all services consume; eliminate duplication of observability, Kafka harness, health, and runtime bootstrap code.
- Stand up an end-to-end OpenTelemetry pipeline: OTel SDK in every service → OTLP → OTel Collector → Grafana LGTM (Loki/Tempo/Mimir). Local dev uses `grafana/otel-lgtm`; production keeps the same wiring but with separately scaled LGTM services.
- Deliver four production-grade services whose implementation follows the order-service template: DDD domain, ports/adapters, transactional outbox via Debezium, REST API, Temporal workflows for long-running operations, structured logging, health probes, architecture tests.
- Wire the Order Service to use the new Customer and Catalog APIs without changing the order-service public API or event contract.
- Enforce cross-service discipline through architecture tests: domain purity, sole-writer database rule, no peer-service imports of internal packages, `buf breaking` against pinned proto baselines.

**Non-Goals:**

- Extracting Payment, Inventory, and Shipping from the Order Service. These remain in-module stubs; they have substantial extraction concerns (PCI scope, allocation logic, carrier integration) that warrant their own change cycles. The Phase 2 design reserves space for them by defining the peer-service interaction pattern that future extractions will follow.
- Multi-region active-active deployment. Phase 2 assumes a single region with HA within the region; multi-region is a Phase 3+ concern.
- An API gateway. The MVP has no gateway; Phase 2 adds services behind the same `localhost`/service-name convention. A gateway is a Phase 3+ concern.
- Replacing Kafka. Debezium CDC over Kafka is the platform's chosen event backbone; Phase 2 does not introduce alternatives.
- Replacing PostgreSQL. PostgreSQL remains the sole persistence layer; Phase 2 introduces new schemas (notification, customer, catalog, reporting) but no new database engine.
- A service mesh (Istio/Linkerd). The platform stays on container-native networking; mTLS and routing concerns are deferred to a Phase 3+ change.

## Decisions

### Decision D1 — Single Go `platform/` module lives in-repo

The shared platform module lives in `platform/` inside the same repository as the services. The order-service and Phase 2 services reference it through a `replace` directive in development and through a tagged version in CI.

**Rationale:** The platform is changing rapidly during Phase 2; cross-repo refactoring would slow the work. In-repo with a strict module boundary gives the best of both worlds — a single CI surface and easy local refactors while keeping the public API of `platform/` strict. The order-service's existing `internal/observability/` is promoted to `platform/observability/` over the course of Phase 2a, and the order-service then imports `platform/observability` instead of its local copy.

**Alternatives considered:**
- *Separate repo*: clean isolation, independent versioning. Rejected because cross-repo refactoring during the Phase 2 ramp-up would add substantial coordination overhead, and the current project is a single-team monorepo.
- *Vendored copy per service*: zero build-time coupling. Rejected because every bug fix and every observability improvement would require touching every service; that is exactly what the platform module is meant to prevent.

**Risk:** A platform API change ripples to every service. Mitigation: the `platform/` module carries `internal/` packages that services cannot import; only the stable `pkg/` surface is public. CI runs `make platform-verify` and `make services-verify` in that order, so a breaking platform change fails the platform job first, before any service job runs.

### Decision D2 — OTel SDK + Collector + LGTM

Phase 2 adopts the OTel SDK with an OTLP gRPC exporter in every service. Every service exports to a single OTel Collector (one container in compose, one DaemonSet+gateway in production). The collector forwards traces to Tempo, metrics to Mimir, and logs to Loki. Grafana visualizes all three.

**Rationale:** OTel is the industry standard (CNCF graduated, 2026) and the collector pattern lets us swap backends without touching application code. Apps stay SDK-only; the collector owns routing, sampling, and redaction. This matches the platform's stated direction in `docs/local-vs-production.md` (which already lists OTLP as a production target).

**Alternatives considered:**
- *Apps → backends directly*: simpler topology, but apps now know about Tempo/Mimir/Loki specifically and we cannot swap them. Rejected.
- *Datadog/Honeycomb/SaaS*: zero ops, but vendor lock and cost at scale. Rejected for now; the OTLP exporter means we can add SaaS export later by changing collector config.
- *Prometheus scrape + Tempo OTLP + Loki via Promtail*: viable but two pipelines (push + scrape). Rejected in favor of one pipeline (OTLP) plus a single scrape exporter for legacy compatibility if needed.

**Risk:** Tail-sampling in the collector can drop traces that look interesting in retrospect. Mitigation: collector config preserves 100% of error traces (`status_code != OK`) and 100% of traces whose duration exceeds a configurable threshold; tail-sampling only applies to successful short traces.

### Decision D3 — `grafana/otel-lgtm` for local; LGTM services in production

Local dev uses a single `grafana/otel-lgtm:v0.11.0` container that bundles Loki, Tempo, Mimir, and Grafana behind one OTLP endpoint. Production runs separate, scaled LGTM services plus the OTel Collector as a gateway. Both use the same wire format; the difference is operational scale, not data shape.

**Rationale:** Local dev experience matters for velocity. A single container starts fast, exposes one endpoint, and behaves like production. The migration to scaled LGTM is a deployment concern, not a code change.

**Alternatives considered:**
- *Always separate services*: matches production exactly but doubles the Compose footprint and the boot time. Rejected for local; kept for production.
- *Tempo + Mimir + Loki all-in-one image*: same as `otel-lgtm`. The Grafana image is the de-facto standard for this in 2026.

**Risk:** Local behavior diverges from production. Mitigation: the collector config is shared between local and production with environment-conditional exporters; the collector's `logging` exporter is enabled in local for diagnostics and disabled in production. The release-cadence CI runs the production-like collector config in the e2e test, not the local one.

### Decision D3.5 — Capability-gated cache (Redis/Valkey) admission

The platform exposes a `Cache` interface and a keyspace declaration scheme, but the platform module imports ZERO cache vendor SDKs. A service admits a cache client (`github.com/redis/go-redis/v9` or `github.com/valkey-io/valkey-glide/go`) only after authoring an ADR per `order-service/docs/adr/0004-optional-infrastructure.md`. The architecture test enforces the gate: any service that imports a cache vendor package without a corresponding ADR fails the build.

**Rationale:** This honors the platform's existing ADR-0004 discipline. Cache admission is a per-service decision driven by measured capability demand, not a platform-wide mandate. The platform provides the interface, the TTL bands, the keyspace conventions, and the observability hooks; the vendor SDK choice is a service-level ADR.

**Alternatives considered:**
- *Platform-wide Redis*: every service gets Redis whether they need it or not. Rejected for violating ADR-0004 and adding operational surface for no benefit.
- *No cache at all*: forces every read-mostly path through PostgreSQL. Rejected because the catalog service's 5-second quote cache and the notification dispatcher's per-channel rate limit both benefit measurably.
- *Use PostgreSQL as the cache (UNLOGGED tables + LISTEN/NOTIFY)*: viable but does not match the access pattern (atomic counters, sliding windows) and adds load to the authoritative store. Rejected for those workloads.

**Specific service-level admissions authorized by this design (each backed by a service ADR drafted as part of Phase 2):**
- `catalog-service` admits Redis for the 5-second price-quote cache. The cache is invalidated on price change via `SCAN MATCH catalog:quote:<product_id>:*` (never `KEYS`). The source of truth remains PostgreSQL; the cache is a cache-aside accelerator.
- `notification-service` admits Redis for the per-channel rate limiter (Lua / `INCR`+`EXPIRE NX` piped). The provider's native rate limiter is the primary defense; the cache is the secondary defense for cross-channel bursts.

No other Phase 2 service admits a cache. The order-service does not need one (its idempotency store is already PostgreSQL-backed).

**Risk:** Service ADRs are inconsistent in quality. Mitigation: the architecture test requires the ADR file to exist and to follow the five-point template from `0004-optional-infrastructure.md`; the architecture test does NOT validate the ADR's content (that remains a human review), but the existence check is mechanical.

### Decision D3.6 — Kafka retry topic chain (non-blocking retries)

Every consumer is wired with a retry-topic chain: `<source-topic>.retry.1000` (1s), `.retry.8000` (8s), `.retry.60000` (60s), `.retry.300000` (5m), `.retry.1800000` (30m), and `<source-topic>.dlq`. Each retry topic carries the same payload as the source plus a `retry-attempt` header. After the 30-minute retry exhausts, the record is published to the DLQ with `dlq-reason` and `dlq-diagnostics` headers.

**Rationale:** Non-blocking retries are the 2026 best practice (per Spring Kafka, Confluent, and the LinkedIn engineering blogs). Blocking retries on the consumer thread starve the partition; non-blocking retries let the consumer keep moving while a delayed-retry consumer (the platform's `RetryConsumer`) re-injects records back to the source topic on schedule. Exponential backoff with jitter (`±20%`) avoids thundering herd on shared downstream recoveries.

**Alternatives considered:**
- *In-process backoff*: simple but blocks the partition. Rejected.
- *Single retry topic with priority-based re-injection*: more complex than the chain pattern; no measurable benefit. Rejected.
- *Kafka Streams DLQ (KIP-1034)*: only applies to Kafka Streams pipelines, not vanilla KafkaConsumer. Tracked as future work but not adopted in Phase 2.

**Risk:** Retry topic proliferation doubles topic count. Mitigation: topics are auto-created by the platform's `infrastructure init` role with the documented partition count and replication factor; operators see the full list in `docs/topology.md`.

### Decision D3.7 — Temporal Worker Versioning v2

Every Temporal worker is configured with `worker.DeploymentOptions{DeploymentSeriesName=<service>-<worker>.vN, BuildID=<git SHA>}` (`worker.DeploymentOptions` is the SDK's public alias for the internal `WorkerDeploymentOptions`; both names refer to the same type). New workflow starts route to the deployment specified by the routing configuration; in-flight workflows continue on their original deployment until they complete or the routing rule changes.

**Rationale:** Worker Versioning v2 was **graduated to GA in Temporal Server 1.31.0 (2026-04-29)**, replacing the public-preview status it had through 1.30. The previous draft of this design said "1.30+", which was conservative but inaccurate; the platform pins Temporal Server **`v1.31.2` (released 2026-07-08)** in compose. Worker Versioning v2 eliminates the "in-flight workflow breaks because the worker was upgraded" failure mode that the old `GetVersion` pattern only patches. Build IDs derived from the git SHA make the worker-version-to-code mapping deterministic.

**Alternatives considered:**
- *No versioning*: harmless while only one worker deployment exists. Rejected because Phase 2 introduces peer-service workers; coordinated rollouts require versioning.
- *GetVersion patching*: the older pattern. Rejected because it is non-deterministic-friendly (workflow code carries a runtime conditional) and because Worker Versioning v2 supersedes it.
- *Namespace-per-service*: gives per-service versioning for free but multiplies namespaces. Rejected per Decision D6.

**Risk:** Workers that are not yet versioned are silently routed to the latest. Mitigation: the platform's `runtime.DeploymentVersion(...)` helper fail-fasts if the build ID is empty; CI rejects a build that does not set the build ID via `make verify-static`.

### Decision D3.8 — Deterministic-workflow enforcement via `workflowcheck`

The platform enforces deterministic-workflow code via the official
Temporal analyzer `go.temporal.io/sdk/contrib/tools/workflowcheck v0.5.0`
(2026-06-22). `workflowcheck` is a `go vet`-compatible static analyzer
that walks every workflow source file and rejects non-deterministic API
usage (`time.Now`, `time.Since`, `math/rand` global, `crypto/rand.Reader`,
`os.Stdin`/`Stdout`/`Stderr`, raw goroutines, channel `range`/`send`/`recv`,
map `range`). Workflow code MUST use the Temporal SDK's deterministic
helpers (`workflow.Now`, `workflow.Go`, `workflow.NewChannel`,
`workflow.SideEffect`).

> **Correction**: a previous draft of this design called the tool
> `workflowaudit`. There is no Temporal product by that name. The real
> tool is `workflowcheck`, and it is `go vet`-compatible.

The platform ships a per-service allowlist at
`platform/workflows/.workflowcheck.yaml` that EXTENDS the default
non-deterministic set with `os.Getenv`, `context.Background`,
`net.LookupHost`, and `os.Hostname` (so a workflow that calls any of
these fails the build). Workflow code that legitimately needs a
non-deterministic call SHALL add a `//workflowcheck:ignore` comment
above the line with a justification string; the comment is reviewed in
code review.

CI runs `go vet -vettool $(go tool workflowcheck) ./...` on every PR
that touches a `workflows/` directory, and the architecture test
`test/architecture/workflowcheck_passes_test.go` asserts the
`workflowcheck` tool is part of the `tool` directive in `go.mod`.

**Rationale:** The order-service MVP already declares this requirement in
`service-template/task-queue.md` but does not enforce it mechanically.
`workflowcheck` closes the gap; a workflow that calls `time.Now` would
silently produce a different timestamp on each replay, producing
non-deterministic replay errors that are notoriously hard to debug.

**Alternatives considered:**
- *Test-time replay only*: existing pattern, catches violations when the
  replay test runs against recorded history. Rejected because violations
  are caught late and only on workflows that have recorded history.
- *Hand-rolled analyzer*: the previous proposal floated a
  `workflowaudit` name; rejected because `workflowcheck` is shipped by
  Temporal itself, in the same monorepo as the Go SDK, and is already
  battle-tested against the SDK's own workflow code.
- *Manual code review*: insufficient at the platform's growth rate.
  Rejected.

**Risk:** False positives on legitimate uses (e.g., `time.Now` in a
helper function called from a workflow). Mitigation: the analyzer
accepts a `//workflowcheck:ignore` comment with a justification string;
the comment is reviewed in code review. False positives in Temporal's
own SDK (which the tool was designed to validate) are filed upstream.

### Decision D4 — Protobuf contracts via Buf, monorepo

All cross-service contracts live in `services/<name>/proto/` (per service) and in `platform/proto/` (shared envelopes). A top-level `buf.yaml` workspace ties them together. Breaking-change baselines are stored under `services/<name>/proto-baseline/<version>/` and are generated at archive time.

**Rationale:** Buf is the de-facto standard for Protobuf management in 2026 (replaces `protoc` workflows). Workspace mode allows each service to keep its own proto package while sharing lint and breaking rules. Per-service proto directories keep the ownership boundary clear.

**Alternatives considered:**
- *Single shared proto repo*: every service depends on one `contracts` repo. Rejected because it duplicates the cross-repo coupling we just decided against.
- *Code-generated Go types per service*: each service generates its own. Rejected because it splits the wire-format contract across multiple repos.

**Risk:** Buf workspace mode is newer and less battle-tested than `protoc`. Mitigation: the platform `Makefile.platform` template pins Buf to `v1.49.0` and runs `buf build` and `buf lint` on every PR.

### Decision D5 — One schema per service, sole-writer rule

Each service owns one PostgreSQL schema (`notification`, `customer`, `catalog`, `reporting`). No service writes to another service's schema. The Order Service's existing `order` schema is unchanged. The platform module exposes a `database.WithSchema(schemaName)` helper that every service uses; the architecture test fails any code path that writes to a foreign schema.

**Rationale:** The sole-writer rule is the foundation that lets services extract safely (per `docs/extraction.md`). Architecture tests enforce it mechanically.

**Alternatives considered:**
- *Database per service*: stronger isolation. Rejected because it doubles the operational footprint and most services share the same Postgres instance in compose. Database-per-service remains a Phase 3+ option for high-scale services.
- *Schema-per-aggregate*: too granular; complicates foreign-key reasoning.

**Risk:** A service's schema migration blocks another service's release if they share the database. Mitigation: every schema migration is forward-only and additive; the platform runs migrations as a one-shot role before the service starts; concurrent migrations are isolated per schema.

### Decision D6 — One Temporal namespace per environment, per-service task queues

The platform uses one Temporal namespace per environment (`prod`, `staging`, `dev`) shared by all services. Each service declares its own task queue (`order`, `notification`, `customer`, `catalog`, `reporting`) and worker identity.

**Rationale:** Per-namespace-per-service is too granular for the platform's current operational maturity. One namespace per environment is the standard pattern; per-service task queues give operational isolation without infrastructure sprawl.

**Alternatives considered:**
- *Namespace per service*: stronger isolation but multiplies the namespace count and the worker registration effort. Deferred to a Phase 3+ change if needed.
- *No Temporal at all*: rejected because the Customer service's GDPR purge needs durable scheduling, and the Order Service already uses Temporal.

**Risk:** A noisy neighbor on the Temporal cluster affects every service. Mitigation: each service's worker is rate-limited per task queue, and the Temporal namespace carries per-queue limits configured at deployment time.

### Decision D7 — Kafka topics, one per bounded context

Each service owns one main topic (`notification.events.v1`, `customer.events.v1`, `catalog.events.v1`) plus per-purpose sub-topics (`notification.dispatch.v1` for the outbox). Topic naming convention: `<domain>.<purpose>.v<n>`. The platform's `infrastructure init` role creates topics with the documented partition count and replication factor.

**Rationale:** One topic per bounded context keeps consumer group ownership clear and aligns with the platform's docs (`docs/ownership.md`). Per-purpose sub-topics isolate high-volume dispatch traffic from low-volume domain-event traffic.

**Alternatives considered:**
- *One topic for everything*: rejected; consumer offsets would be coupled and high-volume traffic would saturate low-volume consumers.
- *Per-aggregate topics*: rejected; too granular and complicates consumer reasoning.

**Risk:** Topic proliferation makes operations harder. Mitigation: a top-level `docs/topology.md` enumerates every topic, its owner, its consumer groups, and its retention policy. The `infrastructure init` role is the single source of truth for topic creation.

### Decision D8 — REST for synchronous peer calls; events for async

Cross-service synchronous calls (Order → Catalog for price quote, Order → Customer for reference) use REST with the OTel HTTP middleware. Cross-service asynchronous updates (Catalog → Order, Customer → Order, every domain event → Reporting) use Kafka. No service uses gRPC for peer calls in Phase 2.

**Rationale:** REST matches the existing order-service convention. gRPC would add a new technology without a Phase 2 win — there is no high-volume low-latency peer call that benefits from gRPC's streaming or schema. Every REST call uses OTel HTTP middleware so traces span peer boundaries.

**Alternatives considered:**
- *gRPC for peer calls*: stronger contracts, better streaming. Deferred to a Phase 3+ change if a high-volume call emerges.
- *Async-only via Kafka*: forces every synchronous UX path to be eventual. Rejected because Order needs the price quote before persisting the line item.

**Risk:** REST synchronous calls become a coupling point. Mitigation: every cross-service REST call has a configurable timeout (default 2 seconds), every call has a typed error so the caller surfaces a 503 to the user, and the OTel HTTP middleware records latency and error rate per peer.

### Decision D9 — Architecture tests live next to the code

Each service carries an `internal/architecture/` package with tests for domain purity (no infra imports in domain), sole-writer database rule, no peer-service internal imports, and dependency direction (adapters depend on ports; ports depend on domain). The order-service's existing tests are extracted to a `platform/architecture/` template that every service copies.

**Rationale:** Tests next to the code catch drift in the same PR. The platform's `architecture/` template ensures every service runs the same baseline set of tests, so a violation in one service cannot be silently allowed in another.

**Alternatives considered:**
- *Top-level architecture tests only*: easier to add but slower to fail. Rejected; per-service tests fail on the offending service's job, not the shared job.

**Risk:** Architecture tests can be bypassed by ignoring test failures. Mitigation: architecture tests run in `make verify-pr` and CI fails on any ignored failure; the order-service already follows this pattern.

### Decision D10 — Compose overlay pattern for environment-specific config

The Phase 2 Compose layout uses base `docker-compose.yaml` plus per-environment overlays (`docker-compose.tools.yaml`, `docker-compose.lgtm.yaml`). The base file declares the data plane (Postgres, Kafka, Debezium, Temporal); overlays add optional tooling and observability without modifying the base.

**Rationale:** Matches the existing `deploy/docker-compose.tools.yaml` overlay from the MVP. Local devs start the data plane; ops start the overlays as needed; CI starts everything for e2e tests.

**Alternatives considered:**
- *Single docker-compose.yaml*: simpler but forces every user to pull every image. Rejected.
- *Docker Compose profiles only*: viable but doesn't separate the data plane from tooling visually. Overlays are clearer.

**Risk:** Overlay drift (a service exists in the base but not in an overlay). Mitigation: a smoke test in CI applies each overlay in turn and asserts that the resulting container set has the expected total.

## Risks / Trade-offs

- **Risk:** Platform module API churn breaks multiple services in one PR. **Mitigation:** the platform module exposes only `pkg/` and keeps everything else `internal/`; the order-service is migrated to the new platform APIs in a single dedicated PR at the start of Phase 2a; subsequent platform PRs are gated on `make services-verify` for every dependent service.

- **Risk:** OTel Collector becomes a single point of failure in production. **Mitigation:** production deploys the collector as a DaemonSet (one per node); a load-balanced gateway collector aggregates for cross-node sampling. Local dev runs one collector container.

- **Risk:** New services share the same Postgres instance, so a runaway query in one service affects every service. **Mitigation:** per-service connection pools with bounded size; per-service statement timeouts; per-service `pg_stat_statements` tracking; the architecture test rejects cross-schema joins in domain code.

- **Risk:** Cross-service Kafka consumer lag emerges when one consumer is slow. **Mitigation:** every consumer exposes a `consumer_lag_seconds` metric and a `consumer_lag_threshold` alert; the `infrastructure init` role documents the per-topic retention policy; dead-letter topics carry messages that exceed retry limits.

- **Risk:** Secrets (SES keys, Twilio tokens) leak into logs or metrics. **Mitigation:** the platform's `redact.go` already declares the secret field names; the observability stack adds a final-pass redactor in the OTel Collector (in production) so even unredacted traces cannot escape.

- **Risk:** Late-arriving events produce inconsistent projections in the reporting service. **Mitigation:** reporting service treats every event idempotently; the projection row records the `last_event_id` and `last_event_offset`; the replay command allows deterministic re-application.

- **Risk:** Phase 2 takes longer than expected because the platform foundation is bigger than the MVP. **Mitigation:** Phase 2a (platform) is gated on a working `make verify-pr` for the platform module alone, before any service is built; Phase 2b–e land incrementally so each service ships against the same platform contract.

## Migration Plan

### Phase 2a — Platform foundation (no new services)

1. Create `platform/` Go module with `platform/observability`, `platform/contracts`, `platform/kafka`, `platform/health`, `platform/runtime`.
2. Migrate `order-service/internal/observability/` to `platform/observability/` and have `order-service` import `platform/observability`.
3. Add OTel SDK wiring in `order-service`; expose `/metrics` endpoint; propagate trace context across HTTP and Kafka.
4. Add `deploy/docker-compose.lgtm.yaml` overlay and the `otel-collector-config.yaml`.
5. Verify: order-service passes `make verify-pr` end-to-end and its OTel data lands in LGTM during a local run.

### Phase 2b — Notification service

1. Create `services/notification-service/` Go module.
2. Implement `notification-aggregate` and `notification-dispatcher` specs.
3. Define `notification.events.v1` and `notification.dispatch.v1` topics.
4. Wire SMTP provider behind `NotificationProvider` interface.
5. Verify: end-to-end test — an `OrderShipped` event from order-service triggers a notification email via SMTP.

### Phase 2c — Customer service

1. Create `services/customer-service/` Go module.
2. Implement `customer-profile` and `customer-gdpr-export` specs.
3. Define `customer.events.v1` topic.
4. Add `customer-migrate` and `customer-infrastructure-init` roles.
5. Verify: end-to-end test — create a customer via REST, GDPR export returns the JSON payload, GDPR purge after retention window erases the row.

### Phase 2d — Catalog service

1. Create `services/catalog-service/` Go module.
2. Implement `catalog-product` and `catalog-pricing-snapshot` specs.
3. Define `catalog.events.v1` topic.
4. Update `order-service` to call `GET /api/v1/products/{id}/quote` before persisting line items.
5. Verify: end-to-end test — create a product, set a price, create an order that captures the quote, change the price, confirm the order's price_snapshot_id still resolves.

### Phase 2e — Reporting service

1. Create `services/reporting-service/` Go module.
2. Implement `reporting-projection` spec.
3. Subscribe to all `*.events.v1` topics.
4. Add `report_daily_revenue` aggregation.
5. Verify: end-to-end test — create an order, confirm `report_orders` row appears within 5 seconds and `report_daily_revenue` aggregates correctly.

### Phase 2f — Cross-service verification

1. Run the release-cadence CI job against the Phase 2 image set (per `phase-1-follow-ups`).
2. Run the rollback rehearsal against a pinned prior Phase 1 image and the new schema.
3. Verify every service's OTel data lands in LGTM with the correct `service.name` resource attribute.
4. Confirm architecture tests pass for every service against the new platform contracts.

### Rollback

Per-service rollback follows the order-service pattern: forward-fix migrations, expand/contract for breaking changes, prior image remains compatible with the current schema for one release. Cross-service rollback requires dual-roll when a contract changes: if Customer v2 removes a field Order depends on, both services roll together. The release cadence (per `phase-1-follow-ups`) prevents two services cross-cutting within 24 hours. A regression in the platform module triggers a coordinated rollback of every dependent service to its last-known-good image; the platform module is versioned so the rollback target is a single tag.

## Open Questions

- **Q1: SMTP provider for local dev.** Should the local stack ship a `mailhog` (or equivalent) SMTP catcher for development? **Default answer:** yes, add `mailhog` to the base compose and route SMTP traffic there in local dev; production swaps to SES.
- **Q2: Catalog fixture data.** How much seed data should the catalog service ship with for local dev and e2e tests? **Default answer:** a small `catalog/seed.sql` (5 products, 3 categories) used by the local stack and by every service's integration tests.
- **Q3: Reporting freshness SLO.** The spec proposes 5 seconds; should this be tighter (e.g., 2 seconds) or looser? **Default answer:** 5 seconds is the right starting point; tighten in Phase 3 once we have operational data.
- **Q4: Cross-service tracing sample rate.** The OTel Collector defaults to 100% sampling; should we apply head-based sampling in production? **Default answer:** head-based 10% with tail-based preservation for errors and slow requests; tune after observing real traffic.
- **Q5: Notification provider fallbacks.** If SES is down, should notifications fall back to SMTP automatically? **Default answer:** no — fallbacks add operational complexity and obscure failures; instead, the retry policy backoff covers transient SES failures and the quarantine handles persistent failures. Open for Phase 3.