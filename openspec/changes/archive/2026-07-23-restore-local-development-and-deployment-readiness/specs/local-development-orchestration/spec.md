## MODIFIED Requirements

### Requirement: Reproducible developer preflight

The platform SHALL provide a single preflight command that verifies the supported Go, Docker, Docker Compose, kubectl, and kind versions, confirms both linux/arm64 and linux/amd64 image availability, validates required ports and host resources, and reports actionable remediation without changing developer data.

#### Scenario: Supported workstation passes preflight

- **WHEN** a developer runs the preflight command on a workstation satisfying the documented prerequisites
- **THEN** the command exits zero and records the detected tool versions and architecture

#### Scenario: Missing prerequisite fails before startup

- **WHEN** a required tool, image architecture, port, or minimum resource is unavailable
- **THEN** the command exits non-zero before starting containers or clusters and identifies the failed prerequisite

### Requirement: Canonical full-stack Compose lifecycle

The platform SHALL expose one canonical root command that supplies the pinned interpolation environment, combines the base data plane with all eight service overlays, optionally includes tools and LGTM profiles, builds local service images, and waits a bounded time for required services to become healthy.

#### Scenario: Clean full-stack startup

- **WHEN** a developer runs the canonical full-stack command from a clean checkout with no project containers
- **THEN** Compose starts PostgreSQL, Kafka, Debezium, Temporal, OpenTelemetry, and all required roles for the eight services using non-empty pinned image references
- **AND** the command exits zero only after required health checks pass

#### Scenario: Unresolved interpolation fails during validation

- **WHEN** a required image version or Compose input is absent
- **THEN** the Compose validation phase exits non-zero before creating containers and names the unresolved input

#### Scenario: Full-stack startup is repeatable

- **WHEN** the canonical startup command is run twice without configuration changes
- **THEN** the second run exits zero without duplicating topics, connectors, namespaces, or migrations

### Requirement: In-network cross-service acceptance test

The platform SHALL run the cross-service smoke test as a workload on the Compose network and SHALL verify every required API, worker, orchestrator, consumer, data-plane dependency, and telemetry path for all eight services.

#### Scenario: Complete platform passes smoke test

- **WHEN** all required Compose workloads are healthy and the smoke workload runs
- **THEN** service DNS names resolve inside the Compose network, the end-to-end workflow succeeds, and a machine-readable evidence report is written to the host artifact directory

#### Scenario: Missing service or telemetry fails closed

- **WHEN** a required service role is absent, unhealthy, unreachable, or produces no required telemetry
- **THEN** the smoke workload exits non-zero and records the failed dependency or assertion

### Requirement: Pinned local kind lifecycle

The platform SHALL provide idempotent commands to create a pinned kind cluster, load uniquely tagged local images or use a documented local registry, apply all local service overlays, wait for rollout readiness, run the Kubernetes smoke test, collect diagnostics, and delete the cluster.

#### Scenario: Local Kubernetes deployment succeeds

- **WHEN** a developer runs the local Kubernetes startup command after preflight
- **THEN** a named kind cluster is created with the pinned node image, all eight service images are available to the nodes, all local overlays apply, and required workloads become ready within the documented timeout

#### Scenario: Local deployment failure preserves diagnostics

- **WHEN** any local Kubernetes workload fails to become ready
- **THEN** the command exits non-zero after collecting events, pod descriptions, logs, rendered manifests, and image inventory

#### Scenario: Teardown is idempotent

- **WHEN** the developer runs the kind teardown command repeatedly
- **THEN** the target cluster and local registry resources are absent and each invocation exits zero without deleting unrelated clusters or registries

### Requirement: Safe local cleanup and diagnostics

The platform SHALL distinguish routine shutdown from destructive data reset and SHALL scope both operations to the configured Compose project or named kind cluster.

#### Scenario: Routine shutdown preserves data

- **WHEN** a developer runs the normal local shutdown command
- **THEN** project workloads stop and project networks are removed while persistent data volumes remain available

#### Scenario: Explicit reset removes only project data

- **WHEN** a developer invokes the separately named destructive reset command and confirms the project identifier
- **THEN** only the target project's containers, networks, and named data volumes are removed and the command reports what was deleted
