# shipping-service Specification

## Purpose
A dedicated `shipping-service` Go module SHALL own the `shipping` Postgres schema, expose a REST HTTP API for shipment dispatch, run its own Temporal worker on task queue `shipping.dispatch.v1`, and emit `shipping.events.v1` from its outbox. The service uses a `ShippingProvider` port that abstracts the carrier integration (one SMTP-stub and one carrier-stub adapter for local dev). The order-service SHALL call it over HTTP via the platform's instrumented client; the order-worker's saga compensation graph SHALL NOT call a `Cancel` inverse operation (the saga accepts orphan shipments and alerts operators). This is the third of three business-domain services extracted from the order-service.

## ADDED Requirements

### Requirement: shipping-service is an independently deployable Go module

`services/shipping-service/` SHALL be a Go module with the same hexagonal layout as `payment-service` and `inventory-service`: `cmd/shipping-service/`, `internal/{domain,application,ports,adapters,runtime,config}`, `migrations/shipping/`, `proto/shipping/v1/` and `contracts/shipping/v1/`, `docs/adr/0001-service-extraction.md`, `Dockerfile.shipping-service`, and `test/architecture/layering_test.go`. The module path SHALL be `github.com/victory1908/shipping-service` (matching the peer services' convention; the `/services/` segment is NOT used). The reserved-namespaces test in `services/order-service/test/architecture/layering_test.go` already declares `github.com/victory1908/shipping-service/` as a reserved prefix. The module SHALL NOT import any other service's `internal/` package.

#### Scenario: shipping-service compiles as a standalone Go module

- **WHEN** a developer runs `cd services/shipping-service && go build ./...`
- **THEN** the build succeeds without any `replace` directive pointing to another service's module

### Requirement: shipping-service owns the shipping Postgres schema and CDC topic

The `shipping` schema SHALL contain the `shipments`, `shipping_events`, `shipping_outbox`, and `shipping_idempotency_keys` tables. The CDC connector SHALL publish every row added to `shipping_outbox` to the `shipping.events.v1` Kafka topic with at-least-once delivery. The `deploy/init-scripts/05-shipping-cdc.sql` migration SHALL create the schema, the tables, the Debezium publication, and the publication slot.

#### Scenario: shipping-migrate creates the shipping schema

- **WHEN** the `shipping-migrate` container runs `shipping-service migrate up`
- **THEN** the `shipping` schema exists with the four tables, the Debezium publication, and the publication slot

#### Scenario: Outbox event lands on shipping.events.v1

- **WHEN** the `DispatchShipment` command commits a `shipments` row and a `shipping_outbox` row in the same transaction
- **THEN** within 5 seconds the Debezium connector publishes the outbox event to `shipping.events.v1` with the `shipment_dispatched` event type

### Requirement: shipping-service exposes a REST API for shipments

The `shipping-api` container SHALL serve the following REST endpoints on `:8085`:

- `POST /api/v1/shipments` — dispatches a new shipment. Body: `{ contract_version, order_id, address: { ... }, carrier: "stub|ups|fedex", idempotency_key }`. Response: `201 Created` with `{ contract_version, shipment_id, status: "dispatched", tracking_number, carrier }`. The endpoint SHALL call the `ShippingProvider.Dispatch` port with the parsed address; on success, the response includes the carrier-assigned tracking number.
- `POST /api/v1/shipments/{id}/cancel` — cancels a dispatched shipment. The endpoint SHALL call `ShippingProvider.Cancel` with the tracking number; the carrier's cancellation confirmation is recorded. Response: `200 OK` with `{ contract_version, shipment_id, status: "cancelled" }`. Note: the order-worker's saga does NOT call this endpoint (no `CancelShipping` activity is registered; see `order-temporal-workflow` spec).
- `POST /api/v1/shipments/{id}/complete` — marks a shipment as delivered (typically called by a webhook from the carrier provider). Body: `{ delivered_at, signature_url? }`. Response: `200 OK` with `{ contract_version, shipment_id, status: "delivered" }`.
- `GET /api/v1/shipments/{id}` — returns the current state of the shipment.
- `GET /health/live`, `GET /health/ready`, `GET /health/startup`, `GET /metrics`.

The `idempotency_key` header on every write endpoint SHALL be recorded in `shipping_idempotency_keys`.

#### Scenario: Shipment dispatch is idempotent on idempotency_key

- **WHEN** `POST /api/v1/shipments` is called twice with the same `idempotency_key`
- **THEN** the second call returns `200 OK` with the original `shipment_id`
- **AND** no second row is inserted into `shipments`

#### Scenario: Shipment dispatch uses the configured ShippingProvider

- **WHEN** `POST /api/v1/shipments` is called with `carrier: "stub"`
- **THEN** the `stub` adapter generates a deterministic tracking number `STUB-<shipment_id>` and records the dispatch
- **AND** no external HTTP call to a real carrier is made

### Requirement: ShippingProvider port abstracts the carrier integration

The `ports.ShippingProvider` interface SHALL define `Dispatch(ctx, DispatchRequest) (DispatchResponse, error)` and `Cancel(ctx, TrackingNumber) error`. The `stub` adapter SHALL return deterministic tracking numbers and SHALL record calls in-memory for testing. The `ups` adapter SHALL call the UPS API (stubbed in local dev, real in production). The `shipping-api` container SHALL load the configured adapter from the `SHIPPING_PROVIDER` env var (default `stub`). The `ShippingProvider` port SHALL be the only way the application layer interacts with carriers; the application layer SHALL NOT import any carrier SDK directly.

#### Scenario: shipping-service uses the stub adapter in local dev

- **WHEN** the `shipping-api` container starts with `SHIPPING_PROVIDER=stub`
- **THEN** the `stub` adapter is wired in
- **AND** `POST /api/v1/shipments` returns a tracking number in the `STUB-<id>` format

#### Scenario: Application layer does not import a carrier SDK

- **WHEN** the architecture test scans `services/shipping-service/internal/application/` for forbidden imports
- **THEN** the test fails if any import path matches a carrier SDK (e.g., `github.com/ups/shipping-sdk`, `github.com/fedex/ship-api`)
- **AND** the test passes if the application layer only imports the local `ports` package

### Requirement: shipping-service runs a Temporal worker on shipping.dispatch.v1

The `shipping-worker` container SHALL open a Temporal client, configure `WorkerDeploymentOptions` with `UseVersioning: true`, `Version.DeploymentName: "shipping.dispatch.v1"`, and `Version.BuildID: platformtemporal.DeploymentVersion()`, and register the following workflows and activities on task queue `shipping.dispatch.v1`:

- Workflow: `ShippingDispatchWorkflow` — runs `ShippingDispatchActivity` followed by a `RecordDispatchEvent` activity; on failure, the workflow returns a typed `ShippingDispatchError`.
- Activity: `ShippingDispatchActivity` — calls the `DispatchShipment` command handler with the input `order_id`, `address`, `carrier`, and `idempotency_key`; returns the `shipment_id` and `tracking_number`.
- Activity: `ShippingCancelActivity` — calls the `CancelShipment` command handler with the input `shipment_id` and `idempotency_key`; returns the `shipment_id` and `status: "cancelled"`. This activity is registered but NOT called by the order-worker's saga compensation (see `order-temporal-workflow` spec).
- Activity: `RecordDispatchEvent` — writes a `shipment_dispatched` outbox event.

The worker SHALL start the underlying `worker.Worker` via `worker.New(c, "shipping.dispatch.v1", worker.Options{DeploymentOptions: ...})`; activity options SHALL use `platformtemporal.NewValidatedActivityOptions` with `ScheduleToClose=5m`, `StartToClose=30s`, `ScheduleToStart=30s`, `Heartbeat=10s`, and `RetryAttempts=5`.

#### Scenario: shipping-worker registers the workflow and activity set

- **WHEN** the `shipping-worker` container starts with `SHIPPING_TEMPORAL_ADDRESS=temporal:7233`, `SHIPPING_TEMPORAL_TASK_QUEUE=shipping.dispatch.v1`
- **THEN** the worker registers `ShippingDispatchWorkflow` (as `shipping.dispatch.v1`) and the three activities on task queue `shipping.dispatch.v1`
- **AND** the worker registers with `DeploymentSeriesName: "shipping.dispatch.v1"` and `BuildID: <PLATFORM_DEPLOYMENT_VERSION or GIT_SHA or "dev">`

### Requirement: Shipping dispatch is idempotent and uses stable operation_id

The `ShippingDispatchActivity` SHALL derive a stable `operation_id` from the workflow ID using `platformtemporal.OperationIDFor(workflowID, "shipping.dispatch")`. The activity body SHALL check `shipments` for a row with `operation_id` matching before performing the side effect.

#### Scenario: Shipping dispatch is idempotent across retries

- **WHEN** `ShippingDispatchActivity` is invoked twice with the same `operation_id` and the first invocation succeeded
- **THEN** the second invocation observes the prior result and returns `nil` without performing a second dispatch

### Requirement: Shipping dispatch uses the saga pattern with typed errors

The `ShippingDispatchWorkflow` SHALL use `platformtemporal.NewSaga` for forward and compensation tracking. On `NonRetryableApplicationError` from the forward path, the workflow runs `ShippingCancelActivity` with the original `operation_id` to cancel the shipment. Compensation failures SHALL be recorded as `CompensationFailureV1` events.

#### Scenario: Successful shipping dispatch

- **WHEN** `ShippingDispatchWorkflow` is started with a valid `order_id` and the dispatch succeeds
- **THEN** the workflow runs `ShippingDispatchActivity` → `RecordDispatchEvent` in forward order
- **AND** no compensation activities run

#### Scenario: Failed dispatch triggers compensation

- **WHEN** `ShippingDispatchActivity` succeeds but `RecordDispatchEvent` fails
- **THEN** the workflow runs the compensation path: `ShippingCancelActivity` with the original `operation_id`
- **AND** the shipment is cancelled and the tracking number is released

### Requirement: shipping-service has an ADR documenting the extraction

`services/shipping-service/docs/adr/0001-service-extraction.md` SHALL follow the 5-point admission format.

#### Scenario: shipping-service ADR exists and passes the architecture test

- **WHEN** the architecture test scans for the ADR
- **THEN** the test verifies the file exists and contains the five required sections

### Requirement: shipping-service is exposed via docker-compose overlay

The `deploy/docker-compose.shipping-service.yaml` overlay SHALL add the `shipping-migrate`, `shipping-api`, `shipping-worker`, `shipping-infrastructure-init`, and `shipping-topics-init` containers. The `shipping-topics-init` container creates the `shipping.events.v1` topic with 3 partitions. The `shipping-api` container SHALL bind `:8085` and `:9095`. The `shipping-worker` container SHALL depend on `temporal: condition: service_healthy`.

#### Scenario: shipping-service containers start in dependency order

- **WHEN** `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.shipping-service.yaml up -d` runs
- **THEN** the `shipping-topics-init` container completes before `shipping-api` starts
- **AND** the `shipping-worker` container starts only after `temporal` is `service_healthy` and `shipping-migrate` has completed`
