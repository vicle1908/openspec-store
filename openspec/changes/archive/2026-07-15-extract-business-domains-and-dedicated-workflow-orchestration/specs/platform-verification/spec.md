## ADDED Requirements

### Requirement: Cross-service smoke test contract for each new service

The `tests/cross-service-smoke/` directory SHALL include a contract test for each of the three new services introduced by the `extract-business-domains-and-dedicated-workflow-orchestration` change. Each contract test SHALL:

1. Start the service's `*-api` container in the smoke stack.
2. Make at least one HTTP call to a write endpoint (e.g., `POST /api/v1/payments/{intent_id}/capture` for the payment contract).
3. Assert that the HTTP call returns the expected response (e.g., `200 OK` with `status: "captured"`).
4. Assert that the corresponding outbox event is published to the service's Kafka topic within 10 seconds.
5. Assert that the service's `*-worker` container's `/health/ready` returns `200 OK` during the test.

The contract test SHALL be named `Test<Service>Contract` and SHALL live in `tests/cross-service-smoke/<service>_contract_test.go`.

#### Scenario: TestPaymentContract passes

- **WHEN** the smoke stack is up and `TestPaymentContract` runs
- **THEN** the test calls `POST /api/v1/payments/{intent_id}/capture` against `payment-api:8083`
- **AND** the test asserts a `200 OK` response with `status: "captured"`
- **AND** the test asserts a `payment_capture` event on `payments.events.v1` within 10 seconds
- **AND** the test asserts `payment-worker`'s `/health/ready` returns `200 OK`

#### Scenario: TestInventoryContract passes

- **WHEN** the smoke stack is up and `TestInventoryContract` runs
- **THEN** the test calls `POST /api/v1/inventory/reservations` against `inventory-api:8084`
- **AND** the test asserts a `201 Created` response with `reservation_id`
- **AND** the test asserts an `inventory_reserved` event on `inventory.events.v1` within 10 seconds

#### Scenario: TestShippingContract passes

- **WHEN** the smoke stack is up and `TestShippingContract` runs
- **THEN** the test calls `POST /api/v1/shipments` against `shipping-api:8085`
- **AND** the test asserts a `201 Created` response with `shipment_id` and `tracking_number`
- **AND** the test asserts a `shipment_dispatched` event on `shipping.events.v1` within 10 seconds

### Requirement: Full orchestration test exercises the remote-activity saga

The `tests/cross-service-smoke/` directory SHALL include a `TestOrderFulfillmentWithRemoteActivities` test that runs the full `OrderFulfillmentWorkflow` against the real `payment-service`, `inventory-service`, `shipping-service`, and `notification-service` HTTP APIs. The test SHALL:

1. Publish an `OrderCreated` event to `orders.events.v1` via the order-service's Kafka producer.
2. Wait for the `order-orchestrator` to consume the event and start an `OrderFulfillmentWorkflow`.
3. Wait for the workflow to make four HTTP calls (one per forward activity) to the three peer services (`ValidateInventoryActivityV1`, `ProcessPaymentActivityV1`, `ReserveInventoryActivityV1`, `MarkOrderShippedActivityV1`).
4. Assert that the workflow completes successfully.
5. Force a failure (e.g., kill the payment-service container after `ProcessPaymentActivityV1` has captured the payment) and verify the workflow enters the compensation path.
6. Assert that the compensation activities make two HTTP calls (Refund Payment via `payment.Client.Refund`, Release Inventory via `inventory.Client.Release`); the saga does NOT call Cancel Shipping because `MarkOrderShippedActivityV1` has no compensation in the current workflow (per `order-temporal-workflow` and `order-remote-activities` specs).
7. Assert that the workflow completes with the compensation result.
8. Assert that the OTel trace captures the full saga as a single trace.

#### Scenario: TestOrderFulfillmentWithRemoteActivities passes end-to-end

- **WHEN** the smoke stack is up and `TestOrderFulfillmentWithRemoteActivities` runs
- **THEN** the test verifies all eight assertions
- **AND** the test completes within 60 seconds

#### Scenario: TestOrderFulfillmentWithRemoteActivities detects saga compensation failure

- **WHEN** the test kills the payment-service container mid-saga (after `ValidateInventoryActivityV1` succeeds and before `ProcessPaymentActivityV1` completes)
- **THEN** the `ProcessPaymentActivityV1` activity returns a non-retryable error (or `ErrPeerUnavailable` from the open circuit breaker)
- **AND** the workflow enters the compensation path
- **AND** the compensation activities make HTTP calls to the inventory service (Release) but NOT to the shipping service (no Cancel Shipping activity is registered in the current saga)
- **AND** the workflow completes with the compensation result

### Requirement: Replay test for the remote-activity workflow

The `services/order-service/test/compatibility/order_fulfillment_replay_test.go` file SHALL be updated to include a recorded history that contains `ActivityTaskScheduled` events for `ValidateInventoryActivityV1`, `ProcessPaymentActivityV1`, `ReserveInventoryActivityV1`, `MarkOrderShippedActivityV1` (in that order — matching the saga sequence in `services/order-service/internal/adapters/temporal/workflow.go`), with the recorded inputs matching the protobuf-generated types from the new services' `contracts/` packages. The replay test SHALL run the new workflow code against the recorded history and SHALL pass.

#### Scenario: Replay test passes against recorded remote-activity history

- **WHEN** the test framework runs the replay test with a recorded history
- **THEN** the workflow produces the same result as the recorded history
- **AND** the test passes

#### Scenario: Replay test detects non-deterministic change in remote activity order

- **WHEN** the workflow code reorders the `ReserveInventoryActivityV1` and `ProcessPaymentActivityV1` activities
- **THEN** the replay test fails with a non-deterministic-replay error
- **AND** the test output points at the file and line of the reordered activity

### Requirement: Release gate runs the full cross-service smoke test

The `.github/workflows/verify.yml` CI pipeline SHALL run the full cross-service smoke test (including the four new contract tests and the full orchestration test) before the release is published. The release SHALL be blocked if any test fails or times out. The smoke test timeout SHALL be extended from 30m to 45m to accommodate the additional tests.

#### Scenario: CI release gate runs the full smoke test

- **WHEN** a release is published
- **THEN** the CI pipeline runs `make test-e2e-up` and `cd tests/cross-service-smoke && go test -count=1 -timeout=45m -v ./...`
- **AND** the release is blocked if any test fails or times out
