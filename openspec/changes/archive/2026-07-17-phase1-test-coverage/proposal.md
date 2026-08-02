# phase1-test-coverage

## Why

The test-coverage-gap-closure spec was just synced to main specs. The audit found that five critical-gap services (customer, notification, payment, inventory, shipping) have 1-3 tests each versus a target of 30 minimum unit tests, and none meet the 90/90/80 branch coverage thresholds. Phase 1 closes the most critical gaps across these services and expands architecture test coverage for catalog-service.

## What Changes

- Add 30+ unit tests to `customer-service` covering domain (customer, GDPR) and application layers
- Add 30+ unit tests to `notification-service` covering domain and application layers
- Add 30+ unit tests to `payment-service` covering domain and application layers
- Add 30+ unit tests to `inventory-service` covering domain and application layers
- Add 30+ unit tests to `shipping-service` covering domain and application layers
- Add shared test helpers (`testutil` package) to each of the five critical-gap services for database fixture setup, mock port implementations, and protobuf message construction
- Add architecture tests (`solewriter_test.go`, port-adapter conformance, domain purity) to `customer-service`, `notification-service`, `payment-service`, `inventory-service`, and `shipping-service`
- Expand `catalog-service` architecture tests with sole-writer, port-adapter conformance, and domain purity tests
- Add PostgreSQL integration tests using testcontainers for `payment-service`, `inventory-service`, and `shipping-service` adapter layers
- Expand cross-service smoke tests in `order-service` to cover customer-service, notification-service, catalog-service, and reporting-service protobuf contracts
- Add coverage enforcement to CI via `go test -coverprofile` with threshold gates

## Capabilities

### New Capabilities

_None. This change implements existing specifications._

### Modified Capabilities

- `test-coverage-gap-closure`: Implement Phase 1 requirements -- critical-gap unit test expansion (5 services), architecture test expansion (6 services), integration tests (3 services), cross-service smoke test expansion, shared test helpers, and CI coverage gates

## Impact

**Services affected:**
- `customer-service` -- heaviest change: new unit tests, architecture tests, testutil package
- `notification-service` -- new unit tests, architecture tests, testutil package
- `payment-service` -- new unit tests, architecture tests, integration tests, testutil package
- `inventory-service` -- new unit tests, architecture tests, integration tests, testutil package
- `shipping-service` -- new unit tests, architecture tests, integration tests, testutil package
- `catalog-service` -- expanded architecture tests only (sole-writer, port-adapter, domain purity)
- `order-service` -- expanded cross-service smoke tests for customer, notification, catalog, reporting contracts
- `reporting-service` -- no changes (already meets targets at 15 tests with sole-writer)

**CI pipeline:**
- New coverage threshold gate step: `go test -coverprofile` with 90/90/80 enforcement per service
- Integration test step requiring testcontainers (Docker-in-CI)
- Architecture test step running `test/architecture/` package for all services

**Dependencies:**
- `testcontainers-go` added to `go.mod` for payment, inventory, and shipping integration tests
- `stretchr/testify` already present across all services (no change)
