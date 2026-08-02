## ADDED Requirements

### Requirement: Per-service task queue convention extends to the three new services

The per-service task queue convention SHALL cover the three new services introduced by the `extract-business-domains-and-dedicated-workflow-orchestration` change in addition to the existing services. The full set of per-service task queues (matching the actual constants in the codebase) SHALL be:

| Service | Task Queue (string) | Source |
|---|---|---|
| `order-service` | `order-fulfillment.v1` | `services/order-service/internal/adapters/temporal/constants.go::OrderFulfillmentTaskQueueV1` |
| `payment-service` (new) | `payment.capture.v1` | (proposed; no constant today) |
| `inventory-service` (new) | `inventory.reservation.v1` | (proposed; no constant today) |
| `shipping-service` (new) | `shipping.dispatch.v1` | (proposed; no constant today) |
| `notification-service` | `notification.dispatch.v1` | `services/notification-service/application/orchestration/workflow.go::DispatchTaskQueue` |
| `customer-service` (purge) | `customer.purge.v1` | `services/customer-service/application/orchestration/workflow.go::TaskQueuePurge` |
| `customer-service` (export) | `customer.gdpr.v1` | `services/customer-service/application/orchestration/workflow.go::TaskQueueExport` |
| `reporting-service` | `reporting.admin.v1` | `services/reporting-service/internal/runtime/config.go::TemporalTaskQueue` |
| `catalog-service` | `catalog.admin.v1` | `services/catalog-service/internal/application/orchestration/price_rollback.go::TaskQueue` |

Note the mixed convention: the order-service uses dashes (`order-fulfillment.v1`) while the peer services use dots (`notification.dispatch.v1`, `customer.purge.v1`, etc.). This is a pre-existing inconsistency the new services SHALL NOT replicate; the new services SHALL use the dotted form (`payment.capture.v1`, `inventory.reservation.v1`, `shipping.dispatch.v1`).

The task queue name SHALL be defined as a Go constant in the service's `application/orchestration/` package (or, for the order-service, `internal/adapters/temporal/constants.go`) and SHALL be referenced by both the orchestrator (when starting a workflow) and the worker (when registering the task queue). The task queue name SHALL be supplied to the worker via the service's `<SERVICE>_TEMPORAL_TASK_QUEUE` env var; the worker SHALL fail fast if the env var is empty.

#### Scenario: All nine task queues are defined as constants

- **WHEN** the architecture test scans for Temporal task queue string literals in `services/<service>/application/orchestration/` (or `internal/adapters/temporal/constants.go` for order-service)
- **THEN** the test verifies that all nine task queue names are defined as exported constants
- **AND** the test fails if any of the nine task queue names is hard-coded as a string literal in a non-constant location

#### Scenario: Each worker uses the per-service task queue env var

- **WHEN** a worker container starts with `<SERVICE>_TEMPORAL_TASK_QUEUE` set to the service's task queue
- **THEN** the worker registers the workflow and activity set on that task queue
- **AND** the worker fails fast with `FAIL: missing <SERVICE>_TEMPORAL_TASK_QUEUE env var` if the env var is empty

### Requirement: Worker Versioning v2 adoption is required for all nine workers

Every Temporal worker in every service SHALL register with `UseVersioning: true`, a non-empty `BuildID`, and a service-specific `DeploymentSeriesName` (matching the task queue). The `BuildID` SHALL be supplied by `platformtemporal.DeploymentVersion()`, which reads `PLATFORM_DEPLOYMENT_VERSION` → `GIT_SHA` → `dev` in that order (per `platform/temporal/deployment.go::DeploymentVersion`). The worker SHALL fail fast with `FAIL: DeploymentVersion is empty` if no source produces a value (the default `dev` always produces a value, so this only triggers if the deployment chain is broken).

The `DeploymentSeriesName` mapping is:

- `order-service`: `order-fulfillment.v1`
- `payment-service`: `payment.capture.v1`
- `inventory-service`: `inventory.reservation.v1`
- `shipping-service`: `shipping.dispatch.v1`
- `notification-service`: `notification-dispatch.v1` (per `services/notification-service/application/orchestration/workflow.go::DispatchDeploymentSeries`)
- `customer-service`: `customer.purge.v1` (matches `TaskQueuePurge`)
- `reporting-service`: `reporting` (per `services/reporting-service/adapters/temporal/worker.go::Settings.DeploymentName` default)
- `catalog-service`: `catalog.admin.v1` (matches `services/catalog-service/internal/application/orchestration/price_rollback.go::TaskQueue`)

#### Scenario: All nine workers register Worker Versioning v2

- **WHEN** the architecture test scans for `worker.DeploymentOptions{UseVersioning: true, ...}` in `services/<service>/cmd/<service>/`
- **THEN** the test verifies that all eight services' `runWorker` functions configure the worker with `UseVersioning: true` and a non-empty `BuildID` and `DeploymentSeriesName`

#### Scenario: All nine workers fall back to BuildID="dev" when no env var is set

- **WHEN** any of the nine worker containers starts with `PLATFORM_DEPLOYMENT_VERSION=`, `GIT_SHA=`, and the platform's default `"dev"` applies
- **THEN** the worker uses `BuildID: "dev"` and continues with `UseVersioning: true`
- **AND** the architecture test verifies that the `runWorker` function calls `platformtemporal.DeploymentVersion()` (not a literal `""` or other hard-coded value) before passing to `temporal.NewWorker(...)`

### Requirement: Activity options validation applies to all nine workers

The `platformtemporal.NewValidatedActivityOptions` helper SHALL be used by all nine workers for every activity registration. Every activity SHALL declare explicit timeouts: `StartToCloseTimeout`, `ScheduleToCloseTimeout`, `ScheduleToStartTimeout`, and (for long-running activities) `HeartbeatTimeout`. The default `ScheduleToCloseTimeout` SHALL be 5 minutes; the default `StartToCloseTimeout` SHALL be 30 seconds; the default `ScheduleToStartTimeout` SHALL be 30 seconds; the default `HeartbeatTimeout` (when set) SHALL be 10 seconds. The helper SHALL return a validation error if any field is zero or if `StartToClose > ScheduleToClose` (per `platform/temporal/activity_options.go::Validate`).

The order-service's current activity options are set inline in `services/order-service/internal/adapters/temporal/workflow.go::awaitActivity` with `activityStartToClose = 5 * time.Minute`, `activityHeartbeat = 30 * time.Second`, and `ScheduleToCloseTimeout: activityStartToClose * 2`. These values exceed the platform's defaults (30s StartToClose) but pass the `Validate` invariants (StartToClose < ScheduleToClose). The remote-activity refactor SHALL keep the existing values for the order-service to preserve replay test compatibility; new services SHALL adopt the platform defaults.

#### Scenario: All nine workers use NewValidatedActivityOptions

- **WHEN** the architecture test scans for `w.RegisterActivityWithOptions` calls in `services/<service>/cmd/<service>/`
- **THEN** the test verifies that every such call uses activity options that have passed `platformtemporal.NewValidatedActivityOptions` (or, for the order-service, have explicit validated values matching the invariants)
- **AND** the test fails if any activity is registered with zero timeouts
