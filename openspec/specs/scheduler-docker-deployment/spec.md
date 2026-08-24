# scheduler-docker-deployment Specification

## Purpose

Scheduler Docker deployment defines how the tdt-scheduler runs as a Docker service on the single ecosystem PostgreSQL server, with restart supervision and health monitoring.

## Requirements

_(Baseline: no requirements defined. All requirements are introduced by the `centralized-scheduling-module` change.)_

### Requirement: Docker scheduler service on the single ecosystem PostgreSQL server

The system SHALL provide a Docker `scheduler` service as the long-lived DBOS host for every movable cron or interval workload. The scheduler SHALL remain defined and built by the dedicated `tdt-scheduler` repository using its canonical workspace-root build context, and tdt-observability SHALL not redefine it. All Python execution in the scheduler container SHALL use the locked scheduler environment through `uv run`. The scheduler SHALL connect through a configurable shared runtime network to the single ecosystem PostgreSQL server owned by agent-core, SHALL use its own `tdt_scheduler` application database and auto-derived `tdt_scheduler_dbos_sys` system database, and SHALL NOT stand up or select a second generic runtime PostgreSQL server. The scheduler SHALL also join the configurable observability network and export OTLP only to `http://otel-gateway:4317` after the compatibility transition.

#### Scenario: Scheduler starts against the ecosystem Postgres server

- **WHEN** the coordinated operator command starts the scheduler project
- **THEN** the repository-owned `scheduler` service SHALL run `agent-core-scheduler serve`
- **AND** it SHALL connect to the agent-core-owned `tdt_scheduler` database over the selected runtime network
- **AND** no scheduler-owned or tdt-observability-owned generic runtime PostgreSQL service SHALL be created

#### Scenario: Scheduler does not launch against an unready database

- **WHEN** the scheduler starts in a separate Compose project from PostgreSQL
- **THEN** its entrypoint SHALL perform a bounded reachability and required-database probe before DBOS initialization
- **AND** failure SHALL produce actionable diagnostics and a non-ready scheduler state rather than relying on invalid cross-project `depends_on`

#### Scenario: Own logical database on the shared server

- **WHEN** the scheduler initializes its durable engine
- **THEN** its application connection SHALL target `tdt_scheduler`
- **AND** its DBOS system connection SHALL target `tdt_scheduler_dbos_sys`
- **AND** both SHALL live on the one agent-core-owned PostgreSQL server

#### Scenario: Scheduler compose is independent from agent-core

- **WHEN** `docker compose -f tdt-scheduler/compose.yaml config --services` runs
- **THEN** the output SHALL list `scheduler` and MAY list `postgres-backup`, but SHALL NOT list agent-core or tdt-observability services
- **AND** `build.context` SHALL resolve to the workspace root
- **AND** `build.dockerfile` SHALL resolve to `tdt-scheduler/Dockerfile`

#### Scenario: Scheduler joins both shared networks

- **WHEN** the coordinated deployment renders the scheduler service
- **THEN** the scheduler SHALL join the selected runtime network for PostgreSQL and the selected observability network for OTLP
- **AND** both network names SHALL be overridable for isolated verification

#### Scenario: Scheduler backup reaches only the runtime database network

- **WHEN** the repository-owned `postgres-backup` service is enabled
- **THEN** it SHALL join the selected runtime network and resolve the agent-core-owned `postgres` alias
- **AND** it SHALL not require the observability network
- **AND** the owner implementation SHALL produce a bounded `pg_dump` artifact for the configured scheduler database
- **AND** backup acceptance SHALL verify its readability and checksum without printing database credentials

#### Scenario: Scheduler host inputs preserve owner parity

- **WHEN** the coordinated deployment supplies scheduler TDT home, workload source, mobile repository, configuration, or credential mounts
- **THEN** the rendered inputs SHALL match the repository-owned scheduler Compose contract at the same source revision
- **AND** the host TDT home source SHALL not default to a container-only path

### Requirement: Restart and recovery supervision via Docker

The Docker `scheduler` service SHALL be supervised by Docker with `restart: unless-stopped`. The durable store is the ecosystem PostgreSQL owned by `agent-core`'s compose (also `restart: unless-stopped`); this change does NOT add a second Postgres service.

#### Scenario: Scheduler restarts after a crash

- **WHEN** the `scheduler` container exits unexpectedly
- **THEN** Docker SHALL restart it, and on restart it SHALL re-run `apply_schedules()` so all schedules are re-activated without manual steps

#### Scenario: Schedules survive container recreation

- **WHEN** the `scheduler` container is recreated while the ecosystem `postgres` data volume is retained
- **THEN** previously registered schedule state and in-flight durable workflows SHALL be recovered from PostgreSQL

#### Scenario: Ecosystem Postgres data volume is named and persistent

- **WHEN** the ecosystem PostgreSQL service (owned by `agent-core` compose) is inspected
- **THEN** its data volume SHALL be a **named volume** (not an anonymous volume) so DBOS state persists across container recreation

#### Scenario: No clock while the host is down

- **WHEN** the `scheduler` container is stopped
- **THEN** scheduled ticks SHALL be missed (no inline passthrough for cron) and SHALL be caught up on the next successful run by idempotent workflow logic

### Requirement: Movable workloads are consolidated in the Docker scheduler

The jira-daily-reports cron (13 reports), the review-coverage scan, code-daily-scan, jira-epic-report, webhook-receiver, and tdt-observability SHALL all run as DBOS `@scheduled_workflow`s inside the single Docker `scheduler` container, not as host-native jobs. All repos SHALL use the `register_fn` pattern with `register_all_schedules()` in their `dbos_scheduling.py` module.

#### Scenario: All repos use register_fn pattern

- **WHEN** `grep -l "register_fn" ~/.tdt/schedules/*.yaml` runs
- **THEN** all 5 YAML manifests SHALL use `register_fn` (no `module:function` patterns)
- **AND** each manifest SHALL point to `<repo>.dbos_scheduling:register_all_schedules`

#### Scenario: Coverage scan runs in the Docker scheduler

- **WHEN** the migration is complete
- **THEN** the coverage scan SHALL execute on its cron inside the `scheduler` container, and the `com.tdt.review-coverage` launchd job SHALL no longer exist

### Requirement: Deployment topology exclusions are honored

The Docker scheduler stack SHALL NOT host workloads that are contract-bound or host-coupled. The `webhook-receiver` (:8080) debouncers SHALL remain in-process and launchd-managed per the binding `ai-review-deployment-state` spec; the `ai-review` (:8090) service SHALL remain launchd-managed; the CLV2 observer SHALL remain native and launchd-supervised due to host-filesystem coupling.

#### Scenario: Contract-bound services are not containerized

- **WHEN** the scheduler stack is deployed
- **THEN** `webhook-receiver` and `ai-review` SHALL continue to run under launchd on :8080 and :8090 respectively, with only their DSN pointed at the Docker PostgreSQL

#### Scenario: Host-coupled observer stays native

- **WHEN** the CLV2 observer is migrated
- **THEN** it SHALL run as a DBOS scheduled workflow from a native, launchd-supervised host — NOT inside the Docker `scheduler` container
