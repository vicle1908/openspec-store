# phase1-test-coverage Design

## Context

The monorepo has 8 Go services. The audit measured unit test counts per service:

| Service | Current tests | Target min | Gap |
|---|---|---|---|
| customer-service | 3 | 30 | 27 |
| notification-service | 2 | 30 | 28 |
| payment-service | 1 | 30 | 29 |
| inventory-service | 1 | 30 | 29 |
| shipping-service | 1 | 30 | 29 |
| catalog-service | 12 | 30 | 18 (plus architecture expansion) |
| reporting-service | 15 | 30 | 15 |
| order-service | 72 | 30 | meets target |

The binding targets from the spec are branch coverage percentages (90% domain, 90% application, 80% adapter), with the 30-test minimum as a floor. Architecture tests currently exist only as `layering_test.go` in each service; the spec requires sole-writer, port-adapter conformance, and domain purity tests as well.

All services use `stretchr/testify` for assertions. The order-service serves as the reference implementation with 72 tests, architecture tests, postgres adapter integration tests, and cross-service smoke tests.

## Goals / Non-Goals

**Goals:**
- Each of the five critical-gap services reaches 30+ unit tests in domain and application layers
- All 7 services (excluding order-service) implement the four architecture test categories: layering, sole-writer, port-adapter conformance, domain purity
- PostgreSQL integration tests exist for payment, inventory, and shipping services using testcontainers
- Cross-service smoke tests cover customer, notification, catalog, and reporting protobuf contracts
- Shared test helpers are consolidated into `testutil` packages per service
- CI enforces coverage thresholds and blocks PRs that regress below them

**Non-Goals:**
- Reaching 90/90/80 coverage thresholds in this phase (Phase 1 focuses on test count floor and architecture tests; coverage threshold enforcement is the CI gate, not the immediate target)
- E2E tests (those are out of scope for Phase 1; the spec's e2e requirement is deferred)
- Refactoring service code to improve testability (tests work against existing interfaces)
- Changing the reporting-service (already has 15 tests plus sole-writer; left for a later phase)
- Modifying the order-service beyond adding smoke tests (it already meets targets)

## Decisions

### D1: Use stdlib `testing` + `testify` for all unit tests

Rationale: Every service already depends on `stretchr/testify`. The order-service reference implementation uses `require` and `assert` from testify. Introducing additional frameworks (gomock, ginkgo) would add dependencies without clear benefit since port interfaces are simple enough to mock by hand.

### D2: Use `testcontainers-go` for integration tests

Rationale: The spec explicitly permits testcontainers or Docker Compose test profiles. `testcontainers-go` provides programmatic container lifecycle management within the test binary, which keeps integration tests self-contained and avoids Docker Compose orchestration complexity. Each test function provisions its own PostgreSQL container, runs migrations, exercises CRUD, and tears down. This matches the order-service postgres adapter test pattern.

### D3: Place architecture tests under `test/architecture/` per service

Rationale: Every service already has a `test/architecture/` directory with `layering_test.go` (or `layers_test.go`). New architecture tests go in the same package to share test helpers and maintain consistency. The existing reporting-service `solewriter_test.go` and `layering_test.go` serve as the template.

### D4: Consolidate test helpers into `internal/testutil/` (or `test/helpers/`)

Rationale: The spec requires shared helpers for database fixture setup, protobuf message construction, and mock port implementations. Each service gets its own `testutil` package containing:
- `db.go` -- `SetupTestDB(t *testing.T) (db *sql.DB, teardown func())` wrapping testcontainers
- `mocks.go` -- mock implementations of the service's port interfaces
- `fixtures.go` -- factory functions for domain objects and protobuf messages

This avoids duplication across test files within a service. Cross-service helper sharing is not in scope for Phase 1.

### D5: Coverage enforcement via `go test -coverprofile` + threshold script

Rationale: The spec requires CI to fail when coverage drops below thresholds. The implementation uses `go test -coverprofile=coverage.out ./internal/domain/... ./internal/application/...` and parses branch coverage with `go tool cover -func`. A simple shell script or Go binary checks the percentages and exits non-zero if any package falls below its threshold. This is added as a CI step per service, not a global gate, so services can be enabled incrementally.

### D6: Cross-service smoke tests verify protobuf contract shape, not live dependencies

Rationale: The spec states smoke tests "verify the protobuf contract shape, not a live dependency." Following the order-service pattern, smoke tests instantiate the client with a test URL, call the endpoint, and assert the response shape matches expectations. They use `testing.Short()` to skip in short mode. New smoke tests follow the same `smoke_*_contract_test.go` naming convention in `cmd/order-service/`.

### D7: Per-service implementation order prioritized by gap size

Rationale: Services are implemented in order of gap size to maximize impact early:
1. payment-service (1 test, needs 29 more)
2. inventory-service (1 test, needs 29 more)
3. shipping-service (1 test, needs 29 more)
4. notification-service (2 tests, needs 28 more)
5. customer-service (3 tests, needs 27 more)
6. catalog-service (architecture expansion only)
7. order-service (smoke test expansion only)

## Risks / Trade-offs

### R1: Integration tests require Docker in CI
**Risk:** CI runners must support Docker for testcontainers. If the CI environment lacks Docker, integration tests fail.
**Mitigation:** Integration tests are gated behind `testing.Short()` and a build tag (`//go:build integration`). CI runs them only in the integration test stage where Docker is available. Unit tests and architecture tests run without Docker.

### R2: Testcontainers slow down local development
**Risk:** Each integration test spins up a PostgreSQL container, which takes 10-30 seconds on first pull.
**Mitigation:** Use `testcontainers.GenericContainer` with a shared container across test functions in the same package (package-level `TestMain`). Subsequent tests reuse the running container. Container images are pre-pulled in CI.

### R3: Mock drift as port interfaces evolve
**Risk:** Hand-written mocks in `testutil/mocks.go` may drift from port interface changes.
**Mitigation:** Mocks live in the same module as the ports they implement. Compiler enforces interface satisfaction (`var _ PortInterface = (*MockPort)(nil)`). A future phase can introduce `moq` or `mockgen` generation if needed.

### R4: Coverage thresholds may be too aggressive for Phase 1
**Risk:** The 90/90/80 targets are the binding spec requirement, but Phase 1 focuses on test count floor. Enforcing coverage gates immediately may cause PR failures before enough tests exist.
**Mitigation:** CI coverage gates are added but initially set to warn (non-blocking). They become blocking once the test count floor is met. This allows incremental progress without blocking the entire team.

### R5: Smoke test expansion depends on protobuf definitions
**Risk:** Smoke tests for customer, notification, catalog, and reporting contracts require knowing the protobuf message shapes and service endpoints. If protobuf definitions are incomplete or undocumented, smoke tests may be incorrect.
**Mitigation:** Smoke tests are derived from the `.proto` files under `openspec/` or `platform/`. Each smoke test file includes a comment referencing the source `.proto` file. If a protobuf definition is missing, the smoke test documents the gap.
