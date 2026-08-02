# worker-placement-policy Specification

## Purpose
This spec defines the Temporal worker placement rule. Each service's worker SHALL live in the same Go module as the service's business logic (no shared `services/workflow-orchestrator/` module), SHALL run as a separate container from the API, SHALL share the service's Postgres database with the API, and SHALL scale independently. The architecture test SHALL verify that every `worker.New` call appears under `services/<name>/cmd/<name>/` and not under any cross-service location.
## Requirements

> **Status**: IMPLEMENTED. Workers live in each service module, run as separate containers, share DB, scale independently, per-service registration.

### Requirement: Worker is in the service's Go module

The Temporal worker for a service SHALL be implemented in the same Go module as the service's business logic. The worker code SHALL live in `services/<service>/cmd/<service>/` (or, for `customer-service` and `reporting-service`, in `services/<service>/internal/runtime/wire.go`). The worker SHALL NOT be implemented in a shared module such as `services/workflow-orchestrator/` or `services/temporal-workers/`. The architecture test SHALL fail if a worker registration call (`w.RegisterWorkflowWithOptions`, `w.RegisterActivityWithOptions`, `workflow.Register`, `workflow.Activity`) appears in any file outside `services/<service>/cmd/<service>/` (where `<service>` matches the task queue's service prefix).

The reserved-prefix test in `services/order-service/test/architecture/layering_test.go::TestHypotheticalPeerServiceCannotImportOrderInternals` already declares `github.com/victory1908/payment-service/`, `github.com/victory1908/inventory-service/`, `github.com/victory1908/shipping-service/` as reserved prefixes. The new modules SHALL use those exact paths.

#### Scenario: order-service worker is in the order-service module

- **WHEN** the architecture test scans for `RegisterWorkflowWithOptions` calls
- **THEN** the test passes if all such calls are in `services/order-service/cmd/order-service/` (or `services/order-service/internal/adapters/temporal/`)
- **AND** the test fails if any such call is in `services/payment-service/`, `services/workflow-orchestrator/`, or `services/temporal-workers/`

#### Scenario: payment-service worker is in the payment-service module

- **WHEN** the architecture test scans for `RegisterWorkflowWithOptions` calls
- **THEN** the test verifies that calls referencing the `payment.capture.v1` task queue are in `services/payment-service/cmd/payment-service/` (or `services/payment-service/internal/adapters/temporal/`)

### Requirement: Worker is in a separate container from the API

The service's worker SHALL be deployed as a separate container from the API. The container's `command` SHALL be `<service>-service worker` (e.g., `order-service worker`, `payment-service worker`); the API's `command` SHALL be `<service>-service api`. The docker-compose overlay SHALL include both containers as separate entries. The worker container SHALL NOT bind the API's HTTP port (e.g., `:8083`); the API container SHALL NOT bind the worker's metrics port. Each container SHALL have its own healthcheck; the worker's healthcheck SHALL target the worker's `/health/ready` endpoint.

#### Scenario: order-worker and order-api are separate containers

- **WHEN** the `deploy/docker-compose.order-service.yaml` overlay is applied
- **THEN** the `order-api` container runs `order-service api` and binds `:8080` and `:9090`
- **AND** the `order-orchestrator` container runs `order-service orchestrator` (no HTTP port bound)
- **AND** the `order-worker` container runs `order-service worker` and binds no API port

#### Scenario: payment-worker and payment-api are separate containers

- **WHEN** the `deploy/docker-compose.payment-service.yaml` overlay is applied
- **THEN** the `payment-api` container runs `payment-service api` and binds `:8083` and `:9093`
- **AND** the `payment-worker` container runs `payment-service worker` and binds no API port

### Requirement: Worker shares the service's database with the API

The worker container SHALL connect to the same Postgres database as the API container, using the same `DATABASE_URL` env var (e.g., `ORDER_DATABASE_URL` for the order-service). The worker SHALL use its own connection pool with a smaller `MaxConnections` (e.g., 10) than the API pool (e.g., 50) to avoid exhausting the database's connection limit. The worker SHALL NOT have a separate database or a separate schema; the schema is owned by the service (per `payment-service`, `inventory-service`, `shipping-service` specs).

#### Scenario: order-worker shares the order service's database

- **WHEN** the `order-worker` container starts with `ORDER_DATABASE_URL=postgres://...` matching the API's `ORDER_DATABASE_URL`
- **THEN** the worker connects to the same `platform` database
- **AND** the worker uses a separate `pgxpool.Pool` with `MaxConnections=10`
- **AND** the worker reads from and writes to the `public` schema (the order service's owned schema, which holds the `orders`, `outbox`, and `idempotency_keys` tables)

#### Scenario: payment-worker shares the payment service's database

- **WHEN** the `payment-worker` container starts with `PAYMENT_DATABASE_URL=postgres://...` matching the API's `PAYMENT_DATABASE_URL`
- **THEN** the worker connects to the same `platform` database
- **AND** the worker uses a separate `pgxpool.Pool` with `MaxConnections=10`
- **AND** the worker reads from and writes to the `payment` schema (the payment service's owned schema)

### Requirement: Worker scales independently of the API

The worker container SHALL be scalable independently of the API container via `docker compose up --scale order-worker=3` (or the equivalent Kubernetes `Deployment` configuration). The platform's `compose-tools-profile` spec SHALL be updated (via a delta in this change) to require that each service's docker-compose overlay includes a `deploy.placement.constraints` block that prefers the worker to run on a different host than the API (for production HA). The smoke test SHALL verify that scaling the worker to 3 replicas does not break the API's request handling.

#### Scenario: Worker scales to 3 replicas

- **WHEN** `docker compose up --scale order-worker=3 -d` runs against the order-service overlay
- **THEN** three `order-worker` containers are started
- **AND** each polls the `order-fulfillment.v1` task queue
- **AND** the API container continues to handle requests without disruption

### Requirement: Worker does not share the API's connection pool instance

The worker's connection pool SHALL be a separate `pgxpool.Pool` from the API's pool, even though both connect to the same database. The pools SHALL NOT share a `*sql.DB` or a `pgxpool.Pool` instance; this prevents accidental transaction sharing. The worker's pool SHALL be sized for the worker's read/write patterns (long-running transactions during workflow execution); the API's pool SHALL be sized for the API's request/response patterns (short-lived transactions). The architecture test SHALL verify that the worker's pool is constructed via a separate `postgres.NewPool(...)` call from the API's pool.

#### Scenario: Worker and API have separate connection pools

- **WHEN** the `runWorker` function and the `runAPI` function are called
- **THEN** each constructs its own `pgxpool.Pool` via `postgres.NewPool(ctx, settings)`
- **AND** the two pools do not share any Go-level state (no `*sql.DB` or `pgxpool.Pool` instance is passed between them)
- **AND** the architecture test verifies the two pools are constructed in separate function calls

### Requirement: Worker registration is per-service code, not a generic factory

Each service's worker registration SHALL be in the service's `cmd/<service>/run.go` `runWorker` function (or a sibling file in the same directory). The registration SHALL NOT be delegated to a generic factory in `platform/temporal/` because the activity set is service-specific. The platform's `temporal.NewFxWorker(...)` helper (in `platform/temporal/worker.go`) is the common foundation; the registration step is per-service code. The architecture test SHALL verify that `RegisterWorkflowWithOptions` and `RegisterActivityWithOptions` calls appear in `services/<service>/cmd/<service>/` and not in `platform/`.

#### Scenario: No generic worker factory in platform/

- **WHEN** the architecture test scans `platform/temporal/` for `RegisterWorkflowWithOptions` or `RegisterActivityWithOptions` calls
- **THEN** the test fails if any such call appears in the `platform/temporal/` package
- **AND** the test passes if all such calls are in `services/<service>/cmd/<service>/`

