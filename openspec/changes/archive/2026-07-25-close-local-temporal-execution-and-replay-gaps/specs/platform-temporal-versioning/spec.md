## ADDED Requirements

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

## MODIFIED Requirements

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
