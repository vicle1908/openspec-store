# order-remote-activities Specification

## Purpose
This spec defines the order-worker's remote-activity boundary. After the extraction, the order-worker's `OrderFulfillmentWorkflow` activities (validate inventory, process payment, reserve inventory, mark order shipped, refund payment, release inventory) SHALL call the peer services' REST APIs via the platform's OTel-instrumented HTTP client with per-peer circuit breakers. The local in-process stub activities SHALL be preserved under a `Deprecated:` comment for soft-rollback support but SHALL NOT be the default.
## Requirements
### Requirement: order-worker activities call remote services via HTTP

> **Status**: IMPLEMENTED. Remote activities implemented with HTTP calls to payment, inventory, shipping services.

The `services/order-service/cmd/order-service/worker_activities_remote.go` file SHALL define `remoteFulfillmentActivities` that holds three typed client interfaces (in `services/order-service/internal/application/clients/`):

- `payment.Client` with methods `Capture(ctx, CaptureRequest) (CaptureResponse, error)` and `Refund(ctx, RefundRequest) (RefundResponse, error)`
- `inventory.Client` with methods `Reserve(ctx, ReserveRequest) (ReserveResponse, error)`, `Release(ctx, ReleaseRequest) (ReleaseResponse, error)`, and `Confirm(ctx, ConfirmRequest) (ConfirmResponse, error)`
- `shipping.Client` with methods `Dispatch(ctx, DispatchRequest) (DispatchResponse, error)` and `Cancel(ctx, CancelRequest) (CancelResponse, error)`

Each client interface SHALL be implemented by a concrete struct in `services/order-service/internal/application/clients/`:

- `clients/payment_client.go` — `NewPaymentClient(PeerConfig, *http.Client) (payment.Client, error)`. Uses the platform's instrumented `platform/http` HTTP client. Sets the `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id` headers from the incoming context. Sets the `Idempotency-Key` header from the request's `idempotency_key` field.
- `clients/inventory_client.go` — same pattern.
- `clients/shipping_client.go` — same pattern.

The `OrderFulfillmentWorkflow`'s activity methods (currently registered in `services/order-service/internal/adapters/temporal/activities.go` as `ValidateInventoryActivityV1`, `ProcessPaymentActivityV1`, `ReserveInventoryActivityV1`, `MarkOrderShippedActivityV1`, `RefundPaymentActivityV1`, `ReleaseInventoryActivityV1`) SHALL be implemented by `remoteFulfillmentActivities` and SHALL call the appropriate client method. The activity input/output types SHALL be the generated protobuf types from the new services' `contracts/` packages.

The interfaces implemented by `remoteFulfillmentActivities` are the existing ones in `services/order-service/internal/adapters/temporal/activities.go`:

- `InventoryActivities`: `ValidateInventory`, `ReserveInventory`, `ReleaseInventory`
- `PaymentActivities`: `ProcessPayment`, `RefundPayment`
- `ShippingActivities`: `MarkOrderShipped`

These match the `temporaladapter.InventoryActivities`, `temporaladapter.PaymentActivities`, and `temporaladapter.ShippingActivities` interface assertions in the existing `worker_activities.go` (`var _ temporaladapter.InventoryActivities = localFulfillmentActivities{}` etc.). The remote implementation SHALL preserve these interface assertions.

#### Scenario: ReserveInventoryActivityV1 calls the inventory-service HTTP API

- **WHEN** `OrderFulfillmentWorkflow` runs the `ReserveInventoryActivityV1` activity
- **THEN** the activity calls `inventory.Client.Reserve(ctx, ReserveRequest{...})` over HTTP
- **AND** the HTTP request hits `cfg.Peers.InventoryServiceURL + "/api/v1/inventory/reservations"`
- **AND** the HTTP request carries the `Idempotency-Key` header set to the activity's `operation_id`
- **AND** the HTTP request propagates the platform's W3C Trace Context and correlation headers
- **AND** the activity returns the `reservation_id` from the HTTP response

#### Scenario: ProcessPaymentActivityV1 calls the payment-service HTTP API

- **WHEN** `OrderFulfillmentWorkflow` runs the `ProcessPaymentActivityV1` activity
- **THEN** the activity calls `payment.Client.Capture(ctx, CaptureRequest{...})` over HTTP
- **AND** the HTTP request hits `cfg.Peers.PaymentServiceURL + "/api/v1/payments/{intent_id}/capture"`

#### Scenario: MarkOrderShippedActivityV1 calls the shipping-service HTTP API

- **WHEN** `OrderFulfillmentWorkflow` runs the `MarkOrderShippedActivityV1` activity
- **THEN** the activity calls `shipping.Client.Dispatch(ctx, DispatchRequest{...})` over HTTP
- **AND** the HTTP request hits `cfg.Peers.ShippingServiceURL + "/api/v1/shipments"`

#### Scenario: ValidateInventoryActivityV1 reads inventory availability

- **WHEN** `OrderFulfillmentWorkflow` runs the `ValidateInventoryActivityV1` activity (the first forward activity, before payment)
- **THEN** the activity calls `inventory.Client.GetAvailability(ctx, GetRequest{order_id, items})` over HTTP
- **AND** the HTTP request hits `cfg.Peers.InventoryServiceURL + "/api/v1/inventory/availability"`
- **AND** a `false` `available` response causes the workflow to enter the compensation path with no compensations registered (this activity has no inverse operation)

### Requirement: Each remote client applies a per-peer circuit breaker

> **Status**: IMPLEMENTED. Circuit breaker (sony/gobreaker) configured per peer with 5-failure threshold.

The `payment.Client`, `inventory.Client`, and `shipping.Client` implementations SHALL each wrap the underlying HTTP client with a `sony/gobreaker` circuit breaker. The circuit breaker configuration SHALL be:

- `Name`: the peer name (e.g., `"payment"`, `"inventory"`, `"shipping"`)
- `MaxRequests`: 1 (number of requests allowed in half-open state)
- `Interval`: 30s (the cyclic period of the closed-state counter)
- `Timeout`: 5s (the open-state duration before transitioning to half-open)
- `ReadyToTrip`: returns `true` after 5 consecutive failures

When the circuit is open, the client SHALL return `clients.ErrPeerUnavailable` immediately without making the HTTP call. The activity SHALL treat `clients.ErrPeerUnavailable` as a `temporal.NewNonRetryableApplicationError("peer_unavailable", "PEER_UNAVAILABLE", err)` so the workflow takes the fast compensation path.

#### Scenario: Circuit breaker opens after 5 consecutive failures

- **WHEN** 5 consecutive HTTP calls to the `payment-service` return 5xx
- **THEN** the circuit breaker transitions to open state
- **AND** the next 5 seconds of HTTP calls return `clients.ErrPeerUnavailable` without making the call
- **AND** after 5 seconds, the circuit transitions to half-open and the next call is attempted

#### Scenario: Activity returns NonRetryableApplicationError on circuit-open

- **WHEN** the `ProcessPaymentActivityV1` is invoked while the payment circuit is open
- **THEN** the activity returns `temporal.NewNonRetryableApplicationError("peer_unavailable", "PEER_UNAVAILABLE", clients.ErrPeerUnavailable)`
- **AND** the workflow does NOT retry the activity
- **AND** the workflow runs the compensation path (`RefundPaymentActivityV1` with the inverse `operation_id`)

### Requirement: Peer URLs are configurable via env vars

> **Status**: IMPLEMENTED. Peer URLs configurable via env vars with defaults for compose and production.

The `cfg.Peers` struct in `services/order-service/internal/config/config.go` SHALL be extended with three new fields:

- `PaymentServiceURL` (env var `ORDER_PAYMENT_URL`, default `http://payment-api:8083` in compose, empty in production)
- `InventoryServiceURL` (env var `ORDER_INVENTORY_URL`, default `http://inventory-api:8084` in compose, empty in production)
- `ShippingServiceURL` (env var `ORDER_SHIPPING_URL`, default `http://shipping-api:8085` in compose, empty in production)

Each field SHALL have a companion `*Timeout` field (env var `ORDER_*_TIMEOUT`, default `5s`). The `runWorker` role in `cmd/order-service/roles.go` SHALL call `MakePaymentClient`, `MakeInventoryClient`, `MakeShippingClient` with the configured URLs and timeouts. If any peer URL is empty in production (where the `DEPLOYMENT_ENV` is `prod`), the worker SHALL fail-fast with a configuration error. If any peer URL is empty in local dev (where `DEPLOYMENT_ENV` is `local`), the worker SHALL print a yellow warning and fall back to the in-process stub (preserved in `worker_activities_local.go`).

#### Scenario: Worker fails fast on missing peer URL in production

- **WHEN** the `order-worker` container starts with `DEPLOYMENT_ENV=prod` and `ORDER_PAYMENT_URL=` (empty)
- **THEN** the worker exits with a non-zero status and prints `FAIL: missing ORDER_PAYMENT_URL in production`

#### Scenario: Worker falls back to in-process stub in local dev

- **WHEN** the `order-worker` container starts with `DEPLOYMENT_ENV=local` and `ORDER_PAYMENT_URL=` (empty)
- **THEN** the worker prints `WARN: ORDER_PAYMENT_URL is empty; falling back to in-process payment stub` and continues
- **AND** the activity uses the `localFulfillmentActivities` adapter (preserved in `worker_activities_local.go`)

### Requirement: Saga compensation calls the inverse operations

> **Status**: IMPLEMENTED. Saga compensation implemented with inverse operations for payment and inventory.

The `OrderFulfillmentWorkflow` saga SHALL preserve its 4-step forward execution (`ValidateInventoryActivityV1` → `ProcessPaymentActivityV1` → `ReserveInventoryActivityV1` → `MarkOrderShippedActivityV1`, per `services/order-service/internal/adapters/temporal/workflow.go`) and its 2-step inverse-order compensation (`RefundPaymentActivityV1` ← `ReleaseInventoryActivityV1`):

- `ReleaseInventoryActivityV1` calls `inventory.Client.Release(ctx, ReleaseRequest{reservation_id})` (inverse of `ReserveInventoryActivityV1`).
- `RefundPaymentActivityV1` calls `payment.Client.Refund(ctx, RefundRequest{capture_id, amount_minor})` (inverse of `ProcessPaymentActivityV1`).

`MarkOrderShippedActivityV1` has NO compensation in the current workflow (no `CancelShipping` activity is registered — the spec must not introduce one). `ValidateInventoryActivityV1` has no compensation either (it only reads availability; on failure the workflow finalises without any compensating action).

#### Scenario: Successful forward path

- **WHEN** all four forward activities succeed
- **THEN** the workflow completes with `Status: "completed"` and `TrackingNumber` set; no compensation runs

#### Scenario: Failed shipping dispatch triggers inverse-order compensation

- **WHEN** `ReserveInventoryActivityV1` and `ProcessPaymentActivityV1` succeed but `MarkOrderShippedActivityV1` fails with `NonRetryableApplicationError`
- **THEN** the workflow runs the compensation path in inverse order: `RefundPaymentActivityV1` → `ReleaseInventoryActivityV1`
- **AND** the workflow completes with the result of the last compensation (`Status: "failed"`, `Compensated: true`, `CompensationFailures` populated if any inverse call failed)

### Requirement: Activities are idempotent with operation_id derived from workflow ID

> **Status**: IMPLEMENTED. Operation ID derived from workflow ID; idempotency enforced via Idempotency-Key header.

The `OrderFulfillmentWorkflow` activities SHALL derive a stable `operation_id` from the workflow ID. The existing helper is `services/order-service/internal/adapters/temporal.OperationIDFor(orderID, operationName)`, which returns `WorkflowIDForOrder(orderID) + "/fulfillment/v1/" + operationName` (e.g., `order/01H.../fulfillment/v1/process-payment`). The `operation_id` SHALL be passed as the `Idempotency-Key` header on the HTTP call to the peer service. The peer service's idempotency logic (per its own spec) SHALL detect duplicate operations and return the cached response.

Note: this is the order-service-local `OperationIDFor` helper, which uses string concatenation. The platform's `platform/temporal.OperationIDFor` helper uses a SHA-256 hash and produces different output for the same inputs. The two are not interchangeable; services SHALL use the platform helper for new code but the order-service worker SHALL keep using its own helper to preserve the current activity input validation in `internal/adapters/temporal/activities.go` (which checks `OperationIDFor(orderID, operation) == in.OperationID`).

#### Scenario: ReserveInventoryActivityV1 is idempotent across retries

- **WHEN** `OrderFulfillmentWorkflow` retries the `ReserveInventoryActivityV1` activity with the same `operation_id` after a transient network failure
- **THEN** the `inventory.Client.Reserve` call hits the inventory-service with the same `Idempotency-Key`
- **AND** the inventory-service returns the cached `reservation_id` (per `inventory-service` spec)
- **AND** no duplicate row is created in `inventory_reservations`

### Requirement: The localFulfillmentActivities adapter is preserved as a fallback

> **Status**: IMPLEMENTED. Local fallback adapter preserved in worker_activities_local.go for soft-rollback.

The `services/order-service/cmd/order-service/worker_activities_local.go` file SHALL contain the existing `localFulfillmentActivities` adapter (renamed from `worker_activities.go`). The file SHALL have a `// Deprecated:` comment block explaining that it is the soft-rollback path and SHALL be removed in a follow-up change. The `MakePeerEnricher`-style wiring in `cmd/order-service/roles.go` SHALL be replaced with `MakePaymentClient`, `MakeInventoryClient`, `MakeShippingClient`; the `localFulfillmentActivities` is selected when any peer URL is empty in local dev.

#### Scenario: Soft rollback via env var

- **WHEN** the operator sets `ORDER_PAYMENT_URL=`, `ORDER_INVENTORY_URL=`, `ORDER_SHIPPING_URL=` in `docker-compose.order-service.yaml`
- **THEN** the `order-worker` uses `localFulfillmentActivities` instead of `remoteFulfillmentActivities`
- **AND** the saga compensation graph runs in-process (no network calls)

### Requirement: Replay test verifies the remote-activity workflow

> **Status**: IMPLEMENTED. Replay test exists with recorded history for remote activities.

The `services/order-service/test/compatibility/order_fulfillment_replay_test.go` file SHALL be updated to include a recorded history that contains `ActivityTaskScheduled` events for `ValidateInventoryActivityV1`, `ProcessPaymentActivityV1`, `ReserveInventoryActivityV1`, `MarkOrderShippedActivityV1` (in that order), and the optional compensation activities (`RefundPaymentActivityV1`, `ReleaseInventoryActivityV1`). The recorded inputs SHALL match the protobuf-generated types from the new services' `contracts/` packages. The replay test SHALL run the new workflow code against the recorded history and SHALL pass.

#### Scenario: Replay test passes against recorded remote-activity history

- **WHEN** the test framework runs the replay test with a recorded history that contains the four `ActivityTaskScheduled` events
- **THEN** the workflow produces the same result as the recorded history
- **AND** the test passes

#### Scenario: Replay test detects non-deterministic change in remote activity order

- **WHEN** the workflow code reorders the `ReserveInventoryActivityV1` and `ProcessPaymentActivityV1` activities
- **THEN** the replay test fails with a non-deterministic-replay error
- **AND** the test output points at the file and line of the reordered activity

