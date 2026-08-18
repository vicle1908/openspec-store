# agent-core Scheduler Setup Specification

## Purpose

Define the scheduled workflow registrations and scheduler cleanup integration
owned by `agent-core`.

## Requirements

### Requirement: Stale workflow cleaner registration

The `stale_workflow_cleaner` DBOS scheduled workflow SHALL be registered by `tdt-core/scheduler/maintenance.py` as a built-in framework maintenance workflow, not by `agent-core/scheduler_setup.py`. The workflow body SHALL call the public `tdt_core.scheduler.cli.cancel_stale_error_workflows` and `cancel_stale_enqueued_workflows` functions. The cleaner is loaded via the YAML manifest system or registered during framework bootstrap; it is not an application-layer concern.

#### Scenario: Decorator is registered with correct cron

- **WHEN** the scheduler service starts and loads the framework maintenance workflows
- **THEN** a `ScheduledWorkflowSpec` SHALL be registered with `name="stale_workflow_cleaner"`, `cron="*/30 * * * *"`, `cron_timezone="UTC"`, `automatic_backfill=false`

#### Scenario: Cleaner body calls both public cleanup functions

- **WHEN** the `stale_workflow_cleaner` workflow is invoked by DBOS
- **THEN** it SHALL call `cancel_stale_error_workflows(engine, current_version=<current>)` and `cancel_stale_enqueued_workflows(engine)` exactly once each, passing the engine instance. The error-workflow cleanup receives the current application version explicitly; the enqueued-workflow cleanup resolves it internally.

#### Scenario: Cleaner logs results at INFO level

- **WHEN** the `stale_workflow_cleaner` workflow completes
- **THEN** it SHALL emit a `structlog` INFO entry with fields `cancelled_error=N` and `cancelled_enqueued=M` recording the number of rows cancelled in each pass

#### Scenario: Cleaner is registered independently of application workflows

- **WHEN** `agent-core/scheduler_setup.py` is imported by `tdt-scheduler serve`
- **THEN** the module SHALL NOT register `stale_workflow_cleaner`; that registration SHALL occur in `tdt-core/scheduler/maintenance.py` or via the YAML manifest system, decoupled from application-layer workflow functions

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
