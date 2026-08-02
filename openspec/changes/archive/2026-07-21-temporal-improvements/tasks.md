# Tasks: Temporal Improvements

## Phase 1: Critical -- Worker Versioning v2 for All Services

### 1.1: Fix DeploymentVersion() fail-fast guard
- [x] Add a guard in each service's `runWorker` function that checks `platformtemporal.DeploymentVersion()` is non-empty before constructing `worker.New`
- [x] The guard SHALL panic with `FAIL: DeploymentVersion is empty` if the value is empty
- [x] Verify the `"dev"` default in `platform/temporal/deployment.go` is reachable when both `PLATFORM_DEPLOYMENT_VERSION` and `GIT_SHA` are unset
- [x] Run `go test ./platform/temporal/...` to verify existing deployment tests pass

### 1.2: Wire Worker Versioning v2 for notification-service
- [x] Add `UseVersioning: true`, `BuildID: platformtemporal.DeploymentVersion()`, `DeploymentSeriesName: "notification-dispatch.v1"` to the worker options in `services/notification-service/cmd/notification-service/`
- [x] Add `UseVersioning: true` to all `StartWorkflowOptions` in the notification-service orchestrator
- [x] Run replay test (once created in 2.1) to verify non-determinism safety
- [x] Run `go test ./services/notification-service/...` to verify all tests pass

### 1.3: Wire Worker Versioning v2 for catalog-service
- [x] Add `UseVersioning: true`, `BuildID: platformtemporal.DeploymentVersion()`, `DeploymentSeriesName: "catalog.admin.v1"` to the worker options in `services/catalog-service/cmd/catalog-service/`
- [x] Add `UseVersioning: true` to all `StartWorkflowOptions` in the catalog-service orchestrator
- [x] Run replay test (once created in 2.2) to verify non-determinism safety
- [x] Run `go test ./services/catalog-service/...` to verify all tests pass

### 1.4: Wire Worker Versioning v2 for inventory-service
- [x] Add `UseVersioning: true`, `BuildID: platformtemporal.DeploymentVersion()`, `DeploymentSeriesName: "inventory.reservation.v1"` to the worker options in `services/inventory-service/cmd/inventory-service/`
- [x] Add `UseVersioning: true` to all `StartWorkflowOptions` in the inventory-service orchestrator
- [x] Run replay test (once created in 2.3) to verify non-determinism safety
- [x] Run `go test ./services/inventory-service/...` to verify all tests pass

### 1.5: Wire Worker Versioning v2 for payment-service
- [x] Add `UseVersioning: true`, `BuildID: platformtemporal.DeploymentVersion()`, `DeploymentSeriesName: "payment.capture.v1"` to the worker options in `services/payment-service/cmd/payment-service/`
- [x] Add `UseVersioning: true` to all `StartWorkflowOptions` in the payment-service orchestrator
- [x] Run replay test (once created in 2.4) to verify non-determinism safety
- [x] Run `go test ./services/payment-service/...` to verify all tests pass

### 1.6: Wire Worker Versioning v2 for shipping-service
- [x] Add `UseVersioning: true`, `BuildID: platformtemporal.DeploymentVersion()`, `DeploymentSeriesName: "shipping.dispatch.v1"` to the worker options in `services/shipping-service/cmd/shipping-service/`
- [x] Add `UseVersioning: true` to all `StartWorkflowOptions` in the shipping-service orchestrator
- [x] Run replay test (once created in 2.5) to verify non-determinism safety
- [x] Run `go test ./services/shipping-service/...` to verify all tests pass

### 1.7: Wire Worker Versioning v2 for customer-service (fix panic)
- [x] Re-apply Worker Versioning v2 registration with `UseVersioning: true`, `BuildID: platformtemporal.DeploymentVersion()`, `DeploymentSeriesName: "customer-gdpr.v1"` to the worker options in `services/customer-service/cmd/customer-service/`
- [x] Add `UseVersioning: true` to all `StartWorkflowOptions` in the customer-service orchestrator
- [x] Verify the fail-fast guard from task 1.1 prevents the empty `DeploymentVersion()` panic
- [x] Run `go test ./services/customer-service/...` to verify all tests pass

### 1.8: Wire Worker Versioning v2 for reporting-service
- [x] Add `UseVersioning: true`, `BuildID: platformtemporal.DeploymentVersion()`, `DeploymentSeriesName: "reporting"` to the worker options in `services/reporting-service/cmd/reporting-service/`
- [x] Add `UseVersioning: true` to all `StartWorkflowOptions` in the reporting-service orchestrator
- [x] Run replay test (once created in 2.6) to verify non-determinism safety
- [x] Run `go test ./services/reporting-service/...` to verify all tests pass

### 1.9: Wire Worker Versioning v2 for order-service (complete)
- [x] Ensure existing partial registration includes `UseVersioning: true` on both worker and `startWorkflow` caller
- [x] Add `UseVersioning: true` to `processor.go::startWorkflow` `StartWorkflowOptions` if not already present
- [x] Run existing replay test `test/compatibility/order_fulfillment_replay_test.go` to verify
- [x] Run `go test ./services/order-service/...` to verify all tests pass

### 1.10: Add architecture test for Worker Versioning v2
- [x] Add architecture test that scans all 8 services for `UseVersioning: true` in worker initialization
- [x] Verify the test fails if any service is missing Worker Versioning v2 configuration
- [x] Integrate the test into `make verify-pr` or `make services-verify`
- [x] Run `make services-verify` to confirm all services pass

## Phase 2: High -- Customer-Service Fix and Workflow Replay Tests

### 2.1: Add replay test for notification-service
- [x] Create `services/notification-service/test/compatibility/notification_dispatch_replay_test.go`
- [x] Record a successful workflow execution history for the notification dispatch workflow
- [x] Implement the replay test using `test.NewWorkflowEnvironment()` with `RegisterWorkflowWithOptions`
- [x] Verify the replay test passes: `go test ./services/notification-service/test/compatibility/...`

### 2.2: Add replay test for catalog-service
- [x] Create `services/catalog-service/test/compatibility/price_rollback_replay_test.go`
- [x] Record a successful workflow execution history for the price rollback workflow
- [x] Implement the replay test using `test.NewWorkflowEnvironment()` with `RegisterWorkflowWithOptions`
- [x] Verify the replay test passes: `go test ./services/catalog-service/test/compatibility/...`

### 2.3: Add replay test for inventory-service
- [x] Create `services/inventory-service/test/compatibility/reservation_replay_test.go`
- [x] Record a successful workflow execution history for the inventory reservation workflow
- [x] Implement the replay test using `test.NewWorkflowEnvironment()` with `RegisterWorkflowWithOptions`
- [x] Verify the replay test passes: `go test ./services/inventory-service/test/compatibility/...`

### 2.4: Add replay test for payment-service
- [x] Create `services/payment-service/test/compatibility/capture_replay_test.go`
- [x] Record a successful workflow execution history for the payment capture workflow
- [x] Implement the replay test using `test.NewWorkflowEnvironment()` with `RegisterWorkflowWithOptions`
- [x] Verify the replay test passes: `go test ./services/payment-service/test/compatibility/...`

### 2.5: Add replay test for shipping-service
- [x] Create `services/shipping-service/test/compatibility/dispatch_replay_test.go`
- [x] Record a successful workflow execution history for the shipping dispatch workflow
- [x] Implement the replay test using `test.NewWorkflowEnvironment()` with `RegisterWorkflowWithOptions`
- [x] Verify the replay test passes: `go test ./services/shipping-service/test/compatibility/...`

### 2.6: Add replay test for reporting-service
- [x] Create `services/reporting-service/test/compatibility/admin_replay_test.go`
- [x] Record a successful workflow execution history for the reporting admin workflow
- [x] Implement the replay test using `test.NewWorkflowEnvironment()` with `RegisterWorkflowWithOptions`
- [x] Verify the replay test passes: `go test ./services/reporting-service/test/compatibility/...`

### 2.7: Add replay test for customer-service
- [x] Create `services/customer-service/test/compatibility/purge_replay_test.go` and `export_replay_test.go`
- [x] Record successful workflow execution histories for both the purge and GDPR export workflows
- [x] Implement the replay tests using `test.NewWorkflowEnvironment()` with `RegisterWorkflowWithOptions`
- [x] Verify both replay tests pass: `go test ./services/customer-service/test/compatibility/...`

### 2.8: Verify replay tests catch non-determinism
- [x] Introduce a deliberate `time.Now()` call in one workflow's test double
- [x] Verify the replay test fails with a deterministic-replay error
- [x] Remove the deliberate non-determinism and verify the test passes again

## Phase 3: Medium -- Circuit Breaker and Activity Timeouts

### 3.1: Wire ErrPeerUnavailable as NonRetryableApplicationError in all activities
- [x] In `services/order-service/internal/adapters/temporal/activities.go`, wrap `clients.ErrPeerUnavailable` as `temporal.NewNonRetryableApplicationError("peer_unavailable", "PEER_UNAVAILABLE", err)` in `ValidateInventoryActivityV1`
- [x] Apply the same wrapping in `ProcessPaymentActivityV1`
- [x] Apply the same wrapping in `ReserveInventoryActivityV1`
- [x] Apply the same wrapping in `MarkOrderShippedActivityV1`
- [x] Apply the same wrapping in `RefundPaymentActivityV1`
- [x] Apply the same wrapping in `ReleaseInventoryActivityV1`

### 3.2: Add circuit breaker integration test
- [x] Create `services/order-service/test/integration/circuit_breaker_test.go`
- [x] Mock the downstream HTTP servers to return 5xx for 5 consecutive requests
- [x] Verify the circuit breaker transitions to OPEN state
- [x] Verify the activity returns `NonRetryableApplicationError` with `error_type: "PEER_UNAVAILABLE"`
- [x] Verify the workflow takes the compensation path (RefundPayment and ReleaseInventory run)

### 3.3: Migrate order-service activities to NewValidatedActivityOptions
- [x] Replace inline timeout constants in `services/order-service/internal/adapters/temporal/workflow.go` with `platformtemporal.NewValidatedActivityOptions`
- [x] Ensure `activityStartToClose=5min`, `activityHeartbeat=30s`, `ScheduleToCloseTimeout=10m` pass validation
- [x] Verify existing replay test still passes (timeout values must remain identical for replay compatibility)
- [x] Run `go test ./services/order-service/...` to verify all tests pass

### 3.4: Add architecture test for activity timeout validation
- [x] Add architecture test that verifies all services use `NewValidatedActivityOptions` (or equivalent validated options)
- [x] Verify the test fails if any activity is registered with zero timeouts
- [x] Integrate the test into `make verify-pr` or `make services-verify`

## Completion Criteria

- [x] All 8 services configure Worker Versioning v2 (`UseVersioning: true`, non-empty `BuildID`, service-specific `DeploymentSeriesName`)
- [x] All 8 services have at least one `*_replay_test.go` file that passes
- [x] Customer-service Worker Versioning v2 does not panic in local dev (no env vars set)
- [x] Circuit breaker integration test validates the open-circuit -> compensation path
- [x] All 6 order-service activities wrap `ErrPeerUnavailable` as `NonRetryableApplicationError`
- [x] Order-service activities use `NewValidatedActivityOptions` instead of raw `worker.ActivityOptions`
- [x] Architecture test enforces Worker Versioning v2 across all 8 services
- [x] `make services-verify` passes for all services
