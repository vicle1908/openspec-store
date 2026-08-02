# self-hosted-temporal-nexus Specification

## Purpose
TBD - created by archiving change introduce-self-hosted-temporal-nexus-contracts. Update Purpose after archive.
## Requirements
### Requirement: Self-hosted Temporal exposes routable Nexus callbacks

Local Docker Compose Temporal deployments that advertise Nexus SHALL configure
the frontend HTTP listener on port 7243, the cluster HTTP address, and the
Server 1.31+ system callback URL behavior. Kubernetes and cloud deployment are
outside this change and SHALL NOT be claimed from local evidence.

#### Scenario: Local deployment starts Nexus routing

- **WHEN** the Compose Temporal service starts with Nexus enabled
- **THEN** port 7243 is reachable from the configured Worker network
- **AND** callback routing passes a bounded non-mutating validation

#### Scenario: Local callback route is blocked

- **WHEN** gRPC 7233 is healthy but the local callback listener or container
  network route blocks 7243
- **THEN** Nexus deployment convergence fails
- **AND** the affected handler role is not advertised as ready

#### Scenario: Changed image is validated

- **WHEN** a Temporal, admin-tool, or bootstrap image is changed
- **THEN** deployment validation proves `linux/arm64` support
- **AND** any required emulation fallback is documented with its test evidence

### Requirement: Endpoint registry reconciliation is declarative and idempotent

The self-hosted platform SHALL manage environment-scoped endpoint definitions
declaratively. Reconciliation SHALL create or update an endpoint only when its
desired target and policy differ, SHALL be safe to rerun, and SHALL report
exact drift. A Namespace or Task Queue target change SHALL require retained
drain evidence before cutover.

#### Scenario: Bootstrap is rerun

- **WHEN** endpoint reconciliation runs twice with the same desired state
- **THEN** the second run creates no duplicate and reports convergence

#### Scenario: Target drifts

- **WHEN** the live endpoint target differs from the declared target
- **THEN** reconciliation reports the exact diff and blocks deployment
- **AND** it does not silently switch an active endpoint

#### Scenario: Endpoint is removed

- **WHEN** an endpoint is no longer desired
- **THEN** reconciliation verifies no pending or in-flight operation requires
  it before deletion
- **AND** deletion evidence records the previous target and drain result

### Requirement: Deployment validation uses a non-mutating Nexus canary

Local Docker Compose acceptance SHALL validate callback routing, endpoint
resolution, authorization, handler polling, and result delivery through an
isolated non-mutating canary or disposable test Operation. Routine liveness and
readiness SHALL NOT invoke a mutating domain Operation.

#### Scenario: Canary succeeds

- **WHEN** deployment acceptance runs against the declared endpoint
- **THEN** the canary reaches the expected handler and returns its versioned
  result
- **AND** no business aggregate, external provider, or outbox table changes

#### Scenario: Canary is unauthorized

- **WHEN** the test caller lacks endpoint permission
- **THEN** acceptance fails with a redacted authorization result
- **AND** the handler does not execute

### Requirement: Nexus readiness and dependency state are observable

Every provider SHALL expose local handler registration, poller convergence,
build identity, callback route state, and declared contract inventory. Every
caller SHALL expose endpoint retry and circuit state as dependency health.
Metrics SHALL include schedule-to-start, execution and end-to-end latency,
retry, duplicate, reconciliation, failure, and circuit state without
high-cardinality payload labels.

#### Scenario: Advertised handler is missing

- **WHEN** a provider Worker runs but an advertised handler is not registered
- **THEN** its handler readiness returns `503`
- **AND** evidence identifies the missing endpoint, Service, and Operation

#### Scenario: Remote endpoint becomes unavailable

- **WHEN** a caller's destination pair times out repeatedly
- **THEN** dependency health and circuit state become degraded/open
- **AND** caller readiness remains based on its local ability to serve its role

#### Scenario: Operation succeeds

- **WHEN** an operation completes successfully
- **THEN** logs and metrics include endpoint, Operation version, operation
  identity, duration, and outcome
- **AND** request/response payloads and secrets are absent

