## ADDED Requirements

### Requirement: Worker Versioning v2 adoption
Every Temporal worker SHALL adopt Worker Versioning v2 (the build-ID-based deployment versioning model that became GA in Temporal Server v1.30+). The platform SHALL configure each worker's `WorkerDeploymentOptions` with a `DeploymentSeriesName` matching the convention `<service>-<worker>.vN` (e.g., `order-fulfillment.v1`, `order-fulfillment.v2`). The platform SHALL provide a `runtime.DeploymentVersion(...)` helper that returns the worker's build ID at startup and SHALL fail-fast if the build ID is empty. The platform SHALL provide a routing helper that picks the right worker deployment for new workflow starts based on configuration.

#### Scenario: Worker registers with a deployment series
- **WHEN** a Temporal worker starts
- **THEN** it registers with the configured `DeploymentSeriesName` and a non-empty build ID

#### Scenario: New workflow starts use the routing configuration
- **WHEN** the orchestrator code calls `Temporal.StartWorkflow(...)` with `UseVersioning=true`
- **THEN** the start routes to the deployment specified by the routing configuration

#### Scenario: Old workflow continues on the old deployment
- **WHEN** a workflow that started under `<service>-<worker>.v1` receives a signal
- **THEN** the signal is delivered to a worker registered under `<service>-<worker>.v1` (or a worker with `ramping-version=<service>-<worker>.v2` and `ramp.percent=0`)

### Requirement: Deterministic workflow code
Workflow code SHALL call only Temporal SDK APIs that are deterministic. The platform SHALL provide a `workflowaudit` static-analysis tool. `workflowaudit` lives at `tools/workflowaudit/` in the repository root (it is a standalone Go binary in the monorepo's `tools/` directory, NOT inside the `platform/` module — putting it in `platform/` would force every service that doesn't use Temporal to take a `go.temporal.io/sdk` dependency transitively). The tool walks the workflow source tree of the service under test (supplied via `--service-root` or via `make workflow-audit`) and fails the build if any of the following appear in a workflow function: `time.Now`, `time.Since`, `time.Until`, `math/rand`, `crypto/rand`, `os.Getenv`, `os.Args`, `net.LookupHost`, `net.Dial`, `http.Get`, `http.Post`, `database/sql.Open`, `pgx.Connect`, goroutines (`go func()`) outside of `workflow.Go`, channels (`make(chan ...)`) outside of `workflow.Channel`, `context.Background()`, `context.TODO()`. Workflow code SHALL use `workflow.Now(ctx)`, `workflow.SideEffect`, `workflow.DeterministicKeys`, `workflow.NewChannel`, `workflow.Go`, and the SDK's deterministic helpers.

#### Scenario: Workflow using time.Now is rejected
- **WHEN** `workflowaudit` walks the workflow source tree
- **THEN** any reference to `time.Now` inside a function whose first argument is `workflow.Context` fails the build

#### Scenario: Workflow spawning a goroutine is rejected
- **WHEN** `workflowaudit` walks the workflow source tree
- **THEN** any `go func()` call inside a workflow function fails the build

#### Scenario: Workflow using context.Background is rejected
- **WHEN** `workflowaudit` walks the workflow source tree
- **THEN** any `context.Background()` or `context.TODO()` inside a workflow function fails the build

### Requirement: Explicit activity timeouts
Every Temporal activity SHALL declare explicit timeouts in its options: `StartToCloseTimeout`, `ScheduleToCloseTimeout`, `ScheduleToStartTimeout` (when applicable), and `HeartbeatTimeout` (when the activity is long-running). The platform SHALL provide a `temporal.NewValidatedActivityOptions(...)` helper that requires every timeout to be set and rejects the zero value. The default `StartToCloseTimeout` SHALL be 30 seconds; the default `ScheduleToCloseTimeout` SHALL be 5 minutes; the default `HeartbeatTimeout` (when set) SHALL be 10 seconds.

#### Scenario: Activity without explicit timeout is rejected
- **WHEN** the platform's `NewValidatedActivityOptions` is called without all four timeout fields
- **THEN** the helper returns a validation error

#### Scenario: Activity uses default timeouts
- **WHEN** the activity does not specify any timeout and the platform defaults are applied
- **THEN** the activity's effective `StartToCloseTimeout` is 30 seconds and `ScheduleToCloseTimeout` is 5 minutes

#### Scenario: Long-running activity has heartbeat
- **WHEN** an activity is expected to take longer than 30 seconds
- **THEN** the activity options include `HeartbeatTimeout` and the activity body calls `activity.RecordHeartbeat(ctx)` at least once per heartbeat interval

### Requirement: Idempotent activities with stable operation_id
Every Temporal activity SHALL derive a stable `operation_id` from the workflow ID using the platform's `OperationIDFor(workflowID, operationName)` helper. The activity input SHALL include the `operation_id` and the activity body SHALL check the destination system for the operation's presence before performing the side effect. If the side effect has already been applied, the activity returns the cached result and `nil` (the receipt-row state `started` is the canonical signal that the side effect was applied).

#### Scenario: Activity is idempotent across retries
- **WHEN** the activity is invoked twice with the same `operation_id`
- **THEN** the second invocation observes the prior result and returns `nil` without re-applying the side effect

#### Scenario: Activity retry detects already-applied side effect
- **WHEN** the activity is retried after a Temporal timeout and the side effect already landed
- **THEN** the activity returns `nil` and the workflow continues

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
A saga-style workflow SHALL execute activities in forward order and, on non-retryable failure of any forward activity, SHALL execute the compensations for all previously-succeeded forward activities in INVERSE order. The platform SHALL provide a `temporal.NewSaga(activities, compensations)` helper that enforces the inverse-order rule and tracks which compensations have run. A compensation failure SHALL NOT block subsequent compensations; compensation failures SHALL be recorded as `CompensationFailureV1` and emitted as a workflow event for human intervention.

#### Scenario: Successful forward path
- **WHEN** all forward activities succeed
- **THEN** no compensations run and the workflow completes with the result of the last forward activity

#### Scenario: Failed forward activity triggers inverse compensation
- **WHEN** the third forward activity fails with `NonRetryableApplicationError`
- **THEN** compensations for activities 2 and 1 run in inverse order (compensation of 2, then compensation of 1)

#### Scenario: Compensation failure does not block subsequent compensations
- **WHEN** the compensation of activity 2 fails
- **THEN** the compensation of activity 1 still runs and the workflow records a `CompensationFailureV1` for activity 2

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

### Requirement: Workflow replay tests
The platform SHALL require every workflow to ship a replay test that runs the workflow against a recorded history. The replay test SHALL live in `test/compatibility/<workflow>_replay_test.go` and SHALL use the Temporal test framework's `test.NewWorkflowEnvironment()` with a `RegisterWorkflowWithOptions` call that references the workflow function. The replay test SHALL fail if the workflow code change would cause a non-deterministic replay.

#### Scenario: Replay test passes against recorded history
- **WHEN** the recorded history is replayed against the new workflow code
- **THEN** the test passes and the workflow produces the same result

#### Scenario: Replay test detects non-deterministic change
- **WHEN** the workflow code introduces a non-deterministic API call
- **THEN** the replay test fails with a deterministic-replay error

### Requirement: Temporal namespace strategy
The platform SHALL use one Temporal namespace per environment (`prod`, `staging`, `dev`). Each service SHALL declare its task queue as `<service>.<role>.vN` and SHALL NOT share task queues across services. The platform SHALL NOT adopt namespace-per-service (the operational overhead outweighs the isolation benefit at the platform's current scale).

#### Scenario: Service uses its own task queue
- **WHEN** a service starts a Temporal worker
- **THEN** the worker registers on the task queue `<service>.<role>.vN` and no other service polls that queue

#### Scenario: Namespace-per-environment is documented
- **WHEN** the service's `local-vs-production.md` is reviewed
- **THEN** the document specifies the namespace per environment and the per-env auth posture

### Requirement: Temporal activity version validation
The platform SHALL require every activity input/output to carry a `contract_version` field. The activity's `validateVersionedOperation` helper SHALL compare the input's `contract_version` against the activity's registered version and SHALL return a `NonRetryableApplicationError` with reason `contract_version_mismatch` if the versions do not match. The platform SHALL provide a typed error `ErrContractVersionMismatch` for the application's convenience.

#### Scenario: Activity rejects unknown contract version
- **WHEN** an activity receives input with `contract_version` greater than the activity's registered version
- **THEN** the activity returns `ErrContractVersionMismatch` and the workflow does not retry

#### Scenario: Activity accepts the current contract version
- **WHEN** an activity receives input with `contract_version` equal to the activity's registered version
- **THEN** the activity processes the input normally

### Requirement: Force-terminate runbook support
The platform SHALL expose a CLI subcommand `temporal-workflow terminate --workflow-id=<id>` that calls `Temporal.TerminateWorkflow(ctx, workflowID, runID, reason)`. The platform SHALL NOT delete a Temporal namespace to clear a backlog (namespace deletion is irreversible and destroys every workflow history). The platform SHALL NOT lower retry policy below `MaximumAttempts=3` during an incident.

#### Scenario: Operator terminates a stuck workflow
- **WHEN** the operator runs `temporal-workflow terminate --workflow-id=<id>`
- **THEN** the workflow enters `Terminated` state and the terminal event includes the operator's reason

#### Scenario: Retry policy floor is enforced
- **WHEN** the architecture test scans activity options
- **THEN** every activity has `MaximumAttempts >= 3`