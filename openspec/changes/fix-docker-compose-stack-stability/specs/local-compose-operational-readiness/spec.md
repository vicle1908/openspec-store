## MODIFIED Requirements

### Requirement: Full local operational readiness is evidence-backed

The canonical local readiness gate SHALL start an isolated full Compose project
without fixed host-port collisions, wait for all required service healthchecks
and one-shot initializers, execute real HTTP, Temporal/Nexus, Postgres, and
Kafka operations, and write a machine-readable manifest containing image
identities, health state, workflow results, replay results, side-effect counts,
connector/task state, topic metadata, and failure diagnostics.

#### Scenario: Concurrent Compose projects do not collide on application Redis

- **GIVEN** the canonical application stack and another Compose project run on
the same Docker host
- **WHEN** both projects create their internal Redis services
- **THEN** neither project SHALL claim host port `6379` for application Redis
- **AND** application clients SHALL reach Redis through the project-network
service name and port `redis:6379`.

#### Scenario: Full stack collector is optional to focused stacks

- **GIVEN** the shipping-focused acceptance topology contains only the base,
shipping, and Nexus-local Compose files
- **WHEN** Testcontainers renders and starts the focused topology
- **THEN** it SHALL not fail because of an undeclared `otel-collector` service
- **AND** the focused operation SHALL complete with its evidence artifact.

#### Scenario: Full LGTM topology remains observable

- **GIVEN** the full stack includes the base and LGTM overlays
- **WHEN** services export OTLP while the collector is converging
- **THEN** exporter retry/backoff SHALL tolerate collector startup
- **AND** the LGTM smoke operation SHALL complete or record actionable collector
failure diagnostics.

### Requirement: One-shot infrastructure initialization is explicit

Compose initialization services such as `temporal-admin-tools` SHALL use
`restart: "no"`, and dependent services SHALL consume their result through
`service_completed_successfully` rather than treating the initializer as a
long-running health endpoint.

#### Scenario: Successful Temporal schema initialization

- **WHEN** `temporal-admin-tools` completes schema setup successfully
- **THEN** the container MAY exit and remain stopped
- **AND** dependent Temporal services SHALL proceed.

#### Scenario: Failed Temporal schema initialization

- **WHEN** `temporal-admin-tools` exits non-zero before completing schema setup
- **THEN** dependent services SHALL not be considered ready
- **AND** the readiness evidence SHALL identify the initializer failure.

### Requirement: Compose model validation protects runtime contracts

The repository SHALL validate supported Compose renderings and SHALL reject a
fixed catalog Redis host publication on `6379`, preserve one-shot initializer
semantics, and permit the focused topology to render without undeclared service
dependencies.

#### Scenario: Supported Compose models validate

- **WHEN** `make compose-validate` runs
- **THEN** base, application, LGTM, tools, full, and arm64 models SHALL validate
- **AND** the command SHALL exit zero.
