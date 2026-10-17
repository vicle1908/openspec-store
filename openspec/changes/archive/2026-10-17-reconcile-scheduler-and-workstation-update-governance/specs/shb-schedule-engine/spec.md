# shb-schedule-engine Specification Delta

## MODIFIED Requirements

### Requirement: Health and Operational Visibility
The service SHALL expose health and schedule-state information via an ASGI HTTP service on port `9110`, sufficient to distinguish owner status, database readiness, manifest reload status, and registered jobs, using modern Starlette/FastAPI lifespan event handling.

#### Scenario: Health and schedule inspection
- **WHEN** an operator requests `/scheduler/health`, `/scheduler/schedules`, or `/scheduler/schedules/{name}`
- **THEN** the service SHALL return current ownership, persistence, reload, and schedule information without exposing credentials

#### Scenario: On-demand trigger
- **WHEN** an operator invokes `shb-schedule run-now <job_name>`, `shb-schedule run-now --workflow <job_name>`, or the supported trigger endpoint
- **THEN** the service SHALL submit the job through the durable execution path, enforce ownership, and return an identifiable execution result

### Requirement: Containerized Orchestration via Docker Compose
The `shb-schedule` service SHALL provide containerized orchestration via Docker Compose with a `postgres:18.6-alpine` database and scheduler container, eliminating host init dependencies while supporting local SQLite mode. The scheduler SHALL declare a `stop_grace_period` of at least 60 seconds to ensure durable transactions and PostgreSQL advisory locks drain cleanly upon termination.
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

#### Scenario: Workstation lifecycle drain and stack status alignment
- **WHEN** `docker-service.sh drain`, `docker-service.sh stop`, or `docker-service.sh status` (`--json`) is executed on the host
- **THEN** `docker-service.sh` SHALL enforce a default drain timeout of at least 65 seconds so `stop_grace_period: 60s` is never truncated by a 30-second `SIGKILL`
- **AND** `docker-service.sh status` and `docker-service.sh status --json` SHALL inspect and report registered `COMPOSE_STACKS` state including `shb-schedule`

#### Scenario: Uniform cross-platform behavior
- **WHEN** the same `compose.yaml` is executed on macOS, Linux, or a CI runner with a running Docker daemon
- **THEN** the resulting scheduler behavior (manifest parsing, durable workflow execution, health endpoints) SHALL be identical across those platforms

### Requirement: Host and Container Workload Partitioning
The system SHALL maintain a strict operational boundary between host toolchain maintenance and containerized application scheduling. Headless operational banking workloads SHALL execute containerized, while workstation-coupled package upgrades requiring host macOS binaries SHALL execute natively on the host environment, be excluded from recurring Linux container cron registration, and skip cleanly when invoked on-demand in containerized runtimes.

#### Scenario: Host-targeted schedule excluded from Linux container cron registration
- **WHEN** the containerized Linux scheduler reconciles manifests from `/etc/shb/schedules` and encounters a manifest declaring `execution_target: host` (such as `workstation-daily-update`)
- **THEN** the Linux container daemon SHALL exclude that manifest from recurring `DBOS.apply_schedules` registration so it does not race with the host macOS LaunchAgent at 08:00 AM
- **AND** if a persisted schedule record for that host-only job exists in PostgreSQL `workflow_schedules`, the reconciler SHALL retire it via `DBOS.delete_schedule`
- **AND** host macOS CLI invocations (`shb-schedule validate`, `shb-schedule list`, `shb-schedule run-now`) SHALL continue to discover and execute the manifest on Darwin

#### Scenario: Containerized execution skips host-only package managers cleanly
- **WHEN** `workstation-daily-update` is dispatched on-demand inside the containerized Linux scheduler runtime
- **THEN** missing host binaries (`brew`, `mas`, `pmset`) SHALL be detected without process exceptions
- **AND** the affected workflow steps SHALL return `SKIPPED` status with recorded diagnostic reasons

#### Scenario: Headless operational workflows execute successfully inside the container
- **WHEN** headless banking workloads (`daily-shb-docs-sync`, `eod-settlement-recon`, `nightly-compliance-scan`) are dispatched inside the container
- **THEN** the workflows SHALL connect to the isolated PostgreSQL backend and execute their steps cleanly
- **AND** when target repositories or settlement ledgers are unmounted in base production mode, the workflows SHALL deterministically return fail-closed `PARTIAL` or `ACTION_REQUIRED` status rather than raising unhandled exceptions
