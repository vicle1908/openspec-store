# shb-schedule-engine Specification Delta

## ADDED Requirements

### Requirement: Container HTTP Endpoints SHALL Guard Unpersisted Host-Targeted Schedules

The scheduler HTTP control plane (`GET /scheduler/schedules` and `POST /scheduler/schedules/{name}/trigger`) SHALL evaluate `ScheduleReconciler.should_persist(manifest)` so that host-targeted manifests (`execution_target: host`) on non-Darwin container runtimes are reported with their `execution_target` and `persisted: false` state and cannot be dispatched through `DBOS.trigger_schedule`.

#### Scenario: Triggering a host-only schedule on a Linux container returns HTTP 409 instead of HTTP 500
- **WHEN** an operator sends `POST /scheduler/schedules/workstation-daily-update/trigger` to the containerized Linux scheduler where `should_persist(manifest)` is `False`
- **THEN** the endpoint SHALL return HTTP 409 Conflict with a structured diagnostic message explaining that `execution_target: host` schedules are not persisted in container DBOS
- **AND** it SHALL NOT invoke `DBOS.trigger_schedule("workstation-daily-update")` or raise an unhandled 500 exception

#### Scenario: Schedule listing includes execution_target and persistence state
- **WHEN** `GET /scheduler/schedules` is queried on the scheduler server
- **THEN** each returned schedule object SHALL include `execution_target` and `persisted` boolean fields reflecting `should_persist(manifest)`
