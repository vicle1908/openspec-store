## ADDED Requirements

### Requirement: OrderFulfillmentWorkflow is observable end-to-end
The Order Service's `OrderFulfillmentWorkflow` SHALL emit OTel spans for the workflow execution, each activity execution, and each compensation, and SHALL propagate the inbound `traceparent` from the orchestrator's `startWorkflow` call so the trace continues across the Temporal boundary.

#### Scenario: Workflow spans appear in Tempo
- **WHEN** a workflow is started from the orchestrator's `processor.go::startWorkflow` with a non-empty inbound trace context
- **THEN** the resulting workflow execution emits a `WorkflowExecution` span in Tempo whose `parent.span_id` matches the inbound `traceparent`'s span ID

#### Scenario: Activity spans appear as children of the workflow span
- **WHEN** `ValidateInventoryActivity` runs inside the workflow
- **THEN** the activity emits an `ActivityExecution` span whose `parent.span_id` matches the workflow span

### Requirement: OrderFulfillmentWorkflow is registered with Worker Versioning v2
The Temporal worker that hosts `OrderFulfillmentWorkflow` SHALL register with `WorkerDeploymentOptions{ DeploymentSeriesName: "order-fulfillment.v1", BuildID: <from runtime.DeploymentVersion()> }`. The orchestrator's `startWorkflow` calls SHALL pass `UseVersioning: true`.

#### Scenario: Worker registers with deployment series name
- **WHEN** `internal/runtime/worker.go` constructs `worker.New(client, taskQueue, worker.Options{...})`
- **THEN** the options include `WorkerDeploymentOptions{ DeploymentSeriesName: "order-fulfillment.v1", BuildID: "<git SHA>" }` (verified by `grep -A 4 'WorkerDeploymentOptions{' internal/runtime/worker.go`)

#### Scenario: Orchestrator starts workflows with versioning
- **WHEN** `processor.go::startWorkflow` constructs `client.StartWorkflowOptions`
- **THEN** the options include `UseVersioning: true`

### Requirement: Activities carry a stable `operation_id` and validated `contract_version`
Every Order Service activity input/output SHALL carry `contract_version` (the platform version) and `operation_id` (the stable per-(workflowID, operation) identifier). The activity body SHALL call `validateVersionedOperation(input)` from the platform's `platform/temporal/contract_version.go`.

#### Scenario: operation_id is stable across retries
- **WHEN** the same activity is retried because of a transient failure
- **THEN** the `operation_id` value matches across attempts (it is derived from `OperationIDFor(workflowID, operation)`)

#### Scenario: contract_version mismatch fails fast
- **WHEN** an activity input's `contract_version` does not match the platform's current `ContractVersionV1`
- **THEN** `validateVersionedOperation` returns `ErrContractVersionMismatch` and the activity fails immediately (not retried)

## ADDED Requirements

### Requirement: Activities declare explicit timeouts sourced from the platform
Activities SHALL declare `StartToCloseTimeout`, `ScheduleToCloseTimeout`, and (for long-running activities) `HeartbeatTimeout` via the platform's `NewValidatedActivityOptions` helper, which enforces presence of these fields at compile time. The order-service's existing constants (`activityStartToClose=5min`, `activityHeartbeat=30s`, `ScheduleToCloseTimeout=activityStartToClose*2`) move into the platform module so future services inherit the same bounds.

#### Scenario: NewValidatedActivityOptions refuses missing timeouts
- **WHEN** a service constructs activity options without `StartToCloseTimeout` and `ScheduleToCloseTimeout`
- **THEN** `NewValidatedActivityOptions` returns an error and the activity cannot register

#### Scenario: Compensations get tighter timeouts than forward steps
- **WHEN** a compensation activity is registered
- **THEN** its `StartToCloseTimeout` is half the forward-step timeout (the platform enforces this in `NewValidatedActivityOptions`)

### Requirement: Worker lifecycle uses fx.StartStopHook
The order-service's Temporal worker SHALL adopt the platform's `fx.StartStopHook` lifecycle wrapper, replacing the existing `fx.Hook`. The hook enforces a 30s stop timeout and emits lifecycle spans.

#### Scenario: Worker lifecycle emits OTel spans
- **WHEN** the worker stops via SIGTERM
- **THEN** an OTel span `worker.stop` is emitted whose duration matches the stop call wall time

#### Scenario: Worker stop respects 30s budget
- **WHEN** an in-flight activity does not return within 30s of `OnStop` being invoked
- **THEN** the worker is force-cancelled and the architecture test `test/architecture/worker_no_blocking_run_test.go` passes (the existing code already satisfies this constraint)