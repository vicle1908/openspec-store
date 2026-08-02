# payment-service Specification

## Purpose
A dedicated `payment-service` Go module SHALL own the `payment` Postgres schema, expose a REST HTTP API for payment intents and captures, run its own Temporal worker on task queue `payment.capture.v1`, and emit `payments.events.v1` from its outbox. The service is the sole writer for the `payment` schema; the order-service SHALL call it over HTTP via the platform's instrumented client; the order-worker's saga compensation graph SHALL call the same client's inverse operations. This is the first of three business-domain services (`payment`, `inventory`, `shipping`) extracted from the order-service as part of the dedicated-workflow-orchestration refactor.

## ADDED Requirements

### Requirement: payment-service is an independently deployable Go module

`services/payment-service/` SHALL be a Go module with the same hexagonal layout as the existing peer services (`notification-service`, `customer-service`, `reporting-service`, `catalog-service`): `cmd/payment-service/` (the binary entrypoint), `internal/{domain,application,ports,adapters,runtime,config}` (the layered packages), `migrations/payment/` (the SQL migrations), `proto/payment/v1/` (the protobuf source files) and `contracts/payment/v1/` (the generated Go code), `docs/adr/0001-service-extraction.md` (the extraction ADR), `Dockerfile.payment-service` (the container build), and `test/architecture/layering_test.go` (the hexagonal architecture test). The module path SHALL be `github.com/victory1908/payment-service` (matching the peer services' module path convention; the `/services/` segment is NOT used, mirroring the existing `notification-service`, `customer-service`, `reporting-service`, `catalog-service` modules). The reserved-namespaces test in `services/order-service/test/architecture/layering_test.go` already declares `github.com/victory1908/payment-service/` as a reserved prefix. The module SHALL NOT import any other service's `internal/` package; the architecture test SHALL enforce this. The `go.mod` SHALL NOT have a `replace` directive pointing to another service's module.

#### Scenario: payment-service compiles as a standalone Go module

- **WHEN** a developer runs `cd services/payment-service && go build ./...`
- **THEN** the build succeeds without any `replace` directive pointing to another service's module
- **AND** the architecture test `test/architecture/layering_test.go` reports zero violations

#### Scenario: payment-service does not import another service's internals

- **WHEN** the architecture test scans `services/payment-service/internal/` for forbidden imports
- **THEN** the test fails if any import path matches `github.com/victory1908/order-service/internal/`, `github.com/victory1908/notification-service/internal/`, `github.com/victory1908/customer-service/internal/`, `github.com/victory1908/reporting-service/internal/`, `github.com/victory1908/catalog-service/internal/`, or `github.com/victory1908/services/order-service/internal/`
- **AND** the test also fails if any import path matches `github.com/victory1908/inventory-service/internal/` or `github.com/victory1908/shipping-service/internal/`

### Requirement: payment-service owns the payment Postgres schema and CDC topic

The `payment` schema SHALL contain the `payment_intents`, `payment_captures`, `payment_refunds`, `payment_outbox`, and `payment_idempotency_keys` tables. The `payment` schema is the sole-writer boundary for the payment domain. The CDC connector SHALL publish every row added to `payment_outbox` to the `payments.events.v1` Kafka topic with at-least-once delivery. The `deploy/init-scripts/03-payment-cdc.sql` migration SHALL create the schema, the tables, the Debezium publication, and the publication slot. The `payment-migrate` container in `deploy/docker-compose.payment-service.yaml` SHALL run the migration before any other payment-service container starts. The schema SHALL follow the same Debezium-friendly pattern as the existing `deploy/init-scripts/01-orders-cdc.sql` and `02-notifications-cdc.sql`.

#### Scenario: payment-migrate creates the payment schema

- **WHEN** the `payment-migrate` container runs `payment-service migrate up`
- **THEN** the `payment` schema exists with the five tables, the Debezium publication, and the publication slot
- **AND** the `payments.events.v1` topic is created by the `payment-topics-init` container before the service starts

#### Scenario: Outbox event lands on payments.events.v1

- **WHEN** the `CapturePayment` command commits a `payment_captures` row and a `payment_outbox` row in the same transaction
- **THEN** within 5 seconds the Debezium connector publishes the outbox event to `payments.events.v1` with the `payment_capture` event type

### Requirement: payment-service exposes a REST API for payment intents and captures

The `payment-api` container SHALL serve the following REST endpoints on `cfg.HTTP.Address` (default `:8083`):

- `POST /api/v1/payments/intents` — creates a payment intent. Body: `{ contract_version, order_id, amount_minor, currency, customer_id, idempotency_key }`. Response: `201 Created` with `{ contract_version, payment_intent_id, status: "requires_capture" }`. The endpoint SHALL be idempotent on `idempotency_key`; a duplicate request with the same key returns `200 OK` with the original `payment_intent_id`.
- `POST /api/v1/payments/{intent_id}/capture` — captures a previously-created intent. Body: empty. Response: `200 OK` with `{ contract_version, payment_capture_id, status: "captured", captured_at }`. The endpoint SHALL return `409 Conflict` if the intent is already captured or refunded.
- `POST /api/v1/payments/{capture_id}/refund` — refunds a captured payment. Body: `{ contract_version, amount_minor, reason }`. Response: `200 OK` with `{ contract_version, payment_refund_id, status: "refunded" }`. The endpoint SHALL return `409 Conflict` if the capture is already refunded.
- `GET /api/v1/payments/{intent_id}` — returns the current state of the intent and any associated captures and refunds.
- `GET /health/live`, `GET /health/ready`, `GET /health/startup`, `GET /metrics` — standard platform health and metrics endpoints.

The `idempotency_key` header on every write endpoint SHALL be recorded in the `payment_idempotency_keys` table; a duplicate request SHALL be detected by a unique index on `(endpoint, idempotency_key)` and SHALL return the cached response.

#### Scenario: Payment intent creation is idempotent on idempotency_key

- **WHEN** `POST /api/v1/payments/intents` is called twice with the same `idempotency_key` and the same body
- **THEN** the second call returns `200 OK` with the same `payment_intent_id` as the first call
- **AND** no second row is inserted into `payment_intents`

#### Scenario: Duplicate capture returns 409

- **WHEN** `POST /api/v1/payments/{intent_id}/capture` is called twice
- **THEN** the first call returns `200 OK` with `status: "captured"`
- **AND** the second call returns `409 Conflict` with body `{ "error": "intent_already_captured", "intent_id": "..." }`

### Requirement: payment-service runs a Temporal worker on payment.capture.v1

The `payment-worker` container SHALL open a Temporal client using `temporalclient.NewLazyClient(...)`, configure `WorkerDeploymentOptions` with `UseVersioning: true`, `Version.DeploymentName: "payment.capture.v1"`, and `Version.BuildID: platformtemporal.DeploymentVersion()`, and register the following workflows and activities on task queue `payment.capture.v1`:

- Workflow: `PaymentCaptureWorkflow` — runs `PaymentCaptureActivity` followed by a `RecordCaptureEvent` activity; on failure, the workflow returns a typed `PaymentCaptureError`.
- Activity: `PaymentCaptureActivity` — calls the `CapturePayment` command handler with the input `payment_intent_id` and `idempotency_key`; returns the `payment_capture_id` and `captured_at`.
- Activity: `PaymentRefundActivity` — calls the `RefundPayment` command handler with the input `payment_capture_id`, `amount_minor`, and `idempotency_key`; returns the `payment_refund_id`.
- Activity: `RecordCaptureEvent` — writes a `payment_capture` outbox event in the same transaction as the capture state change.

The worker SHALL start the underlying `worker.Worker` via `worker.New(c, "payment.capture.v1", worker.Options{DeploymentOptions: ...})`. The activity options SHALL use `platformtemporal.NewValidatedActivityOptions` with `ScheduleToClose=5m`, `StartToClose=30s`, `ScheduleToStart=30s`, `Heartbeat=10s`, and `RetryAttempts=5`. The worker SHALL fail-fast and exit non-zero if `platformtemporal.DeploymentVersion()` returns an empty string.

#### Scenario: payment-worker registers the workflow and activity set

- **WHEN** the `payment-worker` container starts with `PAYMENT_TEMPORAL_ADDRESS=temporal:7233`, `PAYMENT_TEMPORAL_TASK_QUEUE=payment.capture.v1`
- **THEN** the worker registers `PaymentCaptureWorkflow` (as `payment.capture.v1`) and `PaymentCaptureActivity`, `PaymentRefundActivity`, `RecordCaptureEvent` on task queue `payment.capture.v1`
- **AND** the worker registers with `DeploymentSeriesName: "payment.capture.v1"` and `BuildID: <PLATFORM_DEPLOYMENT_VERSION or GIT_SHA or "dev">`
- **AND** the `/health/ready` endpoint returns `200 OK` within 5 seconds of registration

#### Scenario: payment-worker fails fast on empty DeploymentVersion

- **WHEN** the `payment-worker` container starts with no `PLATFORM_DEPLOYMENT_VERSION`, no `GIT_SHA`, and the platform's `osGetenv("PLATFORM_DEPLOYMENT_VERSION")` and `osGetenv("GIT_SHA")` are both empty
- **THEN** the worker falls back to `"dev"` (per `platform/temporal/deployment.go::DeploymentVersion()` default)
- **AND** the worker exits with non-zero status only if the deployment version lookup chain is broken; the default `"dev"` is acceptable for local dev

### Requirement: Payment-capture activity is idempotent and uses stable operation_id

The `PaymentCaptureActivity` SHALL derive a stable `operation_id` from the workflow ID using `platformtemporal.OperationIDFor(workflowID, "payment.capture")` (the platform's SHA-256-based helper from `platform/temporal/operation_id.go`). The activity input SHALL include the `operation_id`; the activity body SHALL check `payment_captures` for a row with `operation_id` matching before performing the side effect. If a row with the same `operation_id` exists with `status="captured"`, the activity returns the cached result and `nil`. If the row exists with `status="failed"`, the activity returns the cached error. The activity SHALL use a `BeginTx` / `CommitTx` block to make the read-then-write atomic; concurrent invocations of the same `operation_id` SHALL be serialized by a row-level lock on the `payment_idempotency_keys` table.

#### Scenario: Payment capture is idempotent across retries

- **WHEN** `PaymentCaptureActivity` is invoked twice with the same `operation_id` and the first invocation succeeded
- **THEN** the second invocation observes the prior result in `payment_captures` and returns `nil` without performing a second capture
- **AND** no duplicate row is inserted into `payment_captures`
- **AND** no duplicate outbox event is emitted on `payments.events.v1`

#### Scenario: Concurrent invocations of the same operation_id are serialized

- **WHEN** two `PaymentCaptureActivity` invocations with the same `operation_id` are in-flight simultaneously
- **THEN** the first invocation acquires the row lock on `payment_idempotency_keys` and proceeds
- **AND** the second invocation blocks on the lock and proceeds after the first commits
- **AND** only one `payment_captures` row is created

### Requirement: Payment-capture uses the saga pattern with typed errors

The `PaymentCaptureActivity` SHALL return typed errors that distinguish retryable, non-retryable, and compensation failures per the `platform-temporal-versioning` requirement. The `PaymentCaptureWorkflow` SHALL use `platformtemporal.NewSaga` to track the forward and compensation activities. On `NonRetryableApplicationError`, the saga runs the inverse-order compensation: if `RecordCaptureEvent` failed after `PaymentCaptureActivity` succeeded, the workflow runs the `PaymentRefundActivity` with the same `operation_id` to reverse the capture. Compensation failures SHALL be recorded as `CompensationFailureV1` events for human intervention.

#### Scenario: Successful payment capture

- **WHEN** `PaymentCaptureWorkflow` is started with a valid `payment_intent_id` and the capture succeeds
- **THEN** the workflow runs `PaymentCaptureActivity` → `RecordCaptureEvent` in forward order
- **AND** no compensation activities run
- **AND** the workflow completes with the result of `RecordCaptureEvent`

#### Scenario: Failed capture triggers compensation

- **WHEN** `PaymentCaptureActivity` succeeds but `RecordCaptureEvent` fails with `NonRetryableApplicationError`
- **THEN** the workflow runs the compensation path: `PaymentRefundActivity` with the original `operation_id`
- **AND** the workflow completes with the result of the compensation (refund ID or compensation error)

### Requirement: payment-service has an ADR documenting the extraction

The `services/payment-service/docs/adr/0001-service-extraction.md` file SHALL exist and SHALL follow the 5-point admission format (Problem / Considered Alternative / Owner / Integration Boundary / Failure Mode) used by the existing `order-service/docs/adr/0004-optional-infrastructure.md`. The architecture test in `services/payment-service/test/architecture/` SHALL assert the file exists and contains the five required sections.

#### Scenario: payment-service ADR exists and passes the architecture test

- **WHEN** the architecture test scans for `services/payment-service/docs/adr/0001-service-extraction.md`
- **THEN** the test verifies the file exists and contains sections `## Problem`, `## Considered Alternative`, `## Owner`, `## Integration Boundary`, `## Failure Mode`
- **AND** the test fails if any section is missing or empty

### Requirement: payment-service is exposed via docker-compose overlay

The `deploy/docker-compose.payment-service.yaml` overlay SHALL add the following containers: `payment-migrate` (runs migrations, completes successfully once), `payment-api` (HTTP API on `:8083`, metrics on `:9093`), `payment-worker` (Temporal worker on task queue `payment.capture.v1`, with `PAYMENT_TEMPORAL_*` env vars), `payment-infrastructure-init` (placeholder that prints `payment-service infrastructure init: ok`), `payment-topics-init` (creates the `payments.events.v1` Kafka topic with 3 partitions, matching the partition count used by `orders.events.v1` and `notifications.events.v1`). The overlay SHALL set `PAYMENT_DATABASE_URL=postgres://platform:platform_secret@postgres:5432/platform?sslmode=disable` and `PAYMENT_KAFKA_BROKERS=kafka:29092`. The overlay SHALL depend on `temporal: condition: service_healthy` for the `payment-worker` container.

#### Scenario: payment-service containers start in dependency order

- **WHEN** `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.payment-service.yaml up -d` runs
- **THEN** the `payment-topics-init` container completes before `payment-api` starts
- **AND** the `payment-migrate` container completes before `payment-api` starts
- **AND** the `payment-api` container starts only after `postgres` is `service_healthy` and `kafka` is `service_healthy`
- **AND** the `payment-worker` container starts only after `temporal` is `service_healthy` and `payment-migrate` has completed
