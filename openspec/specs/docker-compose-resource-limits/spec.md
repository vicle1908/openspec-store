# docker-compose-resource-limits Specification

## Purpose

Define bounded CPU, memory, and health-check resource behavior for local Compose workloads.

## Requirements

> **Status**: IMPLEMENTED. All Docker Compose services include deploy.resources limits and reservations blocks matching tier allocations.

### Requirement: Resource limits on API containers

> **Status**: IMPLEMENTED. Docker Compose files include deploy.resources.limits and reservations blocks.

All Docker Compose service definitions SHALL include `deploy.resources.limits` and `deploy.resources.reservations` blocks matching the resource tiers from container-resource-standards.

#### Scenario: API container respects memory limit
- **WHEN** the container attempts to allocate more memory than the limit
- **THEN** the container is killed with OOM

#### Scenario: API container receives guaranteed CPU
- **WHEN** the host is under CPU pressure
- **THEN** the container receives at least its reserved CPU allocation

### Requirement: Resource limits on worker containers

> **Status**: IMPLEMENTED. Worker containers have resource limits matching Tier 2/3 allocations.

Worker containers (Temporal workers, Kafka consumers) SHALL include appropriate resource limits following the Tier 2 or Tier 3 allocation based on the service role.

#### Scenario: Worker respects resource constraints
- **WHEN** the worker processes a burst of messages
- **THEN** CPU and memory usage stays within defined limits

### Requirement: Resource limits on orchestrator containers

> **Status**: IMPLEMENTED. Orchestrator containers have Tier 3 resource allocations (256Mi/512Mi, 200m/500m).

Orchestrator containers (Temporal orchestrators for order-service and catalog-service) SHALL include Tier 3 resource allocations (256Mi request, 512Mi limit, 200m request, 500m limit).

#### Scenario: Orchestrator handles workflow spikes
- **WHEN** multiple concurrent workflows execute
- **THEN** the orchestrator has sufficient resources to complete them

### Requirement: Consistency between Compose and K8s

> **Status**: IMPLEMENTED. Resource values match between Docker Compose and K8s templates.

The resource values in Docker Compose SHALL match the values in the K8s resource templates to ensure parity between local development and production.

#### Scenario: Local development mirrors production constraints
- **WHEN** a developer runs the stack locally
- **THEN** the same memory and CPU constraints apply as in production

### Requirement: Healthcheck timeout configuration

> **Status**: IMPLEMENTED. Healthcheck configurations include 2s timeout minimum for resource constraints.

Healthcheck configurations SHALL include appropriate timeout values that account for resource constraints (2s timeout minimum recommended).

#### Scenario: Healthcheck respects container constraints
- **WHEN** the container is under resource pressure
- **THEN** the healthcheck timeout allows sufficient time for the probe to complete

### Requirement: Resource limits on migrate containers

> **Status**: IMPLEMENTED. Migration containers have reduced resource limits (64Mi/50m) for completion.

Migration containers SHALL have reduced resource limits (64Mi memory, 50m CPU) since they run to completion and exit.

#### Scenario: Migration completes within resource budget
- **WHEN** migrations run
- **THEN** they complete with minimal resource footprint and exit successfully
