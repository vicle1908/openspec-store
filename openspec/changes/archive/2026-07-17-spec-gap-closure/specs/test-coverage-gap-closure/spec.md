# test-coverage-gap-closure Specification

## Purpose

Close the test coverage gap across non-order services. The audit revealed that `order-service` has 72 tests (meets targets) while six other services have 1-15 tests, far below the 90/90/80 coverage targets (unit/integration/e2e). This spec defines the minimum test requirements every service SHALL meet.

## ADDED Requirements

### Requirement: Unit test coverage targets per service
Every service SHALL maintain unit test coverage meeting minimum thresholds: 90% branch coverage for domain packages, 90% branch coverage for application packages, and 80% branch coverage for adapter packages. Coverage SHALL be measured by `go test -coverprofile` and enforced by CI.

#### Scenario: Service meets unit coverage threshold
- **WHEN** CI runs `go test -coverprofile` for a service's `internal/domain/`, `internal/application/`, and `internal/adapters/` packages
- **THEN** branch coverage for domain and application packages SHALL be at least 90%, and branch coverage for adapter packages SHALL be at least 80%

#### Scenario: Coverage regression is blocked
- **WHEN** a pull request introduces changes that drop any service's coverage below the threshold
- **THEN** CI SHALL fail and the pull request SHALL NOT be merged

### Requirement: Critical-gap services reach minimum unit test count
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

### Requirement: Architecture test expansion beyond layering
Every service SHALL implement architecture tests beyond `layering_test.go`. Each service SHALL have tests covering at minimum: layering (import isolation), sole-writer (database schema ownership), port-adapters contract conformance, and domain purity (no framework annotations in domain). These tests SHALL live under `test/architecture/` and run in CI.

#### Scenario: All services have sole-writer architecture test
- **WHEN** CI runs architecture tests for any service
- **THEN** a `solewriter_test.go` (or equivalent) SHALL exist and pass, confirming the service is the sole writer of its own PostgreSQL schema

#### Scenario: All services have port-adapter conformance test
- **WHEN** CI runs architecture tests for any service
- **THEN** a port-adapter conformance test SHALL exist and pass, confirming every adapter implements at least one port interface

#### Scenario: All services have domain purity test
- **WHEN** CI runs architecture tests for any service
- **THEN** a domain purity test SHALL exist and pass, confirming domain packages contain no framework annotations, HTTP handler registrations, or infrastructure imports

#### Scenario: Catalog service expands beyond existing architecture tests
- **WHEN** the `catalog-service` architecture test suite runs
- **THEN** it SHALL include sole-writer, port-adapter conformance, and domain purity tests in addition to the existing `layering_test.go`, `cache_admission_test.go`, `osshim_test.go`, and `runtime_test.go`

### Requirement: Integration tests for services with database adapters
Every service that has a PostgreSQL adapter SHALL have integration tests that exercise the adapter against a real PostgreSQL instance (via testcontainers or Docker Compose test profile). Integration tests SHALL cover CRUD operations for each repository, transaction rollback behavior, and connection pool resilience.

#### Scenario: Inventory service has postgres integration tests
- **WHEN** CI runs integration tests for `inventory-service`
- **THEN** tests SHALL exercise the postgres adapter against a containerized PostgreSQL instance, covering create/read/update/delete paths for each repository

#### Scenario: Payment service has postgres integration tests
- **WHEN** CI runs integration tests for `payment-service`
- **THEN** tests SHALL exercise the postgres adapter against a containerized PostgreSQL instance, covering payment record persistence and retrieval

#### Scenario: Shipping service has postgres integration tests
- **WHEN** CI runs integration tests for `shipping-service`
- **THEN** tests SHALL exercise the postgres adapter against a containerized PostgreSQL instance, covering shipment record persistence and retrieval

#### Scenario: Transaction rollback is verified
- **WHEN** an integration test triggers a partial failure within a database transaction
- **THEN** the test SHALL confirm that no partial writes persisted and the database state matches the pre-transaction state

### Requirement: Cross-service smoke tests cover all service interactions
The existing cross-service contract smoke tests in `order-service/cmd/order-service/` (covering inventory, payment, and shipping contracts) SHALL be expanded to cover every inter-service communication path. Each smoke test SHALL verify the protobuf contract shape, not a live dependency.

#### Scenario: Customer service interaction is smoke-tested
- **WHEN** the cross-service smoke test suite runs
- **THEN** a smoke test SHALL verify that the customer-service protobuf contract for customer lookup is consumed correctly by the order-service (or whichever service calls it)

#### Scenario: Notification service interaction is smoke-tested
- **WHEN** the cross-service smoke test suite runs
- **THEN** a smoke test SHALL verify that the notification-service protobuf contract for dispatch is consumed correctly by its caller(s)

#### Scenario: Catalog service interaction is smoke-tested
- **WHEN** the cross-service smoke test suite runs
- **THEN** a smoke test SHALL verify that the catalog-service protobuf contract for product and pricing queries is consumed correctly by its caller(s)

#### Scenario: Reporting service interaction is smoke-tested
- **WHEN** the cross-service smoke test suite runs
- **THEN** a smoke test SHALL verify that the reporting-service consumes order events with the correct protobuf envelope shape

### Requirement: Test helpers and fixtures are shared
Each service SHALL maintain shared test helpers under `internal/testutil/` or `test/helpers/` for common patterns such as database fixture setup, protobuf message construction, and mock port implementations. Duplicated test helper code across packages within the same service SHALL be consolidated.

#### Scenario: Shared database test helper exists
- **WHEN** a service has integration tests requiring a database
- **THEN** a shared helper function SHALL exist that provisions a test database, runs migrations, and returns a teardown function

#### Scenario: Shared mock ports exist
- **WHEN** a service has unit tests that need to substitute an adapter
- **THEN** mock implementations of the service's port interfaces SHALL be available in a shared `testutil` or `test/helpers` package, not duplicated across test files
