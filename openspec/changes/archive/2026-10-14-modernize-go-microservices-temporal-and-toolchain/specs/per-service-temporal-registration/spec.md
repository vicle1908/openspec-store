## MODIFIED Requirements

### Requirement: Every service has a runWorker role

Each service's `cmd/<service>/` SHALL have a `runWorker` function. The function SHALL construct and manage the worker lifecycle using the shared `platformtemporal.NewManagedWorker` abstraction with bounded graceful shutdown. All Temporal workflows and activity registrations SHALL be sourced from the service's driven adapter package at `internal/adapters/temporal/`.

#### Scenario: order-worker registers the workflow and activity set

- **WHEN** the `order-worker` container starts with `ORDER_TEMPORAL_ADDRESS=temporal:7233`, `ORDER_TEMPORAL_NAMESPACE=default`, `ORDER_TEMPORAL_TASK_QUEUE=order-fulfillment.v1`
- **THEN** the worker registers `OrderFulfillmentWorkflow` (as `order.fulfillment.v1`) and the activity set on task queue `order-fulfillment.v1`
- **AND** the worker registers with `DeploymentSeriesName: "order-fulfillment-v1"` and `BuildID: <PLATFORM_DEPLOYMENT_VERSION or GIT_SHA or "dev">`

#### Scenario: payment-worker registers the workflow and activity set

- **WHEN** the `payment-worker` container starts with `PAYMENT_TEMPORAL_ADDRESS=temporal:7233`, `PAYMENT_TEMPORAL_TASK_QUEUE=payment.capture.v1`
- **THEN** the worker registers `PaymentCaptureWorkflow` (as `payment.capture.v1`) and the activity set on task queue `payment.capture.v1`
- **AND** the worker registers with `DeploymentSeriesName: "payment-capture-v1"` and `BuildID: <...>`

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

#### Scenario: Order worker starts with platform managed worker lifecycle
- **WHEN** the `order-worker` container starts with `ORDER_TEMPORAL_TASK_QUEUE=order-fulfillment.v1`
- **THEN** the worker lifecycle is managed via `platformtemporal.NewManagedWorker`
- **AND** the worker exposes fail-closed readiness and bounded graceful termination

## ADDED Requirements

### Requirement: Driven adapter packaging for Temporal bindings

All Temporal workflow declarations, activity handlers, and worker registration adapters SHALL reside in the secondary driven adapter package `internal/adapters/temporal/`. Services SHALL NOT place Temporal SDK imports or workflow logic in `internal/application/orchestration/` or core domain packages.

#### Scenario: Clean hexagonal isolation of Temporal SDK dependencies
- **WHEN** a service implements Temporal workflows or activities
- **THEN** all Temporal SDK types and registration hooks are confined to `internal/adapters/temporal/`
- **AND** the core application domain does not import `go.temporal.io/sdk`
