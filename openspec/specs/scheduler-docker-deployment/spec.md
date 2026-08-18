# scheduler-docker-deployment Specification

## Purpose

Scheduler Docker deployment defines how the tdt-scheduler runs as a Docker service on the single ecosystem PostgreSQL server, with restart supervision and health monitoring.
## Requirements

_(Baseline: no requirements defined. All requirements are introduced by the `centralized-scheduling-module` change.)_

### Requirement: Docker scheduler service on the single ecosystem PostgreSQL server

The system SHALL provide a Docker `scheduler` service (long-lived DBOS host) that owns every movable cron/interval workload. The scheduler SHALL live in a dedicated `tdt-scheduler/` directory at the workspace root, with its own `compose.yaml` and build context. All Python execution in the scheduler container SHALL use `uv run` (not direct venv python calls) to ensure proper project resolution and dependency management. The scheduler SHALL connect to the **single ecosystem PostgreSQL server** — `agent-core`'s pinned `postgres:18.6-trixie` — using **its own logical database** (`tdt_scheduler`, with the auto-derived `tdt_scheduler_dbos_sys` system DB), and SHALL NOT stand up a second Postgres server/instance.

#### Scenario: Scheduler starts against the ecosystem Postgres server

- **WHEN** `docker compose up -d` is run from `tdt-scheduler/` for the scheduler service
- **THEN** the `scheduler` service SHALL start, run `tdt-scheduler serve` as its entrypoint, and connect to its `tdt_scheduler` database on the ecosystem PostgreSQL server — no second Postgres server is created

#### Scenario: Scheduler does not launch against an unready database

- **WHEN** the `scheduler` service starts
- **THEN** it SHALL wait for the ecosystem PostgreSQL to be reachable before launching DBOS — via `depends_on: { postgres: { condition: service_healthy } }` (when postgres is co-located) or by connecting to the postgres service over a shared Docker network or the published `127.0.0.1` port

#### Scenario: Own logical database on the shared server

- **WHEN** the `scheduler` service initializes the engine
- **THEN** its `DBOS_DATABASE_URL` SHALL point at a dedicated `tdt_scheduler` logical database on the one ecosystem PostgreSQL server — distinct from agent-core's `agent_core` database and from webhook-receiver's database

#### Scenario: Scheduler compose is independent from agent-core

- **WHEN** `docker compose -f tdt-scheduler/compose.yaml config --services` runs
- **THEN** the output SHALL list `scheduler` (and optionally `postgres-backup`) without `app` or other agent-core services
- **AND** the build `context` SHALL be `.` (the `tdt-scheduler/` directory itself)

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
The jira-daily-reports cron (13 reports) and the review-coverage scan SHALL both run as DBOS `@scheduled_workflow`s inside the single Docker `scheduler` container, not as host-native jobs.

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
