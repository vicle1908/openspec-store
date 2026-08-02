# inventory-service Specification

## Purpose
This spec defines the inventory-service extraction. The inventory-service SHALL own the `inventory` Postgres schema as sole writer, publish inventory events to the `inventory.events.v1` Kafka topic via Debezium CDC, and run an `InventoryReservationWorkflow` Temporal workflow on task queue `inventory.reservation.v1`. The service SHALL expose REST endpoints for reservation, release, and confirmation; the order-worker SHALL call these endpoints as remote activities rather than in-process handlers.
## Requirements
### Requirement: inventory-service is an independently deployable Go module

> **Status**: IMPLEMENTED. inventory-service exists as independent Go module with hexagonal layout.

`services/inventory-service/` SHALL be a Go module with the same hexagonal layout as `payment-service`: `cmd/inventory-service/`, `internal/{domain,application,ports,adapters,runtime,config}`, `migrations/inventory/`, `proto/inventory/v1/` and `contracts/inventory/v1/`, `docs/adr/0001-service-extraction.md`, `Dockerfile.inventory-service`, and `test/architecture/layering_test.go`. The module path SHALL be `github.com/victory1908/inventory-service` (matching the peer services' convention; the `/services/` segment is NOT used). The reserved-namespaces test in `services/order-service/test/architecture/layering_test.go` already declares `github.com/victory1908/inventory-service/` as a reserved prefix. The module SHALL NOT import any other service's `internal/` package.

#### Scenario: inventory-service compiles as a standalone Go module

- **WHEN** a developer runs `cd services/inventory-service && go build ./...`
- **THEN** the build succeeds without any `replace` directive pointing to another service's module

### Requirement: inventory-service owns the inventory Postgres schema and CDC topic

> **Status**: LOCAL-VERIFIED. The canonical inventory connector, exact
> publication and slot, idempotent Compose/kind registration, and a retained
> local acceptance probe prove delivery from `inventory.inventory_outbox` to
> `inventory.events.v1`. This status does not claim cloud deployment readiness.

The `inventory` schema SHALL contain the `inventory_levels` (per-SKU on-hand, reserved, available quantities), `inventory_reservations` (the reservation ledger), `inventory_outbox`, and `inventory_idempotency_keys` tables. The CDC connector SHALL publish every row added to `inventory_outbox` to the `inventory.events.v1` Kafka topic with at-least-once delivery. The `deploy/init-scripts/04-inventory-cdc.sql` migration SHALL create the schema, the tables, the Debezium publication, and the publication slot. The schema SHALL enforce `available_quantity = on_hand_quantity - reserved_quantity` via a CHECK constraint or a generated column; the schema SHALL use optimistic concurrency via a `version` integer column on `inventory_levels` for safe concurrent updates.

#### Scenario: inventory-migrate creates the inventory schema

- **WHEN** the `inventory-migrate` container runs `inventory-service migrate up`
- **THEN** the `inventory` schema exists with the four tables, the Debezium publication, and the publication slot
- **AND** the `inventory_levels` table has a `version` column for optimistic concurrency

#### Scenario: Outbox event lands on inventory.events.v1

- **WHEN** the `ReserveInventory` command commits an `inventory_reservations` row and an `inventory_outbox` row in the same transaction
- **THEN** within 5 seconds the Debezium connector publishes the outbox event to `inventory.events.v1` with the `inventory_reserved` event type

### Requirement: inventory-service exposes a REST API for reservations

> **Status**: IMPLEMENTED. REST endpoints exist for reservation, release, confirm, and availability checks.

The `inventory-api` container SHALL serve the following REST endpoints on `:8084`:

- `POST /api/v1/inventory/reservations` — reserves inventory for a list of SKUs. Body: `{ contract_version, order_id, lines: [{ sku, quantity }], idempotency_key }`. Response: `201 Created` with `{ contract_version, reservation_id, status: "reserved", lines: [...] }`. The endpoint SHALL atomically check `available_quantity >= quantity` for all lines and decrement the `available_quantity` for all lines; if any line has insufficient inventory, the endpoint SHALL return `409 Conflict` and SHALL NOT partially reserve.
- `POST /api/v1/inventory/reservations/{id}/release` — releases a previously-reserved reservation. The endpoint SHALL increment `available_quantity` by the reserved quantity for all lines. Response: `200 OK` with `{ contract_version, reservation_id, status: "released" }`.
- `POST /api/v1/inventory/reservations/{id}/confirm` — confirms a previously-reserved reservation, transitioning it to a permanent deduction. The endpoint SHALL decrement `on_hand_quantity` and zero out the `reserved_quantity` for the reservation's lines. Response: `200 OK` with `{ contract_version, reservation_id, status: "confirmed" }`.
- `GET /api/v1/inventory/availability?order_id=<id>` — returns `available: bool` for the order's lines. Used by the order-worker's `ValidateInventoryActivityV1` activity.
- `GET /api/v1/inventory/{sku}` — returns the current `on_hand_quantity`, `reserved_quantity`, and `available_quantity` for a SKU.
- `GET /health/live`, `GET /health/ready`, `GET /health/startup`, `GET /metrics`.

The `idempotency_key` header on every write endpoint SHALL be recorded in `inventory_idempotency_keys`; duplicate requests return the cached response.

#### Scenario: Multi-line reservation is atomic

- **WHEN** `POST /api/v1/inventory/reservations` is called with 3 lines and one line has insufficient inventory
- **THEN** the endpoint returns `409 Conflict` with body `{ "error": "insufficient_inventory", "sku": "..." }`
- **AND** no `inventory_reservations` row is created
- **AND** no `available_quantity` is decremented for any line

#### Scenario: Optimistic concurrency conflict returns 409

- **WHEN** two concurrent `POST /api/v1/inventory/reservations` calls attempt to reserve the last unit of the same SKU
- **THEN** the first call succeeds with `201 Created` and decrements `available_quantity` to 0
- **AND** the second call returns `409 Conflict` with body `{ "error": "version_conflict", "current_version": N }`
- **AND** the second call does NOT decrement `available_quantity` below 0

### Requirement: inventory-service runs a Temporal worker on inventory.reservation.v1

> **Status**: IMPLEMENTED. Temporal worker configured with versioning; workflows and activities registered.

The `inventory-worker` container SHALL open a Temporal client, configure `WorkerDeploymentOptions` with `UseVersioning: true`, `Version.DeploymentName: "inventory-reservation-v1"`, and `Version.BuildID: platformtemporal.DeploymentVersion()`, and register the following workflows and activities on task queue `inventory.reservation.v1`:

- Workflow: `InventoryReservationWorkflow` — runs `InventoryReserveActivity` followed by a `RecordReservationEvent` activity; on failure, the workflow returns a typed `InventoryReservationError`.
- Activity: `InventoryReserveActivity` — calls the `ReserveInventory` command handler with the input `order_id`, `lines`, and `idempotency_key`; returns the `reservation_id` and the per-line state.
- Activity: `InventoryReleaseActivity` — calls the `ReleaseReservation` command handler with the input `reservation_id` and `idempotency_key`; returns the `reservation_id` and `status: "released"`.
- Activity: `InventoryConfirmActivity` — calls the `ConfirmReservation` command handler with the input `reservation_id` and `idempotency_key`.
- Activity: `RecordReservationEvent` — writes an `inventory_reserved` outbox event.

The worker SHALL start the underlying `worker.Worker` via `worker.New(c, "inventory.reservation.v1", worker.Options{DeploymentOptions: ...})`; activity options SHALL use `platformtemporal.NewValidatedActivityOptions` with `ScheduleToClose=5m`, `StartToClose=30s`, `ScheduleToStart=30s`, `Heartbeat=10s`, and `RetryAttempts=5`. The `InventoryReserveActivity` SHALL call `activity.RecordHeartbeat(ctx, heartbeat)` every 5 seconds during the database transaction to support long-running reservations.

#### Scenario: inventory-worker registers the workflow and activity set

- **WHEN** the `inventory-worker` container starts with `INVENTORY_TEMPORAL_ADDRESS=temporal:7233`, `INVENTORY_TEMPORAL_TASK_QUEUE=inventory.reservation.v1`
- **THEN** the worker registers `InventoryReservationWorkflow` (as `inventory.reservation.v1`) and the four activities on task queue `inventory.reservation.v1`
- **AND** the worker registers with `DeploymentSeriesName: "inventory-reservation-v1"` and `BuildID: <PLATFORM_DEPLOYMENT_VERSION or GIT_SHA or "dev">`
- **AND** the `/health/ready` endpoint returns `200 OK` within 5 seconds of registration

### Requirement: Inventory reservation is idempotent and uses stable operation_id

> **Status**: IMPLEMENTED. Operation ID derived from workflow ID; idempotency checks in place.

The `InventoryReserveActivity` SHALL derive a stable `operation_id` from the workflow ID using `platformtemporal.OperationIDFor(workflowID, "inventory.reserve")`. The activity body SHALL check `inventory_reservations` for a row with `operation_id` matching before performing the side effect. If a row exists with `status="reserved"`, the activity returns the cached result. Concurrent invocations of the same `operation_id` SHALL be serialized by a row-level lock on `inventory_idempotency_keys`.

#### Scenario: Inventory reservation is idempotent across retries

- **WHEN** `InventoryReserveActivity` is invoked twice with the same `operation_id` and the first invocation succeeded
- **THEN** the second invocation observes the prior result and returns `nil` without performing a second reservation
- **AND** no duplicate row is inserted into `inventory_reservations`
- **AND** no duplicate outbox event is emitted on `inventory.events.v1`

### Requirement: Inventory reservation uses the saga pattern with typed errors

> **Status**: IMPLEMENTED. Saga pattern implemented with forward and compensation tracking.

The `InventoryReservationWorkflow` SHALL use `platformtemporal.NewSaga` for forward and compensation tracking. On `NonRetryableApplicationError` from the forward path, the workflow runs `InventoryReleaseActivity` with the original `operation_id` to release the reservation. Compensation failures SHALL be recorded as `CompensationFailureV1` events.

#### Scenario: Successful inventory reservation

- **WHEN** `InventoryReservationWorkflow` is started with a valid `order_id` and the reservation succeeds
- **THEN** the workflow runs `InventoryReserveActivity` → `RecordReservationEvent` in forward order
- **AND** no compensation activities run

#### Scenario: Failed reservation triggers compensation

- **WHEN** `InventoryReserveActivity` succeeds but `RecordReservationEvent` fails
- **THEN** the workflow runs the compensation path: `InventoryReleaseActivity` with the original `operation_id`
- **AND** the reservation is released and the `available_quantity` is restored

### Requirement: inventory-service has an ADR documenting the extraction

> **Status**: IMPLEMENTED. ADR exists at docs/adr/0001-service-extraction.md with 5-point format.

`services/inventory-service/docs/adr/0001-service-extraction.md` SHALL follow the 5-point admission format. The architecture test SHALL assert the file exists and contains the five required sections.

#### Scenario: inventory-service ADR exists and passes the architecture test

- **WHEN** the architecture test scans for the ADR
- **THEN** the test verifies the file exists and contains `## Problem`, `## Considered Alternative`, `## Owner`, `## Integration Boundary`, `## Failure Mode`

### Requirement: inventory-service is exposed via docker-compose overlay

> **Status**: IMPLEMENTED. Docker Compose overlay exists with all required containers and dependencies.

The `deploy/docker-compose.inventory-service.yaml` overlay SHALL add the `inventory-migrate`, `inventory-api`, `inventory-worker`, `inventory-infrastructure-init`, and `inventory-topics-init` containers. The `inventory-topics-init` container creates the `inventory.events.v1` topic with 3 partitions. The `inventory-api` container SHALL bind `:8084` and `:9094`. The `inventory-worker` container SHALL depend on `temporal: condition: service_healthy`.

#### Scenario: inventory-service containers start in dependency order

- **WHEN** `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.inventory-service.yaml up -d` runs
- **THEN** the `inventory-topics-init` container completes before `inventory-api` starts
- **AND** the `inventory-migrate` container completes before `inventory-api` starts
- **AND** the `inventory-worker` container starts only after `temporal` is `service_healthy` and `inventory-migrate` has completed
