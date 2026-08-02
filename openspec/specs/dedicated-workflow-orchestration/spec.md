# dedicated-workflow-orchestration Specification

## Purpose
This spec defines the per-domain service extraction for the `extract-business-domains-and-dedicated-workflow-orchestration` change. Each business domain (order, payment, inventory, shipping, notification, customer, reporting, catalog) SHALL run as an independent Go service with its own Postgres schema as the sole writer, its own Kafka topic for emitted events, its own Temporal task queue for workflow execution, and its own Dockerfile + docker-compose overlay. The order-service's workflow orchestrator SHALL call the three extracted services over HTTP instead of in-process command handlers, with the saga compensation path also crossing the real network boundary.
## Requirements

> **Status**: LOCAL IMPLEMENTED. Services, remote activities, worker placement,
> contracts, full cross-service smoke, and direct Temporal execution pass in
> retained local Compose and kind evidence. Cloud rollout remains separate.
>
> **Status semantics and acceptance evidence:** `IMPLEMENTED` annotations below describe source-level artifacts, not proof that the deployed system converges. Full orchestration readiness requires `make dev-up`, `make dev-smoke`, and `make validate-deployment` to pass for the target commit, with the `microservices.deployment-validation/v1` manifest and referenced smoke report retained under `artifacts/deployment-validation/<run-id>/` (or the configured artifact root).

### Requirement: Each business domain is an independent Go service

> **Status**: IMPLEMENTED. All eight services exist as independent Go modules with separate schemas and topics.

The platform's business domains are:

| Domain | Service | Postgres Schema | Kafka Topic | Temporal Task Queue | Workflow Type (registered) |
|---|---|---|---|---|---|
| Order | `order-service` | `public` (the order-service's `orders` tables; sole writer) | `orders.events.v1` | `order-fulfillment.v1` | `order.fulfillment.v1` |
| Payment | `payment-service` (new) | `payment` | `payments.events.v1` | `payment.capture.v1` | `payment.capture.v1` |
| Inventory | `inventory-service` (new) | `inventory` | `inventory.events.v1` | `inventory.reservation.v1` | `inventory.reservation.v1` |
| Shipping | `shipping-service` (new) | `shipping` | `shipping.events.v1` | `shipping.dispatch.v1` | `shipping.dispatch.v1` |
| Notification | `notification-service` (worker stub) | `notification` | `notifications.dispatch.v1` | `notification.dispatch.v1` | `notification.dispatch.v1` |
| Customer | `customer-service` (worker stub) | `customer` | `customers.events.v1` | `customer.purge.v1` and `customer.gdpr.v1` | `customer.purge.v1` and `customer.gdpr.v1` |
| Reporting | `reporting-service` (worker stub) | `reporting` | (read-only) | `reporting.admin.v1` | `ReportingDailyRevenueRollup` |
| Catalog | `catalog-service` (workflow defined, worker not wired) | `catalog` | (read-only) | `catalog.admin.v1` | `PriceRollbackWorkflow.v1` |

Each service SHALL be a separate Go module under `services/<name>/`. New service modules SHALL use the module path `github.com/victory1908/<name>` (matching the existing `notification-service`, `customer-service`, `reporting-service`, `catalog-service`). The `order-service` module path remains the exception (`github.com/victory1908/services/order-service`); new services SHALL NOT introduce the `/services/` segment to preserve the established convention. Each service SHALL own its Postgres schema as the sole writer. Each service SHALL emit events from its outbox to its Kafka topic via Debezium CDC. Each service SHALL run a Temporal worker on its own task queue. The architecture test SHALL verify that all eight service modules exist and have the required structure (`cmd/<name>/`, `internal/{domain,application,ports,adapters,runtime,config}`, `migrations/<schema>/`).

#### Scenario: All eight service modules exist

- **WHEN** the architecture test lists `services/` directories
- **THEN** the list contains `order-service`, `payment-service`, `inventory-service`, `shipping-service`, `notification-service`, `customer-service`, `reporting-service`, `catalog-service`
- **AND** each directory contains `cmd/`, `internal/`, `migrations/`, `Dockerfile.<name>`, and `go.mod`

#### Scenario: All eight services have a docker-compose overlay

- **WHEN** the architecture test lists `deploy/docker-compose.*.yaml` files
- **THEN** the list contains overlays for all eight services

### Requirement: Cross-domain operations are real remote activities

> **Status**: IMPLEMENTED. Order service uses remote activities with HTTP calls to payment, inventory, shipping services.

When a workflow in one domain (e.g., `order-service`) needs to perform an operation in another domain (e.g., `payment-service`), the activity SHALL be a real HTTP call to the target service's REST API. The activity SHALL NOT be an in-process call to a local command handler. The activity SHALL use the platform's OTel-instrumented HTTP client, the per-peer circuit breaker, and the per-peer timeout. The activity input/output SHALL be the generated protobuf types from the target service's `contracts/` package.

The order-service's `OrderFulfillmentWorkflow` activities are the canonical example. The actual forward activities (per `services/order-service/internal/adapters/temporal/workflow.go`) are:

- `ValidateInventoryActivityV1` (activity name `order.fulfillment.validate-inventory.v1`) — reads availability, currently returns `available: true` from the local stub
- `ProcessPaymentActivityV1` (activity name `order.fulfillment.process-payment.v1`) — captures payment; in the remote-activities refactor this calls `payment.Client.Capture` over HTTP
- `ReserveInventoryActivityV1` (activity name `order.fulfillment.reserve-inventory.v1`) — reserves stock; in the remote-activities refactor this calls `inventory.Client.Reserve` over HTTP
- `MarkOrderShippedActivityV1` (activity name `order.fulfillment.mark-shipped.v1`) — marks the order shipped; in the remote-activities refactor this calls `shipping.Client.Dispatch` over HTTP

The actual compensations (per the existing `registerCompensation` calls in `workflow.go`) are:

- `RefundPaymentActivityV1` (activity name `order.fulfillment.refund-payment.v1`) — inverse of `ProcessPaymentActivityV1`
- `ReleaseInventoryActivityV1` (activity name `order.fulfillment.release-inventory.v1`) — inverse of `ReserveInventoryActivityV1`

`MarkOrderShippedActivityV1` has NO compensation in the current saga (the spec must not invent a `CancelShipping` activity that does not exist in the workflow code). The notification dispatch is NOT a step of `OrderFulfillmentWorkflow`; the `notification-service` has its own workflow triggered by Kafka events from the order-service's outbox, not by a remote activity from the order-worker.

#### Scenario: OrderFulfillmentWorkflow activities call the peer services over HTTP

- **WHEN** the `OrderFulfillmentWorkflow` runs the four forward activities
- **THEN** each activity makes an HTTP call to the corresponding peer service (`payment-service` for `ProcessPaymentActivityV1`, `inventory-service` for `ReserveInventoryActivityV1` and `ValidateInventoryActivityV1`, `shipping-service` for `MarkOrderShippedActivityV1`)
- **AND** the HTTP call is observable in the OTel trace as a child span of the activity's span
- **AND** the HTTP call propagates the W3C Trace Context and the platform's correlation headers

#### Scenario: Saga compensation runs across the real network boundary

- **WHEN** the `OrderFulfillmentWorkflow` enters the compensation path
- **THEN** `RefundPaymentActivityV1` calls `payment.Client.Refund` over HTTP
- **AND** `ReleaseInventoryActivityV1` calls `inventory.Client.Release` over HTTP
- **AND** the compensation network call is observable in the OTel trace

### Requirement: Worker placement is in the business service module

> **Status**: IMPLEMENTED. Workers live in each service's cmd/ directory; architecture tests enforce placement.

The Temporal worker for a service SHALL live in the same Go module as the service's business logic. The worker SHALL NOT be in a shared "workflow service" module. The worker SHALL be a separate container from the API. The worker SHALL share the service's database with the API. The worker SHALL scale independently of the API. These rules are normative and are enforced by the architecture test (see `worker-placement-policy` spec).

#### Scenario: order-worker is in services/order-service/cmd/order-service/

- **WHEN** the architecture test scans for `worker.New` or `worker.New(client, ...)` calls
- **THEN** the test verifies that all such calls are in `services/<service>/cmd/<service>/`
- **AND** no such call appears in `services/workflow-orchestrator/` or `services/temporal-workers/`

### Requirement: Workflow ID is a meaningful business identifier

> **Status**: IMPLEMENTED. Workflow IDs use meaningful business identifiers (order/<id>, customer-purge-<id>, etc.).

The Temporal Workflow ID for each workflow SHALL be a meaningful business identifier. The existing convention (per the order-service's `internal/application/orchestration/workflow_id.go` and `internal/adapters/temporal/constants.go`) is:

| Workflow | Workflow ID |
|---|---|
| Order fulfillment | `order/<order_id>` (helper: `WorkflowIDForOrder(orderID)` in `services/order-service/internal/adapters/temporal/constants.go`) |
| Customer purge | `customer-purge-<customer_id>` (set by `temporal_starter.go`) |
| Customer GDPR export | `customer-gdpr-<customer_id>-<idempotency_key>` (set by `temporal_starter.go`) |

The new services SHALL adopt the same meaningful-ID pattern:

- `payment.capture-<payment_intent_id>` for the payment capture workflow
- `inventory.reservation-<reservation_id>` for the inventory reservation workflow
- `shipping.dispatch-<shipment_id>` for the shipping dispatch workflow

The `WorkflowIDReusePolicy` SHALL be `WORKFLOW_ID_REUSE_POLICY_USE_EXISTING` for event-driven workflows (per the `platform-temporal-versioning` spec).

#### Scenario: order-orchestrator starts OrderFulfillmentWorkflow with a meaningful ID

- **WHEN** the `order-orchestrator` consumes a `OrderCreated` event from `orders.events.v1`
- **THEN** the orchestrator calls `Temporal.StartWorkflow(ctx, StartWorkflowOptions{ID: WorkflowIDForOrder(orderID), TaskQueue: "order-fulfillment.v1", WorkflowIDReusePolicy: USE_EXISTING}, OrderFulfillmentWorkflow, input)`
- **AND** a duplicate event with the same `order_id` short-circuits to the existing workflow (no second workflow is started)

### Requirement: The order-service no longer contains in-process payment/inventory/shipping commands

> **Status**: IMPLEMENTED. Remote activities implemented; local stubs deprecated and preserved for local dev.

The `services/order-service/cmd/order-service/worker_activities.go` file's `localFulfillmentActivities` struct SHALL be replaced by `remoteFulfillmentActivities` (per the `order-remote-activities` spec). The `localFulfillmentActivities` struct SHALL be preserved in `worker_activities_local.go` as a deprecated fallback (used only when peer URLs are empty in local dev). The `services/order-service/internal/application/commands/` package SHALL NOT contain `payment.NewPaymentHandler`, `inventory.NewInventoryHandler`, or `shipping.NewShippingHandler` types; these are removed because the corresponding operations are now remote calls in the order-worker's activities.

The current order-service does NOT have any of these `payment.*`, `inventory.*`, `shipping.*` handlers in `internal/application/commands/` — they only exist inside `worker_activities.go` as in-process stubs. The refactor's goal is to remove the stubs and replace them with HTTP clients.

#### Scenario: order-service no longer contains in-process payment/inventory/shipping stubs

- **WHEN** the architecture test scans `services/order-service/cmd/order-service/worker_activities.go`
- **THEN** the test fails if the file contains `localFulfillmentActivities` (it was renamed)
- **AND** the test verifies that `worker_activities_remote.go` exists with the `remoteFulfillmentActivities` struct
- **AND** the test verifies that `worker_activities_local.go` exists with a `// Deprecated:` comment block

### Requirement: Cross-service contracts are protobuf-managed

> **Status**: IMPLEMENTED. Proto files exist; buf generate produces Go contracts committed to repo.

The wire DTOs for cross-service HTTP calls SHALL be defined in protobuf and generated to Go. The `.proto` files SHALL live in `services/<service>/proto/<domain>/v1/` (matching the existing order-service convention under `services/order-service/proto/order/v1/`). The generated `.pb.go` files SHALL be committed to the repo at `services/<service>/contracts/<domain>/v1/` (matching the existing `services/order-service/contracts/order/v1/` directory layout). The `buf.yaml` at the repo root SHALL include all `proto/**/*.proto` files. The `contract_version` field SHALL be the first field of every cross-service message (per `cross-service-workflow-contracts` spec).

#### Scenario: payment contract is protobuf-managed

- **WHEN** a developer runs `buf lint` against `services/payment-service/proto/`
- **THEN** the command exits 0
- **AND** the `payment.proto` file has the `contract_version` field as the first field of every message

#### Scenario: order-service imports the payment contract

- **WHEN** the order-service builds
- **THEN** the `go.mod` has a `replace` directive pointing to `services/payment-service/contracts/`
- **AND** the order-service's `clients/payment_client.go` imports `github.com/victory1908/payment-service/contracts/payment/v1`
- **AND** the build succeeds

### Requirement: The cross-service smoke test exercises the full orchestration

> **Status**: LOCAL IMPLEMENTED. The canonical cross-service smoke exercises
> all eight services, CDC delivery, the order lifecycle, notification,
> reporting freshness, GDPR export, required telemetry, and direct execution
> of all 13 advertised Temporal Workflow types.

The `tests/cross-service-smoke/` SHALL include a `TestOrderFulfillmentWithRemoteActivities` test that:

1. Starts a real `OrderFulfillmentWorkflow` via the order-service's orchestrator.
2. Verifies that the workflow makes HTTP calls (one per forward activity) to the new services' APIs.
3. Forces a failure (e.g., kills the payment-service container) and verifies that the workflow enters the compensation path.
4. Verifies that the compensation activities (`RefundPaymentActivityV1`, `ReleaseInventoryActivityV1`) make HTTP calls to the corresponding peer services.
5. Verifies that the workflow completes with the compensation result.
6. Verifies that the OTel trace captures the full saga as a single trace with the workflow span as the root and the activity spans as children.

#### Scenario: TestOrderFulfillmentWithRemoteActivities passes end-to-end

- **WHEN** the test runs against the full docker-compose stack
- **THEN** the test verifies all six assertions above
- **AND** the test completes within 60 seconds
- **AND** the test fails the release if any assertion fails

### Requirement: The change is rolled out in five sequential phases

> **Status**: LOCAL IMPLEMENTED. The full eight-service topology, Temporal
> namespace and worker convergence, reporting outcome, cross-service smoke,
> telemetry, and direct Workflow execution pass together with retained local
> evidence. This does not claim cloud rollout or CI/CD completion.

The change SHALL be rolled out in five sequential phases, each with its own feature flag and its own rollback boundary:

1. **Phase 1 (Day 1–3) — Schema and migrations**: author the three new SQL schemas, the Debezium publications, the CDC connector configs, the outbox tables. Run migrations against the local Postgres.
2. **Phase 2 (Day 4–7) — Service skeletons**: author the three new Go service modules with the `runApi` role only. No Temporal worker yet.
3. **Phase 3 (Day 8–12) — Worker extraction**: author `runWorker` for each new service, convert the order-worker's `localFulfillmentActivities` to `remoteFulfillmentActivities`. Verify by running the full `OrderFulfillmentWorkflow` against the three real remote services.
4. **Phase 4 (Day 13–15) — Stub worker wiring**: complete the unwired stub workers (notification, customer, reporting, catalog).
5. **Phase 5 (Day 16–18) — Cross-service smoke + archive**: extend `tests/cross-service-smoke/` with the four new contract tests; run `make test-e2e-up` end-to-end; archive the change via `openspec archive`.

#### Scenario: Phase 1 completes successfully

- **WHEN** the `payment-migrate`, `inventory-migrate`, `shipping-migrate` containers run
- **THEN** the `payment`, `inventory`, `shipping` schemas exist with all required tables
- **AND** the Debezium publications and publication slots are created
- **AND** the `payments.events.v1`, `inventory.events.v1`, `shipping.events.v1` topics are created

#### Scenario: Phase 3 verifies the remote-activity saga

- **WHEN** the `order-orchestrator` starts an `OrderFulfillmentWorkflow` against the full docker-compose stack
- **THEN** the workflow's `ReserveInventoryActivityV1` makes an HTTP call to `http://inventory-api:8084/api/v1/inventory/reservations`
- **AND** the workflow's `ProcessPaymentActivityV1` makes an HTTP call to `http://payment-api:8083/api/v1/payments/{intent_id}/capture`
- **AND** the workflow's `MarkOrderShippedActivityV1` makes an HTTP call to `http://shipping-api:8085/api/v1/shipments`
- **AND** the workflow completes successfully

#### Scenario: Phase 5 archives the change

- **WHEN** `openspec archive --change extract-business-domains-and-dedicated-workflow-orchestration --yes` runs
- **THEN** the seven new capabilities appear in `openspec/specs/`
- **AND** the four deltas are merged into the existing specs (`platform-temporal-versioning`, `platform-extensibility`, `platform-verification`, `order-temporal-workflow`)
- **AND** the change directory is moved to `openspec/changes/archive/`

### Requirement: Canonical eight-service Compose topology

The platform SHALL maintain one root Compose file set that includes the base data plane and the order, payment, inventory, shipping, notification, customer, catalog, and reporting service overlays. The same file set SHALL be used by local full-stack startup and cross-service CI.

#### Scenario: Canonical model includes all service boundaries

- **WHEN** CI renders the canonical Compose model and lists its services
- **THEN** every required API, worker, orchestrator, consumer, migration, topic initializer, and infrastructure initializer for all eight services is present

#### Scenario: Undefined cross-service dependency is rejected

- **WHEN** an overlay declares a dependency on a service absent from the canonical model
- **THEN** Compose model validation exits non-zero before images are built or containers are created

### Requirement: Cross-service workflow validates real network boundaries

The full-stack acceptance test SHALL exercise the order workflow through the deployed HTTP, Temporal, PostgreSQL, Kafka, and reporting boundaries and SHALL NOT replace a required peer service with an in-process implementation or test double.

#### Scenario: Order workflow reaches extracted services

- **WHEN** the acceptance test creates an order and drives fulfillment to completion
- **THEN** payment, inventory, and shipping calls cross their deployed HTTP boundaries, Temporal records the workflow, public events traverse Kafka, and reporting observes the outcome

#### Scenario: Acceptance provisions inventory through the owning service

- **WHEN** the acceptance test creates a catalog product whose identifier is used as the inventory SKU
- **THEN** it provisions on-hand stock through the deployed inventory-service API before creating the order
- **AND** it does not write the inventory schema directly or substitute a repository or in-process test double
- **AND** the validation activity uses the read-only inventory availability endpoint while the reservation activity remains the sole stock-holding mutation

#### Scenario: Peer failure produces retry-safe evidence

- **WHEN** a configured peer service fails during the acceptance workflow
- **THEN** the workflow follows its retry or compensation contract without duplicate externally visible effects and the evidence report identifies the failed boundary and final state
