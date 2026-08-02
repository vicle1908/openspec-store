# circuit-breaker Specification

## Purpose
The platform implements circuit breaker pattern for outbound HTTP and gRPC calls to prevent cascading failures across services.

## Requirements

> **Status**: DEFERRED. Design defined in spec; no circuit breaker implementation, middleware, metrics, or configuration found in codebase.

### Requirement: Circuit breaker states

> **Status**: DEFERRED. Circuit breaker design exists in phase5-platform-features; no implementation found.

The circuit breaker SHALL maintain three states: `CLOSED`, `OPEN`, and `HALF-OPEN`. State transitions SHALL be deterministic based on failure/success counts and timeout configuration.

#### Scenario: CLOSED to OPEN transition
- **WHEN** the circuit breaker is in `CLOSED` state and consecutive failures reach the configured threshold (default 5)
- **THEN** the circuit breaker transitions to `OPEN` state

#### Scenario: OPEN to HALF-OPEN transition
- **WHEN** the circuit breaker is in `OPEN` state and the recovery timeout (default 30s) has elapsed
- **THEN** the circuit breaker transitions to `HALF-OPEN` state

#### Scenario: HALF-OPEN to CLOSED transition
- **WHEN** the circuit breaker is in `HALF-OPEN` state and the success threshold (default 2) is met
- **THEN** the circuit breaker transitions to `CLOSED` state

#### Scenario: HALF-OPEN to OPEN transition
- **WHEN** the circuit breaker is in `HALF-OPEN` state and a failure occurs
- **THEN** the circuit breaker transitions back to `OPEN` state

### Requirement: Failure criteria

> **Status**: DEFERRED. Failure criteria defined in spec; no implementation found.

For HTTP calls, the circuit breaker SHALL treat 5xx status codes as failures and 4xx status codes as successes. For gRPC calls, `UNAVAILABLE`, `DEADLINE_EXCEEDED`, and `INTERNAL` status codes SHALL be treated as failures. Connection timeouts SHALL be treated as failures.

#### Scenario: HTTP 5xx triggers failure count
- **WHEN** a downstream HTTP call returns 500
- **THEN** the circuit breaker increments the failure counter

#### Scenario: HTTP 4xx does not trigger failure count
- **WHEN** a downstream HTTP call returns 404
- **THEN** the circuit breaker does not increment the failure counter

#### Scenario: gRPC UNAVAILABLE triggers failure count
- **WHEN** a downstream gRPC call returns `UNAVAILABLE`
- **THEN** the circuit breaker increments the failure counter

### Requirement: Circuit breaker middleware

> **Status**: DEFERRED. Middleware design exists; pkg/resilience not implemented.

The circuit breaker SHALL be available as HTTP middleware and gRPC unary interceptor via `pkg/resilience`. The middleware SHALL be configurable per service target with independent state machines.

#### Scenario: HTTP client uses circuit breaker
- **WHEN** an HTTP client is configured with circuit breaker middleware targeting `order-service`
- **THEN** all calls to `order-service` pass through the circuit breaker; calls to other services are unaffected

#### Scenario: Open circuit returns immediately
- **WHEN** the circuit breaker for `order-service` is in `OPEN` state
- **THEN** an HTTP call to `order-service` returns 503 Service Unavailable without making a network call

### Requirement: Metrics

> **Status**: DEFERRED. Metrics design exists; no circuit breaker metrics implementation found.

The circuit breaker SHALL expose metrics for monitoring: current state, failure count, success count, and last state transition time. Metrics SHALL be available via Prometheus endpoint.

#### Scenario: Metrics endpoint reports circuit state
- **WHEN** the circuit breaker is queried for metrics
- **THEN** the response includes `circuit_breaker_state`, `circuit_breaker_failures`, and `circuit_breaker_successes`

### Requirement: Configuration

> **Status**: DEFERRED. Configuration schema defined; no YAML configuration implementation found.

The circuit breaker SHALL be configurable via YAML with the following fields: `enabled` (bool), `failure_threshold` (int, default 5), `recovery_timeout_ms` (int, default 30000), `half_open_max_calls` (int, default 3), `success_threshold` (int, default 2).

#### Scenario: Circuit breaker is disabled by configuration
- **WHEN** `circuit_breaker.enabled` is `false`
- **THEN** all circuit breaker middleware is a no-op passthrough
