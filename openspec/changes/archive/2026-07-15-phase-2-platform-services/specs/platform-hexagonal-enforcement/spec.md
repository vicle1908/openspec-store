## ADDED Requirements

### Requirement: Hexagonal layer isolation
Every service's Go code SHALL conform to a strict layering: `cmd → adapters → ports → application → domain`. The platform's `test/architecture/` package SHALL enforce the following import rules via Go's `golang.org/x/tools/go/packages` API:

| Layer | MAY import | MUST NOT import |
|---|---|---|
| `internal/domain/<service>/` | stdlib, `platform/contracts`, `platform/observability` (read-only types only), Protobuf-generated code under `contracts/<domain>/vN/` | any adapter, any port, any infrastructure package, any peer service's `internal/` |
| `internal/application/` | `internal/domain/`, `internal/ports/`, `platform/contracts`, `platform/observability` (logging), `platform/health` (check registration), `platform/cache` (typed interface only) | any adapter, any `internal/adapters/...` package |
| `internal/ports/` | `internal/domain/`, stdlib, Protobuf-generated code | any adapter, any infrastructure package |
| `internal/adapters/<kind>/` | `internal/ports/`, `internal/application/` (where the adapter is a driven adapter that needs to invoke application logic), `internal/domain/` (for type definitions only), Protobuf-generated code, vendor SDK, `platform/kafka`, `platform/runtime`, `platform/observability`, `platform/health`, `platform/cache` (adapter implementation) | any other adapter (an HTTP adapter MUST NOT import a Kafka adapter and vice versa) |
| `cmd/` | any layer | n/a |

#### Scenario: Domain package imports no adapter
- **WHEN** `TestDomainDoesNotImportAdapters` runs against the service's module
- **THEN** the test fails any import of `internal/adapters/...` from any file under `internal/domain/<service>/`

#### Scenario: Application package imports no adapter
- **WHEN** `TestApplicationDoesNotImportAdapters` runs against the service's module
- **THEN** the test fails any import of `internal/adapters/...` from any file under `internal/application/`

#### Scenario: Adapters do not import each other
- **WHEN** `TestAdaptersDoNotImportEachOther` runs against the service's module
- **THEN** the test fails any cross-adapter import (e.g., `internal/adapters/http` importing `internal/adapters/postgres`)

#### Scenario: Ports do not import adapters
- **WHEN** `TestPortsDoNotImportAdapters` runs against the service's module
- **THEN** the test fails any import of `internal/adapters/...` from any file under `internal/ports/`

### Requirement: Sole-writer database rule
Every service SHALL be the sole writer of its own PostgreSQL schema. The architecture test `TestSoleWriterRule` SHALL enforce this by scanning every SQL migration file in `migrations/<service>/` and every `database/sql.Exec`, `database/sql.Query`, `pgx.Exec`, or `pgxpool.Query` call site in `internal/adapters/postgres/` and confirming that the schema name in the migration matches the service name (e.g., `notifications` for the notification service). Any INSERT/UPDATE/DELETE/TRUNCATE statement that references a foreign schema name SHALL fail the test. The naming convention SHALL be `schema = singular service name` (e.g., `order`, `customer`, `catalog`, `notification`, `reporting`) and `table = plural entity name` (e.g., `orders`, `customers`, `products`, `notifications`, `outbox`, `receipts`, `prices`, `report_orders`) — a service's migrations and repositories SHALL use this convention so the architecture test's name-pattern check is unambiguous.

#### Scenario: Migration targets the service's schema
- **WHEN** a migration file contains `CREATE TABLE notifications`
- **THEN** the architecture test confirms the schema is `notifications` and the service is `notification-service`

#### Scenario: Foreign-schema write is rejected
- **WHEN** the application code executes `INSERT INTO customers.addresses VALUES (...)` from the notification service
- **THEN** the architecture test fails the build

#### Scenario: Cross-schema JOIN is rejected in domain code
- **WHEN** the application code in any service executes a JOIN that crosses schema boundaries
- **THEN** the architecture test fails the build

### Requirement: No peer-service internal imports
A service SHALL NOT import any other service's `internal/` package. The cross-service architecture test `TestHypotheticalPeerServiceCannotImportOrderInternals` SHALL walk the dependency graph of every service module and confirm that no service imports another service's `internal/`, `cmd/`, `migrations/`, or `contracts/` (except via `platform/contracts`, which is the canonical envelope). The test SHALL be cross-service — it runs once per CI pipeline with knowledge of every service module.

#### Scenario: Notification service does not import customer internals
- **WHEN** the cross-service architecture test runs
- **THEN** no file under `services/notification-service/internal/` imports a package under `services/customer-service/internal/`

#### Scenario: Cross-service shared types come from platform
- **WHEN** a service needs to share a type with another service
- **THEN** the type lives under `platform/contracts/` (read-only types) or under the producer service's `contracts/<domain>/vN/` (Protobuf)

### Requirement: No domain-type leakage in shared libraries
The shared `platform/` module SHALL NOT expose domain types from any service. The platform module's `pkg/` directory SHALL contain only infrastructure primitives (logger, tracer, metrics, cache interface, Kafka harness, health, runtime, contracts). Any domain type that two services need to share SHALL live in the producer service's `contracts/<domain>/vN/` and SHALL be consumed via the Protobuf-generated types only.

#### Scenario: Platform module exposes no domain types
- **WHEN** the platform module's `go doc ./pkg/...` output is reviewed
- **THEN** no type matches the pattern `<service>.<domain>` (e.g., `notification.Notification`, `order.Order`)

#### Scenario: Service importing platform does not get a peer's domain
- **WHEN** the notification service imports `platform/contracts`
- **THEN** the imported symbols are limited to the envelope helpers, the Protobuf common types, and the platform utility types

### Requirement: Domain invariants in the domain layer
A service's domain layer SHALL encode every invariant in the aggregate root or value object. The architecture test `TestDomainInvariantsAreEnforced` SHALL scan every public method on every aggregate and confirm: (1) the method returns a typed sentinel error when the invariant is violated (e.g., `ErrInvalidStatusTransition`, `ErrConcurrencyConflict`); (2) the method does not panic for any input; (3) the method does not log or produce metrics (those are concerns of the application layer).

#### Scenario: Invalid transition returns a typed error
- **WHEN** a domain method receives input that violates an invariant
- **THEN** the method returns a typed sentinel error and does NOT panic

#### Scenario: Domain method does not log
- **WHEN** the architecture test scans every public method on every aggregate
- **THEN** no method references `zap.Logger`, `slog.Logger`, `otel.Tracer`, or `prometheus.Counter`

#### Scenario: Domain method does not produce metrics
- **WHEN** the architecture test scans every public method on every aggregate
- **THEN** no method increments a metric

### Requirement: Ports expressed as interfaces, not concrete types
Every cross-boundary dependency in `internal/ports/` SHALL be expressed as a Go interface. The architecture test `TestPortsAreInterfaces` SHALL confirm that every type in `internal/ports/` whose name ends in `Repository`, `UnitOfWork`, `Service`, `Client`, `Gateway`, `Store`, `Provider`, `Sender`, `Dispatcher`, or `Reader` is declared as an interface (the test verifies the type kind via `go/types`).

#### Scenario: Repository is an interface
- **WHEN** `internal/ports/notification_repository.go` declares `type NotificationRepository interface { ... }`
- **THEN** the architecture test confirms the type kind is `interface`

#### Scenario: Repository as a concrete type is rejected
- **WHEN** a file declares `type NotificationRepository struct { ... }`
- **THEN** the architecture test fails the build

### Requirement: Adapter implements exactly one port
Every adapter in `internal/adapters/<kind>/` SHALL implement exactly one port interface (or a small, well-justified set). The architecture test `TestAdapterImplementsExactlyOnePort` SHALL use Go's type system to confirm that an adapter struct satisfies exactly one port interface. An adapter that satisfies multiple ports SHALL fail the test unless a documented exception is registered.

#### Scenario: Postgres adapter implements only NotificationRepository
- **WHEN** the architecture test inspects `internal/adapters/postgres/notification_repository.go`
- **THEN** the type satisfies `ports.NotificationRepository` and no other port

#### Scenario: Adapter implementing multiple ports is flagged
- **WHEN** an adapter struct satisfies two port interfaces
- **THEN** the architecture test fails unless the exception is registered in `internal/adapters/<kind>/exceptions.go`

### Requirement: Build tags for optional infrastructure
Every adapter that uses a vendor SDK with a large transitive dependency (Kafka, Temporal, Redis, OpenSearch) SHALL be gated by a build tag. The architecture test SHALL verify that the adapter's file has a `//go:build` directive listing the relevant tag (e.g., `//go:build kafka`). A service that uses Kafka SHALL include the `kafka` tag in its `Makefile`'s build commands; a service that uses Temporal SHALL include the `temporal` tag. The base build SHALL compile without the tag (so a service that does not use Kafka can build a small binary).

#### Scenario: Kafka adapter is build-tag-gated
- **WHEN** a file under `internal/adapters/kafka/` references `github.com/twmb/franz-go`
- **THEN** the file has a `//go:build kafka` directive

#### Scenario: Base build excludes the Kafka adapter
- **WHEN** `go build ./...` runs without the `kafka` tag
- **THEN** the build succeeds and the resulting binary does not link franz-go

#### Scenario: Kafka-tagged build includes the adapter
- **WHEN** `go build -tags kafka ./...` runs
- **THEN** the build succeeds with the Kafka adapter compiled in

### Requirement: Architecture test coverage
Every service SHALL include the following architecture tests in `test/architecture/` (each is a Go test that exits non-zero on violation):

| Test | Purpose |
|---|---|
| `TestDomainDoesNotImportAdapters` | Domain layer is pure |
| `TestApplicationDoesNotImportAdapters` | Application layer is pure |
| `TestAdaptersDoNotImportEachOther` | Cross-adapter coupling is forbidden |
| `TestPortsDoNotImportAdapters` | Ports do not depend on adapters |
| `TestSoleWriterRule` | Each service owns its schema |
| `TestPortsAreInterfaces` | Cross-boundary types are interfaces |
| `TestAdapterImplementsExactlyOnePort` | Adapters are focused |
| `TestDomainInvariantsAreEnforced` | Domain invariants return typed errors |
| `TestBuildTagIsolation` | Optional adapters are build-tag-gated |
| `TestCacheKeyspaceDeclaration` (when cache is used) | All cache keys follow the canonical pattern |
| `TestWorkerVersioningIsConfigured` (when Temporal is used) | Worker Versioning v2 is configured |
| `TestDeterministicWorkflowCode` (when Temporal is used) | Workflow code uses only deterministic APIs |

The architecture tests SHALL run as part of `make verify-pr` and SHALL fail the build on any violation. The architecture tests SHALL be invoked before `make test-unit` so a layering violation fails fast.

#### Scenario: Architecture test fails the PR gate
- **WHEN** a service introduces a layering violation
- **THEN** `make verify-pr` exits non-zero at the architecture-test step

#### Scenario: Architecture tests run before unit tests
- **WHEN** `make verify-pr` runs
- **THEN** the architecture tests complete before the unit tests start

### Requirement: Architecture tests are themselves testable
The architecture test code SHALL itself be unit-tested. A test in `test/architecture/architecture_test_test.go` SHALL verify that each architecture test detects a planted violation and produces a meaningful error message. A test that fails to detect a planted violation SHALL fail the build.

#### Scenario: Architecture test detects a planted domain→adapter import
- **WHEN** a temporary `internal/domain/test/` package is added that imports an adapter
- **THEN** `TestDomainDoesNotImportAdapters` fails the build

#### Scenario: Architecture test produces a meaningful error
- **WHEN** `TestSoleWriterRule` detects a cross-schema INSERT
- **THEN** the error message names the service, the schema, the table, and the offending file/line