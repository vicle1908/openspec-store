# tdt-scheduler-cancel-orphan-enqueued-cli Specification

## Purpose
Provide a `tdt-scheduler cancel-orphan-enqueued` CLI for cleaning up DBOS `ENQUEUED` rows whose
`application_version` is no longer registered. After a deploy that retires a code path, DBOS
keeps these rows forever and re-fires them on every scheduler tick, even after the originating
process is gone. The CLI removes them in bulk, complementing `cancel-stale-errors` (which
targets `ERROR` rows).

## Requirements
### Requirement: cancel-orphan-enqueued CLI exists
The `tdt-scheduler` CLI SHALL expose a `cancel-orphan-enqueued` subcommand
alongside the existing `cancel-stale-errors`, `apply`, `serve`, `status`, and
`schedules` subcommands.

#### Scenario: CLI is discoverable
- **WHEN** an operator runs `python -m tdt_core.scheduler.cli --help`
- **THEN** the help text SHALL list `cancel-orphan-enqueued`

#### Scenario: CLI requires scheduler to be enabled
- **WHEN** an operator runs `cancel-orphan-enqueued` with
  `SCHEDULER_ENABLED=false`
- **THEN** the CLI SHALL exit non-zero with the message
  `Scheduler is disabled. Set SCHEDULER_ENABLED=true.`

### Requirement: cancel-orphan-enqueued targets orphan rows only
The CLI SHALL cancel only ENQUEUED rows whose `application_version` is NOT in
the set of currently registered application versions. Rows for the live
scheduler SHALL be untouched.

#### Scenario: Rows for live app_version survive
- **WHEN** `application_version=68f54a61a61951b8dab0cfdb62dc9384` is the
  latest entry in `dbos.application_versions`
- **THEN** all ENQUEUED rows with that `application_version` SHALL remain
  ENQUEUED after the CLI runs

#### Scenario: Rows for retired app_version are cancelled
- **WHEN** an ENQUEUED row has `application_version=22ed88a9b86d1f6bc7e36fb4323a8202`
  and that version is NOT in `dbos.application_versions`
- **THEN** the row SHALL transition to status `CANCELLED` after the CLI runs

### Requirement: cancel-orphan-enqueued supports a staleness threshold
The CLI SHALL accept a `--older-than-hours` option (default 24) and SHALL
only cancel ENQUEUED rows whose `created_at` is older than the threshold. This
prevents racing a tick that has just enqueued a workflow in the same minute
as the CLI invocation.

#### Scenario: Recent ENQUEUED rows survive
- **WHEN** an ENQUEUED row was created 1 hour ago and `--older-than-hours=24`
  is in effect
- **THEN** the row SHALL NOT be cancelled

#### Scenario: Old ENQUEUED rows are cancelled
- **WHEN** an ENQUEUED row was created 48 hours ago and `--older-than-hours=24`
  is in effect
- **THEN** the row SHALL be cancelled

### Requirement: cancel-orphan-enqueued emits JSON summary
The CLI SHALL emit a JSON object on stdout with the keys `action`,
`cancelled`, `current_versions`, `threshold_hours`, and `older_than_iso`.

#### Scenario: Successful run emits summary
- **WHEN** the CLI cancels N rows
- **THEN** stdout SHALL contain
  `{"action": "cancel_orphan_enqueued", "cancelled": N, ...}` and the exit
  code SHALL be 0

#### Scenario: Idempotent on second run
- **WHEN** the CLI runs a second time immediately after a successful run
- **THEN** `cancelled` SHALL be 0 and the exit code SHALL be 0
