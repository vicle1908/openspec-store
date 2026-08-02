## ADDED Requirements

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

### Requirement: Per-peer circuit breaker on each activity's HTTP client

The HTTP clients used by the four forward activities and the two compensation activities SHALL each apply a `sony/gobreaker` circuit breaker with the configuration specified in the `order-remote-activities` spec. When the circuit is open, the client SHALL return `clients.ErrPeerUnavailable` immediately; the activity SHALL treat this as a `NonRetryableApplicationError` and the workflow SHALL take the fast compensation path.

#### Scenario: Circuit breaker opens after 5 consecutive failures

- **WHEN** 5 consecutive HTTP calls to any peer service return 5xx
- **THEN** the circuit breaker transitions to open state
- **AND** the next 5 seconds of HTTP calls to that peer return `clients.ErrPeerUnavailable`
- **AND** the activity returns `NonRetryableApplicationError` and the workflow runs compensation

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
