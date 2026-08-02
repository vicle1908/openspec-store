# scheduler-health-api Specification

## Purpose

Scheduler health API exposes a FastAPI REST endpoint for querying scheduler state, listing registered schedules, inspecting individual schedule details, and triggering manual runs.
## Requirements

_(Baseline: no requirements defined. All requirements are introduced by the `centralized-scheduling-module` change.)_

### Requirement: Health endpoint
The system SHALL provide a `GET /scheduler/health` FastAPI endpoint returning overall scheduler status.

#### Scenario: Health check with enabled scheduler
- **WHEN** `GET /scheduler/health` is called and scheduling is enabled
- **THEN** the response SHALL include `{"enabled": true, "scheduling_enabled": true, "initialized": true, "schedule_count": <int>, "dbos_connected": true}`

#### Scenario: Health check with disabled scheduler
- **WHEN** `GET /scheduler/health` is called and scheduling is disabled
- **THEN** the response SHALL include `{"enabled": false, "scheduling_enabled": false}`

### Requirement: Schedules list endpoint
The system SHALL provide a `GET /scheduler/schedules` FastAPI endpoint returning all registered schedules, backed by `DBOSClient.list_schedules()`.

#### Scenario: List schedules via API
- **WHEN** `GET /scheduler/schedules` is called
- **THEN** the response SHALL be a JSON array with each schedule's schedule name (`schedule_name`), workflow name (`workflow_name`), cron expression (`schedule`), status, and `last_run_time` (from DBOS `last_fired_at`); it SHALL NOT include `next_run_time` in the list response because DBOS exposes no next-run API

### Requirement: Single schedule detail endpoint
The system SHALL provide a `GET /scheduler/schedules/{name}` FastAPI endpoint.

#### Scenario: Get schedule by name
- **WHEN** `GET /scheduler/schedules/jira-standup` is called
- **THEN** the response SHALL include the full details of the "jira-standup" schedule
- **AND** the response SHALL include `next_run_time`, computed best-effort from the cron expression and `last_run_time` via `croniter`; it MAY be `null` if insufficient data is available

#### Scenario: Schedule not found
- **WHEN** `GET /scheduler/schedules/nonexistent` is called
- **THEN** the response SHALL be `404 Not Found`

### Requirement: Trigger schedule endpoint
The system SHALL provide a `POST /scheduler/schedules/{name}/trigger` FastAPI endpoint that runs the schedule's workflow immediately, independent of its cron clock.

**DBOS validation (2026):** For an immediate run inside the same application runtime, DBOS provides `DBOS.trigger_schedule(schedule_name)`. For external management (the health API’s intended use case), the trigger endpoint SHALL call `DBOSClient.trigger_schedule(schedule_name)`.

**Implementation constraint (this change):** The trigger endpoint MUST be implemented via `DBOSClient.trigger_schedule(schedule_name)` (schedule-name based), because the health API is intended to manage schedules externally and must not assume access to in-process workflow function objects.

#### Scenario: Trigger schedule via API
- **WHEN** `POST /scheduler/schedules/jira-standup/trigger` is called
- **THEN** the "jira-standup" schedule's workflow SHALL be triggered immediately via `DBOSClient.trigger_schedule("jira-standup")` (independent of cron timing) and the endpoint SHALL return `{"status": "ok", "schedule": "jira-standup", "action": "triggered"}`

### Requirement: FastAPI router is mountable
The system SHALL provide a `scheduler_router` that can be included in any FastAPI app via `app.include_router(scheduler_router, prefix="/scheduler")`.

#### Scenario: Mount router in existing app
- **WHEN** `app.include_router(scheduler_router, prefix="/scheduler")` is called
- **THEN** all scheduler endpoints SHALL be available under the `/scheduler` prefix

