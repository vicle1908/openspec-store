# agent-core Scheduler Setup Specification

## Purpose

Define the scheduled workflow registrations and scheduler cleanup integration
owned by `agent-core`.

## Requirements

### Requirement: Stale workflow cleaner registration

The system SHALL register a `_stale_workflow_cleaner` DBOS scheduled workflow
in `agent-core/scheduler_setup.py` using the
`@_ENGINE.scheduled_workflow(cron="*/30 * * * *", cron_timezone="UTC", name="stale_workflow_cleaner")`
decorator. The workflow body SHALL call the public
`tdt_core.scheduler.cli.cancel_stale_error_workflows` and
`cancel_stale_enqueued_workflows` functions.

The cleaner is registered alongside the existing `daily_android_scan` and
`daily_ios_scan` scheduled workflows in the same module. The
`automatic_backfill=false` semantics match the cleanup intent — old
unprocessed ticks are not back-filled.

#### Scenario: Decorator is registered with correct cron

- **WHEN** `agent-core/scheduler_setup.py` is imported by
  `tdt-scheduler serve`
- **THEN** a `ScheduledWorkflowSpec` SHALL be registered in the engine's
  `ScheduleRegistry` with `name="stale_workflow_cleaner"`, `cron="*/30 * * *
  *"`, `cron_timezone="UTC"`, `automatic_backfill=false`

#### Scenario: Cleaner body calls both public cleanup functions

- **WHEN** the `_stale_workflow_cleaner` workflow is invoked by DBOS
- **THEN** it SHALL call `cancel_stale_error_workflows(engine,
  current_version=<current>)` AND
  `cancel_stale_enqueued_workflows(engine, current_version=<current>)`
  exactly once each, passing the engine instance and current application
  version

#### Scenario: Cleaner logs results at INFO level

- **WHEN** the `_stale_workflow_cleaner` workflow completes
- **THEN** it SHALL emit a `structlog` INFO entry with fields
  `cancelled_error=N` and `cancelled_enqueued=M` recording the number of
  rows cancelled in each pass

### Requirement: Scheduler setup module imports and exports

The system SHALL import the now-public `cancel_stale_error_workflows` and
`cancel_stale_enqueued_workflows` functions from `tdt_core.scheduler.cli`
in `agent-core/scheduler_setup.py`. The functions are used by the
`_stale_workflow_cleaner` scheduled workflow body.

#### Scenario: Imports resolve at module load

- **WHEN** `agent-core/scheduler_setup.py` is imported by
  `tdt-scheduler serve`
- **THEN** both `cancel_stale_error_workflows` and
  `cancel_stale_enqueued_workflows` SHALL be importable from
  `tdt_core.scheduler.cli` without an `ImportError`
