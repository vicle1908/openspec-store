# tdt-scheduler-ownership-contract Specification

## Purpose
Establish that only the canonical scheduler service (`tdt-scheduler`) may register global DBOS
schedules via `SchedulerEngine.apply_schedules()`. All other TDT services (`ai-review`,
`webhook-receiver`, `jira-daily-reports`, etc.) must only call `engine.initialize()` and
register debouncers/queues. The guard prevents `ModuleNotFoundError` workflows that arise when
multiple processes with different `application_version`s race to deserialize each other's
serialized workflow arguments.

## Requirements
### Requirement: Only the canonical scheduler may apply global schedules
The `SchedulerEngine.apply_schedules()` method SHALL refuse to register schedules
when the engine's `app_name` is not `tdt-scheduler`, and SHALL raise
`SchedulerContractViolationError` with a clear remediation message instead.

#### Scenario: Non-owner process calls apply_schedules
- **WHEN** a process with `SCHEDULER_APP_NAME=tdt-ai-review` (or any value other
  than `tdt-scheduler`) calls `SchedulerEngine(...).apply_schedules()`
- **THEN** the engine SHALL raise `SchedulerContractViolationError` whose message
  names the offending `app_name`, names the canonical `tdt-scheduler` owner,
  and points operators at the `SCHEDULER_ENFORCE_OWNERSHIP=false` escape hatch

#### Scenario: Canonical scheduler calls apply_schedules
- **WHEN** a process with `SCHEDULER_APP_NAME=tdt-scheduler` (or the yaml
  default `tdt-scheduler`) calls `SchedulerEngine(...).apply_schedules()`
- **THEN** the engine SHALL proceed with schedule registration and SHALL NOT
  raise

#### Scenario: Test fixture opts out via env var
- **WHEN** a process sets `SCHEDULER_ENFORCE_OWNERSHIP=false` and calls
  `apply_schedules()` with a non-owner `app_name`
- **THEN** the engine SHALL proceed without raising, so existing test
  fixtures that build a `SchedulerEngine` with `app_name="tdt-test"` continue
  to work

### Requirement: Application services MUST NOT call apply_schedules in lifespan
The FastAPI lifespans of `ai-review` and `webhook-receiver` SHALL NOT call
`engine.apply_schedules()`. They SHALL call `engine.initialize()` so their
debouncers work, and they SHALL emit a structured log
`scheduler_engine_initialized` with `schedules_applied=False`.

#### Scenario: ai-review lifespan emits schedules_applied=False
- **WHEN** the ai-review FastAPI app starts and the scheduler is enabled
- **THEN** the `scheduler_engine_initialized` structlog event SHALL include
  `schedules_applied=False` and `apply_schedules` SHALL NOT have been called

#### Scenario: webhook-receiver lifespan emits schedules_applied=False
- **WHEN** the webhook-receiver FastAPI app starts and the scheduler is enabled
- **THEN** the `scheduler_engine_initialized` structlog event SHALL include
  `schedules_applied=False` and `apply_schedules` SHALL NOT have been called

### Requirement: Health endpoint surfaces schedules_applied
The `/health` endpoint of `ai-review` SHALL expose
`scheduler.schedules_applied: bool` alongside the existing
`scheduler.{enabled,initialized,dbos_connected}` fields so operators can
verify at a glance that the service is not competing for global schedule
ownership.

The `webhook-receiver` `/health/ingress` endpoint is the public ingress health
view and intentionally does not expose scheduler internals; operators verify
schedule ownership on webhook-receiver by inspecting the
`scheduler_engine_initialized` log event (which includes `schedules_applied=False`)
and by confirming the service never invokes `apply_schedules` (covered by
`test_create_app_does_not_call_apply_schedules`).

#### Scenario: ai-review /health reports schedules_applied
- **WHEN** an operator curls `/health` on ai-review
- **THEN** the response SHALL include `scheduler.schedules_applied: false`

#### Scenario: webhook-receiver confirms ownership via logs
- **WHEN** an operator greps the webhook-receiver logs for
  `scheduler_engine_initialized`
- **THEN** each event SHALL include `schedules_applied=False`
- **AND** no log event SHALL indicate `apply_schedules` was called
