# Local Service Verification

## Purpose

Define fail-closed, reproducible local verification requirements for every
service in the go-microservices repository.

## Requirements

### Requirement: Every service has a fail-closed local verification gate
Each service SHALL expose a default local verification target that runs static
checks, unit tests, race tests, compatibility checks, required fuzz regression,
and the configured coverage threshold. A missing tool, test suite, manifest, or
invalid numeric result MUST fail the target rather than print a skip or success.

#### Scenario: Required verification component is absent
- **WHEN** a service verification target references a missing validator, fuzz suite, manifest, or deployment file
- **THEN** the target exits non-zero and identifies the missing component

#### Scenario: Threshold override is not supplied
- **WHEN** a developer runs the default service or root verification target
- **THEN** the repository's real coverage threshold is enforced without a diagnostic override

### Requirement: Coverage measurement is numeric and reproducible
Every service SHALL generate a coverage profile from a successful test run,
extract exactly one numeric aggregate percentage, retain package-level detail,
and enforce at least 80% aggregate statement coverage. Test output or a failed
test command MUST NOT be interpreted as a passing percentage.

#### Scenario: Service is below threshold
- **WHEN** the numeric aggregate coverage is below 80%
- **THEN** verification exits non-zero and reports the service, measured percentage, and threshold

#### Scenario: Test run fails before coverage calculation
- **WHEN** any test fails while generating the coverage profile
- **THEN** verification reports the test failure and does not replace it with a synthetic passing coverage value

### Requirement: Default unit tests do not require live infrastructure
Tests that require another service, PostgreSQL, Redis, Kafka, Temporal, or
another live process SHALL use an explicit integration or end-to-end build tag
and SHALL run only after their declared prerequisites are ready.

#### Scenario: Default service tests run on a clean host
- **WHEN** a developer runs `go test ./...` without local service containers
- **THEN** unit and architecture tests complete without DNS, port, or credential failures

#### Scenario: Live contract smoke test runs without prerequisites
- **WHEN** a live-stack smoke test is selected but its declared dependency is unavailable
- **THEN** the tagged acceptance command fails with a transport diagnostic rather than contaminating the default unit gate

### Requirement: Required fuzz suites are executable
Inventory and shipping, plus any service whose default verification policy
declares a required fuzz suite, SHALL provide fuzz targets for the declared
untrusted HTTP, event, or contract parsing boundaries, committed seed corpora,
a deterministic regression mode, and a bounded short-fuzz mode. A service
Makefile MUST fail if it declares a required fuzz target whose implementation is missing.

#### Scenario: Regression corpus executes
- **WHEN** inventory, shipping, or another service with a declared required fuzz suite runs its per-commit fuzz regression target
- **THEN** every committed seed executes without panic and invalid inputs return typed validation errors

#### Scenario: Fuzz implementation is missing
- **WHEN** a declared fuzz target has no runner or fuzz package
- **THEN** service verification exits non-zero and identifies the service

### Requirement: Generated contract verification distinguishes external failure
Contract-owning services SHALL use pinned Buf and generator versions, validate
source contracts, and compare deterministic generated output. Authentication,
quota, or network failure from a required remote plugin MUST be reported as an
external tooling failure and MUST NOT be treated as successful generation.

#### Scenario: Generated output is stale
- **WHEN** pinned generation succeeds and changes committed contract bindings
- **THEN** verification exits non-zero and reports the generated files that differ

#### Scenario: Remote plugin quota is exhausted
- **WHEN** the pinned generator cannot run because the remote registry rejects the request for quota or authentication
- **THEN** verification exits non-zero with the external failure category and does not claim contract incompatibility or success

### Requirement: Architecture checks are trimpath and order independent
Architecture tests SHALL locate their module without depending on absolute
runtime source paths and SHALL terminate under `go test -trimpath`. Tests that
inspect unordered collections MUST select records by stable identity rather
than iteration position.

#### Scenario: Trimpath architecture suite runs
- **WHEN** a service architecture suite runs with `-trimpath` and the race detector
- **THEN** module discovery terminates and all checks operate on the intended service root

#### Scenario: Shuffled unit suite runs
- **WHEN** service tests run with a deterministic shuffle seed
- **THEN** assertions remain stable and do not depend on map iteration or prior test order

### Requirement: Live verification covers real lifecycle and integration behavior

Each service's local integration gate SHALL distinguish process health from
real operations. For Shipping, the gate MUST exercise dispatch, replay,
completion, cancellation, persistence inspection, and outbox/CDC observation.
Temporal/Nexus acceptance MUST record workflow terminal status and operation
identity. A passing health probe alone MUST NOT produce a passing integration
result.

#### Scenario: Real lifecycle passes

- **WHEN** the local gate dispatches a shipment, replays it, and completes or cancels it through the public boundary
- **THEN** the expected HTTP responses, persisted state, and exactly-once business side-effect count are verified

#### Scenario: Integration dependency is unavailable

- **WHEN** Kafka, Debezium, Postgres, Temporal, or a required service is unreachable
- **THEN** the integration gate exits non-zero and retains diagnostics rather than reporting health-only success

#### Scenario: Focused and full evidence are distinct

- **WHEN** only the Temporal/Nexus pilot is executed
- **THEN** evidence is labeled focused and cannot satisfy the full eight-service Compose readiness gate

### Requirement: Explicit service integration gates provision dependencies and fail closed

Every service with a live PostgreSQL, Redis, Kafka, Temporal, or peer-service
integration suite SHALL declare an explicit tagged integration target and its
required dependencies. When selected, the target MUST provision those
dependencies through the repository Testcontainers harness or an explicitly
declared focused Compose cohort, wait for their usable state, execute the
required tests, and retain diagnostics and evidence. Missing environment
variables, Docker access, fixtures, migrations, or dependencies MUST fail the
selected target rather than silently skip required tests.

#### Scenario: Required database integration suite is selected

- **WHEN** a service's database integration target is invoked
- **THEN** the target provisions the pinned database, applies the service-owned migrations, runs every required tagged test, and writes service-integration evidence

#### Scenario: Required integration test reports skipped

- **WHEN** an explicitly selected integration suite skips because a DSN, endpoint, fixture, or dependency is absent
- **THEN** the service integration target exits non-zero and identifies the skipped test and missing prerequisite

#### Scenario: Default tests run without live dependencies

- **WHEN** the same service runs its default unit, architecture, compatibility, race, fuzz-regression, or coverage gate
- **THEN** no Testcontainers fixture or live dependency is started
- **AND** any existing Docker-based tool check remains separately identified from live integration evidence

#### Scenario: Service integration state is isolated

- **WHEN** a service integration suite creates, updates, rolls back, retries, or deletes test records
- **THEN** all operations occur in the run-scoped fixture owned by that service test
- **AND** no shared development or other service database is mutated

### Requirement: Integration inventory status is truthful

The repository SHALL maintain a machine-readable inventory that distinguishes
`present`, `external-only`, and `not-configured` integration suites, including
their build tags, commands, dependencies, owner, evidence class, and artifact
path. An aggregate target MUST fail when a suite marked required is
`external-only` or `not-configured`; a default gate MUST NOT silently promote
an absent suite to passing evidence.

#### Scenario: Required service has no runnable integration target

- **WHEN** the inventory marks a required service integration suite as `not-configured` or `external-only`
- **THEN** the aggregate container target exits non-zero and identifies the missing command or fixture
- **AND** the service is not counted as having passed integration verification

#### Scenario: Optional Docker provider check is used

- **WHEN** a developer runs a non-authoritative optional test outside an explicitly selected integration target
- **THEN** the test may skip because the Testcontainers provider is unavailable
- **AND** no selected integration or aggregate evidence is emitted from that skip

### Requirement: Service integration fixtures use canonical runtime pins

Service integration fixtures SHALL resolve dependency versions from the same
repository-owned pins used by local deployment. Duplicate hard-coded fallback
versions in service helpers MUST NOT produce authoritative evidence. Each
service integration manifest MUST record the effective image, host platform,
migration identity, and test command.

#### Scenario: Service helper pin differs from local deployment

- **WHEN** a service integration helper requests a different dependency version than the canonical repository pin
- **THEN** authoritative verification fails with the service, dependency, declared value, and canonical value

#### Scenario: Canonical pin is used

- **WHEN** a service integration fixture starts successfully
- **THEN** its manifest records the canonical image reference and resolved local identity used by the test

#### Scenario: Service migration fails on the canonical image

- **WHEN** a service-owned migration cannot reach head on the canonical dependency image
- **THEN** the integration target exits non-zero and retains migration and container diagnostics
- **AND** adapter tests do not run against a partially initialized schema
