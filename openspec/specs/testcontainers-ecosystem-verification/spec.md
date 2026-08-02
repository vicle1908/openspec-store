# testcontainers-ecosystem-verification Specification

## Purpose

Defines deterministic disposable dependency fixtures and focused multi-container cohorts with exact evidence, cleanup, image compatibility, and execution cadence while preserving canonical full-stack readiness as a separate authority.

## Requirements

### Requirement: Container-backed dependency fixtures are deterministic

Every explicitly selected service integration target SHALL provision its
declared live dependencies through the repository's Testcontainers harness.
The harness MUST resolve runtime images from the canonical repository pins,
apply the owning service's canonical migrations or initialization, use bounded
protocol-level readiness, and expose only run-scoped connection information to
the selected test process. Missing Docker access, missing pins, failed
initialization, or an unavailable dependency MUST fail the selected target.

#### Scenario: PostgreSQL adapter fixture becomes usable

- **WHEN** a service integration target selects its PostgreSQL adapter suite
- **THEN** the harness starts the canonically pinned PostgreSQL image, waits for the final server, applies the service-owned migrations, and proves a query succeeds before executing adapter assertions

#### Scenario: Selected integration dependency is unavailable

- **WHEN** the integration target cannot reach Docker or cannot start a required dependency within its bounded timeout
- **THEN** the target exits non-zero with the dependency, image reference, phase, and redacted diagnostics
- **AND** the required test is not reported as skipped or passing

#### Scenario: Runtime image pin is absent

- **WHEN** the harness cannot resolve a required image version from the canonical repository pin file
- **THEN** startup fails before any test container is claimed as ready
- **AND** the manifest records a configuration failure without selecting a fallback image

#### Scenario: Diagnostic image override is used

- **WHEN** a developer explicitly overrides a fixture image for diagnosis
- **THEN** the manifest records the declared and effective image references and labels the result non-authoritative
- **AND** that result cannot satisfy release-significant compatibility evidence

### Requirement: Compose builds and client lifecycle are source-bound

The focused Compose harness MUST use the repository's pinned
`testcontainers-go` and Compose module versions, preflight every Compose build
context, and build local service images from the exact source revision before
accepting them as authoritative evidence. It MUST retain image IDs or digests,
build contexts, and commands. Every Compose run MUST perform scoped `Down`
cleanup followed by client `Close`, and MUST retain Reaper or equivalent
ownership cleanup status.

#### Scenario: Focused stack contains local build images

- **WHEN** the selected Compose model contains a `build` entry or a local-only image reference
- **THEN** the harness builds it from an allowlisted repository context for the exact run revision
- **AND** evidence records the image identity, context, and build command before service assertions are accepted

#### Scenario: Pre-existing local image is unrelated

- **WHEN** a required local image exists but its recorded source revision or build context does not match the selected run
- **THEN** the harness rebuilds or rejects the image before startup
- **AND** it does not report the focused cohort as authoritative using the stale image

#### Scenario: Compose clients are closed after cleanup

- **WHEN** a focused cohort passes, fails, or is interrupted
- **THEN** the harness calls scoped `Down` and then closes the Compose and Testcontainers clients
- **AND** the manifest records cleanup and client-closure outcomes

### Requirement: Fixture ownership and cleanup are run-scoped

Each Testcontainers invocation SHALL derive a collision-resistant run identity
and unique stack or network identity. It MUST prove the exact identity is
absent before claiming ownership, isolate databases, schemas, ports, networks,
and volumes from other runs, capture diagnostics before teardown, and remove
only resources it owns. Cleanup failure MUST fail the selected target.

#### Scenario: Two service integration runs execute concurrently

- **WHEN** two supported service fixtures run at the same time
- **THEN** each uses a distinct run identity, network, dependency state, and mapped endpoints
- **AND** neither run reads, mutates, or removes the other run's resources

#### Scenario: Test assertion fails

- **WHEN** a required assertion fails after containers have started
- **THEN** the harness captures bounded redacted logs and container state before terminating owned resources
- **AND** the final manifest retains both the assertion failure and cleanup outcome

#### Scenario: Requested identity already exists

- **WHEN** a caller supplies a stack or network identity that already owns containers, networks, or volumes
- **THEN** the harness refuses ownership, performs no destructive cleanup, and exits non-zero

#### Scenario: Cleanup cannot remove an owned resource

- **WHEN** workload assertions pass but an owned container, network, or volume cannot be removed
- **THEN** the manifest records cleanup as failed and the overall target exits non-zero

### Requirement: Focused ecosystem cohorts reuse canonical topology

A focused ecosystem cohort SHALL use Testcontainers to manage the repository's
existing Compose base and selected overlays rather than duplicate the same
multi-container topology as generic definitions. The cohort MUST use a unique
stack identifier, inject the exact run and evidence identity, wait for required
roles and one-shot initializers, and exercise public service and infrastructure
boundaries. A health-only or dependency-only run MUST NOT satisfy a focused
ecosystem scenario.

#### Scenario: Shipping focused cohort passes

- **WHEN** the Shipping ecosystem cohort runs against the base, Shipping, Nexus, and required evidence overlays
- **THEN** it exercises real HTTP and Nexus dispatch, exact replay, conflicting input, concurrent duplicates, lease-expiry recovery, completion, cancellation, PostgreSQL inspection, Kafka delivery, Debezium connector state, and Temporal terminal state
- **AND** it retains the expected carrier, Shipment, operation, outbox, workflow, and event counts for the exact run identity

#### Scenario: Shipping duplicate delivery is retried safely

- **WHEN** concurrent HTTP and Nexus callers use the same operation identity and canonical fingerprint
- **THEN** callers observe the documented in-progress, attach, or retained-replay outcomes
- **AND** the cohort observes one logical carrier effect, one Shipment transition, one completed operation, and one dispatch outbox fact

#### Scenario: Shipping dependency becomes unavailable

- **WHEN** PostgreSQL, Kafka, Debezium, Temporal, or a required Shipping role becomes unavailable during the focused cohort
- **THEN** the cohort exits non-zero, records the failed boundary and bounded diagnostics, and does not report a health-only pass

#### Scenario: Existing Compose behavior is reused

- **WHEN** the focused cohort resolves its selected topology
- **THEN** its manifest lists the exact repository Compose files and environment pins used
- **AND** the cohort does not substitute separately maintained generic definitions for those roles

### Requirement: Testcontainers evidence is exact and independently classified

Every service integration and focused ecosystem run SHALL write a
schema-versioned `microservices.testcontainers-ecosystem/v1` manifest. The
manifest MUST record source revision, dirty state, run identity, cohort,
evidence class, host platform, declared and resolved images, selected topology,
required checks, child artifacts and hashes, start and finish times, redacted
diagnostics, ownership, and cleanup. The only accepted classes SHALL be
`service-integration` and `focused-ecosystem`.

#### Scenario: Passing service integration evidence is retained

- **WHEN** all required adapter operations pass and owned resources are cleaned up
- **THEN** the manifest reports `service-integration`, identifies the exact service and source revision, lists every required check as passed, and records successful cleanup

#### Scenario: Cross-run child artifact is supplied

- **WHEN** a manifest references a child artifact whose run identity, stack identity, source revision, or hash does not match
- **THEN** validation exits non-zero and identifies the mismatched field

#### Scenario: Focused evidence is offered as full readiness

- **WHEN** a caller supplies `focused-ecosystem` evidence where canonical full-stack Compose evidence is required
- **THEN** validation rejects it and requires a passing `canonical-full-stack` manifest

#### Scenario: Evidence contains a secret-shaped value

- **WHEN** manifest or retained log validation detects a credential, password-bearing DSN, Docker authentication value, or provider payload
- **THEN** the selected target fails evidence validation and retains only a redacted diagnostic category

### Requirement: Container-backed integration execution is explicit and fail closed

The repository SHALL expose deterministic targets for one service integration
suite, all service container integration suites, one focused ecosystem cohort,
and the aggregate container verification gate. Selecting one of these targets
MUST require Docker and MUST treat missing tests, skipped required tests,
unsupported images, failed negative controls, or missing evidence as failures.
Default unit and architecture tests SHALL remain runnable without live service
fixtures or Testcontainers. Existing explicitly named Docker tool containers
remain separate from the Testcontainers evidence contract.

#### Scenario: Developer runs the default unit gate without a Testcontainers provider

- **WHEN** a developer runs the default service or root pull-request gate on a host without a Testcontainers provider
- **THEN** unit, architecture, compatibility, fuzz-regression, and coverage checks run without attempting to provision Testcontainers or live application fixtures
- **AND** any existing short-lived tool-container check is reported under its own command rather than as integration evidence

#### Scenario: Developer selects all service integration suites

- **WHEN** the aggregate service integration target is selected on a supported Docker host
- **THEN** every declared service integration suite runs against its provisioned dependencies
- **AND** the aggregate result fails if any required suite skips, fails, or omits its manifest

#### Scenario: Negative control unexpectedly passes

- **WHEN** a fixture lifecycle, cross-run evidence, cleanup, image-substitution, or dependency-outage negative control unexpectedly passes
- **THEN** the aggregate container verification target exits non-zero

#### Scenario: CI workflow definition runs a focused cohort

- **WHEN** the Docker-capable integration workflow is triggered for a relevant change or manual dispatch
- **THEN** it runs the pinned Go toolchain, service integration gate, focused cohort, and evidence validators
- **AND** it uploads bounded evidence and diagnostics even when a required step fails

### Requirement: Container images and Docker access remain trusted boundaries

The harness SHALL start only repository-declared image references and existing
Compose files for authoritative evidence. It MUST NOT accept arbitrary image
names from untrusted test payloads, mount unrelated host directories, expose
Docker credentials, or require production secrets. Selected images MUST support
`linux/arm64` and `linux/amd64`, or the run MUST record an explicitly approved
emulation fallback and its trade-off.

#### Scenario: Untrusted test input supplies an image name

- **WHEN** a test payload attempts to select an image or Compose file outside the repository-declared allowlist
- **THEN** the harness rejects the input before contacting Docker

#### Scenario: Native image platform is missing

- **WHEN** a required image lacks the host's native supported platform
- **THEN** the authoritative run fails before startup unless an approved fallback is explicitly configured
- **AND** the manifest records the fallback, affected image, platform, and performance trade-off

#### Scenario: CI runner accesses Docker

- **WHEN** the integration workflow starts Testcontainers on a CI runner
- **THEN** Docker API access is limited to the host-side verification process and repository-declared containers
- **AND** no production credential is required or emitted
