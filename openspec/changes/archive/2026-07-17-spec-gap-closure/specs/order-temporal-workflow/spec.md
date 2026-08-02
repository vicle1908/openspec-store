# order-temporal-workflow Delta Specification

## Purpose

This delta updates the main `order-temporal-workflow` spec to reflect the actual implementation status discovered during the spec-gap-closure audit. Three requirements have modified status annotations.

## MODIFIED Requirements

### Requirement: Per-peer circuit breaker on each activity's HTTP client [DEFERRED]

> **Status**: DEFERRED. The main spec marks this as IMPLEMENTED, but the circuit breaker is configured in the HTTP clients (`clients/payment_client.go`, `clients/inventory_client.go`, `clients/shipping_client.go`) without full integration into the activity error-path contract. The activity body does NOT treat `ErrPeerUnavailable` as a `NonRetryableApplicationError` in all code paths; the fast-compensation-path wiring is incomplete. The `sony/gobreaker` dependency exists but the open-circuit → activity failure → workflow compensation chain is not fully exercised by tests.

The HTTP clients used by the four forward activities and the two compensation activities SHALL each apply a `sony/gobreaker` circuit breaker with the configuration specified in the `order-remote-activities` spec. When the circuit is open, the client SHALL return `clients.ErrPeerUnavailable` immediately; the activity SHALL treat this as a `NonRetryableApplicationError` and the workflow SHALL take the fast compensation path.

#### Scenario: Circuit breaker opens after 5 consecutive failures

- **WHEN** 5 consecutive HTTP calls to any peer service return 5xx
- **THEN** the circuit breaker transitions to open state
- **AND** the next 5 seconds of HTTP calls to that peer return `clients.ErrPeerUnavailable`
- **AND** the activity returns `NonRetryableApplicationError` and the workflow runs compensation

#### Scenario: Circuit breaker integration test validates compensation path

- **WHEN** the activity receives `ErrPeerUnavailable` from the HTTP client
- **THEN** the activity wraps the error as `NonRetryableApplicationError` with a stable `error_type`
- **AND** the workflow compensation branch is triggered without retrying the activity

### Requirement: OrderFulfillmentWorkflow is registered with Worker Versioning v2 [PARTIAL]

> **Status**: PARTIAL. Basic versioning exists (worker registration with `BuildID` and `DeploymentSeriesName` in `internal/runtime/worker.go`), but full Worker Versioning v2 as specified — with `WorkerDeploymentOptions{ DeploymentSeriesName: "order-fulfillment.v1", BuildID: <from runtime.DeploymentVersion()> }` and `UseVersioning: true` on the orchestrator's `startWorkflow` calls — is not yet wired end-to-end. The orchestrator's `processor.go::startWorkflow` does not yet pass `UseVersioning: true`.

The Temporal worker that hosts `OrderFulfillmentWorkflow` SHALL register with `WorkerDeploymentOptions{ DeploymentSeriesName: "order-fulfillment.v1", BuildID: <from runtime.DeploymentVersion()> }`. The orchestrator's `startWorkflow` calls SHALL pass `UseVersioning: true`.

#### Scenario: Worker registers with deployment series name

- **WHEN** `internal/runtime/worker.go` constructs `worker.New(client, taskQueue, worker.Options{...})`
- **THEN** the options include `WorkerDeploymentOptions{ DeploymentSeriesName: "order-fulfillment.v1", BuildID: "<git SHA>" }` (verified by `grep -A 4 'WorkerDeploymentOptions{' internal/runtime/worker.go`)

#### Scenario: Orchestrator starts workflows with versioning

- **WHEN** `processor.go::startWorkflow` constructs `client.StartWorkflowOptions`
- **THEN** the options include `UseVersioning: true`

### Requirement: Activities declare explicit timeouts sourced from the platform [PARTIAL]

> **Status**: PARTIAL. The order-service defines activity timeouts inline in `services/order-service/internal/adapters/temporal/workflow.go` (`activityStartToClose=5min`, `activityHeartbeat=30s`, `ScheduleToCloseTimeout=activityStartToClose*2`), and the platform's `NewValidatedActivityOptions` helper exists in `platform/temporal/activity_options.go`. However, not all activities across all services use the validated helper; some services register activities with raw `worker.ActivityOptions` bypassing the platform's compile-time enforcement.

Activities SHALL declare `StartToCloseTimeout`, `ScheduleToCloseTimeout`, and (for long-running activities) `HeartbeatTimeout` via the platform's `NewValidatedActivityOptions` helper, which enforces presence of these fields at compile time. The order-service's existing constants (`activityStartToClose=5min`, `activityHeartbeat=30s`, `ScheduleToCloseTimeout=activityStartToClose*2`) move into the platform module so future services inherit the same bounds.

#### Scenario: NewValidatedActivityOptions refuses missing timeouts

- **WHEN** a service constructs activity options without `StartToCloseTimeout` and `ScheduleToCloseTimeout`
- **THEN** `NewValidatedActivityOptions` returns an error and the activity cannot register

#### Scenario: Compensations get tighter timeouts than forward steps

- **WHEN** a compensation activity is registered
- **THEN** its `StartToCloseTimeout` is half the forward-step timeout (the platform enforces this in `NewValidatedActivityOptions`)
