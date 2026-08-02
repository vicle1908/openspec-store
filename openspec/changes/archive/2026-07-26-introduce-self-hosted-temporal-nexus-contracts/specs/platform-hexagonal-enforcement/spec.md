## MODIFIED Requirements

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

## ADDED Requirements

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
