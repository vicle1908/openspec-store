# tdt-scheduler-ownership-contract Specification Delta

## MODIFIED Requirements

### Requirement: Health endpoint surfaces schedules_applied
The `/health` endpoint of `ai-review` SHALL expose `scheduler.schedules_applied: bool` alongside the existing `scheduler.{enabled,initialized,dbos_connected}` fields so operators can verify at a glance that the service is not competing for global schedule ownership.

#### Scenario: ai-review /health reports schedules_applied
- **WHEN** an operator curls `/health` on ai-review
- **THEN** the response SHALL include `scheduler.schedules_applied: false`

#### Scenario: webhook-receiver confirms ownership via logs
- **WHEN** an operator greps the webhook-receiver logs for `scheduler_engine_initialized`
- **THEN** each event SHALL include `schedules_applied=False`
- **AND** no log event SHALL indicate `apply_schedules` was called

## ADDED Requirements

### Requirement: Public ingress health endpoint omits scheduler internals
The `webhook-receiver` `/health/ingress` endpoint SHALL serve as the public ingress health view and SHALL NOT expose internal scheduler state; operators SHALL verify schedule ownership on `webhook-receiver` via the `scheduler_engine_initialized` structured log event (`schedules_applied=False`).

#### Scenario: webhook-receiver public ingress health omits scheduler state
- **WHEN** an operator queries `/health/ingress` on `webhook-receiver`
- **THEN** the response SHALL report public ingress readiness without exposing internal scheduler fields
- **AND** `test_create_app_does_not_call_apply_schedules` SHALL verify that `apply_schedules` is never invoked
