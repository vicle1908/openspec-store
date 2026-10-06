# Spec Delta: shb-schedule-engine

## ADDED Requirements

### Requirement: Containerized Orchestration via Docker Compose
The `shb-schedule` service SHALL be deployable and operable exclusively through a Docker Compose stack comprising a `postgres:18.6-alpine` database service and the scheduler application container, with no dependency on host init systems (`launchd`, `systemd`) or host-installed binaries.

#### Scenario: Bringing up the scheduler stack
- **WHEN** an operator runs `docker compose up -d` within the `shb-schedule` project root
- **THEN** the Compose stack SHALL start a PostgreSQL 18.6 (Alpine) service and the `shb-schedule` application container
- **AND** the application container SHALL wait for the database service health check to report healthy before initializing the DBOS Transact runtime

#### Scenario: Database health gating
- **WHEN** the `db` service has not yet passed its health check
- **THEN** the `scheduler` service SHALL NOT begin initialization
- **AND** once the check passes, the `scheduler` service SHALL proceed without operator intervention

#### Scenario: Uniform cross-platform behavior
- **WHEN** the same `compose.yaml` is executed on macOS, Linux, or a CI runner with a running Docker daemon
- **THEN** the resulting scheduler behavior (manifest parsing, durable workflow execution, health endpoints) SHALL be identical across those platforms

### Requirement: PostgreSQL 18.6 Backend with Schema Isolation
The scheduler SHALL persist its durable execution history, schedule registry, and queue state in a PostgreSQL 18.6 database, with all DBOS system tables created under a dedicated `shb_scheduler` schema (or equivalent configurable schema name). The database SHALL be provisioned from a clean state on first launch with no external migration scripts required.

#### Scenario: Clean initialization
- **WHEN** the scheduler container first connects to an empty PostgreSQL `shb_scheduler` database
- **THEN** the DBOS Transact runtime SHALL apply its full system schema (tables, indexes, migrations) automatically
- **AND** the service SHALL report a healthy status without requiring operator-run migrations

#### Scenario: Data isolation
- **WHEN** the scheduler writes execution history or schedule state
- **THEN** it SHALL write only to the configured `shb_scheduler` schema and SHALL NOT modify other PostgreSQL schemas or databases on the same server

### Requirement: Lean Container Mount Policy
The production `shb-schedule` container SHALL mount only the schedule manifest directory (`~/.shb/schedules/*.yaml`) as a read-only volume. It SHALL NOT mount source-code repositories or host working trees in base production mode.

#### Scenario: Minimal host coupling in production
- **WHEN** the base `compose.yaml` (without local development override) is started
- **THEN** the running container SHALL have access to the manifest files at a stable in-container path
- **AND** the container SHALL NOT have bind-mounted access to `~/Developer/shb/*` repositories

#### Scenario: Local development override
- **WHEN** an operator starts the stack with `compose.override.yaml` present
- **THEN** the override MAY additionally mount the developer workspace read-only for local audit workloads
- **AND** the base production profile SHALL remain unchanged and portable

### Requirement: Health and Operability via Standard Interfaces
The containerized scheduler SHALL expose the HTTP health and schedule-status endpoints on host port `9110`, listening on `0.0.0.0` inside the container so the published port is reachable, and SHALL be triggerable via the existing CLI commands executed inside the container (`docker compose exec scheduler shb-schedule ...`).

#### Scenario: Health check visibility
- **WHEN** an operator queries `http://127.0.0.1:9110/scheduler/health` after `docker compose up`
- **THEN** the endpoint SHALL return ownership, persistence, and schedule status without exposing credentials

#### Scenario: Container-reachable binding
- **WHEN** the scheduler process starts inside the container
- **THEN** it SHALL bind port `9110` on the container's non-loopback interface so the host-published port mapping resolves

#### Scenario: On-demand trigger inside container
- **WHEN** an operator runs `docker compose exec scheduler shb-schedule run-now <job-name>`
- **THEN** the job SHALL be submitted through the durable execution path and return an identifiable execution result

### Requirement: Removal of Host Service Installers
The scheduler SHALL NOT expose a host service-installation command; operators SHALL manage the scheduler lifecycle through Docker Compose or explicit environment overrides.

#### Scenario: Service installer no longer offered
- **WHEN** an operator runs `shb-schedule --help`
- **THEN** the command help SHALL NOT list a `service` command group
- **AND** invoking `shb-schedule service install` SHALL fail as an unrecognized command
- **AND** the scheduler documentation SHALL describe containerized operation instead of host LaunchAgent or systemd installation
