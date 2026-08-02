# schedule-hot-reload Specification

## Purpose

Define the hot-reload mechanism that allows schedule changes to be applied without scheduler restart. The scheduler watches `~/.tdt/schedules/` for changes and re-applies schedules on the next healthcheck cycle or on SIGUSR1 signal. DBOS handles schedule upsert idempotently — re-registering a schedule with the same name replaces the existing one.

## ADDED Requirements

### Requirement: Detect reload trigger

The scheduler SHALL detect schedule changes by monitoring the `.reload` sentinel file in `~/.tdt/schedules/`.

#### Scenario: Detects .reload file change

- **WHEN** `~/.tdt/schedules/.reload` is created or modified after the scheduler last checked
- **THEN** the scheduler SHALL re-read all YAML manifests and re-apply schedules via `apply_schedules()`

#### Scenario: Ignores unchanged .reload file

- **WHEN** `~/.tdt/schedules/.reload` has not changed since last check
- **THEN** the scheduler SHALL NOT re-apply schedules

#### Scenario: Handles missing .reload file

- **WHEN** `~/.tdt/schedules/.reload` does not exist
- **THEN** the scheduler SHALL check for it on every healthcheck cycle but SHALL NOT treat its absence as an error

### Requirement: Hot-reload on healthcheck cycle

The reload check SHALL run during the existing healthcheck cycle (every 60 seconds), aligned with the existing `scheduler-healthcheck.md` contract.

#### Scenario: Reload checked on healthcheck

- **WHEN** the scheduler performs a healthcheck
- **THEN** it SHALL also check the `.reload` sentinel file's modification time

#### Scenario: Graceful reload without disrupting healthcheck

- **WHEN** a reload is triggered during healthcheck
- **THEN** the healthcheck SHALL still return 200 OK even if reload fails

### Requirement: Re-apply schedules via DBOS upsert

On hot-reload, the scheduler SHALL re-register all YAML-loaded schedules via `ScheduleRegistry.register()` and call `apply_schedules()`. DBOS handles schedule upsert idempotently — re-registering a schedule with the same name replaces the existing configuration.

#### Scenario: Replaces schedules via upsert

- **WHEN** `~/.tdt/schedules/jira-skill.yaml` is updated with a new schedule
- **THEN** the scheduler SHALL call `apply_schedules()` which DBOS processes as an upsert

#### Scenario: Handles partial failure

- **WHEN** one manifest in a set fails to parse during hot-reload
- **THEN** the scheduler SHALL log a warning, skip the failed manifest, and apply the remaining valid manifests

### Requirement: Hot-reload via SIGUSR1 signal

The scheduler SHALL accept SIGUSR1 to trigger an immediate hot-reload.

#### Scenario: Signal triggers reload

- **WHEN** `kill -USR1 <scheduler_pid>` is sent
- **THEN** the scheduler SHALL immediately re-read all YAML manifests and re-apply schedules

#### Scenario: Signal during reload is queued

- **WHEN** a SIGUSR1 arrives while a reload is in progress
- **THEN** the reload SHALL be re-triggered after the current one completes (at most one pending reload)

### Requirement: Log hot-reload events

The system SHALL emit structured log events for hot-reload operations, using structlog.

#### Scenario: Logs reload trigger

- **WHEN** a hot-reload is triggered
- **THEN** it SHALL log `schedule.reload_triggered` with fields: `manifests_count`, `source` (scheduled or signal)

#### Scenario: Logs successful reload

- **WHEN** hot-reload completes successfully
- **THEN** it SHALL log `schedule.reload_completed` with fields: `schedules_applied`, `manifests_count`, `duration_ms`

#### Scenario: Logs failed reload

- **WHEN** hot-reload fails due to parse error
- **THEN** it SHALL log `schedule.reload_failed` with fields: `error`, `manifest_path`, `skipped_count`

### Requirement: No restart required

The scheduler SHALL apply schedule changes without restart, process exit, or service disruption.

#### Scenario: Webhook-selftest continues during reload

- **WHEN** `webhook-selftest` fires during a hot-reload
- **THEN** the workflow SHALL execute normally without interruption

#### Scenario: In-flight workflows survive reload

- **WHEN** a workflow is executing when hot-reload occurs
- **THEN** the workflow SHALL continue to completion without being affected by the reload

### Requirement: Repin version on reload (DBOS compatibility)

On hot-reload, the scheduler SHALL ensure it remains the canonical version owner via `DBOS.set_latest_application_version()`.

#### Scenario: Repins version after reload

- **WHEN** hot-reload applies new schedules
- **THEN** it SHALL call `DBOS.set_latest_application_version()` to maintain version ownership

### Requirement: Health endpoint surfaces reload state

The `/scheduler/health` endpoint SHALL expose reload state for observability.

#### Scenario: Health endpoint includes reload metadata

- **WHEN** an operator curls `/scheduler/health`
- **THEN** the response SHALL include `reload.last_triggered_at`, `reload.last_applied_at`, and `reload.manifests_loaded`
