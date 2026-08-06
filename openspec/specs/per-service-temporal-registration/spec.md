# per-service-temporal-registration Specification

## Purpose
This spec defines how each service registers its workflows and activities on its own Temporal task queue. Every service's `runWorker` role SHALL connect to the Temporal server, register its workflow functions on its assigned task queue, and register its activity implementations with explicit activity options (`StartToCloseTimeout`, `ScheduleToCloseTimeout`, retry policy). The registration SHALL use the platform's `platformtemporal.NewValidatedActivityOptions` helper so missing or invalid timeouts fail the worker boot.
## Requirements

> **Status**: LOCAL IMPLEMENTED. The self-hosted topology bootstraps the
> application namespace before workers, and retained local kind and Compose
> acceptance confirm workflow and activity pollers on all nine owned task
> queues plus direct execution of every advertised Workflow. This evidence does
> not establish staging or production readiness.
>
> **Acceptance evidence:** `make dev-up`, `make dev-smoke`, and `make validate-deployment` must pass for the target commit. Retain the `go-microservices.deployment-validation/v1` manifest at `artifacts/deployment-validation/<run-id>/manifest.json` (or the configured artifact root) with namespace bootstrap and task-queue/worker readiness results.

### Requirement: Every service has a runWorker role

> **Status**: LOCAL IMPLEMENTED. Worker entry points, dependency-complete
> registrations, lifecycle behavior, pollers, and direct Workflow execution
> are verified across all eight services.

Each service's `cmd/<service>/` SHALL have a `runWorker` function. The function:

1. Loads the service's `Config` with the role-aware config loader (e.g., `config.Load(config.RoleWorker)`).
2. Reads the Temporal connection settings: `cfg.Temporal.Address` (default `localhost:7233`), `cfg.Temporal.Namespace` (default `default`), `cfg.Temporal.TaskQueue` (default per service, see table below).
3. Derives the `BuildID` via `platformtemporal.DeploymentVersion()` (which reads `PLATFORM_DEPLOYMENT_VERSION` → `GIT_SHA` → `dev` in that order, per `platform/temporal/deployment.go`); fails fast with a non-zero exit and stderr message `FAIL: DeploymentVersion is empty` if no source produces a value.
4. Opens a Temporal client via the official SDK (`temporalclient.NewLazyClient(...)`).
5. Constructs the `worker.Worker` via `worker.New(c, taskQueue, opts)`, where `opts.DeploymentOptions.UseVersioning = true`, the default versioning behavior is explicit, and `opts.DeploymentOptions.Version.DeploymentName` is the service's SDK-valid deployment identity rather than the task queue.
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
| `notification-service` | `notification.dispatch.v1` (`internal/application/orchestration/workflow.go::DispatchTaskQueue`) | `NotificationFulfillmentWorkflow` (registered as `notification.dispatch.v1`) |
| `customer-service` (purge) | `customer.purge.v1` (`internal/application/orchestration/workflow.go::TaskQueuePurge`) | `CustomerPurgeWorkflow` (registered as `customer.purge.v1`) |
| `customer-service` (export) | `customer.gdpr.v1` (`internal/application/orchestration/workflow.go::TaskQueueExport`) | `CustomerGDPRExportWorkflow` (registered as `customer.gdpr.v1`) |
| `reporting-service` | `reporting.admin.v1` (`internal/runtime/config.go::TemporalTaskQueue`) | `DailyRevenueRollupWorkflow` (registered as `ReportingDailyRevenueRollup`) |
| `catalog-service` | `catalog.admin.v1` (`internal/application/orchestration/price_rollback.go::TaskQueue`) | `PriceRollbackWorkflow` (registered as `PriceRollbackWorkflow.v1`) |

A single worker binary SHALL register on all task queues owned by its service. The customer-service's `runWorker` registers workflows on both `customer.purge.v1` and `customer.gdpr.v1`; the other services register on a single task queue.

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

### Requirement: WorkerDeploymentOptions is service-specific

> **Status**: LOCAL IMPLEMENTED. Explicit per-Workflow registration behavior,
> service-specific deployment identities, and bounded worker lifecycle checks
> pass focused and local runtime verification.

Each service's `runWorker` role SHALL configure `WorkerDeploymentOptions` with:

- `UseVersioning`: `true` (mandatory per the `platform-temporal-versioning` spec; `DeploymentOptions.Validate()` returns an error otherwise, per `platform/temporal/deployment.go`)
- `Version.DeploymentName`: the SDK-valid service deployment identity (e.g., `order-fulfillment-v1`, `notification-dispatch-v1`, `customer-workflows-v1`), independent from the stable task queue
- `Version.BuildID`: the value returned by `platformtemporal.DeploymentVersion()`

The `deployment.go::DefaultDeploymentOptions()` factory returns `DeploymentOptions{BuildID: DeploymentVersion(), UseVersioning: true, SeriesName: ""}`; services SHALL set `SeriesName` to their task queue before passing to the SDK.

#### Scenario: Worker validates WorkerDeploymentOptions

- **WHEN** the `runWorker` function calls `platformtemporal.DefaultDeploymentOptions().Validate()` (or equivalent) before creating the worker
- **THEN** the validation returns `nil` (the options are valid)
- **AND** the worker is created with `DeploymentOptions{UseVersioning: true, Version: WorkerDeploymentVersion{DeploymentName: "order-fulfillment-v1", BuildID: <DeploymentVersion()>}}`

#### Scenario: Worker fails fast on empty BuildID

- **WHEN** the `runWorker` function is called and `platformtemporal.DeploymentVersion()` returns an empty string (none of `PLATFORM_DEPLOYMENT_VERSION`, `GIT_SHA`, `dev` produces a value)
- **THEN** the function returns exit code 1 and prints `FAIL: DeploymentVersion is empty` to stderr
- **AND** the function does NOT call `temporalclient.NewLazyClient` or `worker.New`

### Requirement: Activity options use the platform's validated defaults

> **Status**: LOCAL IMPLEMENTED. Shared option validation, complete SDK
> conversion, bounded retries, and heartbeat-policy invariants are verified
> across all inventoried Activity call sites.

Each activity registration SHALL use `platformtemporal.NewValidatedActivityOptions` with values matching the `platform-temporal-versioning` requirement (StartToClose 30s, ScheduleToClose 5m, ScheduleToStart 30s, Heartbeat 10s for long-running activities, RetryAttempts 5). The helper SHALL return a validation error if any field is zero or if `StartToClose > ScheduleToClose`. The activity options SHALL be applied via `workflow.WithActivityOptions(ctx, workflow.ActivityOptions{...})` in the workflow code (or, for the `order-service`, the existing constants `activityStartToClose = 5 * time.Minute` and `activityHeartbeat = 30 * time.Second` in `services/order-service/internal/adapters/temporal/workflow.go` SHALL be aligned with this default for the new remote activities).

#### Scenario: Activity uses validated default options

- **WHEN** an activity's options are constructed via `platformtemporal.NewValidatedActivityOptions(platformtemporal.ActivityOptions{ScheduleToClose: 5*time.Minute, StartToClose: 30*time.Second, ScheduleToStart: 30*time.Second, Heartbeat: 10*time.Second, RetryAttempts: 5})`
- **THEN** the helper returns a `platformtemporal.ActivityOptions` struct with all five fields set
- **AND** the validation passes (no field is zero)

#### Scenario: Activity with StartToClose greater than ScheduleToClose is rejected

- **WHEN** an activity's options have `StartToClose: 10*time.Minute, ScheduleToClose: 5*time.Minute`
- **THEN** the helper returns a validation error citing the violation

### Requirement: Health probe is wired into the worker lifecycle

> **Status**: LOCAL IMPLEMENTED. Local readiness proves namespace and poller
> convergence, and direct execution acceptance proves every advertised
> Workflow reaches its expected terminal state.

The `/health/ready` HTTP probe SHALL return `503 Service Unavailable` while the worker is registering; `200 OK` after registration completes; `503 Service Unavailable` again if the worker stops. The probe SHALL use a `sync/atomic.Bool` (or equivalent) that the worker sets to `true` after registration completes and to `false` on `w.Stop()`. The probe SHALL have a 1-second timeout.

#### Scenario: Health probe returns 503 before registration

- **WHEN** the `runWorker` function is starting and the worker is not yet registered
- **THEN** a GET to `/health/ready` returns `503 Service Unavailable` with body `{ "status": "starting" }`

#### Scenario: Health probe returns 200 after registration

- **WHEN** the worker is registered and running
- **THEN** a GET to `/health/ready` returns `200 OK` with body `{ "status": "ready", "worker": "started", "task_queue": "<service-task-queue>" }`

### Requirement: All eight services have working Temporal workers

The following eight services SHALL each have a dependency-complete Temporal
worker that registers and successfully executes the indicated Workflow set on
its owned task queue:

| Service | Task Queue | Workflow(s) |
|---|---|---|
| `order-service` | `order-fulfillment.v1` | `OrderFulfillmentWorkflow` |
| `payment-service` | `payment.capture.v1` | `PaymentCaptureWorkflow`, `PaymentRefundWorkflow` |
| `inventory-service` | `inventory.reservation.v1` | `InventoryReservationWorkflow`, `InventoryReleaseWorkflow`, `InventoryConfirmWorkflow` |
| `shipping-service` | `shipping.dispatch.v1` | `ShippingDispatchWorkflow`, `ShippingCancelWorkflow` |
| `notification-service` | `notification.dispatch.v1` | `NotificationFulfillmentWorkflow` |
| `customer-service` (purge) | `customer.purge.v1` | `CustomerPurgeWorkflow` |
| `customer-service` (export) | `customer.gdpr.v1` | `CustomerGDPRExportWorkflow` |
| `reporting-service` | `reporting.admin.v1` | `DailyRevenueRollupWorkflow` |
| `catalog-service` | `catalog.admin.v1` | `PriceRollbackWorkflow` |

The canonical task queue, Workflow type, Activity type, Workflow ID, and Worker
Deployment names listed above SHALL be the only identities emitted by the new
implementation. Prior local executions using other identities are out of
scope and MUST be absent from the clean local namespace before acceptance.

#### Scenario: All advertised Workflows execute locally

- **WHEN** the canonical eight-service Compose topology completes
  infrastructure readiness and the Temporal execution acceptance runs
- **THEN** every Workflow in the table starts with an isolated idempotent
  fixture and reaches its expected terminal state
- **AND** the result is retained in versioned machine-readable evidence

#### Scenario: Unknown Workflow or Activity fails execution acceptance

- **WHEN** a worker omits an advertised Workflow or an Activity referenced by
  that Workflow
- **THEN** the corresponding execution acceptance entry fails
- **AND** the diagnostic identifies the service, task queue, Workflow type, and
  unhandled type

#### Scenario: Stable routing identities are preserved

- **WHEN** dependency and registration repairs are applied
- **THEN** all existing task queues, type names, Workflow ID schemes, deployment
  names, and local Build ID behavior remain unchanged

### Requirement: Temporal namespace bootstrap precedes workers

Every self-hosted Temporal deployment SHALL register each configured application namespace idempotently after the Temporal frontend becomes ready and before any service worker starts. Schema creation alone MUST NOT satisfy this readiness condition.

#### Scenario: Missing default namespace is created

- **WHEN** the Temporal database schemas and frontend are ready but the configured `default` namespace is absent
- **THEN** the namespace initializer creates `default` with the configured retention period and exits zero only after it can describe the namespace

#### Scenario: Existing namespace is preserved

- **WHEN** the configured namespace already exists with valid settings
- **THEN** the namespace initializer exits zero without deleting the namespace or changing workflow history

#### Scenario: Namespace bootstrap failure blocks workers

- **WHEN** the namespace cannot be described or created within the bounded retry period
- **THEN** the initializer exits non-zero, Temporal-dependent workers do not start, and diagnostics include the Temporal address, namespace, and final error

### Requirement: Worker convergence is part of deployment readiness

Temporal infrastructure readiness SHALL require successful namespace bootstrap,
valid workflow and activity pollers, expected Worker Deployment metadata, and
current routing on every owned task queue. Temporal execution readiness SHALL
additionally require every advertised Workflow to complete its local execution
acceptance. Poller convergence MUST NOT be reported as proof of registered type
completeness or Workflow execution success.

#### Scenario: All service workers converge

- **WHEN** the full eight-service deployment completes startup
- **THEN** all required task queues expose valid workflow and activity pollers
- **AND** infrastructure readiness evidence records deployment name, build ID,
  poller counts, and routing status

#### Scenario: All advertised Workflows pass execution readiness

- **WHEN** infrastructure readiness has passed and local Temporal execution
  acceptance runs
- **THEN** every advertised Workflow reaches its expected terminal state
- **AND** execution readiness evidence records its Workflow ID, run ID, task
  queue, type, terminal state, duration, and result

#### Scenario: Poller-only success remains partial

- **WHEN** all expected pollers are visible but any advertised Workflow has not
  executed successfully
- **THEN** infrastructure readiness may pass
- **BUT** Temporal execution readiness and aggregate local acceptance fail

#### Scenario: Polling errors fail infrastructure readiness

- **WHEN** a worker repeatedly receives namespace, task-queue, or server polling
  errors
- **THEN** the worker remains unready, the deployment readiness command exits
  non-zero, and the polling error is retained in evidence

### Requirement: Worker deployment identity is valid and independent from task queues

Every versioned worker SHALL retain its existing task-queue and workflow registration names while using a service-specific Worker Deployment name that contains no SDK-reserved `.` separator. Every worker SHALL set an explicit default versioning behavior supported by the pinned Temporal Go SDK.

#### Scenario: Stable queue uses a valid deployment identity

- **WHEN** the notification worker polls task queue `notification.dispatch.v1`
- **THEN** its Worker Deployment name is `notification-dispatch-v1`, its task-queue name remains unchanged, and workflow plus activity pollers register successfully

#### Scenario: Invalid deployment identity fails readiness

- **WHEN** a worker is configured with a Worker Deployment name containing `.` or omits its default versioning behavior
- **THEN** startup or registration fails, the worker remains unready, and diagnostics identify the invalid deployment option

### Requirement: Worker registrations are dependency-complete

Every locally advertised Temporal worker SHALL register every Workflow type and
Activity type referenced by its Workflow set. Each registered Activity
implementation SHALL be constructed with its real application handlers,
service-owned persistence adapters, and idempotency dependencies; a zero-value
Activity bundle with nil required dependencies MUST fail worker construction
before polling begins.

#### Scenario: Payment worker constructs real Activities

- **WHEN** the payment worker starts
- **THEN** it registers capture, refund, capture-event, and refund-event
  Activities using an Activity bundle constructed from payment-owned handlers
  and its unit of work
- **AND** executing either payment Workflow does not dereference a nil
  dependency

#### Scenario: Inventory worker constructs real Activities

- **WHEN** the inventory worker starts
- **THEN** it registers reserve, release, confirm, and all referenced
  event-recording Activities using inventory-owned handlers and its unit of work
- **AND** executing any inventory Workflow does not dereference a nil dependency

#### Scenario: Shipping worker constructs real Activities

- **WHEN** the shipping worker starts
- **THEN** it registers dispatch, cancel, and all referenced event-recording
  Activities using shipping-owned handlers and its unit of work
- **AND** executing either shipping Workflow does not dereference a nil
  dependency

#### Scenario: Missing Activity dependency blocks readiness

- **WHEN** a required command handler, repository, unit of work, or idempotency
  dependency is absent during worker construction
- **THEN** worker startup fails with a diagnostic naming the missing dependency
- **AND** the worker does not report a ready poller

### Requirement: Catalog price rollback is a Temporal Workflow

Catalog SHALL register a deterministic `PriceRollbackWorkflow` under the stable
type name `PriceRollbackWorkflow.v1` and register every Activity it invokes on
task queue `catalog.admin.v1`. The Workflow SHALL use Temporal Workflow APIs for
time and Activity execution. It SHALL discover catalog-owned historical price
snapshots through `GetPriceHistory` in stable pages of at most 100, reissue each
selected snapshot through `SetPriceHandler`, preserve its amount, currency, tax
class, and effective window, retain the deterministic cursor and issued-count
progress in Workflow state, and report the actual number of snapshots issued.
Each reissue SHALL use an idempotency key derived from Workflow ID and source
Snapshot ID. The Workflow SHALL Continue-As-New with carried progress after a
bounded page count. It SHALL NOT write another service's schema or bypass the
catalog transactional outbox.

The opaque history cursor SHALL freeze the source set at the rollback
`RequestedAt` cutoff and paginate by deterministic
`effective_at DESC, price_id DESC` keyset order. The repository MUST honor the
cursor; reissued prices created after the cutoff MUST NOT appear in later
discovery pages.

#### Scenario: Catalog worker registers executable types

- **WHEN** the catalog worker starts on `catalog.admin.v1`
- **THEN** it registers `PriceRollbackWorkflow.v1`, snapshot discovery, and
  retry-safe snapshot reissue Activities
- **AND** a local starter can execute the Workflow to its expected terminal
  state

#### Scenario: Catalog Workflow replays current-code deterministically

- **WHEN** a clean-slate price-rollback Event History generated by the current
  catalog worker is replayed
- **THEN** replay completes without a nondeterminism error
- **AND** the Workflow does not call `time.Now`, perform I/O, or invoke an
  Activity implementation directly

#### Scenario: Catalog rollback Activity preserves ownership

- **WHEN** the price-rollback Activity changes catalog state
- **THEN** the change uses catalog-owned application and persistence ports
- **AND** any emitted event follows the catalog transactional-outbox boundary

#### Scenario: Catalog rollback resumes after partial progress

- **WHEN** snapshot reissue fails transiently after at least one snapshot has
  completed
- **THEN** Temporal retries from durable Workflow and Activity history
- **AND** already completed snapshots are not duplicated because each reissue
  uses a stable per-snapshot idempotency key

#### Scenario: Large rollback bounds Event History

- **WHEN** a product has enough price-history pages to reach the configured
  per-run page limit
- **THEN** the Workflow Continues-As-New with its frozen next cursor and issued
  count
- **AND** no completed snapshot is reissued in the new run

#### Scenario: Reissued rows do not shift discovery pagination

- **WHEN** a reissue Activity creates a new price while later source-history
  pages remain
- **THEN** the next opaque cursor continues after the last source tuple inside
  the original request-time cutoff
- **AND** the new price is not rediscovered by the same rollback

### Requirement: Canonical Activity identities are executable and current

Every `ExecuteActivity` call SHALL use the canonical Activity type constant
declared by its owning service. Workers using custom Workflow or Activity names
SHALL set `DisableRegistrationAliasing: true`, SHALL keep duplicate-registration
checking enabled, and SHALL register every canonical type exactly once.

Payment, inventory, and shipping executions SHALL use only their dotted `.v1`
Activity names. Bare names and compatibility wrappers SHALL NOT be registered
or scheduled. The local namespace SHALL be clean before any new execution
starts.

#### Scenario: Canonical peer Activity names match registrations

- **WHEN** architecture verification compares payment, inventory, and shipping
  `ExecuteActivity` call sites with worker registrations
- **THEN** every call uses the matching dotted `.v1` constant
- **AND** no canonical call relies on a function-name alias

#### Scenario: Old Activity identity is rejected

- **WHEN** a Workflow or Activity request uses a bare or otherwise old name
- **THEN** registration aliasing does not resolve it
- **AND** execution fails before any external side effect

#### Scenario: Duplicate registration fails startup

- **WHEN** a worker attempts to register two handlers for the same canonical
  Workflow or Activity type
- **THEN** worker construction fails before polling
- **AND** readiness remains false

### Requirement: Nexus advertisement and handler registration are explicit

A service SHALL declare every Nexus endpoint, Service, Operation, contract
version, handler Workflow, Task Queue, and owning context it advertises. Its
owned Temporal adapter SHALL register each declared handler on the expected
Worker. A service without a Nexus declaration SHALL NOT register an implicit
handler or endpoint.

#### Scenario: Shipping handler is registered

- **WHEN** the Shipping Worker starts with `shipping.commands.v1` enabled
- **THEN** every declared Operation and handler Workflow is registered on the
  owned Task Queue
- **AND** startup evidence matches the context map and generated contract
  inventory

#### Scenario: Declaration and Worker differ

- **WHEN** an advertised Operation has no canonical handler registration or is
  registered under a different durable name
- **THEN** startup fails before readiness
- **AND** diagnostics identify the declaration and observed registration

#### Scenario: Unadvertised service starts

- **WHEN** a service has no Nexus declaration
- **THEN** its existing Workflow and Activity Worker starts normally
- **AND** no empty or implicit Nexus endpoint is created

### Requirement: Local Nexus registration controls handler readiness

Handler readiness SHALL remain false until all declared local handlers,
pollers, Worker build identity, and callback-routing prerequisites converge.
A fatal registration or callback error SHALL make the handler role unready and
stop it within the configured shutdown budget.

#### Scenario: Local poller is absent

- **WHEN** the advertised handler is registered but no local poller serves its
  Task Queue
- **THEN** the handler role returns `503`
- **AND** diagnostics identify the endpoint, Service, Operation, and Task Queue

#### Scenario: Nexus Worker stops

- **WHEN** the Worker stops or reports a fatal error after convergence
- **THEN** handler readiness returns `503`
- **AND** the runtime emits a structured shutdown or fatal-error record

#### Scenario: Remote provider is unavailable to a caller

- **WHEN** a caller Worker remains locally registered but a remote endpoint is
  unavailable
- **THEN** caller Worker readiness is based on its local ability to accept and
  durably process work
- **AND** remote availability is reported through dependency and circuit state

### Requirement: Legacy Temporal placement is inventoried and frozen

Every Temporal-using service SHALL identify whether its Workflow/Activity
wrappers live in the canonical Temporal adapter or in an approved legacy
`internal/application/orchestration` exception. A legacy exception SHALL list
its packages and SHALL NOT add Nexus imports or expand transport-facing
responsibilities.

#### Scenario: Pilot touches a legacy Shipping package

- **WHEN** the Shipping pilot modifies a Workflow, Activity wrapper, or
  registration
- **THEN** the touched code moves to or is implemented in the canonical
  Temporal adapter
- **AND** application commands remain executable through in-memory ports

#### Scenario: Unlisted legacy package imports Temporal

- **WHEN** a non-adapter package outside the approved legacy inventory imports
  a Temporal SDK subpackage
- **THEN** registration/architecture validation fails

