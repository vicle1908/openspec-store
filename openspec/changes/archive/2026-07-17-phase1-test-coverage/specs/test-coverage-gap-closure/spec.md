# test-coverage-gap-closure Delta — Phase 1 Implementation

## MODIFIED Requirements

### Requirement: Critical-gap services reach minimum unit test count

> **Status**: IN PROGRESS. Phase 1 implements this requirement for 5 services.

The following services currently have critical test gaps and SHALL each reach a minimum of 30 unit tests within the domain and application layers: `customer-service` (currently 3 tests), `notification-service` (currently 2 tests), `payment-service` (currently 1 test), `inventory-service` (currently 1 test), and `shipping-service` (currently 1 test). The 30-test minimum is a floor; the coverage percentage thresholds in the previous requirement remain the binding target.

#### Scenario: Customer service reaches minimum unit tests
- **WHEN** the `customer-service` test suite runs
- **THEN** it SHALL contain at least 30 unit tests across `internal/domain/customer/`, `internal/domain/gdpr/`, and `internal/application/`

#### Scenario: Payment service reaches minimum unit tests
- **WHEN** the `payment-service` test suite runs
- **THEN** it SHALL contain at least 30 unit tests across `internal/domain/` and `internal/application/`

#### Scenario: Shipping service reaches minimum unit tests
- **WHEN** the `shipping-service` test suite runs
- **THEN** it SHALL contain at least 30 unit tests across `internal/domain/` and `internal/application/`

#### Scenario: Inventory service reaches minimum unit tests
- **WHEN** the `inventory-service` test suite runs
- **THEN** it SHALL contain at least 30 unit tests across `internal/domain/` and `internal/application/`

#### Scenario: Notification service reaches minimum unit tests
- **WHEN** the `notification-service` test suite runs
- **THEN** it SHALL contain at least 30 unit tests across `internal/domain/notification/` and `internal/application/`

#### Scenario: Implementation approach — shared test helpers
- **WHEN** each critical-gap service implements its test suite
- **THEN** shared test helpers (mocks, fixtures, DB setup) SHALL live in `internal/testutil/` to avoid duplication across test files

#### Scenario: Implementation approach — domain-first testing
- **WHEN** tests are added to a critical-gap service
- **THEN** domain layer tests SHALL be implemented first (state machines, invariants, events), followed by application layer tests (command handlers, idempotency), following the order-service reference pattern
