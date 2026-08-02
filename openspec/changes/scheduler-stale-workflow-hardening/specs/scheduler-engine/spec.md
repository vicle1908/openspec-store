## ADDED Requirements

### Requirement: Stale workflow cleaner scheduled workflow

The system SHALL register a `_stale_workflow_cleaner` DBOS scheduled workflow
inside the Docker `tdt-scheduler:local` container, firing every 30 minutes at
`*/30 * * * *` UTC. The workflow SHALL call the existing
`cancel_stale_error_workflows` and `cancel_stale_enqueued_workflows` cleanup
functions against the shared system database (`tdt_scheduler_dbos_sys`). The
workflow SHALL be idempotent — multiple runs with no stale rows are no-ops.

#### Scenario: Stale ERROR rows from a previous application_version are auto-cancelled

- **WHEN** the scheduled cleaner fires and `dbos.workflow_status` contains rows
  with `status='ERROR' AND application_version <> current_version`
- **THEN** the cleaner SHALL update those rows to `status='CANCELLED'` and log
  `cancelled_error=N` at INFO level

#### Scenario: Stale ENQUEUED rows from a previous application_version are auto-cancelled

- **WHEN** the scheduled cleaner fires and `dbos.workflow_status` contains rows
  with `status='ENQUEUED' AND application_version <> current_version`
- **THEN** the cleaner SHALL update those rows to `status='CANCELLED'` and log
  `cancelled_enqueued=M` at INFO level

#### Scenario: No stale rows means no-op

- **WHEN** the scheduled cleaner fires and `dbos.workflow_status` contains no
  rows matching the cancellation criteria
- **THEN** the cleaner SHALL return without raising and log at DEBUG level

#### Scenario: Schedule honors the ownership contract

- **WHEN** the `_stale_workflow_cleaner` workflow is registered and
  `apply_schedules()` is called
- **THEN** the ownership contract enforced by `apply_schedules()` SHALL be
  respected (only `app_name=tdt-scheduler` may register, or
  `SCHEDULER_ENFORCE_OWNERSHIP=false` is set)

## MODIFIED Requirements

### Requirement: SchedulerEngine scheduled_workflow decorator

The system SHALL provide a `scheduled_workflow()` decorator that registers a
cron-triggered workflow with the `ScheduleRegistry`. The decorator and
`apply_schedules()` SHALL together enforce the ownership contract described in
`tdt-scheduler-ownership-contract`: `apply_schedules()` refuses to register
schedules when the engine's `app_name` is not `tdt-scheduler`, unless
`SCHEDULER_ENFORCE_OWNERSHIP=false`.

The decorator is the registration mechanism for `_stale_workflow_cleaner`,
which SHALL be registered by `agent-core/scheduler_setup.py` alongside the
existing `daily_android_scan` and `daily_ios_scan` scheduled workflows.

#### Scenario: Apply schedules activates all registered specs

- **WHEN** `engine.apply_schedules()` is called after registering multiple
  specs (including `_stale_workflow_cleaner`) and the engine's `app_name` is
  `tdt-scheduler`
- **THEN** all registered specs (including the cleaner) SHALL be atomically
  pushed to DBOS via `DBOS.apply_schedules()`

#### Scenario: Apply schedules refuses non-owner app_name

- **WHEN** `engine.apply_schedules()` is called and the engine's `app_name` is
  not `tdt-scheduler` and `SCHEDULER_ENFORCE_OWNERSHIP` is unset or `true`
- **THEN** the engine SHALL raise `SchedulerContractViolationError` whose
  message names the offending `app_name` and the canonical owner, and SHALL
  NOT register any schedules (including the cleaner)

#### Scenario: Apply schedules honors SCHEDULER_ENFORCE_OWNERSHIP=false

- **WHEN** `engine.apply_schedules()` is called with a non-owner `app_name`
  and `SCHEDULER_ENFORCE_OWNERSHIP=false` in the environment
- **THEN** the engine SHALL proceed with registration without raising