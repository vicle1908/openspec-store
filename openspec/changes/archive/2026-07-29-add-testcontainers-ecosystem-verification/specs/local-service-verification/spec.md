## ADDED Requirements

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
