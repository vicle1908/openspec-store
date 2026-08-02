# Capability: tdt-scheduler-ownership-contract

## Purpose
Define which TDT processes may register global DBOS schedules, and make that
ownership enforceable at the engine layer so misconfiguration fails fast.

## ADDED Requirements

### Requirement: Only the canonical scheduler may apply global schedules
The `SchedulerEngine.apply_schedules()` method SHALL refuse to register schedules
when the engine's `app_name` is not `tdt-scheduler`, and SHALL raise
`SchedulerContractViolation` with a clear remediation message instead.

#### Scenario: Non-owner process calls apply_schedules
- **WHEN** a process with `SCHEDULER_APP_NAME=tdt-ai-review` (or any value other
  than `tdt-scheduler`) calls `SchedulerEngine(...).apply_schedules()`
- **THEN** the engine SHALL raise `SchedulerContractViolation` whose message
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
The `/health` endpoint of `ai-review` and `webhook-receiver` SHALL expose
`scheduler.schedules_applied: bool` alongside the existing
`scheduler.{enabled,initialized,dbos_connected}` fields so operators can
verify at a glance that the service is not competing for global schedule
ownership.

#### Scenario: /health reports schedules_applied
- **WHEN** an operator curls `/health` on ai-review or webhook-receiver
- **THEN** the response SHALL include `scheduler.schedules_applied: false`
