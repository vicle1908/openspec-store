# Delta Specification: shb-scheduler-docker-lifecycle

## ADDED Requirements

### Requirement: Scheduler container image parity with committed repository HEAD

Whenever commits in `/Users/androidteam/Developer/shb/shb-schedule` modify `src/shb_schedule/` or container runtime configuration, the `shb-schedule-scheduler-1` Docker container SHALL be rebuilt and recreated so the live HTTP API on `127.0.0.1:9110` serves the committed code.

#### Scenario: Rebuilt scheduler container exposes host schedule persistence fields
- **WHEN** `shb-schedule-scheduler-1` is rebuilt from current `shb/shb-schedule` `main` via `docker compose up -d --build scheduler`
- **THEN** `GET http://127.0.0.1:9110/scheduler/schedules/workstation-daily-update` SHALL return HTTP `200` including `"execution_target": "host"` and `"persisted": false`
- **AND** `POST http://127.0.0.1:9110/scheduler/schedules/workstation-daily-update/trigger` SHALL return HTTP `409 Conflict`
