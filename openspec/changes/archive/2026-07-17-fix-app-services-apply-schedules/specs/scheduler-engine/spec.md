# Capability: scheduler-engine (delta)

## ADDED Requirements

### Requirement: SchedulerEngine scheduled_workflow decorator
The system SHALL provide a `scheduled_workflow()` decorator that registers a cron-triggered workflow with the `ScheduleRegistry`. The decorator and `apply_schedules()` SHALL together enforce the ownership contract described in `tdt-scheduler-ownership-contract`: `apply_schedules()` refuses to register schedules when the engine's `app_name` is not `tdt-scheduler`, unless `SCHEDULER_ENFORCE_OWNERSHIP=false`.

#### Scenario: Apply schedules activates all registered specs
- **WHEN** `engine.apply_schedules()` is called after registering multiple specs and the engine's `app_name` is `tdt-scheduler`
- **THEN** all registered specs SHALL be atomically pushed to DBOS via `DBOS.apply_schedules()`

#### Scenario: Apply schedules refuses non-owner app_name
- **WHEN** `engine.apply_schedules()` is called and the engine's `app_name` is not `tdt-scheduler` (for example `tdt-ai-review` or `tdt-webhook-receiver`) and `SCHEDULER_ENFORCE_OWNERSHIP` is unset or `true`
- **THEN** the engine SHALL raise `SchedulerContractViolation` whose message names the offending `app_name` and the canonical owner, and SHALL NOT register any schedules
- **AND** the `apply_schedules` function SHALL have a docstring section "Ownership contract" that links to `tdt-scheduler-ownership-contract`

#### Scenario: Apply schedules honors SCHEDULER_ENFORCE_OWNERSHIP=false
- **WHEN** `engine.apply_schedules()` is called with a non-owner `app_name` and `SCHEDULER_ENFORCE_OWNERSHIP=false` in the environment
- **THEN** the engine SHALL proceed with registration without raising
