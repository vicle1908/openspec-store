# scheduler-postgres-watchdog Specification

## Purpose
Establishes daily Postgres logical backups with retention, a scheduler healthcheck endpoint on port 9100, and a documented restore procedure.
## Requirements
### Requirement: Postgres daily logical backup

The system SHALL produce a daily compressed logical backup of the
`agent-core` Postgres database and retain it on the host filesystem.

#### Scenario: Backup runs while the database is healthy

- **GIVEN** the `postgres` container is healthy and accepts connections on
  `127.0.0.1:5432`
- **WHEN** 03:00 UTC elapses
- **THEN** a `pg_dump --format=custom --compress=9 -d agent_core`
  SHALL run inside the `postgres-backup` container
- **AND** the output SHALL be written to
  `~/.tdt/backups/postgres/YYYY-MM-DD.pgdump`
- **AND** the backup container SHALL log `pg_dump_completed` with the file
  size in bytes
- **AND** the container SHALL exit 0

#### Scenario: Backup runs while the database is unhealthy

- **GIVEN** the `postgres` container is unreachable (restart loop, crash,
  network issue)
- **WHEN** 03:00 UTC elapses
- **THEN** `pg_dump` SHALL fail with a non-zero exit code
- **AND** the failure SHALL be logged at WARN level inside the backup
  container's stderr
- **AND** the container SHALL exit non-zero so `restart: unless-stopped`
  retries the next day
- **AND** the most-recent successful backup in
  `~/.tdt/backups/postgres/` SHALL remain on disk

#### Scenario: Retention window is enforced

- **GIVEN** more than 7 daily backups and more than 4 weekly backups
  exist in `~/.tdt/backups/postgres/`
- **WHEN** a new daily backup completes successfully
- **THEN** the retention script SHALL delete daily backups older than 7
  days
- **AND** the retention script SHALL retain the most-recent backup of
  each ISO week for the last 4 weeks
- **AND** the script SHALL log `backups_pruned` with the count of files
  deleted

### Requirement: Scheduler service healthcheck

The system SHALL expose a `/scheduler/health` endpoint inside the `scheduler`
process by mounting the existing `tdt_core.scheduler.health.scheduler_router`
under prefix `/scheduler` on `127.0.0.1:9100`. The Docker compose
`healthcheck:` on the `scheduler` service SHALL probe this endpoint.

> **Origin (validated 2026-06-27):** the router already exists in
> `tdt-core/src/tdt_core/scheduler/health.py` (built by
> `centralized-scheduling-module` task 3.1–3.5). The defect is the
> **mount**: `cli.py::_serve()` does not import `scheduler_router`
> and does not start uvicorn. This requirement closes that gap.

#### Scenario: Scheduler is healthy after cold start

- **GIVEN** the `scheduler` container has just started and DBOS is
  initializing
- **WHEN** at least 120 s has elapsed since container start
- **AND** the `tdt-scheduler serve` process has mounted
  `scheduler_router` in a daemon thread on `127.0.0.1:9100`
- **THEN** `curl -fsS http://127.0.0.1:9100/scheduler/health` SHALL
  return a 200 response with JSON body containing `"enabled": true`,
  `"scheduling_enabled": true`, `"initialized": true`,
  `"schedule_count": <int>`, `"dbos_connected": true`
- **AND** Docker SHALL mark the container as `healthy`

#### Scenario: Scheduler hang is detected

- **GIVEN** the `tdt-scheduler serve` Python process is hung (no DBOS
  workflow has fired in 10 minutes) but the container is still running
- **WHEN** the healthcheck `curl` times out after 10 s
- **THEN** the healthcheck SHALL fail
- **AND** after 3 consecutive failures (`retries: 3`) Docker SHALL
  restart the container via `restart: unless-stopped`

#### Scenario: Cold start tolerates long startup

- **GIVEN** the `scheduler` container has just started
- **WHEN** less than 120 s has elapsed since container start
- **THEN** the healthcheck SHALL NOT count failures against the retry
  budget (`start_period: 120s`)

### Requirement: Restore procedure is documented

The system SHALL provide a runbook at
`tdt-meta/docs/operations/postgres-restore.md` describing the
single-command restore flow.

#### Scenario: Operator restores from a daily backup

- **GIVEN** a known-good `pgdump` file at
  `~/.tdt/backups/postgres/YYYY-MM-DD.pgdump`
- **AND** the `scheduler` and `app` services are stopped
- **WHEN** the operator runs the documented restore command
- **THEN** the database SHALL be reloaded from the snapshot
- **AND** on restart the `scheduler` service SHALL resume firing
  registered schedules from the DBOS system tables in the restored DB

