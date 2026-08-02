# platform-hexagonal-enforcement Specification

## Purpose

This spec defines the hexagonal-architecture layering rules enforced by the architecture tests: domain has no infrastructure imports, application depends only on ports, adapters implement ports, and runtime wires everything via Fx. The spec also codifies the sole-writer database rule (each Postgres table is owned by exactly one service) and the build-tag pattern for optional infrastructure.
## Requirements
### Requirement: Hexagonal layer isolation

Every service's Go code SHALL conform to the repository's inside/outside
hexagonal boundary. Architecture verification SHALL evaluate direct imports by
package-prefix and SHALL evaluate transitive dependencies for domain purity and
in-repository layer direction. It MUST NOT report a third-party SDK's
transitive dependencies as direct imports.

The canonical boundaries are:

| Layer | MAY import | MUST NOT directly import |
|---|---|---|
| `internal/domain/` | stdlib and explicitly approved pure value libraries | ports, application, adapters, generated transport contracts, infrastructure frameworks, peer internals |
| `internal/application/` | owned domain and purpose-named ports; approved pure platform policy types | owned adapters, peer internals/contracts, `net/http`, generated Protobuf transport DTOs, circuit-breaker libraries, Fx, Zap, OTel, pgx, Kafka, Redis, Temporal, or Nexus SDKs |
| inventoried legacy `internal/application/orchestration/` | application imports plus the existing Temporal `workflow`, `activity`, `temporal`, and `platform/temporal` policy helpers declared in the legacy-exception inventory | Nexus SDK, new transport clients, owned adapters, Fx, Zap, OTel, pgx, Kafka, Redis, or direct external I/O |
| `internal/ports/` | owned domain/application value types and stdlib | adapters, generated transport contracts, vendor SDKs, and infrastructure implementations |
| `internal/adapters/<kind>/` | owned ports/application/domain, generated contracts, vendor SDKs, approved platform adapters | peer-service internals and another adapter kind except a documented composition boundary |
| `cmd/` and `internal/runtime/` | all owned layers required for composition | peer-service internals |

New or modified Temporal/Nexus Workflow wrappers, handlers, clients, and
registration code SHALL live under `internal/adapters/temporal`. Existing
legacy orchestration packages SHALL be explicitly inventoried, SHALL NOT add
Nexus dependencies, and SHALL NOT expand their framework-facing surface.
Temporal determinism and Worker safety SHALL also be enforced by the canonical
Temporal inventory validator and upstream Workflow checker.

#### Scenario: Direct application infrastructure import fails

- **WHEN** an application package directly imports HTTP, a peer generated
  contract, a circuit-breaker library, Temporal/Nexus, Fx, Zap, OTel, pgx,
  Kafka, Redis, or an owned adapter
- **THEN** the architecture suite fails with the package, source location, and
  direct import
- **AND** the violation cannot be hidden behind another application package

#### Scenario: Inventoried legacy Temporal package is checked

- **WHEN** an existing `internal/application/orchestration` package imports an
  approved Temporal Workflow API
- **THEN** the verifier accepts only the exact inventoried package and prefix
- **AND** any Nexus import, direct external I/O, or new unlisted orchestration
  package fails validation

#### Scenario: Temporal transitive dependency is not misreported

- **WHEN** an approved adapter or inventoried legacy package imports a Temporal
  API whose dependency graph contains Fx, Zap, or OTel
- **THEN** the application direct-import test does not report those transitive
  dependencies
- **AND** canonical Temporal Worker and determinism verification still runs

#### Scenario: Domain purity remains transitive

- **WHEN** domain code reaches an infrastructure, generated transport, port, or
  adapter package through an intermediate dependency
- **THEN** the domain-purity gate fails
- **AND** the diagnostic identifies the complete forbidden dependency path

#### Scenario: Application cannot import owned adapters

- **WHEN** any package under `internal/application/` imports
  `internal/adapters/` or a legacy service-local adapter path
- **THEN** the application-layer gate fails
- **AND** runtime composition remains outside the application layer

#### Scenario: New Nexus code is adapter-owned

- **WHEN** a service adds a Nexus handler, caller, registration, or SDK type
- **THEN** it resides under the service's Temporal adapter
- **AND** the application is executable against an in-memory port substitute
  without Temporal Server, HTTP, Kafka, or PostgreSQL

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

### Requirement: Architecture test coverage [PARTIAL]

> **Status**: PARTIAL. Most services include a `layering_test.go` in `test/architecture/` that covers a subset of the 12 required test categories. The full matrix of 12 tests (`TestDomainDoesNotImportAdapters`, `TestApplicationDoesNotImportAdapters`, `TestAdaptersDoNotImportEachOther`, `TestPortsDoNotImportAdapters`, `TestSoleWriterRule`, `TestPortsAreInterfaces`, `TestAdapterImplementsExactlyOnePort`, `TestDomainInvariantsAreEnforced`, `TestBuildTagIsolation`, `TestCacheKeyspaceDeclaration`, `TestWorkerVersioningIsConfigured`, `TestDeterministicWorkflowCode`) is not present in every service. Several services have only 4-6 of the 12 required tests, and the `TestDomainInvariantsAreEnforced`, `TestCacheKeyspaceDeclaration`, and `TestWorkerVersioningIsConfigured` tests are missing from most services.

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

#### Scenario: Architecture test completeness check

- **WHEN** the architecture test suite runs for any service
- **THEN** every test in the 12-test matrix above is present in `test/architecture/` for that service (or explicitly documented as not applicable with a reason)
- **AND** the CI pipeline verifies that no required test is missing by scanning `test/architecture/*_test.go` for the expected test function names
- **AND** a missing test function causes the CI step to fail with a message identifying which test is absent and in which service

#### Scenario: Temporal-using services include temporal-specific tests

- **WHEN** a service imports `platform/temporal` or registers Temporal workers
- **THEN** `test/architecture/` includes `TestWorkerVersioningIsConfigured` and `TestDeterministicWorkflowCode`
- **AND** the absence of either test fails the CI gate

### Requirement: Architecture tests are themselves testable
The architecture test code SHALL itself be unit-tested. A test in `test/architecture/architecture_test_test.go` SHALL verify that each architecture test detects a planted violation and produces a meaningful error message. A test that fails to detect a planted violation SHALL fail the build.

#### Scenario: Architecture test detects a planted domain→adapter import
- **WHEN** a temporary `internal/domain/test/` package is added that imports an adapter
- **THEN** `TestDomainDoesNotImportAdapters` fails the build

#### Scenario: Architecture test produces a meaningful error
- **WHEN** `TestSoleWriterRule` detects a cross-schema INSERT
- **THEN** the error message names the service, the schema, the table, and the offending file/line

### Requirement: Context boundaries are explicit and testable

The repository SHALL maintain a canonical bounded-context map that records
context owners, aggregates, ubiquitous-language terms, commands, facts,
upstream/downstream relationships, and contract mappings. Architecture
validation SHALL reject a cross-context integration that is absent from the
map or imports a peer's private model.

#### Scenario: Declared relationship is implemented

- **WHEN** Order invokes the Shipping dispatch command
- **THEN** the context map identifies Order as caller and Shipping as provider
- **AND** source dependencies cross the boundary only through the declared
  contract and adapters

#### Scenario: Physical service is mistaken for shared domain

- **WHEN** two services attempt to share one aggregate or domain package
- **THEN** context-map validation fails
- **AND** the relationship must be expressed through an integration contract
  or the services must be documented as one context before implementation

### Requirement: Architecture validators prove their scan coverage

Every architecture validator SHALL use exact repository/package layer roots,
prefix-aware forbidden-import matching, and a cross-service module inventory.
It SHALL fail if an expected layer contains files but zero files/packages were
scanned. Each rule SHALL have a planted violating fixture that must produce the
expected actionable diagnostic.

#### Scenario: Forbidden SDK subpackage is imported

- **WHEN** a fixture imports `go.temporal.io/sdk/workflow` under a pure
  application package
- **THEN** a rule configured for prefix `go.temporal.io/sdk` fails
- **AND** it reports the importing package and source file

#### Scenario: Layer path is misspelled

- **WHEN** a validator searches `application/` while source exists only under
  `internal/application/`
- **THEN** the validator fails for zero scan coverage
- **AND** it does not report a false pass

#### Scenario: Cross-service test has no assertions

- **WHEN** a planted peer-internal import is added
- **THEN** the cross-service architecture fixture must fail
- **AND** a test that merely parses packages without evaluating imports is
  rejected by architecture-test self-validation

### Requirement: Ports describe purpose rather than transport

Application ports SHALL describe provider-owned use cases or required
capabilities without naming HTTP, Nexus, Kafka, PostgreSQL, Temporal, or a
vendor SDK. Multiple driving or driven adapters SHALL be substitutable for the
same purposeful port in isolated application tests.

#### Scenario: Order dispatches through a port

- **WHEN** Order needs to request Shipment dispatch
- **THEN** its application depends on a purpose-named Shipping command port
- **AND** HTTP and Nexus adapters can implement that port without changing the
  application command

#### Scenario: Transport client is placed in application

- **WHEN** application code constructs an HTTP request or Nexus client
- **THEN** architecture validation fails
- **AND** the transport implementation must move to an adapter

### Requirement: Unit of work binds every transactional collaborator

A unit of work SHALL supply repositories, idempotency storage, and outbox
storage bound to one transaction handle. Application code SHALL NOT begin a
transaction and then obtain pool-backed collaborators for work claimed to be
atomic. External network calls SHALL NOT execute while that database
transaction is open.

#### Scenario: Atomic aggregate and outbox commit succeeds

- **WHEN** an application transaction saves an aggregate, retained operation
  result, and outbox fact
- **THEN** every write uses the same transaction handle
- **AND** commit makes all writes visible together

#### Scenario: Repository escapes the transaction

- **WHEN** a unit of work begins a transaction but returns a pool-backed
  repository or outbox writer
- **THEN** transaction-bound integration validation fails
- **AND** rollback evidence proves that no claimed atomic write survives

#### Scenario: Provider call occurs inside a transaction

- **WHEN** an application command performs carrier, HTTP, Nexus, or Kafka I/O
  while a database transaction remains open
- **THEN** transaction-boundary validation fails
- **AND** the flow must persist intent, close the transaction, perform the
  side effect idempotently, and finalize in a new transaction

### Requirement: Integration contracts do not enter the domain

Nexus and Kafka DTOs, endpoint/topic names, Temporal/Nexus clients,
registration calls, transport metrics, and generated Protobuf types SHALL live
in adapters or dedicated generated-contract modules. Domain and ports packages
SHALL NOT import them. Adapters SHALL map integration contracts to owned
application/domain types.

#### Scenario: Domain imports Nexus infrastructure

- **WHEN** an architecture check finds a Temporal, Nexus, Kafka, or generated
  transport import under `internal/domain/`
- **THEN** the hexagonal-layer gate fails and identifies the dependency path

#### Scenario: Handler maps to an application command

- **WHEN** a Nexus handler receives a versioned request
- **THEN** it validates and maps the request to an owned application command
- **AND** no peer internal or private aggregate type crosses the boundary

### Requirement: Nexus mutations preserve sole-writer ownership

A Nexus handler SHALL write only the provider context's PostgreSQL schema and
SHALL commit aggregate changes, retained operation result, and outbox records
atomically. Cross-context state changes SHALL use contracts and Kafka facts,
not shared tables, distributed database transactions, or direct repositories.

#### Scenario: Handler writes owned data

- **WHEN** a Shipping Nexus operation finalizes Shipment state
- **THEN** all writes target Shipping-owned tables in one transaction
- **AND** the committed outbox fact is eligible for Kafka publication

#### Scenario: Handler attempts a peer write

- **WHEN** a handler writes another context's schema or imports its repository
- **THEN** architecture or integration validation fails before deployment

