# ops-postgres-backup-sidecar-alerting Specification

## Purpose

Define the contract for monitoring the `postgres-backup` sidecar's output directory. The sidecar is best-effort: it only runs while the Docker compose stack is up. A stale backup directory is a signal that the stack (or the sidecar specifically) has been down, which the operator must investigate.

## ADDED Requirements

### Requirement: Backup freshness is monitored

The observability stack SHALL track the most recent `.pgdump` file in `~/.tdt/backups/postgres/` and raise an alert when the file is older than the configured threshold.

#### Scenario: Latest backup is fresh
- **WHEN** the most recent `.pgdump` file is less than 24 hours old
- **THEN** no `postgres_backup_stale` alert is raised

#### Scenario: Latest backup is stale
- **WHEN** the most recent `.pgdump` file is older than 26 hours (24h cron interval + 2h slack)
- **THEN** a `postgres_backup_stale` alert of severity `warning` is raised
- **AND** the alert body SHALL include the most recent file's name, age in hours, and the cron schedule (`03:00 UTC`)

#### Scenario: Backup directory is missing entirely
- **WHEN** `~/.tdt/backups/postgres/` does not exist
- **THEN** a `postgres_backup_stale` alert of severity `error` is raised
- **AND** the alert body SHALL indicate the directory is absent

### Requirement: Alert catalog documents the rule

The `tdt-meta/docs/operations/observability-runbook.md` SHALL include the new alert in its "Alert Catalog" section, with: query, threshold, severity, runbook link.

#### Scenario: Operator reads the runbook
- **WHEN** an operator opens `observability-runbook.md`
- **THEN** the Alert Catalog SHALL list `postgres_backup_stale` with the full rule definition
- **AND** the runbook SHALL link to `postgres-restore.md#sidecar-availability` for recovery steps

### Requirement: Postgres restore doc explains sidecar contract

The `tdt-meta/docs/operations/postgres-restore.md` SHALL include a "Sidecar availability" subsection explaining when backups stop, expected gap behavior, and how to interpret the alert.

#### Scenario: Operator reads postgres-restore.md
- **WHEN** an operator opens `postgres-restore.md`
- **THEN** the "Sidecar availability" section SHALL state:
  - The sidecar runs only while `agent-core-local-postgres-backup-1` is up
  - The cron loop runs `pg_dump` at `03:00 UTC` daily
  - Backups are retained for 30 days inside the container
  - A gap > 24h almost always means the compose stack has been down
- **AND** the section SHALL cross-link to the `postgres_backup_stale` alert definition