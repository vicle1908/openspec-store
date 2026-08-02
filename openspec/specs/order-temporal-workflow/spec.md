# order-temporal-workflow Specification

## Purpose
The platform implements Workflow initiation is durable and idempotent An Order-owned Kafka consumer SHALL start fulfillment from the committed `OrderCreated` integration event, SHALL persist a stateful event receipt before committing its Kafka offset, and SHALL use determin
## Requirements
### Requirement: Workflow initiation is durable and idempotent
An Order-owned Kafka consumer SHALL start fulfillment from the committed `OrderCreated` integration event, SHALL persist a stateful event receipt before committing its Kafka offset, and SHALL use deterministic workflow ID `order/<order-id>` with workflow-ID reuse rejected. A `pending` receipt MUST remain retryable until workflow initiation is durably confirmed as `started`.

#### Scenario: API process crashes after order commit
- **WHEN** Order creation commits and the API process stops before any Temporal call
- **THEN** Debezium publishes the outbox event and the orchestration consumer starts fulfillment after recovery

#### Scenario: OrderCreated is delivered twice
- **WHEN** the orchestration consumer receives the same event ID more than once
- **THEN** it records or finds one receipt and converges on one workflow execution without duplicate fulfillment effects

#### Scenario: Consumer stops after pending receipt
- **WHEN** the consumer persists a pending receipt and stops before workflow initiation
- **THEN** redelivery retries workflow initiation rather than treating the event as complete

#### Scenario: Consumer stops before offset commit
- **WHEN** workflow initiation succeeds but the consumer stops before marking the receipt started or committing the Kafka offset
- **THEN** redelivery observes the existing workflow through its deterministic ID, marks the receipt started, and commits without creating another execution

### Requirement: Workflow code is deterministic
Order workflow implementations SHALL use deterministic Temporal SDK APIs and SHALL perform I/O, wall-clock access, randomness, and service calls only through recorded workflow APIs or activities.

#### Scenario: Workflow replay
- **WHEN** a completed workflow history is replayed against its compatible worker build
- **THEN** replay completes without a nondeterminism error

### Requirement: Activities and compensations are idempotent
Every activity and compensation SHALL accept a stable operation ID and tolerate retries without duplicating an external effect.

#### Scenario: Payment activity retries after timeout
- **WHEN** payment capture succeeded remotely but its activity response was lost
- **THEN** the retry returns the existing capture result rather than charging again

### Requirement: Fulfillment activities cover the full saga
The Order fulfillment workflow SHALL expose a versioned activity surface that, at MVP, comprises `ValidateInventory`, `ReserveInventory`, `ProcessPayment`, `MarkOrderShipped`, and their compensations `ReleaseInventory` and `RefundPayment`. Each activity SHALL validate its versioned input contract (`Version`, `OrderID`, `OperationID`) and SHALL return a `NonRetryableApplicationError` with a stable `error_type` for invalid inputs and missing dependency wiring so the workflow can fail fast without burning retry budget. Forwarding activities to a not-yet-deployed downstream capability SHALL be implemented by injecting typed activity interfaces (e.g. `InventoryActivities`, `PaymentActivities`, `ShippingActivities`) through the worker composition root rather than calling them directly inside the workflow code.

#### Scenario: Activity receives an unknown contract version
- **WHEN** a caller submits a `Version` value other than the supported contract version
- **THEN** the activity returns a non-retryable validation error and the workflow records a terminal compensation failure rather than invoking a downstream capability

### Requirement: Workflow evolution protects in-flight executions
Worker deployments SHALL use stable task queues and Temporal worker deployment versioning; incompatible logic changes SHALL use SDK versioning or a new workflow type.

#### Scenario: New worker deployment
- **WHEN** a new worker build is promoted while workflows are in flight
- **THEN** existing executions remain routed to a compatible build until migration is explicitly completed

### Requirement: Service boundaries are contract based
The Order workflow SHALL invoke future Payment, Inventory, and Shipping capabilities through versioned activity inputs/results, service-owned task queues, child workflows, or Nexus operations without importing their domain packages.

#### Scenario: Inventory service extraction
- **WHEN** inventory logic moves to an independently deployed service
- **THEN** the Order workflow keeps its orchestration contract while the Inventory service owns execution and data

### Requirement: Workflow state does not replace domain state
Temporal SHALL own orchestration history while PostgreSQL remains authoritative for current Order business state.

#### Scenario: Query current order
- **WHEN** an API client requests current Order state
- **THEN** the service reads the Order model rather than treating workflow history as its query database

### Requirement: Activities declare explicit timeouts sourced from the platform [PARTIAL]

> **Status**: PARTIAL. The order-service defines activity timeouts inline in `services/order-service/internal/adapters/temporal/workflow.go` (`activityStartToClose=5min`, `activityHeartbeat=30s`, `ScheduleToCloseTimeout=activityStartToClose*2`), and the platform's `NewValidatedActivityOptions` helper exists in `platform/temporal/activity_options.go`. However, not all activities across all services use the validated helper; some services register activities with raw `worker.ActivityOptions` bypassing the platform's compile-time enforcement.

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

### Requirement: OrderFulfillmentWorkflow is observable end-to-end
The Order Service's `OrderFulfillmentWorkflow` SHALL emit OTel spans for the workflow execution, each activity execution, and each compensation, and SHALL propagate the inbound `traceparent` from the orchestrator's `startWorkflow` call so the trace continues across the Temporal boundary.

#### Scenario: Workflow spans appear in Tempo
- **WHEN** a workflow is started from the orchestrator's `processor.go::startWorkflow` with a non-empty inbound trace context
- **THEN** the resulting workflow execution emits a `WorkflowExecution` span in Tempo whose `parent.span_id` matches the inbound `traceparent`'s span ID

#### Scenario: Activity spans appear as children of the workflow span
- **WHEN** `ValidateInventoryActivity` runs inside the workflow
- **THEN** the activity emits an `ActivityExecution` span whose `parent.span_id` matches the workflow span

### Requirement: OrderFulfillmentWorkflow is registered with Worker Versioning v2 [PARTIAL]

> **Status**: PARTIAL. Basic versioning exists (worker registration with `BuildID` and `DeploymentSeriesName` in `internal/runtime/worker.go`), but full Worker Versioning v2 as specified — with `WorkerDeploymentOptions{ DeploymentSeriesName: "order-fulfillment-v1", BuildID: <from runtime.DeploymentVersion()> }` and `UseVersioning: true` on the orchestrator's `startWorkflow` calls — is not yet wired end-to-end. The orchestrator's `processor.go::startWorkflow` does not yet pass `UseVersioning: true`.

The Temporal worker that hosts `OrderFulfillmentWorkflow` SHALL register with `WorkerDeploymentOptions{ DeploymentSeriesName: "order-fulfillment-v1", BuildID: <from runtime.DeploymentVersion()> }`. The orchestrator's `startWorkflow` calls SHALL pass `UseVersioning: true`.

#### Scenario: Worker registers with deployment series name

- **WHEN** `internal/runtime/worker.go` constructs `worker.New(client, taskQueue, worker.Options{...})`
- **THEN** the options include `WorkerDeploymentOptions{ DeploymentSeriesName: "order-fulfillment-v1", BuildID: "<git SHA>" }` (verified by `grep -A 4 'WorkerDeploymentOptions{' internal/runtime/worker.go`)

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

### Requirement: OrderFulfillmentWorkflow activities call remote services over HTTP

The `OrderFulfillmentWorkflow` activities SHALL call the extracted services (`payment-service`, `inventory-service`, `shipping-service`) over HTTP via the platform's OTel-instrumented client. The activities SHALL NOT call in-process command handlers. The activity inputs and outputs SHALL be the generated protobuf types from the extracted services' `contracts/` packages.

The forward activities are exactly the four registered in `services/order-service/internal/adapters/temporal/workflow.go` and `services/order-service/internal/adapters/temporal/activities.go`:

| Activity (function) | Activity name (registered) | Calls (remote) |
|---|---|---|
| `ValidateInventoryActivityV1` | `order.fulfillment.validate-inventory.v1` | `inventory.Client.GetAvailability` |
| `ProcessPaymentActivityV1` | `order.fulfillment.process-payment.v1` | `payment.Client.Capture` |
| `ReserveInventoryActivityV1` | `order.fulfillment.reserve-inventory.v1` | `inventory.Client.Reserve` |
| `MarkOrderShippedActivityV1` | `order.fulfillment.mark-shipped.v1` | `shipping.Client.Dispatch` |

The compensation activities are exactly the two registered in the same files:

| Compensation | Activity name (registered) | Calls (remote) |
|---|---|---|
| `RefundPaymentActivityV1` | `order.fulfillment.refund-payment.v1` | `payment.Client.Refund` |
| `ReleaseInventoryActivityV1` | `order.fulfillment.release-inventory.v1` | `inventory.Client.Release` |

`MarkOrderShippedActivityV1` has NO compensation (no `CancelShipping` activity exists in the workflow code). `ValidateInventoryActivityV1` has NO compensation either.

The activity input SHALL include a `contract_version` field set to `1` (the value of `ContractVersionV1` in `services/order-service/internal/adapters/temporal/constants.go`, an `int`). The activity input SHALL also include an `operation_id` derived via the order-service-local `OperationIDFor(orderID, operation)` helper from `services/order-service/internal/adapters/temporal/constants.go`; this key is sent as the `Idempotency-Key` HTTP header to the peer service.

The activity's HTTP timeout SHALL be read from `cfg.Peers.<Name>Timeout` (e.g., `cfg.Peers.InventoryTimeout`, default `5s`). The activity's `StartToCloseTimeout` SHALL be `5m` (the current default in `services/order-service/internal/adapters/temporal/workflow.go`, `activityStartToClose = 5 * time.Minute`); the `ScheduleToCloseTimeout` SHALL be `10m` (current default: `activityStartToClose * 2`).

#### Scenario: ReserveInventoryActivityV1 calls inventory.Client.Reserve over HTTP

- **WHEN** `OrderFulfillmentWorkflow` runs the `ReserveInventoryActivityV1` activity
- **THEN** the activity calls `inventory.Client.Reserve(ctx, ReserveRequest{...})` over HTTP
- **AND** the HTTP request hits `cfg.Peers.InventoryServiceURL + "/api/v1/inventory/reservations"`
- **AND** the HTTP request carries the `Idempotency-Key` header set to the activity's `operation_id`
- **AND** the HTTP request propagates the platform's W3C Trace Context and correlation headers
- **AND** the HTTP request body is JSON-encoded via `protojson.Marshal` of the `ReserveRequest` type
- **AND** the activity returns the `reservation_id` from the HTTP response

#### Scenario: ProcessPaymentActivityV1 calls payment.Client.Capture over HTTP

- **WHEN** `OrderFulfillmentWorkflow` runs the `ProcessPaymentActivityV1` activity
- **THEN** the activity calls `payment.Client.Capture(ctx, CaptureRequest{...})` over HTTP
- **AND** the HTTP request hits `cfg.Peers.PaymentServiceURL + "/api/v1/payments/{intent_id}/capture"`

#### Scenario: MarkOrderShippedActivityV1 calls shipping.Client.Dispatch over HTTP

- **WHEN** `OrderFulfillmentWorkflow` runs the `MarkOrderShippedActivityV1` activity
- **THEN** the activity calls `shipping.Client.Dispatch(ctx, DispatchRequest{...})` over HTTP
- **AND** the HTTP request hits `cfg.Peers.ShippingServiceURL + "/api/v1/shipments"`

#### Scenario: ValidateInventoryActivityV1 calls inventory.Client.GetAvailability over HTTP

- **WHEN** `OrderFulfillmentWorkflow` runs the `ValidateInventoryActivityV1` activity
- **THEN** the activity calls `inventory.Client.GetAvailability(ctx, GetRequest{order_id, items})` over HTTP
- **AND** the HTTP request hits `cfg.Peers.InventoryServiceURL + "/api/v1/inventory/availability"`
- **AND** a `false` available response causes the workflow to finalise with `Status: "failed"` and no compensation runs

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

### Requirement: Saga compensation activities call the inverse operations

The `OrderFulfillmentWorkflow` saga SHALL preserve its 4-step forward execution (`ValidateInventoryActivityV1` → `ProcessPaymentActivityV1` → `ReserveInventoryActivityV1` → `MarkOrderShippedActivityV1`) and its 2-step inverse-order compensation (`RefundPaymentActivityV1` ← `ReleaseInventoryActivityV1`). The compensation activities SHALL call the inverse operations on the same remote clients:

- `ReleaseInventoryActivityV1` calls `inventory.Client.Release(ctx, ReleaseRequest{reservation_id})` (inverse of `ReserveInventoryActivityV1`).
- `RefundPaymentActivityV1` calls `payment.Client.Refund(ctx, RefundRequest{capture_id, amount_minor})` (inverse of `ProcessPaymentActivityV1`).
- `MarkOrderShippedActivityV1` has no compensation (the carrier API cannot reliably roll back a dispatched shipment; the saga accepts the orphan and alerts operators).
- `ValidateInventoryActivityV1` has no compensation (it only reads; on failure the workflow finalises with no inverse action).

#### Scenario: Successful forward path with no compensation

- **WHEN** all four forward activities succeed
- **THEN** the workflow completes with `Status: "completed"`, `TrackingNumber` set, and no compensation runs

#### Scenario: Failed shipping dispatch triggers inverse-order compensation

- **WHEN** `ReserveInventoryActivityV1` and `ProcessPaymentActivityV1` succeed but `MarkOrderShippedActivityV1` fails with `NonRetryableApplicationError`
- **THEN** the workflow runs the compensation path in inverse order: `RefundPaymentActivityV1` → `ReleaseInventoryActivityV1`
- **AND** the workflow completes with `Status: "failed"`, `Compensated: true`, and `CompensationFailures` populated if any inverse call failed

### Requirement: Workflow ID reuse policy for the remote-activity workflow

The `OrderFulfillmentWorkflow` SHALL be started with `WorkflowIDReusePolicy: WORKFLOW_ID_REUSE_POLICY_USE_EXISTING` and `WorkflowIDConflictPolicy: WORKFLOW_ID_CONFLICT_POLICY_FAIL`. The workflow ID SHALL be `order/<order_id>` (a meaningful business identifier derived from the order ID, per `services/order-service/internal/adapters/temporal/constants.go::WorkflowIDForOrder`). A duplicate event with the same `order_id` short-circuits to the existing workflow.

#### Scenario: Duplicate event with same order_id short-circuits

- **WHEN** the order-orchestrator consumes two `OrderCreated` events with the same `order_id` within 5 minutes
- **THEN** the first event starts the workflow with ID `WorkflowIDForOrder(order_id)` (e.g., `order/01H...`)
- **AND** the second event with `WorkflowIDReusePolicy: USE_EXISTING` returns the existing workflow handle
- **AND** the second event is treated as success (the workflow continues from its current state)

### Requirement: Replay test verifies the remote-activity workflow

The `services/order-service/test/compatibility/order_fulfillment_replay_test.go` file SHALL be updated to include a recorded history that contains the four forward activities (in the order `ValidateInventoryActivityV1`, `ProcessPaymentActivityV1`, `ReserveInventoryActivityV1`, `MarkOrderShippedActivityV1`) and the optional compensation activities (`RefundPaymentActivityV1`, `ReleaseInventoryActivityV1`). The replay test SHALL run the new workflow code against the recorded history and SHALL pass.

#### Scenario: Replay test passes against the recorded remote-activity history

- **WHEN** the test framework runs the replay test with a recorded history
- **THEN** the workflow produces the same result as the recorded history
- **AND** the test passes
