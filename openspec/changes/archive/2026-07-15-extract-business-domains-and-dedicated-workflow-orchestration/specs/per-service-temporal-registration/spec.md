# per-service-temporal-registration Specification

## Purpose
Every service that runs a Temporal worker SHALL have a `cmd/<service>/run.go` `runWorker` role (or equivalent, e.g., `cmd/<service>/main.go` with a `worker` subcommand) that (a) reads its `WorkerDeploymentOptions` from env, (b) fails fast if `BuildID` is empty, (c) registers the workflow and activity set on the service's task queue, (d) starts the worker, and (e) exposes a `/health/ready` probe that returns `503` until the worker is registered. This applies to all eight services in the platform. Today only `order-service` has a fully-wired worker (`services/order-service/internal/adapters/temporal/worker.go`); the other seven services have either partial wiring (`notification-service` has `adapters/temporal/worker.go::NewWorker` defined but not called; `customer-service` and `catalog-service` have workflows defined but no `worker.New` invocation; `reporting-service` has `// TODO: Implement Temporal worker registration` in `internal/runtime/wire.go::newTemporalWorker`) or stub `runWorker` roles that only open a Temporal client. This change SHALL complete the wiring for all eight.

## ADDED Requirements

### Requirement: Every service has a runWorker role

Each service's `cmd/<service>/` SHALL have a `runWorker` function. The function:

1. Loads the service's `Config` with the role-aware config loader (e.g., `config.Load(config.RoleWorker)`).
2. Reads the Temporal connection settings: `cfg.Temporal.Address` (default `localhost:7233`), `cfg.Temporal.Namespace` (default `default`), `cfg.Temporal.TaskQueue` (default per service, see table below).
3. Derives the `BuildID` via `platformtemporal.DeploymentVersion()` (which reads `PLATFORM_DEPLOYMENT_VERSION` → `GIT_SHA` → `dev` in that order, per `platform/temporal/deployment.go`); fails fast with a non-zero exit and stderr message `FAIL: DeploymentVersion is empty` if no source produces a value.
4. Opens a Temporal client via the official SDK (`temporalclient.NewLazyClient(...)`).
5. Constructs the `worker.Worker` via `worker.New(c, taskQueue, opts)`, where `opts.DeploymentOptions.UseVersioning = true` and `opts.DeploymentOptions.Version.DeploymentName` matches the service's task queue.
6. Calls `w.RegisterWorkflowWithOptions(...)` for each workflow in the service's workflow set and `w.RegisterActivityWithOptions(...)` for each activity.
7. Starts the worker with `w.Start()`; blocks on `<-ctx.Done()`; calls `w.Stop()` on shutdown.

The function SHALL expose a `/health/ready` HTTP probe that returns `503 Service Unavailable` until the worker is registered and `200 OK` thereafter.

The canonical task queues per service (matching the actual constants in the codebase) are:

| Service | Task Queue (constant source) | Workflow(s) registered |
|---|---|---|
| `order-service` | `order-fulfillment.v1` (`internal/adapters/temporal/constants.go`) | `OrderFulfillmentWorkflow` (registered as `order.fulfillment.v1`) |
| `payment-service` (new) | `payment.capture.v1` (proposed; no constant today) | `PaymentCaptureWorkflow` (proposed; registered as `payment.capture.v1`) |
| `inventory-service` (new) | `inventory.reservation.v1` (proposed; no constant today) | `InventoryReservationWorkflow` (proposed; registered as `inventory.reservation.v1`) |
| `shipping-service` (new) | `shipping.dispatch.v1` (proposed; no constant today) | `ShippingDispatchWorkflow` (proposed; registered as `shipping.dispatch.v1`) |
| `notification-service` | `notification.dispatch.v1` (`application/orchestration/workflow.go::DispatchTaskQueue`) | `NotificationFulfillmentWorkflow` (registered as `notification.dispatch.v1`) |
| `customer-service` (purge) | `customer.purge.v1` (`application/orchestration/workflow.go::TaskQueuePurge`) | `CustomerPurgeWorkflow` (registered as `customer.purge.v1`) |
| `customer-service` (export) | `customer.gdpr.v1` (`application/orchestration/workflow.go::TaskQueueExport`) | `CustomerGDPRExportWorkflow` (registered as `customer.gdpr.v1`) |
| `reporting-service` | `reporting.admin.v1` (`internal/runtime/config.go::TemporalTaskQueue`) | `DailyRevenueRollupWorkflow` (registered as `ReportingDailyRevenueRollup`) |
| `catalog-service` | `catalog.admin.v1` (`internal/application/orchestration/price_rollback.go::TaskQueue`) | `PriceRollbackWorkflow` (registered as `PriceRollbackWorkflow.v1`) |

A single worker binary SHALL register on all task queues owned by its service. The customer-service's `runWorker` registers workflows on both `customer.purge.v1` and `customer.gdpr.v1`; the other services register on a single task queue.

#### Scenario: order-worker registers the workflow and activity set

- **WHEN** the `order-worker` container starts with `ORDER_TEMPORAL_ADDRESS=temporal:7233`, `ORDER_TEMPORAL_NAMESPACE=default`, `ORDER_TEMPORAL_TASK_QUEUE=order-fulfillment.v1`
- **THEN** the worker registers `OrderFulfillmentWorkflow` (as `order.fulfillment.v1`) and the activity set on task queue `order-fulfillment.v1`
- **AND** the worker registers with `DeploymentSeriesName: "order-fulfillment.v1"` and `BuildID: <PLATFORM_DEPLOYMENT_VERSION or GIT_SHA or "dev">`

#### Scenario: payment-worker registers the workflow and activity set

- **WHEN** the `payment-worker` container starts with `PAYMENT_TEMPORAL_ADDRESS=temporal:7233`, `PAYMENT_TEMPORAL_TASK_QUEUE=payment.capture.v1`
- **THEN** the worker registers `PaymentCaptureWorkflow` (as `payment.capture.v1`) and the activity set on task queue `payment.capture.v1`
- **AND** the worker registers with `DeploymentSeriesName: "payment.capture.v1"` and `BuildID: <...>`

#### Scenario: notification-worker registers the workflow and activity set

- **WHEN** the `notification-worker` container starts with `NOTIFICATION_TEMPORAL_ADDRESS=temporal:7233`, `NOTIFICATION_TEMPORAL_TASK_QUEUE=notification.dispatch.v1`
- **THEN** the worker registers `NotificationFulfillmentWorkflow` (as `notification.dispatch.v1`) and the `Dispatch` activity on task queue `notification.dispatch.v1`

#### Scenario: customer-worker registers the workflow and activity set

- **WHEN** the `customer-worker` container starts with `CUSTOMER_TEMPORAL_ADDRESS=temporal:7233`
- **THEN** the worker registers `CustomerPurgeWorkflow` (as `customer.purge.v1`) on `customer.purge.v1`
- **AND** the worker registers `CustomerGDPRExportWorkflow` (as `customer.gdpr.v1`) on `customer.gdpr.v1`

#### Scenario: reporting-worker registers the workflow and activity set

- **WHEN** the `reporting-worker` container starts with `REPORTING_TEMPORAL_ADDRESS=temporal:7233`, `TEMPORAL_TASK_QUEUE=reporting.admin.v1`
- **THEN** the worker registers `DailyRevenueRollupWorkflow` (as `ReportingDailyRevenueRollup`) and the `DailyRevenueRollupActivity` on task queue `reporting.admin.v1`

#### Scenario: catalog-worker registers the workflow and activity set

- **WHEN** the `catalog-worker` container starts with `CATALOG_TEMPORAL_ADDRESS=temporal:7233`, `TEMPORAL_TASK_QUEUE=catalog.admin.v1`
- **THEN** the worker registers `PriceRollbackWorkflow` (as `PriceRollbackWorkflow.v1`) and the activity on task queue `catalog.admin.v1`

### Requirement: WorkerDeploymentOptions is service-specific

Each service's `runWorker` role SHALL configure `WorkerDeploymentOptions` with:

- `UseVersioning`: `true` (mandatory per the `platform-temporal-versioning` spec; `DeploymentOptions.Validate()` returns an error otherwise, per `platform/temporal/deployment.go`)
- `Version.DeploymentName`: the service's task queue (e.g., `order-fulfillment.v1`, `notification.dispatch.v1`, `customer.purge.v1`)
- `Version.BuildID`: the value returned by `platformtemporal.DeploymentVersion()`

The `deployment.go::DefaultDeploymentOptions()` factory returns `DeploymentOptions{BuildID: DeploymentVersion(), UseVersioning: true, SeriesName: ""}`; services SHALL set `SeriesName` to their task queue before passing to the SDK.

#### Scenario: Worker validates WorkerDeploymentOptions

- **WHEN** the `runWorker` function calls `platformtemporal.DefaultDeploymentOptions().Validate()` (or equivalent) before creating the worker
- **THEN** the validation returns `nil` (the options are valid)
- **AND** the worker is created with `DeploymentOptions{UseVersioning: true, Version: WorkerDeploymentVersion{DeploymentName: "order-fulfillment.v1", BuildID: <DeploymentVersion()>}}`

#### Scenario: Worker fails fast on empty BuildID

- **WHEN** the `runWorker` function is called and `platformtemporal.DeploymentVersion()` returns an empty string (none of `PLATFORM_DEPLOYMENT_VERSION`, `GIT_SHA`, `dev` produces a value)
- **THEN** the function returns exit code 1 and prints `FAIL: DeploymentVersion is empty` to stderr
- **AND** the function does NOT call `temporalclient.NewLazyClient` or `worker.New`

### Requirement: Activity options use the platform's validated defaults

Each activity registration SHALL use `platformtemporal.NewValidatedActivityOptions` with values matching the `platform-temporal-versioning` requirement (StartToClose 30s, ScheduleToClose 5m, ScheduleToStart 30s, Heartbeat 10s for long-running activities, RetryAttempts 5). The helper SHALL return a validation error if any field is zero or if `StartToClose > ScheduleToClose`. The activity options SHALL be applied via `workflow.WithActivityOptions(ctx, workflow.ActivityOptions{...})` in the workflow code (or, for the `order-service`, the existing constants `activityStartToClose = 5 * time.Minute` and `activityHeartbeat = 30 * time.Second` in `services/order-service/internal/adapters/temporal/workflow.go` SHALL be aligned with this default for the new remote activities).

#### Scenario: Activity uses validated default options

- **WHEN** an activity's options are constructed via `platformtemporal.NewValidatedActivityOptions(platformtemporal.ActivityOptions{ScheduleToClose: 5*time.Minute, StartToClose: 30*time.Second, ScheduleToStart: 30*time.Second, Heartbeat: 10*time.Second, RetryAttempts: 5})`
- **THEN** the helper returns a `platformtemporal.ActivityOptions` struct with all five fields set
- **AND** the validation passes (no field is zero)

#### Scenario: Activity with StartToClose greater than ScheduleToClose is rejected

- **WHEN** an activity's options have `StartToClose: 10*time.Minute, ScheduleToClose: 5*time.Minute`
- **THEN** the helper returns a validation error citing the violation

### Requirement: Health probe is wired into the worker lifecycle

The `/health/ready` HTTP probe SHALL return `503 Service Unavailable` while the worker is registering; `200 OK` after registration completes; `503 Service Unavailable` again if the worker stops. The probe SHALL use a `sync/atomic.Bool` (or equivalent) that the worker sets to `true` after registration completes and to `false` on `w.Stop()`. The probe SHALL have a 1-second timeout.

#### Scenario: Health probe returns 503 before registration

- **WHEN** the `runWorker` function is starting and the worker is not yet registered
- **THEN** a GET to `/health/ready` returns `503 Service Unavailable` with body `{ "status": "starting" }`

#### Scenario: Health probe returns 200 after registration

- **WHEN** the worker is registered and running
- **THEN** a GET to `/health/ready` returns `200 OK` with body `{ "status": "ready", "worker": "started", "task_queue": "<service-task-queue>" }`

### Requirement: All eight services have working Temporal workers

After this change is applied, the following eight services SHALL each have a working Temporal worker that registers workflows and activities on the indicated task queue:

| Service | Task Queue | Workflow(s) |
|---|---|---|
| `order-service` | `order-fulfillment.v1` | `OrderFulfillmentWorkflow` |
| `payment-service` | `payment.capture.v1` | `PaymentCaptureWorkflow` |
| `inventory-service` | `inventory.reservation.v1` | `InventoryReservationWorkflow` |
| `shipping-service` | `shipping.dispatch.v1` | `ShippingDispatchWorkflow` |
| `notification-service` | `notification.dispatch.v1` | `NotificationFulfillmentWorkflow` |
| `customer-service` (purge) | `customer.purge.v1` | `CustomerPurgeWorkflow` |
| `customer-service` (export) | `customer.gdpr.v1` | `CustomerGDPRExportWorkflow` |
| `reporting-service` | `reporting.admin.v1` | `DailyRevenueRollupWorkflow` |
| `catalog-service` | `catalog.admin.v1` | `PriceRollbackWorkflow` |

The `platform-temporal-versioning` spec SHALL be updated (via a delta in this change) to require this coverage.

#### Scenario: All nine worker registrations succeed

- **WHEN** the full docker-compose stack is up with all eight overlays (`docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.order-service.yaml -f deploy/docker-compose.payment-service.yaml -f deploy/docker-compose.inventory-service.yaml -f deploy/docker-compose.shipping-service.yaml -f deploy/docker-compose.notification-service.yaml -f deploy/docker-compose.customer-service.yaml -f deploy/docker-compose.reporting-service.yaml -f deploy/docker-compose.catalog-service.yaml up -d`)
- **THEN** `temporal task-queue list` reports nine task queues (one per worker, with `customer.purge.v1` and `customer.gdpr.v1` as separate queues)
- **AND** each worker container's `/health/ready` returns `200 OK` within 30 seconds of stack startup
