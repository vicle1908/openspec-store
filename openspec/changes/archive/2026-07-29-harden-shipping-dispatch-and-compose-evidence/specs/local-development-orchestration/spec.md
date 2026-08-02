## MODIFIED Requirements

### Requirement: Reproducible developer preflight

The platform SHALL provide a single preflight command that verifies the
supported Go, Docker, Docker Compose, kubectl, and kind versions, confirms both
linux/arm64 and linux/amd64 image availability, validates required ports and
host resources, and reports actionable remediation without changing developer
data. When invoked by a readiness run, preflight SHALL receive and validate the
exact `VALIDATION_RUN_ID` and `VALIDATION_COMPOSE_PROJECT`, and SHALL report
whether matching containers, networks, or volumes already exist before
startup. A readiness run SHALL set project ownership only after this exact
absence check passes.

#### Scenario: Supported workstation passes preflight

- **WHEN** a developer runs the preflight command on a workstation satisfying
  the documented prerequisites
- **THEN** the command exits zero and records the detected tool versions,
  architecture, run identity, and project ownership decision

#### Scenario: Missing prerequisite fails before startup

- **WHEN** a required tool, image architecture, port, minimum resource, or
  exact project absence check is unavailable
- **THEN** the command exits non-zero before starting containers or clusters and
  identifies the failed prerequisite

#### Scenario: Existing project is not owned

- **WHEN** preflight finds a container, network, or volume with the requested
  Compose project identity
- **THEN** the readiness wrapper records `owned=false`
- **AND** cleanup cannot remove that project

### Requirement: Canonical full-stack Compose lifecycle

The platform SHALL expose one canonical root command that supplies the pinned
interpolation environment, combines the base data plane with all eight service
overlays, optionally includes tools and LGTM profiles, builds local service
images, and waits a bounded time for required services to become healthy. The
command SHALL create a collision-resistant run ID from UTC time, process ID,
and randomness; derive one unique Compose project unless an exact safe
override is supplied; pass that identity to every validator and operation; and
retain resolved Compose, image platform, health, one-shot exit, and cleanup
state in a per-run evidence directory.

#### Scenario: Clean full-stack startup

- **WHEN** a developer runs the canonical full-stack command from a clean
  checkout with no project containers
- **THEN** Compose starts PostgreSQL, Kafka, Debezium, Temporal,
  OpenTelemetry, and all required roles for the eight services using non-empty
  pinned image references
- **AND** the command exits zero only after required health and initializer
  gates pass and records the exact run/project identity

#### Scenario: Unresolved interpolation fails during validation

- **WHEN** a required image version or Compose input is absent
- **THEN** the Compose validation phase exits non-zero before creating
  containers and names the unresolved input

#### Scenario: Slow dependency converges

- **WHEN** Debezium requires its documented plugin-discovery budget
- **THEN** the lifecycle waits with progress and succeeds if the dependency
  converges before the budget expires

#### Scenario: One-shot initializer fails

- **WHEN** migration, topic, connector, or Nexus reconciliation exits non-zero
- **THEN** the lifecycle exits non-zero and retains the initializer logs and
  dependency diagnostics under the exact run ID

#### Scenario: Full-stack rerun is idempotent

- **WHEN** the same project runs the canonical startup twice
- **THEN** the second run exits zero without duplicating topics, connectors,
  namespaces, migrations, or business side effects

#### Scenario: Two runs are isolated

- **WHEN** two readiness commands execute concurrently
- **THEN** they use different run IDs, Compose projects, evidence directories,
  and container labels
- **AND** each acceptance manifest references only its own artifacts

### Requirement: In-network cross-service acceptance test

The platform SHALL run the cross-service smoke test as a workload on the
Compose network and SHALL verify every required API, worker, orchestrator,
consumer, data-plane dependency, and telemetry path for all eight services.
The smoke writer SHALL include the exact `run_id` and `compose_project` in its
report, and the acceptance caller SHALL pass the expected values explicitly.

#### Scenario: Complete platform passes smoke test

- **WHEN** all required Compose workloads are healthy and the smoke workload
  runs
- **THEN** service DNS names resolve inside the Compose network, the end-to-end
  workflow succeeds, and a machine-readable evidence report containing the
  exact run/project identity is written to the per-run host artifact directory

#### Scenario: Missing service or telemetry fails closed

- **WHEN** a required service role is absent, unhealthy, unreachable, or
  produces no required telemetry
- **THEN** the smoke workload exits non-zero and records the failed dependency
  or assertion under the exact run identity

#### Scenario: Cross-run smoke report is rejected

- **WHEN** the report exists but its run ID or Compose project differs from the
  acceptance invocation
- **THEN** acceptance exits non-zero and does not use the report

### Requirement: Safe local cleanup and diagnostics

The platform SHALL distinguish routine shutdown from destructive data reset and
SHALL scope both operations to the configured Compose project or named kind
cluster. The readiness wrapper SHALL clean up only a project it owns, SHALL
record cleanup status after every exit, and SHALL treat cleanup failure as a
failed readiness result. `KEEP_READINESS_STACK=true` SHALL retain an owned
project by explicit operator request and SHALL record `retained-by-request`;
an unowned project SHALL record `skipped-not-owned` without removal.

#### Scenario: Routine shutdown preserves data

- **WHEN** a developer runs the normal local shutdown command
- **THEN** project workloads stop and project networks are removed while
  persistent data volumes remain available

#### Scenario: Explicit reset removes only project data

- **WHEN** a developer invokes the separately named destructive reset command
  and confirms the project identifier
- **THEN** only the target project's containers, networks, and named data
  volumes are removed and the command reports what was deleted

#### Scenario: Cleanup failure is retained

- **WHEN** a project-owned cleanup command fails
- **THEN** the command retains diagnostics, records `cleanup.status=failed`, and
  exits non-zero even if service acceptance had passed
