# Spec Delta: shb-schedule-engine

## Purpose
Hardens the containerized Docker Compose deployment for `shb-schedule` with graceful termination timeouts, log rotation resource caps, and formal host-vs-container workload boundaries.

## MODIFIED Requirements

### Requirement: Containerized Orchestration via Docker Compose
The `shb-schedule` service SHALL provide standardized containerized orchestration through Docker Compose comprising a `postgres:18.6-alpine` database service and the scheduler container, eliminating dependencies on host init systems (`launchd`, `systemd`) while preserving opt-in local SQLite mode for development. The scheduler service SHALL define a `stop_grace_period` of at least 60 seconds to ensure durable workflow transactions and PostgreSQL advisory locks drain cleanly upon termination.

#### Scenario: Bringing up the scheduler stack
- **WHEN** an operator runs `docker compose up -d` within the `shb-schedule` project root
- **THEN** the Compose stack SHALL start a PostgreSQL 18.6 (Alpine) service and the `shb-schedule` application container
- **AND** the application container SHALL wait for the database service health check to report healthy before initializing the DBOS Transact runtime

#### Scenario: Database health gating
- **WHEN** the `db` service has not yet passed its health check
- **THEN** the `scheduler` service SHALL NOT begin initialization
- **AND** once the check passes, the `scheduler` service SHALL proceed without operator intervention

#### Scenario: Graceful shutdown and transaction drain
- **WHEN** the `scheduler` service receives a `SIGTERM` stop signal during container restart or host shutdown
- **THEN** Docker SHALL allow a `stop_grace_period` of at least 60 seconds before issuing `SIGKILL`
- **AND** the scheduler service SHALL finish active DBOS steps, close database connections, and release PostgreSQL session advisory locks cleanly

#### Scenario: Uniform cross-platform behavior
- **WHEN** the same `compose.yaml` is executed on macOS, Linux, or a CI runner with a running Docker daemon
- **THEN** the resulting scheduler behavior (manifest parsing, durable workflow execution, health endpoints) SHALL be identical across those platforms

## ADDED Requirements

### Requirement: Service Log Hygiene and Resource Bounds
The Docker Compose deployment configuration SHALL enforce bounded log rotation constraints across both database and scheduler services to prevent disk exhaustion from high-frequency health probes and execution telemetry.

#### Scenario: Log rotation policy enforced
- **WHEN** the `db` or `scheduler` services emit container log output
- **THEN** the Docker daemon logging driver SHALL cap individual log files at `10m`
- **AND** the logging driver SHALL retain a maximum of 3 rotated files per container

### Requirement: Host and Container Workload Partitioning
The system SHALL maintain a strict operational boundary between host toolchain maintenance and containerized application scheduling. Headless operational banking workloads SHALL execute containerized, while workstation-coupled package upgrades requiring host macOS binaries SHALL execute natively on the host environment and skip cleanly when invoked in containerized runtimes.

#### Scenario: Containerized execution skips host-only package managers cleanly
- **WHEN** `workstation-daily-update` is dispatched inside the containerized Linux scheduler runtime
- **THEN** missing host binaries (`brew`, `mas`, `pmset`) SHALL be detected without process exceptions
- **AND** the affected workflow steps SHALL return `SKIPPED` status with recorded diagnostic reasons

#### Scenario: Headless operational workflows execute successfully inside the container
- **WHEN** headless banking workloads (`daily-shb-docs-sync`, `eod-settlement-recon`, `nightly-compliance-scan`) are dispatched inside the container
- **THEN** the workflows SHALL connect to the isolated PostgreSQL backend and execute their steps cleanly
