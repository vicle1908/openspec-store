## Why

The microservices platform is moving from a single `order-service` that holds payment, inventory, shipping, and notification flows as in-process `localFulfillmentActivities` stubs to a true dedicated-workflow-orchestration model where each business domain (`order`, `payment`, `inventory`, `shipping`, `notification`, `customer`, `reporting`, `catalog`) is an independent Go service with its own Temporal worker placed in the business service module. Today the platform's order worker hard-codes the inventory/payment/shipping activities to in-process command handlers — the activity never crosses a network boundary, so the "Temporal worker per service" pattern is correct in spirit but the activities are not real cross-service calls. The cross-service enrichment (customer, catalog) does go over HTTP, but those calls live in the application layer, not inside Temporal activities, so retries, timeouts, and saga compensation are split across two execution models. This change extracts `payment-service`, `inventory-service`, and `shipping-service` as first-class Go modules in the monorepo, re-homes the `notification-service` and `customer-service` worker registrations that today ship as stubs, wires `catalog-service`'s `PriceRollbackWorkflow` worker, and converts the order-worker's activities from in-process stubs to typed remote calls against the extracted services via the platform's OTel-instrumented HTTP client. The result: every business domain owns its Temporal worker (worker placed in the business service module, not in a shared workflow service), every cross-domain step is a real remote activity with explicit timeout/retry/circuit-breaker, the saga compensation graph runs across the real service boundary, and the `platform-temporal-versioning` requirement for "every Temporal worker SHALL adopt Worker Versioning v2" becomes true for all eight workers (today only the order and reporting workers register workflows).

The current `OrderFulfillmentWorkflow` saga is a 4-step sequence: `ValidateInventory` → `ProcessPayment` → `ReserveInventory` → `MarkOrderShipped`. Compensations are `RefundPayment` (for `ProcessPayment`) and `ReleaseInventory` (for `ReserveInventory`); `ValidateInventory` and `MarkOrderShipped` have no compensation in the current saga. This change preserves the saga structure but the forward and compensation activities call the extracted services' HTTP endpoints instead of in-process commands.

## What Changes

- Add **three new Go service modules** in `services/`: `payment-service`, `inventory-service`, `shipping-service`. Each follows the existing `services/<name>/` Go module layout (domain/application/ports/adapters), each ships its own Postgres schema (`payment`, `inventory`, `shipping`) and CDC outbox topic (`payments.events.v1`, `inventory.events.v1`, `shipping.events.v1`), each exposes a REST HTTP API on a unique port, and each has its own Temporal worker that registers the activities it owns.
- **Convert `order-worker` activities from in-process stubs to remote calls.** The `localFulfillmentActivities` type in `services/order-service/cmd/order-service/worker_activities.go` is replaced by `remoteFulfillmentActivities` that holds typed clients (`payment.Client`, `inventory.Client`, `shipping.Client`) — each client uses the platform's OTel-instrumented `platform/http` HTTP client, applies a per-peer circuit breaker, and is wired in `cmd/order-service/roles.go` `runWorker()`.
- **Wire the existing stub workers**: `notification-service` worker registers `NotificationFulfillmentWorkflow` + `DispatchActivity`; `customer-service` worker registers `CustomerPurgeWorkflow` + `CustomerGDPRExportWorkflow` + their activities; `customer-service` orchestrator subscribes to `customers.events.v1` and starts workflows; `catalog-service` worker registers `PriceRollbackWorkflow` + activity.
- Add **one Temporal task queue per service** following the existing convention. The new services SHALL adopt the dotted form matching the peer services: `payment.capture.v1`, `inventory.reservation.v1`, `shipping.dispatch.v1`. The existing services already use: `order-fulfillment.v1` (order-service, dashed form), `notification.dispatch.v1`, `customer.purge.v1`, `customer.gdpr.v1`, `reporting.admin.v1`, `catalog.admin.v1`. The `platform-temporal-versioning` spec already requires `<service>.<role>.vN`; the only delta is extending the requirement to include the three new services.
- Add **per-service `cmd/<service>/run.go` worker entrypoint** that opens a Temporal client, configures `WorkerDeploymentOptions` with the service's `DeploymentSeriesName` and a non-empty `BuildID`, registers the workflow and activity set on the service's task queue, and starts the worker with the platform's `temporal.NewWorker(...)` helper.
- Add **per-service `deploy/docker-compose.<service>.yaml` overlay** that adds the new service's role containers (api + worker; orchestrator only if the service is triggered by Kafka, not API), the new Postgres schema in `deploy/init-scripts/`, the new Kafka topic in the topics-init script, and the new Temporal task queue in the worker env.
- Update **`cross-service smoke test`** to include a contract test for each new service: `TestPaymentContract` (create payment intent → capture → assert events on `payments.events.v1`), `TestInventoryContract` (reserve → confirm → assert events), `TestShippingContract` (dispatch → complete → assert events), and `TestOrderFulfillmentWithRemoteActivities` (full saga with all four remote activities).
- Update **`openspec/specs/order-temporal-workflow`** with a delta requirement: the `OrderFulfillmentWorkflow` activities SHALL call `payment.Client.Capture`, `inventory.Client.Reserve`, `shipping.Client.Dispatch` over HTTP via the platform's instrumented client (NOT in-process command handlers). The saga compensation graph is unchanged but the compensation activities call the same remote clients with the inverse operation (`Refund`, `Release`, `Cancel`).
- **BREAKING**: `services/order-service/cmd/order-service/worker_activities.go` is renamed to `remote_activities.go` and its public types change from `localFulfillmentActivities` to `remoteFulfillmentActivities`. The activities registration struct in `cmd/order-service/roles.go` now holds three client interfaces instead of three local interfaces.
- **BREAKING**: the `services/order-service/internal/adapters/temporal/activities.go` interface types (`InventoryActivities`, `PaymentActivities`, `ShippingActivities`) gain a `Remote` suffix; the `localFulfillmentActivities` adapter is removed.

## Capabilities

### New Capabilities

- `payment-service`: A dedicated Go service in `services/payment-service/` that owns the `payment` Postgres schema, exposes `POST /api/v1/payments/intents`, `POST /api/v1/payments/{id}/capture`, `POST /api/v1/payments/{id}/refund`; emits `payments.events.v1` from its outbox; runs a Temporal worker on task queue `payment.capture.v1` that registers `PaymentCaptureActivity`, `PaymentRefundActivity`; uses idempotency keys derived from the order ID; rejects duplicate captures with `409 Conflict`.
- `inventory-service`: A dedicated Go service in `services/inventory-service/` that owns the `inventory` Postgres schema, exposes `POST /api/v1/inventory/reservations`, `POST /api/v1/inventory/reservations/{id}/release`, `POST /api/v1/inventory/reservations/{id}/confirm`; emits `inventory.events.v1` from its outbox; runs a Temporal worker on task queue `inventory.reservation.v1` that registers `InventoryReserveActivity`, `InventoryReleaseActivity`, `InventoryConfirmActivity`; uses optimistic concurrency on `inventory_levels.available_quantity`.
- `shipping-service`: A dedicated Go service in `services/shipping-service/` that owns the `shipping` Postgres schema, exposes `POST /api/v1/shipments`, `POST /api/v1/shipments/{id}/cancel`, `POST /api/v1/shipments/{id}/complete`; emits `shipping.events.v1` from its outbox; runs a Temporal worker on task queue `shipping.dispatch.v1` that registers `ShippingDispatchActivity`, `ShippingCancelActivity`; tracks carrier integration behind a `ShippingProvider` port.
- `order-remote-activities`: The `order-service` Temporal worker SHALL hold typed remote client interfaces (`payment.Client`, `inventory.Client`, `shipping.Client`) wired with the platform's OTel-instrumented HTTP client; the `OrderFulfillmentWorkflow` activities SHALL call these clients; the saga compensation activities SHALL call the inverse operations on the same clients; every remote call SHALL apply a per-peer circuit breaker with a 5-second open state and a 30-second half-open probe.
- `cross-service-workflow-contracts`: A shared `contracts/` package SHALL define the wire DTOs (`PaymentCaptureRequest`, `PaymentCaptureResponse`, `InventoryReservationRequest`, `InventoryReservationResponse`, `ShipmentDispatchRequest`, `ShipmentDispatchResponse`) and the protobuf message types; both producer (extracted service) and consumer (order-worker activity) SHALL import the same generated code so a contract change is a single PR.
- `per-service-temporal-registration`: Every service that runs a Temporal worker SHALL have a `cmd/<service>/run.go` `runWorker` role that (a) reads its `WorkerDeploymentOptions` from env, (b) fails fast if `BuildID` is empty, (c) registers the workflow and activity set on `<service>.<role>.vN` task queue, (d) starts the worker with the platform's `temporal.NewWorker(...)` helper, and (e) exposes a `/health/ready` probe that returns 503 until the worker is registered.
- `worker-placement-policy`: A platform-wide rule that the Temporal worker for a service SHALL live in the same Go module as the service's business logic; the worker SHALL NOT live in a shared "workflow service" module; the worker SHALL be deployed as a separate container from the API and orchestrator roles so the API and worker scale independently; the worker container SHALL share the service's Postgres pool with the API role (via the same `DATABASE_URL`) and SHALL NOT have a separate database.

### Modified Capabilities

- `platform-temporal-versioning`: delta requirement — the per-service task queue convention `<service>.<role>.vN` now covers `payment.capture.v1`, `inventory.reservation.v1`, `shipping.dispatch.v1` in addition to the existing queues; the `Worker Versioning v2` adoption requirement is extended to require that every worker in every service register a non-empty `BuildID` and a service-specific `DeploymentSeriesName`.
- `platform-extensibility`: delta requirement — the three new services (payment, inventory, shipping) are first-class platform capabilities and SHALL each have an ADR at `services/<name>/docs/adr/0001-service-extraction.md` documenting the extraction rationale, the alternatives considered, and the data ownership boundary.
- `platform-verification`: delta requirement — the cross-service smoke test SHALL add a contract test for each new service and the contract test SHALL fail the release if the service is unreachable, if its health check returns non-200, or if a workflow execution against the new service's task queue does not complete within the SLA.
- `order-temporal-workflow`: delta requirement — the `OrderFulfillmentWorkflow` activities SHALL call `payment.Client.Capture`, `inventory.Client.Reserve`, `shipping.Client.Dispatch` over HTTP via the platform's instrumented client; the saga compensation activities SHALL call the inverse operations; the in-process `localFulfillmentActivities` adapter is removed.

## Impact

### New code (services)

- `services/payment-service/` — full Go module: `go.mod` (replaces `payment` schema placeholder), `cmd/payment-service/` (api/worker/migrate roles), `internal/{domain,application,ports,adapters,temporal,runtime,config}`, `migrations/payment/`, `docs/adr/0001-service-extraction.md`, `Dockerfile.payment-service`, `README.md`, `test/architecture/layering_test.go`. ~1,800 LoC of Go + ~200 LoC of SQL.
- `services/inventory-service/` — full Go module mirroring the payment-service layout; owns `inventory_levels`, `inventory_reservations`, `inventory_outbox`, `inventory_idempotency_keys`. ~1,600 LoC of Go + ~200 LoC of SQL.
- `services/shipping-service/` — full Go module mirroring the payment-service layout; owns `shipments`, `shipping_events`, `shipping_outbox`, `shipping_idempotency_keys`; uses a `ShippingProvider` port with one SMTP-stub and one carrier-stub adapter. ~1,400 LoC of Go + ~150 LoC of SQL.
- `services/<payment|inventory|shipping>-service/contracts/` — protobuf definitions (`.proto` files) plus the generated Go code; produces three message families: `Payment*Request`/`Payment*Response`, `Inventory*Request`/`Inventory*Response`, `Shipping*Request`/`Shipping*Response`.

### New code (order-service refactor)

- `services/order-service/cmd/order-service/remote_activities.go` — replaces `worker_activities.go`; defines `remoteFulfillmentActivities` that holds `payment.Client`, `inventory.Client`, `shipping.Client` and implements the activity methods by calling the remote clients.
- `services/order-service/cmd/order-service/roles.go` — `runWorker()` constructs the three remote clients from `cfg.Peers` (new `ORDER_PAYMENT_URL`, `ORDER_INVENTORY_URL`, `ORDER_SHIPPING_URL` env vars), wires them into the activities struct, and fails fast if any peer URL is empty (production) but allows empty in local dev with a yellow warning.
- `services/order-service/internal/adapters/temporal/activities.go` — interface types renamed (`InventoryActivities` → `InventoryRemote`, etc.) to make the remote nature explicit; the `localFulfillmentActivities` adapter is removed.
- `services/order-service/internal/application/clients/` — three new files: `payment_client.go`, `inventory_client.go`, `shipping_client.go`; each follows the existing `clients/customer_client.go` pattern (instrumented HTTP, typed DTO, idempotency-key header).
- `services/order-service/internal/config/config.go` — three new env vars: `ORDER_PAYMENT_URL`, `ORDER_INVENTORY_URL`, `ORDER_SHIPPING_URL`; three new timeouts: `OrderPaymentTimeout`, `OrderInventoryTimeout`, `OrderShippingTimeout`; defaults to the cross-service smoke-test URLs in local dev.

### New code (notification, customer, catalog worker wiring)

- `services/notification-service/cmd/notification-service/main.go` + `internal/runtime/role_impl.go` — `runWorker` role opens a Temporal client, configures `WorkerDeploymentOptions` with `NotificationDispatchDeploymentSeries`, registers `NotificationFulfillmentWorkflow` + `DispatchActivity`, starts the worker, exposes `/health/ready`.
- `services/customer-service/adapters/kafka/orchestrator.go` — Kafka consumer for `customers.events.v1` that starts `CustomerPurgeWorkflow` or `CustomerGDPRExportWorkflow` based on event type; the `TemporalStarter` is wired in (currently defined but not started).
- `services/customer-service/cmd/customer-service/run.go` — `runWorker` role registers both workflows + their activities; `runOrchestrator` role starts the Kafka consumer.
- `services/catalog-service/cmd/catalog-service/main.go` — new `worker` subcommand that registers `PriceRollbackWorkflow` + `RollbackActivity` on task queue `catalog.admin.v1` (per `services/catalog-service/internal/application/orchestration/price_rollback.go::TaskQueue`); the existing `RunPriceRollback` non-Temporal entry point is preserved as a fallback for tests.

### New code (deploy)

- `deploy/docker-compose.payment-service.yaml` — `payment-migrate`, `payment-api`, `payment-worker` containers; `payment-infrastructure-init` script; `payment-topics-init` script (creates `payments.events.v1` with 12 partitions).
- `deploy/docker-compose.inventory-service.yaml` — `inventory-migrate`, `inventory-api`, `inventory-worker`; `inventory-topics-init` (`inventory.events.v1`).
- `deploy/docker-compose.shipping-service.yaml` — `shipping-migrate`, `shipping-api`, `shipping-worker`; `shipping-topics-init` (`shipping.events.v1`).
- `deploy/init-scripts/03-payment-cdc.sql` — `payment` schema, Debezium publication, outbox table.
- `deploy/init-scripts/04-inventory-cdc.sql` — `inventory` schema, Debezium publication, outbox table.
- `deploy/init-scripts/05-shipping-cdc.sql` — `shipping` schema, Debezium publication, outbox table.
- `deploy/tools.env` — pin three new service image versions: `PAYMENT_SERVICE_VERSION=local`, `INVENTORY_SERVICE_VERSION=local`, `SHIPPING_SERVICE_VERSION=local`.
- `Makefile` — three new service-level targets: `payment-build`, `inventory-build`, `shipping-build`; three new compose-up targets; three new smoke-test targets.

### New code (tests)

- `tests/cross-service-smoke/payment_contract_test.go` — `TestPaymentContract`: starts a payment intent via `payment-api`, captures it via the Temporal worker, asserts the event lands on `payments.events.v1` within 10 seconds, asserts the worker-side compensation flow runs on a forced timeout.
- `tests/cross-service-smoke/inventory_contract_test.go` — `TestInventoryContract`: reserves inventory, releases on cancellation, asserts outbox events.
- `tests/cross-service-smoke/shipping_contract_test.go` — `TestShippingContract`: dispatches a shipment, completes it, asserts carrier integration stub was called.
- `tests/cross-service-smoke/order_fulfillment_remote_test.go` — `TestOrderFulfillmentWithRemoteActivities`: full `OrderFulfillmentWorkflow` against the three real remote services; asserts saga compensation runs across the real network boundary.
- `tests/cross-service-smoke/replay_test.go` — replay test for `OrderFulfillmentWorkflow` that uses a recorded history with remote activity calls.

### Modified code

- `services/order-service/go.mod` — adds the new `services/payment-service/contracts/`, `services/inventory-service/contracts/`, `services/shipping-service/contracts/` as local replace directives; adds `github.com/sony/gobreaker` for circuit breakers.
- `services/order-service/cmd/order-service/worker_activities.go` — **DELETED**.
- `services/order-service/cmd/order-service/remote_activities.go` — **NEW**.
- `services/order-service/internal/adapters/temporal/activities.go` — interface types renamed; `localFulfillmentActivities` removed.
- `services/order-service/internal/adapters/temporal/registration.go` — registration call updated for the renamed types.
- `services/notification-service/cmd/notification-service/main.go` — new `worker` subcommand and `runWorker` implementation.
- `services/customer-service/cmd/customer-service/run.go` — `runWorker` and `runOrchestrator` implementations replace the existing stubs.
- `services/catalog-service/cmd/catalog-service/main.go` — new `worker` subcommand.
- `Makefile` — three new build targets, three new compose-up targets, three new smoke-test targets, updated `help` text.
- `deploy/docker-compose.yaml` — adds the new Postgres roles, the new topic-init scripts, the new Temporal task queues to the temporal init script.

### Dependencies (new)

- `github.com/sony/gobreaker v1.0.0` (verified on 2026-07-15) — used for the per-peer circuit breakers on the order-service's outbound HTTP clients. Pinned exactly. The library is widely used (4.2k★) and is a transitive dependency of `platform/http` already; pinning exactly avoids drift.
- `go.temporal.io/sdk v1.46.0` (already present in order-service) — no new SDK imports needed for the three new services; they follow the same pattern.
- `github.com/sony/gobreaker` is the only new runtime dependency; `go.temporal.io/sdk` is already a transitive dep via the `platform/temporal` module.

### Rollout approach

Five phases, executed sequentially with feature flags for partial rollout. Each phase has its own rollback boundary.

1. **Phase 1 (Day 1–3) — Schema and migrations**: author the three new SQL schemas, the Debezium publications, the CDC connector configs, the outbox tables. Run migrations against the local Postgres; verify CDC events flow to `payments.events.v1` etc. via the existing `01-orders-cdc.sql` and `02-notifications-cdc.sql` pattern.
2. **Phase 2 (Day 4–7) — Service skeletons**: author the three new Go service modules with the `runApi` role only. No Temporal worker yet; the API exists and serves the same set of HTTP endpoints that the order-worker will call. Verify with `curl` against the new service ports.
3. **Phase 3 (Day 8–12) — Worker extraction**: author `runWorker` for each new service, register the activity on the per-service task queue, convert the order-worker's `localFulfillmentActivities` to `remoteFulfillmentActivities`. The `MakePeerEnricher`-style wiring in `cmd/order-service/roles.go` is replaced with `MakePaymentClient`, `MakeInventoryClient`, `MakeShippingClient`. Verify by running the full `OrderFulfillmentWorkflow` against the three real remote services; verify saga compensation runs across the network.
4. **Phase 4 (Day 13–15) — Stub worker wiring**: complete the unwired stub workers (notification, customer, catalog). `notification-worker` registers `NotificationFulfillmentWorkflow` + `DispatchActivity`; `customer-worker` registers `CustomerPurgeWorkflow` + `CustomerGDPRExportWorkflow` + activities; `customer-orchestrator` subscribes to `customers.events.v1`; `catalog-worker` registers `PriceRollbackWorkflow` + `RollbackActivity`. Verify each with a smoke test that starts the workflow via the orchestrator and asserts the worker completes it.
5. **Phase 5 (Day 16–18) — Cross-service smoke + archive**: extend `tests/cross-service-smoke/` with the four new contract tests; run `make test-e2e-up` end-to-end; archive the change via `openspec archive --change extract-business-domains-and-dedicated-workflow-orchestration --yes`.

### Rollback approach

The change touches a large surface; rollback must be atomic at the change level (not phase level), with two clean rollback paths:

1. **Full revert** — revert the single change PR. The three new Go modules are removed, the order-service's `remote_activities.go` is replaced by `worker_activities.go`, the `docker-compose.<service>.yaml` overlays are removed, the CDC init scripts are removed. A single `git revert` returns the repo to its pre-change state. The order-worker's in-process stubs come back; the saga compensation graph still runs but inside the order service's process.
2. **Service-by-service disable** — for partial rollout failure, set the env var `ORDER_PAYMENT_URL=`, `ORDER_INVENTORY_URL=`, `ORDER_SHIPPING_URL=` in `docker-compose.order-service.yaml`; the order-worker falls back to a yellow warning and uses the in-process stub. The new services are deployed but unused. This is the recommended "soft rollback" path for Phase 3 and Phase 4 failures.

**No data migration on rollback.** The three new Postgres schemas are NOT dropped on rollback; they are preserved so the new services can be re-enabled without re-running migrations. The Debezium publications are not removed; the Kafka topics are not deleted. Only the Go service code and the docker-compose wiring are reverted.
