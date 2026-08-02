# platform-temporal-versioning Specification

## Purpose
Define the platform-wide rules for deterministic Temporal workflows, versioned
worker deployments, stable task queues, activity safety, and operational
recovery across all eight services and nine owned task queues.
## Requirements
### Requirement: Deterministic workflow code

> **Status**: LOCAL IMPLEMENTED. The module-aware repository auditor and
> upstream `workflowcheck` cover every inventoried Workflow owner, fail closed
> on zero discovery, and pass their intentional nondeterminism controls.
> Current-code Event History replay also passes for all registered Workflow
> types. This local status does not assert cloud or CI/CD execution.

Workflow code SHALL be deterministic: it MUST NOT call `time.Now`, MUST NOT
launch goroutines, MUST NOT use `math/rand`, and MUST NOT perform I/O. Workflow
time SHALL come from `workflow.Now`, or a timestamp already recorded in an
Activity result when that timestamp belongs to the side effect.

The platform SHALL provide a module-aware determinism gate that covers every
inventoried Workflow owner, loads the canonical allowlist, reports discovered
packages and Workflow functions, and fails when the inventory is non-empty but
discovery returns zero. Each service `verify-pr` and the root Temporal gate
SHALL run the upstream Temporal `workflowcheck` or an equivalent validated
entry point in addition to the repository inventory check.

#### Scenario: workflowcheck rejects time.Now and goroutines in workflow code

- **WHEN** a Workflow function calls `time.Now()` or launches a goroutine
- **THEN** the determinism gate fails with the offending Workflow, file, and
  line number

#### Scenario: Zero Workflow discovery fails closed

- **WHEN** the canonical inventory contains Workflow owners but the repository
  auditor loads zero Workflow packages or functions
- **THEN** the auditor exits non-zero
- **AND** it reports the unresolved module or package roots

#### Scenario: Determinism negative control proves the gate

- **WHEN** the gate runs its fixture containing an intentional `time.Now`
  violation
- **THEN** both the repository auditor and the upstream checker reject it
- **AND** a cached or skipped analyzer result cannot count as a pass

#### Scenario: workflowcheck allowlist is consistent across services

- **WHEN** a new service with Temporal Workflows is added
- **THEN** it uses the validated root allowlist or an explicitly reviewed
  service-specific configuration
- **AND** missing Workflow-owner coverage fails the root gate

### Requirement: Explicit activity timeouts

Every activity SHALL declare explicit `StartToCloseTimeout` and `ScheduleToCloseTimeout` values; the platform SHALL reject zero-valued timeouts via `platformtemporal.NewValidatedActivityOptions`.

#### Scenario: NewValidatedActivityOptions refuses missing timeouts

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Idempotent activities with stable operation_id

Every activity that mutates external state SHALL derive a stable `operation_id` from the workflow ID and SHALL be safe to retry; the platform SHALL expose `platformtemporal.OperationID(workflowID, suffix)` as the standard helper.

#### Scenario: OperationID is stable across retries

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Typed activity errors
Activities SHALL return typed errors that distinguish retryable, non-retryable, and compensation failures. The Temporal SDK provides `temporal.NewNonRetryableApplicationError` and `temporal.NewRetryableApplicationError` natively; the platform SHALL provide a sibling helper `temporal.NewCompensationApplicationError(type, message, cause)` that wraps an underlying error as a non-retryable error whose `Details` field carries the string `"compensation"` so the platform's saga dispatcher (see the Saga compensation order requirement below) can recognise it and route it to the workflow's compensation branch instead of the workflow's primary failure branch. The Temporal SDK's `RetryPolicy` SHALL treat `NonRetryableApplicationError` as terminal (no retry), `RetryableApplicationError` as retryable per the configured `MaximumAttempts`, and `CompensationApplicationError` (recognised via the `"compensation"` Details tag) as triggering the workflow's compensation path.

#### Scenario: Non-retryable error fails the activity immediately
- **WHEN** the activity returns `temporal.NewNonRetryableApplicationError("invalid_input", "INVALID_ARGUMENT", err)`
- **THEN** Temporal does NOT retry the activity and the workflow receives the error

#### Scenario: Retryable error retries per MaximumAttempts
- **WHEN** the activity returns `temporal.NewRetryableApplicationError("transient", "TRANSIENT", err)`
- **THEN** Temporal retries the activity per the configured policy (default initial interval 1s, max interval 60s, backoff coefficient 2, max attempts 5)

#### Scenario: Compensation error triggers the workflow compensation path
- **WHEN** the activity returns `temporal.NewCompensationApplicationError("...", "...", err)`
- **THEN** Temporal treats the error as terminal and the workflow's compensation branch runs

### Requirement: Saga compensation order

A saga-style workflow SHALL execute activities in forward order and SHALL execute compensations in INVERSE order on non-retryable failure; the platform's `temporal.NewSaga` helper SHALL enforce this invariant.

#### Scenario: Saga compensation enforces inverse-order execution

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Workflow ID reuse policy
A service that starts a workflow in response to an inbound event SHALL use `WorkflowIDReusePolicy: WORKFLOW_ID_REUSE_POLICY_USE_EXISTING` with `WorkflowIDConflictPolicy: WORKFLOW_ID_CONFLICT_POLICY_FAIL` for idempotent event handling. For saga workflows that may legitimately need to be retried after a terminal failure, the service SHALL use `WorkflowIDReusePolicy: WORKFLOW_ID_REUSE_POLICY_ALLOW_DUPLICATE_FAILED_ONLY`.

#### Scenario: Duplicate event with USE_EXISTING short-circuits
- **WHEN** the consumer starts a workflow with `WorkflowIDReusePolicy=USE_EXISTING` and the workflow ID already exists in `Running` state
- **THEN** Temporal returns the existing workflow handle and the consumer treats the result as success

#### Scenario: Terminal failure can be retried
- **WHEN** the consumer starts a workflow with `WorkflowIDReusePolicy=ALLOW_DUPLICATE_FAILED_ONLY` and the prior workflow is in `Failed` state
- **THEN** Temporal starts a new workflow with the same ID

### Requirement: Temporal Schedule API for recurring workflows
A service that needs cron-like scheduling SHALL use Temporal's Schedule API (GA since Server v1.27). The platform SHALL provide a `temporal.NewSchedule(spec, action)` helper that wraps the Schedule creation. The platform SHALL NOT use the legacy Cron API.

#### Scenario: Service schedules a recurring workflow
- **WHEN** the service starts and the schedule does not exist
- **THEN** the platform creates the schedule with the configured spec and the action

#### Scenario: Legacy Cron API is not used
- **WHEN** the architecture test scans the codebase
- **THEN** any reference to `workflow.NewCronSchedule` or the legacy Cron workflow type fails the build

### Requirement: OpenTelemetry context propagation across Temporal
Every Temporal worker SHALL register the OpenTelemetry propagator from `go.temporal.io/sdk/contrib/opentelemetry v0.7.0` and SHALL configure the worker with `EnableSessionWorker` only when sessions are required. The platform SHALL provide a `temporal.NewTelemetryInterceptor(...)` helper that returns the OTel-aware interceptor chain. Workflows and activities started by an instrumented client SHALL carry the caller's trace context into Temporal, and Temporal's headers SHALL include `traceparent` for cross-service propagation.

#### Scenario: Workflow spans propagate to Temporal
- **WHEN** the orchestrator code starts a workflow from an OTel-instrumented HTTP handler
- **THEN** the workflow execution's first span is a child of the handler's span and shares the trace ID

#### Scenario: Activity spans propagate from the workflow
- **WHEN** the workflow invokes an activity
- **THEN** the activity's span is a child of the workflow's current span

### Requirement: Current-code Workflow replay tests

The platform SHALL require every registered Workflow type to ship a
deterministic regression test that uses Temporal
`worker.NewWorkflowReplayer` against at least one JSON Event History generated
by the current implementation. The replayer SHALL register the Workflow under
its current type name and SHALL fail when the current code emits a command
sequence inconsistent with its generated fixture. Same-input execution in
`testsuite.TestWorkflowEnvironment` MAY remain as a behavioral test but MUST NOT
be labeled or accepted as Event History replay.

Event History fixtures SHALL be version controlled under the owning service's
`test/replay/fixtures/temporal/<workflow-type>/` directory. Normal tests
MUST NOT regenerate fixtures. A fixture update SHALL require an explicit
deterministic-behavior review record describing its source execution and the
intentional command change. Fixtures SHALL be generated with synthetic
non-sensitive inputs. Exported history bytes MUST remain immutable; redaction
SHALL apply only to derived summaries and metadata, not by rewriting encoded
history payloads.

#### Scenario: Replay test passes against current-code Event History

- **WHEN** a JSON Event History generated by the current Workflow code is
  replayed against that code
- **THEN** `WorkflowReplayer` completes without nondeterminism
- **AND** the fixture remains unchanged during the test

#### Scenario: Replay detects an unintended command change

- **WHEN** Workflow code reorders, removes, or unintentionally changes an
  Activity, timer, child Workflow, signal, update, or Continue-As-New command
  represented in its current-code fixture
- **THEN** replay fails with a nondeterminism diagnostic
- **AND** the owning service deterministic-replay gate fails

#### Scenario: Same-input rerun is not accepted as replay

- **WHEN** a test only executes a Workflow again in a fresh test environment
- **THEN** it may count as a functional determinism test
- **BUT** it does not satisfy current-code Event History replay coverage

#### Scenario: Fixture generation is explicit

- **WHEN** an engineer intentionally generates a fixture from an isolated clean
  local Temporal execution
- **THEN** the refresh uses a non-default command
- **AND** the change records Workflow ID, run ID, Workflow type, source revision,
  and deterministic-behavior rationale without retaining secrets

#### Scenario: Synthetic history is not post-processed

- **WHEN** an Event History fixture is exported for replay
- **THEN** its Workflow inputs were synthetic and non-sensitive at execution
  time
- **AND** the exported JSON is replayed without payload mutation

#### Scenario: Old history is outside the cutover

- **WHEN** clean-slate preflight finds a local execution produced by the
  previous implementation
- **THEN** the cutover fails before workers start
- **AND** the project-scoped reset removes the old execution and history

### Requirement: Temporal namespace strategy
The platform SHALL use one Temporal namespace per environment (`prod`, `staging`, `dev`). Each service SHALL declare its task queue as `<service>.<role>.vN` and SHALL NOT share task queues across services. The platform SHALL NOT adopt namespace-per-service (the operational overhead outweighs the isolation benefit at the platform's current scale).

#### Scenario: Service uses its own task queue
- **WHEN** a service starts a Temporal worker
- **THEN** the worker registers on the task queue `<service>.<role>.vN` and no other service polls that queue

#### Scenario: Namespace-per-environment is documented
- **WHEN** the service's `local-vs-production.md` is reviewed
- **THEN** the document specifies the namespace per environment and the per-env auth posture

### Requirement: Temporal activity version validation

Every non-empty serialized Workflow and Activity input/output payload SHALL
carry a positive contract-version field. Before performing an external side
effect, each Activity SHALL compare the received version with its registered
version and SHALL return a non-retryable `ErrContractVersionMismatch` when the
version is unsupported. Mutating Activities SHALL combine this validation with
a stable operation ID so retries cannot duplicate a side effect.

Every payload SHALL use the current contract shape and version. Older payload
versions SHALL be rejected before side effects. Removing or repurposing a field
requires updating the current implementation and regenerating clean-slate
fixtures; no old decoder or compatibility plan is required.

#### Scenario: Activity rejects unknown contract version

- **WHEN** an Activity receives an input contract version greater than or
  otherwise unsupported by its registered version
- **THEN** it returns `ErrContractVersionMismatch` as a non-retryable
  Application Error
- **AND** no external side effect runs

#### Scenario: Activity accepts the current contract version

- **WHEN** an Activity receives the current contract version and a stable
  operation ID
- **THEN** it processes the request normally
- **AND** a retry uses the same operation identity

#### Scenario: Old payload version is rejected

- **WHEN** an Activity receives a payload from an older contract version
- **THEN** it returns `ErrContractVersionMismatch` before any external side effect
- **AND** the local clean-slate cutover does not register an older decoder

### Requirement: Force-terminate runbook support

The platform SHALL expose `temporal-workflow terminate --workflow-id=<id>` and
the command SHALL call the Temporal SDK termination API with the configured
namespace, optional run ID, and operator reason. A successful exit SHALL mean
Temporal accepted the termination request. SDK Not Found status SHALL map to
the typed `ErrWorkflowNotFound`; other client or server errors SHALL be returned
without string matching.

The platform SHALL NOT delete a non-local or shared Temporal namespace to clear
a backlog. For the disposable local project only, the documented clean-slate
reset MAY recreate the namespace and its histories before the new workers start.
The retry policy SHALL NOT be lowered below `MaximumAttempts=3`.

#### Scenario: Operator terminates a stuck Workflow

- **WHEN** the operator runs `temporal-workflow terminate` with a running local
  Workflow ID and reason
- **THEN** the command exits zero only after Temporal accepts the request
- **AND** the execution enters `Terminated` state with the reason in Event
  History

#### Scenario: Missing Workflow returns a typed error

- **WHEN** the operator targets a Workflow or run that does not exist in the
  configured namespace
- **THEN** the command exits non-zero
- **AND** the application receives `ErrWorkflowNotFound`

#### Scenario: Temporal transport error is not reported as success

- **WHEN** the Temporal frontend is unavailable or rejects the request
- **THEN** the command exits non-zero with a redacted connection diagnostic
- **AND** it does not report the Workflow as terminated

#### Scenario: Retry policy floor is enforced

- **WHEN** the architecture test scans Activity retry policies
- **THEN** every explicitly bounded retry policy has
  `MaximumAttempts >= 3`

### Requirement: Per-service task queue convention extends to the three new services

The per-service task queue convention SHALL cover the three new services introduced by the `extract-business-domains-and-dedicated-workflow-orchestration` change in addition to the existing services. The full set of per-service task queues (matching the actual constants in the codebase) SHALL be:

| Service | Task Queue (string) | Source |
|---|---|---|
| `order-service` | `order-fulfillment.v1` | `services/order-service/internal/adapters/temporal/constants.go::OrderFulfillmentTaskQueueV1` |
| `payment-service` | `payment.capture.v1` | `services/payment-service/internal/application/orchestration/constants.go::PaymentCaptureWorkflowV1` |
| `inventory-service` | `inventory.reservation.v1` | `services/inventory-service/internal/application/orchestration/constants.go::InventoryReservationWorkflowV1` |
| `shipping-service` | `shipping.dispatch.v1` | `services/shipping-service/internal/adapters/temporal/constants.go::ShippingDispatchWorkflowV1` |
| `notification-service` | `notification.dispatch.v1` | `services/notification-service/internal/application/orchestration/workflow.go::DispatchTaskQueue` |
| `customer-service` (purge) | `customer.purge.v1` | `services/customer-service/internal/application/orchestration/workflow.go::TaskQueuePurge` |
| `customer-service` (export) | `customer.gdpr.v1` | `services/customer-service/internal/application/orchestration/workflow.go::TaskQueueExport` |
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

> **Status**: LOCAL IMPLEMENTED. Static validation confirms explicit versioning
> behavior and valid deployment names in all eight services. Retained local
> kind and Compose acceptance confirm workflow and activity pollers on all nine
> owned task queues and direct execution of every advertised Workflow. This is
> local evidence, not staging or production deployment proof.

Every Temporal worker in every service SHALL register with `UseVersioning: true`, a non-empty `BuildID`, an explicit default versioning behavior, and a service-specific Worker Deployment name. The deployment name is an operational identity independent from the stable task queue, MUST NOT contain the SDK-reserved `.` separator, and SHALL use this mapping:

- `order-service`: `order-fulfillment-v1`
- `payment-service`: `payment-capture-v1`
- `inventory-service`: `inventory-reservation-v1`
- `shipping-service`: `shipping-dispatch-v1`
- `notification-service`: `notification-dispatch-v1`
- `customer-service`: `customer-workflows-v1`
- `reporting-service`: `reporting`
- `catalog-service`: `catalog-admin-v1`

The `BuildID` SHALL be supplied by `platformtemporal.DeploymentVersion()`, which reads `PLATFORM_DEPLOYMENT_VERSION`, then `GIT_SHA`, then the local `dev` fallback. Stable task queues and workflow registration names SHALL NOT be renamed as part of this migration.

#### Scenario: All workers register valid versioned deployments

- **WHEN** the architecture and runtime checks inspect every service worker
- **THEN** each worker uses the mapped deployment name, a non-empty build ID, `UseVersioning: true`, and an explicit supported default versioning behavior
- **AND** both workflow and activity pollers are observable on every owned task queue

#### Scenario: All nine workers register Worker Versioning v2

- **WHEN** architecture and runtime acceptance inspect the nine owned task queues across all eight services
- **THEN** every worker registers with `UseVersioning: true`, the mapped Worker Deployment name, a non-empty build ID, and explicit versioning behavior

#### Scenario: Stable task queues are preserved

- **WHEN** deployment identities migrate from dotted values to the mapped dash-delimited values
- **THEN** existing task queues such as `payment.capture.v1`, `notification.dispatch.v1`, and `customer.purge.v1` remain unchanged

#### Scenario: Invalid deployment name fails before readiness

- **WHEN** a Worker Deployment name contains `.` or another character rejected by the pinned SDK and server
- **THEN** the worker remains unready, startup evidence records the registration error, and deployment acceptance fails

#### Scenario: Local build identity remains deterministic

- **WHEN** neither `PLATFORM_DEPLOYMENT_VERSION` nor `GIT_SHA` is set in an explicitly local development profile
- **THEN** the worker uses `BuildID: "dev"` and continues with versioning enabled

#### Scenario: All nine workers fall back to BuildID="dev" when no env var is set

- **WHEN** local worker containers have no deployment-version or Git-SHA override
- **THEN** `platformtemporal.DeploymentVersion()` supplies `BuildID: "dev"` consistently for every worker

### Requirement: Activity options validation applies to all nine workers

Every Activity execution SHALL apply SDK `workflow.ActivityOptions` derived from
validated platform options. Each Activity SHALL set a positive
`StartToCloseTimeout` and a bounded `ScheduleToCloseTimeout`, with
`StartToCloseTimeout <= ScheduleToCloseTimeout`. `ScheduleToStartTimeout` SHALL
be optional and SHALL be set only when queue-delay failure is an intentional,
documented contract. Each retry policy SHALL set a positive bounded
`MaximumAttempts` of at least three and MAY declare operation-specific
non-retryable error types.

`HeartbeatTimeout` SHALL be optional and SHALL comply with the heartbeat
progress requirement. The platform conversion SHALL map every supplied
validated field, including retry attempts, into the SDK options. It MUST NOT
silently validate a retry count or timeout and then omit it from the SDK
configuration.

Order's existing longer remote-Activity timeouts SHALL remain stable unless
current-code replay and focused behavior tests prove a safe change.
Other services MAY use different positive values when justified by the
operation, but MUST preserve the validation invariants.

#### Scenario: Validated options map every supplied field

- **WHEN** platform Activity options specify Start-To-Close,
  Schedule-To-Close, optional Schedule-To-Start, optional Heartbeat, and retry
  attempts
- **THEN** the converted SDK options contain the same supplied durations
- **AND** the SDK Retry Policy contains the supplied maximum attempts

#### Scenario: Missing execution bound is rejected

- **WHEN** an Activity policy omits Start-To-Close or Schedule-To-Close, uses a
  non-positive duration, or sets Start-To-Close greater than
  Schedule-To-Close
- **THEN** validation fails before the Activity is executed

#### Scenario: Schedule-To-Start remains operation-specific

- **WHEN** an Activity has no requirement to fail solely because worker
  capacity delayed task pickup
- **THEN** its validated policy leaves Schedule-To-Start unset
- **AND** validation still succeeds

#### Scenario: Retry policy is bounded

- **WHEN** an Activity uses the platform policy conversion
- **THEN** its SDK Retry Policy has a finite `MaximumAttempts` of at least three
- **AND** Schedule-To-Close provides an overall execution bound

#### Scenario: Architecture gate covers every Workflow Activity

- **WHEN** the Temporal architecture gate scans Workflow Activity call sites
  across all eight services
- **THEN** every call site uses validated options or an explicitly reviewed
  order-service policy
- **AND** reporting and notification cannot omit their retry and overall
  timeout mappings

### Requirement: Workflow versioning behavior is explicit for new executions

Every registered Workflow SHALL specify a supported Worker Versioning behavior
in its registration options. New local executions SHALL use
`VersioningBehaviorAutoUpgrade`. This behavior is not a compatibility promise
for old workers or old histories; the clean-slate preflight MUST pass before
workers start.

#### Scenario: New Workflow registration is Auto Upgrade

- **WHEN** a new worker registers a Workflow during the clean-slate cutover
- **THEN** its registration explicitly sets
  `VersioningBehaviorAutoUpgrade`
- **AND** its task queue, Workflow type, and Worker Deployment identity remain
  equal to the current inventory

#### Scenario: Unspecified behavior fails verification

- **WHEN** a Temporal Workflow is registered without an explicit supported
  versioning behavior
- **THEN** the Temporal architecture gate fails and identifies the registration

#### Scenario: Old executions are not accepted

- **WHEN** clean-slate preflight finds a prior local Workflow execution
- **THEN** the worker cutover fails before polling
- **AND** the documented project-scoped reset is required

### Requirement: Heartbeat timeouts correspond to progress recording

An Activity SHALL set `HeartbeatTimeout` only when its implementation records
ongoing progress with `activity.RecordHeartbeat`. Heartbeat recording SHALL
occur at meaningful progress boundaries or periodically below the configured
timeout and SHALL stop when the Activity context is canceled.

#### Scenario: Long-running Activity reports progress

- **WHEN** an Activity can run longer than its heartbeat timeout
- **THEN** it records progress more frequently than the timeout
- **AND** a local test observes heartbeat details or timely cancellation

#### Scenario: Short atomic Activity omits heartbeat timeout

- **WHEN** an Activity performs one bounded database or HTTP operation and
  cannot expose intermediate progress
- **THEN** it relies on Start-To-Close and Schedule-To-Close bounds
- **AND** it does not configure a heartbeat timeout that it cannot satisfy

#### Scenario: Cancellation stops heartbeat and side effects

- **WHEN** Temporal cancels a heartbeating Activity
- **THEN** the heartbeat loop exits with the Activity context
- **AND** the Activity does not continue an external side effect after
  cancellation is observed

### Requirement: Custom registrations and worker shutdown fail closed

Every worker that registers a Workflow or Activity with a custom stable name
SHALL set `DisableRegistrationAliasing: true` and SHALL keep the SDK's duplicate
registration checks enabled. Every local worker SHALL configure a bounded
`WorkerStopTimeout`, connect `OnFatalError` to its owning runtime, and make
readiness false after a fatal error or shutdown begins.

#### Scenario: Function-name alias cannot bypass the canonical name

- **WHEN** code attempts to execute a custom-named Workflow or Activity by its
  Go function reference or implicit function name
- **THEN** registration aliasing does not resolve the call
- **AND** architecture verification requires the canonical string constant

#### Scenario: Fatal worker error reaches the owning process

- **WHEN** the SDK invokes `OnFatalError`
- **THEN** readiness becomes false and the role returns the fatal error
- **AND** the worker stops within the configured shutdown budget

#### Scenario: Duplicate canonical name is rejected

- **WHEN** two handlers register the same canonical Workflow or Activity name
- **THEN** worker construction fails before polling
- **AND** the duplicate is not hidden by
  `DisableAlreadyRegisteredCheck`

### Requirement: Nexus version dimensions evolve independently

The platform SHALL track Protobuf schema version, Nexus Service/Operation
version, handler Workflow implementation version, and Worker
build/deployment version as separate dimensions. Workflow patching or Worker
Versioning SHALL NOT be presented as public contract versioning.

#### Scenario: Compatible field is added

- **WHEN** a producer adds a backward-compatible optional Protobuf field
- **THEN** old callers continue to use the existing Service/Operation version
- **AND** contract compatibility and Event History replay tests pass

#### Scenario: Business contract breaks

- **WHEN** a producer changes Operation semantics or payload incompatibly
- **THEN** it registers a new Service or Operation version and Task Queue
- **AND** the old contract remains routable until callers and in-flight
  operations drain

#### Scenario: Workflow implementation changes compatibly

- **WHEN** handler Workflow code changes without a public contract change
- **THEN** Workflow patching or Worker Versioning preserves replay
- **AND** the public Service/Operation version remains unchanged

### Requirement: Nexus identity participates in durable duplicate protection

Every mutating Nexus request SHALL carry a stable operation identity, business
key, contract version, and deterministic request fingerprint into the handler
Workflow and application command. Database idempotency retention SHALL cover
the business retry window and SHALL NOT rely solely on Temporal Namespace
retention or Workflow ID history.

#### Scenario: Exact duplicate is replayed

- **WHEN** an operation with an already committed identity and matching
  fingerprint is replayed
- **THEN** no second aggregate, provider, or outbox mutation occurs
- **AND** the retained result is returned

#### Scenario: Workflow history has expired

- **WHEN** Temporal retention no longer contains the original Workflow but the
  business idempotency window remains active
- **THEN** the database idempotency record still prevents a duplicate side
  effect

#### Scenario: Identity conflicts with new input

- **WHEN** the same operation identity arrives with a different fingerprint
- **THEN** the handler returns a non-retryable idempotency conflict before any
  side effect

### Requirement: Durable payloads are isolated from domain implementation

Every Nexus and handler Workflow input/output recorded in Event History SHALL
use a versioned durable DTO. Private aggregate structs, domain events,
repository types, adapter types, and generated peer-domain aliases SHALL NOT be
serialized into Event History.

#### Scenario: Domain aggregate evolves

- **WHEN** a private Shipment field or invariant changes
- **THEN** existing Workflow histories continue to replay through the durable
  DTO mapping
- **AND** no public contract change is implied unless integration semantics
  changed

#### Scenario: Unsupported durable version is received

- **WHEN** a handler receives an unsupported DTO or contract version
- **THEN** it returns a non-retryable version error before external I/O
- **AND** migration diagnostics include the version dimensions without payload
  secrets

### Requirement: Namespace strategy remains environment-scoped for the pilot

The Nexus pilot SHALL preserve one Temporal Namespace per environment and
service-owned Task Queues. Endpoint abstraction SHALL hide target details from
callers but SHALL NOT be used to claim security isolation that the shared
Namespace does not provide.

#### Scenario: Pilot endpoint is provisioned

- **WHEN** the Shipping endpoint is created in an environment
- **THEN** it targets the Shipping-owned Task Queue in that environment's
  Namespace
- **AND** callers reference only the endpoint and versioned contract

#### Scenario: Stronger isolation is required

- **WHEN** security or organizational requirements require a separate
  Namespace
- **THEN** a separate migration decision updates the context map,
  authorization, endpoint target, and drain plan
- **AND** the pilot does not silently adopt namespace-per-service

