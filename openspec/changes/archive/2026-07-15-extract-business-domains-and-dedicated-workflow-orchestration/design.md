## Context

The microservices platform is in Phase 2 of its evolution. The `order-service` module today contains the `OrderFulfillmentWorkflow` (registered on Temporal task queue `order-fulfillment.v1`) and three sets of activities (`InventoryActivities`, `PaymentActivities`, `ShippingActivities`) that are implemented by `localFulfillmentActivities` — a single in-process struct that delegates to `commands.OrderService` (which routes to `commands.NewCreateOrderHandler`, `commands.NewConfirmPaymentHandler`, `commands.NewProcessOrderHandler`, `commands.NewShipOrderHandler`). The activities never cross a network boundary; the "saga" is a sequence of in-process method calls wrapped in Temporal's retry/timeout/saga envelope. This is correct for the current stage (zero network overhead, single deployment unit, atomic rollback) but it does not match the platform's published target architecture: each business domain SHALL be an independent Go service, each SHALL own its data, and cross-domain operations SHALL be real remote calls with explicit timeout/retry/circuit-breaker. The platform's `platform-hexagonal-enforcement` test reserves the `payment-service`, `inventory-service`, `shipping-service` package names precisely so that the order-service cannot import them — today, the order-service does not need to import them because the activities are in-process; once the activities become remote calls, the order-service will own typed client interfaces that import the extracted services' generated `contracts/` packages.

The platform's existing Temporal setup is mature for two services (`order-service`, `reporting-service`) and partially wired for three (`notification-service`, `customer-service`, `catalog-service`). The `notification-service` and `customer-service` workers are stubs that open a Temporal client but never register any workflow; the `catalog-service` has `PriceRollbackWorkflow` defined in `application/orchestration/price_rollback.go` but no `runWorker` entry point. The cross-service enrichment calls in the order-service's command pipeline (`commands.PeerEnricher` → `clients.NewCustomerClient`, `clients.NewCatalogClient`) are HTTP calls that work today and demonstrate the platform's OTel-instrumented HTTP client pattern. The pattern is the template for the new peer clients (`payment.Client`, `inventory.Client`, `shipping.Client`).

The Temporal task queue convention `<service>.<role>.vN` is already documented in `platform-temporal-versioning`; the new services extend the convention without breaking it. The Worker Versioning v2 model is already implemented in `platform/temporal/deployment.go` and adopted by the order and reporting workers; the new services adopt the same pattern. The saga compensation helper is in `platform/temporal/saga.go`; the `OrderFulfillmentWorkflow` saga today is a 4-step sequence (reserve inventory → capture payment → ship order → notify) with inverse-order compensation; the change preserves the saga structure but the forward and compensation activities call the extracted services' HTTP endpoints instead of in-process commands.

The cross-service smoke test at `tests/cross-service-smoke/` today exercises the order-service end-to-end; it will gain four contract tests (one per new service plus a full-orchestration test) following the same pattern as the existing `TestOrderE2E`.

## Goals / Non-Goals

**Goals:**

- Add three new Go service modules (`payment-service`, `inventory-service`, `shipping-service`) that follow the existing hexagonal layout, each with its own Postgres schema, its own REST API, its own CDC topic, and its own Temporal worker.
- Convert the `order-worker`'s `localFulfillmentActivities` to `remoteFulfillmentActivities` that call the three new services over HTTP via the platform's instrumented client; the saga compensation graph runs across the real network boundary with explicit per-peer circuit breakers.
- Wire the existing stub workers (`notification-service`, `customer-service`, `catalog-service`) so that all eight services in the platform have a working Temporal worker process that registers the workflow and activity set on its `<service>.<role>.vN` task queue.
- Add per-service `runWorker` entry points with a `WorkerDeploymentOptions` config block that mirrors the existing `platformtemporal.DefaultDeploymentOptions()` pattern; fail-fast on missing `BuildID`; expose a `/health/ready` probe that returns 503 until the worker is registered.
- Add per-service `docker-compose.<service>.yaml` overlays that include the new containers, the new init scripts for the new Postgres schemas and Kafka topics, and the new Temporal task queues in the worker env.
- Update `tests/cross-service-smoke/` to include a contract test for each new service and a full `TestOrderFulfillmentWithRemoteActivities` end-to-end test that runs the saga with all remote activities.
- Update `openspec/specs/platform-temporal-versioning` with a delta requirement that the per-service task queue convention extends to the three new services, and `openspec/specs/order-temporal-workflow` with a delta requirement that the activities call the remote clients.
- Add per-service ADRs at `services/<name>/docs/adr/0001-service-extraction.md` documenting the extraction rationale, the alternatives considered, and the data ownership boundary.

**Non-Goals:**

- Adopting Temporal's Nexus feature for cross-namespace workflow calls. The single namespace per environment is the correct default at the platform's current scale (per `platform-temporal-versioning`).
- Adopting `Temporal Schedule` for any of the new workflows. The new services follow the existing `WorkflowIDReusePolicy` and event-driven trigger pattern; `reporting-service` keeps the schedule-driven pattern.
- Converting the new services' activities to `Local Activities`. Per the Temporal best practices (specifically, "We recommend using regular Activities unless your use case requires very high throughput and large Activity fan-outs of very short-lived Activities"), remote calls to other services are exactly the case where regular Activities are required.
- Migrating the order-service's enrichment HTTP calls (`customer-api`, `catalog-api`) into Temporal activities. Those calls live in the application layer and work correctly; the new remote activities are a separate, additional concern (the saga steps that need Temporal's retry/timeout envelope).
- Replacing the existing `OrderFulfillmentWorkflow` saga with a chain of child workflows. The single-workflow saga is correct for the current complexity; child workflows are an anti-pattern for "code organization" per the Temporal SaaTEM guide ("Do not use Child Workflows to organize code — use standard features of your programming language").
- Building a generic "Temporal worker factory" that all services use. Each service owns its `runWorker` because the activity set is service-specific; the platform helper `temporal.NewWorker(...)` is the common foundation, but the registration step is per-service.
- Building a "workflow service" module that hosts workers for multiple business domains. The user has explicitly chosen the "worker in business service" model, which means each Go service module owns its own worker process.
- Adding observability instrumentation beyond what already exists. The platform's OTel layer (`platform-observability`) is the single source; the new services follow the existing instrumentation pattern.
- Adopting gRPC between services. REST/HTTP via the platform's instrumented client is the established pattern; gRPC is a future optimization for high-throughput internal calls.

## Decisions

### Decision 1: Worker in business service module, not a shared workflow service

**Choice**: Each service that runs a Temporal worker has the worker code in its own Go module (`services/<name>/cmd/<name>-service/run.go` `runWorker`). The worker is NOT in a shared `services/workflow-orchestrator/` module. The worker container is a separate container from the API and orchestrator roles.

**Why**: The user explicitly chose the "worker in business service" model. This matches the Temporal reference app pattern (where each microservice has its own worker process on its own task queue) and the [Temporal best practices guide](https://docs.temporal.io/best-practices/worker) which states that "Workers should be treated as long-running, independently scalable services." A shared workflow service would couple unrelated business domains (e.g., a payment regression would require deploying the workflow service even if the payment API didn't change).

**Alternatives considered**:

- **Shared workflow service hosting all workers** — rejected. Couples unrelated business domains; increases blast radius for a single service change; contradicts the platform's per-service scaling and ownership model.
- **Single Temporal worker per service module but bundled in the same container as the API** — rejected. The API's HTTP request handling and the worker's long-running task polling have different resource profiles; bundling them prevents independent scaling and increases the risk of worker poller starvation under API load.

### Decision 2: Activities are remote HTTP calls, not Local Activities

**Choice**: The `OrderFulfillmentWorkflow` activities (`ReserveInventory`, `CapturePayment`, `DispatchShipping`, `NotifyCustomer`) call the extracted services over HTTP via the platform's instrumented client. They are NOT Local Activities. The activity inputs/outputs are wire DTOs from a shared `contracts/` package.

**Why**: Per the [Temporal cost optimization guide](https://docs.temporal.io/best-practices/cost-optimization) and the SaaTEM Design Patterns guide, Local Activities "should not run for more than a few seconds, inclusive of retries" and "you lose the ability to rate limit & route tasks to workers." A payment capture can take seconds-to-minutes (especially with 3DS); an inventory reservation can block on external systems; a shipping dispatch can take longer. Regular Activities give the saga the per-step retry control and timeout enforcement that the local stubs lack.

**Alternatives considered**:

- **Local Activities calling in-process commands** — rejected. This is the current pattern, and it does not provide cross-service isolation, independent retry, or independent failure detection.
- **Child workflows in the extracted services** — rejected. The activities are simple request/response; a child workflow is overkill and adds event history bloat. Per the SaaTEM guide, "When in doubt, use an Activity."

### Decision 3: Shared `contracts/` package, not independent protobuf projects

**Choice**: The new services each publish a `services/<name>/contracts/` directory containing the protobuf definitions (`.proto` files) AND the generated Go code. The order-service's HTTP clients import the generated Go code from these directories. The `buf.yaml` at the repo root manages the build.

**Why**: A single source of truth for the wire types prevents drift between producer and consumer. The `buf` CLI is the canonical tool for protobuf management in this monorepo (per the existing `contracts/` usage in order-service). Each new service owns its contract because the contract is part of its API surface.

**Alternatives considered**:

- **Independent protobuf projects per service with their own buf modules** — rejected. Adds operational overhead (each service must publish its contract); increases the risk of incompatible versions; the monorepo already has a single `buf.yaml`.
- **Inline Go structs (no protobuf)** — rejected. Protobuf is the canonical contract type in this platform; REST is the wire protocol but the types are defined as protobuf and the platform generates Go from them.

### Decision 4: Per-peer circuit breaker on the order-service HTTP clients

**Choice**: The order-service's `payment.Client`, `inventory.Client`, `shipping.Client` each apply a `sony/gobreaker` circuit breaker with `MaxRequests=1`, `Interval=30s`, `Timeout=5s` (open state duration), and `ReadyToTrip` returning true after 5 consecutive failures. The platform's instrumented HTTP client is wrapped with the circuit breaker.

**Why**: Cross-service calls can fail in cascades. A 5-second open state prevents a slow peer from saturating the order-worker's connection pool; a 30-second probe interval matches the platform's existing `PeerConfig.Timeout` default. The `sony/gobreaker` library is small, well-maintained (4.2k★), and already a transitive dependency of `platform/http`.

**Alternatives considered**:

- **No circuit breaker; let Temporal retry** — rejected. Temporal's retry is per-activity, not per-call within an activity. A single slow payment capture could exhaust the activity's `StartToCloseTimeout` and trigger workflow-level compensation, but a circuit breaker stops the call early so the activity can return a typed error and the workflow can take a fast compensation path.
- **Polly-style retry policies with exponential backoff** — rejected. Temporal's retry is already the outer retry loop; an inner retry layer would double-count and cause subtle timing bugs.
- **Service mesh (Istio/Linkerd) for circuit breaking** — rejected. The local dev environment is docker-compose; a service mesh is not deployed locally. The circuit breaker in the client is the portable path.

### Decision 5: One Temporal task queue per service, not a shared "domain" task queue

**Choice**: Each service has its own task queue. The order-worker's activities DO NOT use the extracted services' task queues; the activities call the extracted services' HTTP APIs (the cross-service call is the work, not the Temporal task). The full set of task queues is:

| Service | Task Queue | Source |
|---|---|---|
| `order-service` | `order-fulfillment.v1` | `services/order-service/internal/adapters/temporal/constants.go::OrderFulfillmentTaskQueueV1` |
| `payment-service` (new) | `payment.capture.v1` | (proposed) |
| `inventory-service` (new) | `inventory.reservation.v1` | (proposed) |
| `shipping-service` (new) | `shipping.dispatch.v1` | (proposed) |
| `notification-service` | `notification.dispatch.v1` | `services/notification-service/application/orchestration/workflow.go::DispatchTaskQueue` |
| `customer-service` (purge) | `customer.purge.v1` | `services/customer-service/application/orchestration/workflow.go::TaskQueuePurge` |
| `customer-service` (export) | `customer.gdpr.v1` | `services/customer-service/application/orchestration/workflow.go::TaskQueueExport` |
| `reporting-service` | `reporting.admin.v1` | `services/reporting-service/internal/runtime/config.go::TemporalTaskQueue` |
| `catalog-service` | `catalog.admin.v1` | `services/catalog-service/internal/application/orchestration/price_rollback.go::TaskQueue` |

Note the inconsistency in the existing codebase: the order-service uses dashes (`order-fulfillment.v1`) while the peer services use dots (`notification.dispatch.v1`, `customer.purge.v1`, etc.). The new services SHALL adopt the dotted form (`payment.capture.v1`, `inventory.reservation.v1`, `shipping.dispatch.v1`) per the peer-services convention.

**Why**: Per the Temporal best practices, "Use separate Task Queues for distinct workloads. This isolation allows you to control rate limiting, prioritize certain workloads, and prevent one workload from starving another." Each service's task queue is sized and scaled independently. The order-worker's activities are work, not task-queue routing; the HTTP call IS the work.

**Alternatives considered**:

- **Single shared task queue for all workflow types** — rejected. Per the [community guidance](https://community.temporal.io/t/best-practices-recommendations-for-orchestrating-microservices-with-temporal/751), "All workers that listen on a given task queue have to support all activity types dispatched to that queue." A shared queue would force every worker to register every activity type, which is exactly the coupling the per-service queues avoid.
- **Per-workflow task queue (one queue per workflow type)** — rejected. Too granular. The platform's per-service task queue is the right granularity because the worker is the unit of scaling.

### Decision 6: Per-service schema isolation, not shared cross-domain tables

**Choice**: The three new services each own a dedicated Postgres schema (`payment`, `inventory`, `shipping`). The cross-service smoke test connects to the `platform` database with each service's schema. The order-service's `orders` schema is unchanged. The `platform-hexagonal-enforcement` test in the order-service is extended to assert that no order-service code imports the new services' internal packages.

**Why**: Database-per-service is the canonical microservices pattern. Each service is the sole writer for its schema; the cross-service read is via HTTP, not via shared tables. This prevents accidental coupling at the data layer.

**Alternatives considered**:

- **Shared `platform` schema with table prefixes** — rejected. The platform's `TestDatabaseTablesOwnedBySingleService` test already enforces the per-service schema boundary for the order-service; the new services follow the same pattern.
- **Database per service (separate Postgres instances)** — rejected. The local dev environment is a single Postgres container; per-service databases would require a per-service Postgres in compose, which is operational overhead for the local case. The per-service-schema pattern is the right middle ground.

### Decision 7: CDC outbox pattern, not dual-write to Kafka

**Choice**: Each new service commits aggregate changes and outbox events in a single Postgres transaction. Debezium reads the outbox and publishes to Kafka. The pattern matches the existing `01-orders-cdc.sql` and `02-notifications-cdc.sql` pattern.

**Why**: Atomic outbox is the only safe pattern for cross-system state changes; dual-write can lose events on a crash between the Postgres commit and the Kafka publish. The platform's CDC init scripts are the established pattern.

**Alternatives considered**:

- **Direct Kafka publish from the API handler** — rejected. Loses events on crash; not atomic with the Postgres commit.
- **Listen-to-self on the service's own events to start the worker** — rejected. The worker is triggered by the order-orchestrator's `ExecuteWorkflow` call, not by self-listening; the orchestrator is the entry point for the workflow lifecycle.

### Decision 8: `runWorker` per service, not a generic worker factory

**Choice**: Each service has its own `cmd/<service>/run.go` `runWorker` function. The function opens a Temporal client, configures `WorkerDeploymentOptions` with the service's `DeploymentSeriesName` and a `BuildID` from `platformtemporal.DeploymentVersion()` (which reads `PLATFORM_DEPLOYMENT_VERSION` or falls back to `GIT_SHA`, or `"dev"`), registers the workflow and activity set on the service's task queue, starts the worker with the platform's `temporal.NewWorker(...)` helper, and exposes a `/health/ready` probe.

**Why**: The activity set is service-specific. A generic factory would require each service to register its activities through a registration callback, which is just indirection. The platform helper is the common foundation; the registration step is per-service code that lives next to the service's domain logic.

**Alternatives considered**:

- **Generic `platform/temporal/worker.go` factory** — rejected. The factory would need to know about each service's activity types, which would couple the platform module to the services. The existing `platform/temporal/worker.go` provides the foundation (`NewWorker`); the registration is per-service.
- **Worker auto-discovery via reflection** — rejected. Adds complexity for no benefit; explicit registration is what Temporal's own reference apps do.

### Decision 9: Hard rollback boundary, not soft rollback

**Choice**: The change is rolled back as a single unit (revert the PR). Partial rollout failure uses an env-var-based fallback (set `ORDER_PAYMENT_URL=` etc. to disable the remote activity and fall back to the in-process stub). The fallback path is preserved by keeping the `localFulfillmentActivities` adapter code in a `_old.go` file that is removed only when the change is fully validated.

**Why**: A hard rollback boundary is the simplest model for a large change that touches many files. The env-var-based fallback provides a soft-rollback path for partial rollout. The `localFulfillmentActivities` code is kept in a deprecated file so a revert can quickly restore the previous behavior.

**Alternatives considered**:

- **Per-phase rollback (revert one phase at a time)** — rejected. The phases have dependencies (Phase 3 depends on Phase 1's schemas and Phase 2's APIs). A per-phase rollback would require carefully un-doing those dependencies, which is more error-prone than a single change-level revert.
- **Feature flag for the remote activity** — considered, not adopted. The flag would add operational complexity and the env-var-based fallback is sufficient for the soft-rollback case.

### Decision 10: Test the saga with the real remote services, not mocks

**Choice**: The cross-service smoke test `TestOrderFulfillmentWithRemoteActivities` runs the full `OrderFulfillmentWorkflow` against the real `payment-service`, `inventory-service`, `shipping-service` HTTP APIs (started in the smoke stack). The test does NOT use mocks.

**Why**: The whole point of the extraction is to test the real cross-service behavior (timeouts, retries, circuit breakers, saga compensation). A mock-based test would only verify the order-worker's logic, not the integration. The smoke test already has the pattern (it starts the order-service in-process; the new services can be added the same way).

**Alternatives considered**:

- **Mock-based unit tests + a small integration test** — rejected. The integration test would still need to be a smoke test (since the services need to be running). Having only the smoke test is simpler and exercises the real path.
- **Testcontainers for the new services in unit tests** — considered, not adopted. The smoke test already has the infrastructure; adding testcontainers would duplicate the setup.

## Risks / Trade-offs

- **[R1] Saga compensation runs across the real network boundary** — if the network is partitioned mid-saga, the forward activity may have committed but the compensation cannot reach the peer. → **Mitigation**: each compensation activity has its own `StartToCloseTimeout` (30s) and `ScheduleToCloseTimeout` (5m); if compensation fails, the workflow records a `CompensationFailureV1` event and the saga is marked for human intervention. The `platform-temporal-versioning` spec already requires this.
- **[R2] Three new services mean three new deployment units, three new failure modes, three new health checks** — operational overhead increases. → **Mitigation**: each new service follows the existing `cmd/<service>/run.go` pattern with `api/worker/migrate/orchestrator/infrastructure/healthcheck` roles; the docker-compose overlay adds the new containers; the smoke test adds the contract tests. The `make help` target is extended with three new build targets.
- **[R3] The cross-service HTTP call adds 1–50ms latency to the saga** — the in-process stub had ~0ms overhead. → **Mitigation**: the platform's instrumented HTTP client is connection-pooled; the per-peer timeout is configurable; the saga's `ScheduleToCloseTimeout` (5m default) is far longer than the per-call latency. A 50ms overhead is acceptable for a saga that takes seconds-to-minutes.
- **[R4] The order-service's saga depends on all three new services being up** — if any of the new services is down, the saga cannot start. → **Mitigation**: each activity has a circuit breaker; if the peer is down, the activity returns a typed `NonRetryableApplicationError` and the saga compensation runs immediately. The activity does not block on a down peer.
- **[R5] The order-service's `localFulfillmentActivities` is renamed to `remoteFulfillmentActivities`** — any code that imports the old type fails to compile. → **Mitigation**: the change updates all call sites in the same PR; the `localFulfillmentActivities` is preserved in `worker_activities_old.go` as a deprecated file for the soft-rollback case; the rename is documented in the order-service's CHANGELOG.
- **[R6] The new services' Temporal workers require the Temporal server to be up before the services start** — the docker-compose `depends_on` clause must include the Temporal health check. → **Mitigation**: the `docker-compose.<service>.yaml` overlays add `temporal: condition: service_healthy` to each worker container's `depends_on` block; the existing pattern is followed.
- **[R7] The three new services' CDC topics (`payments.events.v1`, `inventory.events.v1`, `shipping.events.v1`) must be created before the services start** — Kafka's `auto.create.topics.enable` is true in local dev but false in production. → **Mitigation**: the `*-topics-init` containers run a `kafka-topics.sh` script before the service starts; the production deploy scripts follow the same pattern.
- **[R8] The `sony/gobreaker` library is a new dependency** — adds to the order-service's `go.mod`. → **Mitigation**: the library is well-maintained (4.2k★), small, and has no transitive dependencies; pinned exactly to `v1.0.0` (verified on 2026-07-15). The library is also already a transitive dep of `platform/http`.
- **[R9] The cross-service smoke test takes longer to run** — three new contract tests plus the full orchestration test. → **Mitigation**: the tests run in parallel where possible (each contract test is independent); the full orchestration test reuses the contract test setup; the `make test-e2e` timeout is extended from 30m to 45m.
- **[R10] The change touches 11 files for the order-service alone** — large diff, hard to review. → **Mitigation**: the change is split into 5 phases per the proposal's rollout approach; each phase is a separate commit; the change-level review covers the overall design, the phase-level review covers the implementation.
- **[R11] The three new services each have their own `Dockerfile` and docker-compose overlay** — operational overhead. → **Mitigation**: the `Dockerfile` is generated by a shared template; the compose overlay follows the existing pattern; the Makefile target is the single entry point.
- **[R12] The order-service's `cmd/order-service/roles.go` `runWorker` is the largest file in the change** — 80+ lines of new wiring. → **Mitigation**: the wiring is split into a new `remote_activities.go` file (the activities impl) and a `peer_clients.go` file (the client constructors); `roles.go` is the composition root and is updated to wire them.
- **[R13] The new services' activity inputs/outputs are protobuf-generated** — the order-service must use the generated Go types, not its own structs. → **Mitigation**: the order-service's `clients/` package wraps the generated types with a thin facade; the saga activities see the facade, not the protobuf types directly; this keeps the workflow code clean.
- **[R14] The `localFulfillmentActivities` removal is a breaking change** — any test that imports the old type fails. → **Mitigation**: the order-service's unit tests for the saga are updated to use a mock `remoteFulfillmentActivities`; the test fixture for the saga's replay test is regenerated.
- **[R15] The `platform-temporal-versioning` spec is modified by this change** — the delta requirement must be merged into the canonical spec at archive time. → **Mitigation**: the `openspec archive` command handles the delta merge; the canonical spec is updated as part of Phase 5.

## Migration Plan

The migration is a 5-phase rollout, each phase with its own feature flag and its own rollback boundary. The phases are sequential; each phase is a separate PR.

**Day 0 (this OpenSpec change)**: Author the change in OpenSpec (proposal + design + 7 specs + 4 deltas + tasks), merge with `openspec validate --strict --all` green.

**Phase 1 (Day 1–3) — Schema and migrations**: Author the three new SQL schemas, the Debezium publications, the CDC connector configs, the outbox tables. Run migrations against the local Postgres; verify CDC events flow to `payments.events.v1` etc. via the existing `01-orders-cdc.sql` and `02-notifications-cdc.sql` pattern. **Rollback**: drop the new schemas (preserved on the change-level revert for soft rollback).

**Phase 2 (Day 4–7) — Service skeletons**: Author the three new Go service modules with the `runApi` role only. No Temporal worker yet; the API exists and serves the same set of HTTP endpoints that the order-worker will call. Verify with `curl` against the new service ports. **Rollback**: remove the new docker-compose overlays; the order-service continues to use the in-process stubs.

**Phase 3 (Day 8–12) — Worker extraction**: Author `runWorker` for each new service, register the activity on the per-service task queue, convert the order-worker's `localFulfillmentActivities` to `remoteFulfillmentActivities`. The `MakePeerEnricher`-style wiring in `cmd/order-service/roles.go` is replaced with `MakePaymentClient`, `MakeInventoryClient`, `MakeShippingClient`. Verify by running the full `OrderFulfillmentWorkflow` against the three real remote services; verify saga compensation runs across the network. **Soft rollback**: set `ORDER_PAYMENT_URL=` etc. to disable the remote activity and fall back to the in-process stub.

**Phase 4 (Day 13–15) — Stub worker wiring**: Complete the unwired stub workers (notification, customer, catalog). `notification-worker` registers `NotificationFulfillmentWorkflow` + `DispatchActivity`; `customer-worker` registers `CustomerPurgeWorkflow` + `CustomerGDPRExportWorkflow` + activities; `customer-orchestrator` subscribes to `customers.events.v1`; `catalog-worker` registers `PriceRollbackWorkflow` + `RollbackActivity`. Verify each with a smoke test that starts the workflow via the orchestrator and asserts the worker completes it. **Rollback**: remove the worker container from the docker-compose overlay.

**Phase 5 (Day 16–18) — Cross-service smoke + archive**: Extend `tests/cross-service-smoke/` with the four new contract tests; run `make test-e2e-up` end-to-end; archive the change via `openspec archive --change extract-business-domains-and-dedicated-workflow-orchestration --yes`. The canonical `openspec/specs/` is updated with the new capabilities; the deltas are merged into the existing specs. **Rollback**: revert the archive; the change remains in `openspec/changes/`.

**Full rollback**: revert the single change PR. The three new Go modules are removed, the order-service's `remote_activities.go` is replaced by `worker_activities.go`, the `docker-compose.<service>.yaml` overlays are removed, the CDC init scripts are removed. A single `git revert` returns the repo to its pre-change state. The order-worker's in-process stubs come back; the saga compensation graph still runs but inside the order service's process.

**No data migration on rollback**. The three new Postgres schemas are NOT dropped on rollback; they are preserved so the new services can be re-enabled without re-running migrations. The Debezium publications are not removed; the Kafka topics are not deleted. Only the Go service code and the docker-compose wiring are reverted.

## Open Questions

- **Q1. Should the new services adopt `Temporal Schedule` for any of their workflows?** — `payment-service` could schedule a daily reconciliation workflow; `inventory-service` could schedule a low-stock alert workflow; `shipping-service` could schedule a daily carrier status sync. The existing `reporting-service` uses Temporal Schedule for the daily revenue rollup. Decision deferred to a follow-up change; the current change does not add schedules.
- **Q2. Should the new services publish protobuf contracts to a separate Go module (e.g., `platform/contracts/`) instead of `services/<name>/contracts/`?** — the current design has the contract live with the service that owns the API. An alternative is a central `platform/contracts/` module that all services import. The monorepo's existing `services/order-service/contracts/` pattern argues for per-service contracts; the cross-service smoke test would still need a per-service import. Decision: per-service contracts (current design).
- **Q3. Should the order-service's HTTP client use a generic `platform/http/peer` helper that wraps `sony/gobreaker`?** — the current design wraps `sony/gobreaker` per-client. A generic helper would reduce code duplication but require the platform module to know about the peer types. Decision deferred to a follow-up; the current change has per-client wrappers.
- **Q4. Should the new services' Temporal workers be deployed in Kubernetes with the `temporal-worker-controller` for autoscaling?** — the `temporal-worker-controller` is the recommended Kubernetes pattern per the Temporal best practices. The current local-dev environment is docker-compose, so the controller is not used. Decision deferred to the production-deploy change.
- **Q5. Should the cross-service smoke test use Temporal's `testsuite` package or run against a real Temporal server?** — the current smoke test uses the real Temporal server (started in compose). The `testsuite` package is for unit tests. The current change uses the real server for integration coverage.
- **Q6. Should the order-service's saga call the extracted services' REST APIs or the Temporal worker APIs (i.e., start a child workflow in the extracted service)?** — the current design uses REST APIs (remote activities). The alternative is child workflows. The current design is simpler and matches the Temporal best practice ("When in doubt, use an Activity"). Decision: REST APIs.
- **Q7. Should the new services' CDC topics include all outbox events or only a subset?** — the current design publishes every outbox event to the topic. The alternative is a curated subset (e.g., only `OrderCompleted` events for `payments.events.v1`). The current design follows the existing `01-orders-cdc.sql` pattern.
- **Q8. Should the new services have a separate `Makefile` target per service or a single combined target?** — the current design has three new build targets (`payment-build`, `inventory-build`, `shipping-build`) and a single combined `make build-all-services`. The combined target is the entry point for the production deploy.
