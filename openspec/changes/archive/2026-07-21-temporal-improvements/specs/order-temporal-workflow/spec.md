# order-temporal-workflow Delta Specification

## Purpose

This delta updates the main `order-temporal-workflow` spec to reflect the temporal-improvements change: circuit breaker status advances from DEFERRED to IN PROGRESS, and a new activity timeout enforcement requirement is added.

## MODIFIED Requirements

### Requirement: Per-peer circuit breaker on each activity's HTTP client [IN PROGRESS]

> **Status**: IN PROGRESS. The `sony/gobreaker` dependency exists in `services/order-service/internal/adapters/temporal/clients/`. The HTTP clients (`payment_client.go`, `inventory_client.go`, `shipping_client.go`) create gobreaker instances. However, the activity code in `activities.go` does not consistently treat `ErrPeerUnavailable` as a `NonRetryableApplicationError` in all code paths. The open-circuit -> activity failure -> workflow compensation chain is not fully wired, and no integration test exercises this path. This change completes the wiring and adds the integration test.

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

#### Scenario: All 6 activities handle ErrPeerUnavailable

- **WHEN** any of the 6 activities (ValidateInventory, ProcessPayment, ReserveInventory, MarkOrderShipped, RefundPayment, ReleaseInventory) receives `clients.ErrPeerUnavailable`
- **THEN** the activity returns `temporal.NewNonRetryableApplicationError("peer_unavailable", "PEER_UNAVAILABLE", err)`
- **AND** the workflow does not retry the activity

### Requirement: Activities declare explicit timeouts sourced from the platform [IN PROGRESS]

> **Status**: IN PROGRESS. The order-service defines activity timeouts inline in `services/order-service/internal/adapters/temporal/workflow.go` (`activityStartToClose=5min`, `activityHeartbeat=30s`, `ScheduleToCloseTimeout=activityStartToClose*2`). The platform's `NewValidatedActivityOptions` helper exists in `platform/temporal/activity_options.go`. However, not all activities across all services use the validated helper; some services register activities with raw `worker.ActivityOptions` bypassing the platform's compile-time enforcement. This change ensures all order-service activities use the platform helper.

Activities SHALL declare `StartToCloseTimeout`, `ScheduleToCloseTimeout`, and (for long-running activities) `HeartbeatTimeout` via the platform's `NewValidatedActivityOptions` helper, which enforces presence of these fields at compile time. The order-service's existing constants (`activityStartToClose=5min`, `activityHeartbeat=30s`, `ScheduleToCloseTimeout=activityStartToClose*2`) move into the platform module so future services inherit the same bounds.

#### Scenario: NewValidatedActivityOptions refuses missing timeouts

- **WHEN** a service constructs activity options without `StartToCloseTimeout` and `ScheduleToCloseTimeout`
- **THEN** `NewValidatedActivityOptions` returns an error and the activity cannot register

#### Scenario: Compensations get tighter timeouts than forward steps

- **WHEN** a compensation activity is registered
- **THEN** its `StartToCloseTimeout` is half the forward-step timeout (the platform enforces this in `NewValidatedActivityOptions`)

#### Scenario: Order-service activities use platform helper

- **WHEN** `services/order-service/internal/adapters/temporal/workflow.go` registers activities
- **THEN** it uses `platformtemporal.NewValidatedActivityOptions` instead of raw `worker.ActivityOptions`
- **AND** the activity options pass validation (non-zero timeouts, StartToClose < ScheduleToClose)
