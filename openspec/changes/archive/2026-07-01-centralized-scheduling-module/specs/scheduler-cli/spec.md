## ADDED Requirements

### Requirement: tdt-scheduler CLI entry point
The system SHALL provide a `tdt-scheduler` CLI command (Typer app) for managing schedules across all services.

#### Scenario: CLI is installed
- **WHEN** `tdt-core[scheduler]` is installed
- **THEN** `tdt-scheduler --help` SHALL display available subcommands

### Requirement: List all schedules
The system SHALL provide a `tdt-scheduler schedules list` command that shows all DBOS-managed schedules, backed by `DBOSClient.list_schedules()` / `get_schedule()`.

#### Scenario: List schedules with output
- **WHEN** `tdt-scheduler schedules list` is run
- **THEN** it SHALL display each schedule's schedule name (`schedule_name`), workflow name (`workflow_name`), cron expression (`schedule`), status, and last run time (`last_run_time`, derived from DBOS `last_fired_at`)

#### Scenario: Next-run time is derived, not read from DBOS
- **WHEN** the list output includes a next-run column
- **THEN** that value SHALL be **computed** from the cron expression and `last_fired_at` (e.g. via `croniter`) — DBOS does NOT expose a next-run API, so next-run is best-effort/derived and MAY be omitted rather than fabricated

#### Scenario: List schedules as JSON
- **WHEN** `tdt-scheduler schedules list --json` is run
- **THEN** it SHALL output a JSON array with schedule details

#### Scenario: List schedules when scheduling is disabled
- **WHEN** `tdt-scheduler schedules list` is run and scheduling is disabled
- **THEN** it SHALL print an error and exit with code 1

### Requirement: Pause a schedule
The system SHALL provide a `tdt-scheduler schedules pause <name>` command.

**Naming rule:** All schedule name arguments MUST match the registered name exactly, including the service prefix (e.g. `jira-standup`, not `standup`). The CLI does not perform prefix stripping or fuzzy matching.

#### Scenario: Pause active schedule
- **WHEN** `tdt-scheduler schedules pause jira-standup` is run
- **THEN** the schedule named "jira-standup" SHALL be paused until resumed

### Requirement: Resume a schedule
The system SHALL provide a `tdt-scheduler schedules resume <name>` command.

**Naming rule:** All schedule name arguments MUST match the registered name exactly, including the service prefix (e.g. `jira-standup`, not `standup`). The CLI does not perform prefix stripping or fuzzy matching.

#### Scenario: Resume paused schedule
- **WHEN** `tdt-scheduler schedules resume jira-standup` is run
- **THEN** the paused schedule named "jira-standup" SHALL be resumed

### Requirement: Trigger a schedule immediately
The system SHALL provide a `tdt-scheduler schedules trigger <name>` command.

**Naming rule:** All schedule name arguments MUST match the registered name exactly, including the service prefix (e.g. `jira-standup`, not `standup`). The CLI does not perform prefix stripping or fuzzy matching.

**DBOS validation (2026):** DBOS provides `trigger_schedule(schedule_name)` for in-process immediate runs. When triggering via external management, use `DBOSClient.trigger_schedule(schedule_name)`.

**Implementation constraint (this change):** `tdt-scheduler schedules trigger` MUST trigger an immediate run via `DBOSClient.trigger_schedule(schedule_name)`, because the CLI is an external management surface.

#### Scenario: Trigger schedule on demand
- **WHEN** `tdt-scheduler schedules trigger jira-standup` is run
- **THEN** the schedule named "jira-standup" SHALL be triggered immediately via `DBOSClient.trigger_schedule("jira-standup")` regardless of its cron timing

### Requirement: Delete a schedule
The system SHALL provide a `tdt-scheduler schedules delete <name>` command.

**Naming rule:** All schedule name arguments MUST match the registered name exactly, including the service prefix (e.g. `jira-standup`, not `standup`). The CLI does not perform prefix stripping or fuzzy matching.

#### Scenario: Delete schedule
- **WHEN** `tdt-scheduler schedules delete jira-standup` is run
- **THEN** the schedule named "jira-standup" SHALL be permanently removed from DBOS

### Requirement: Scheduler status
The system SHALL provide a `tdt-scheduler status` command that shows overall scheduler health and host connectivity.

#### Scenario: Status with enabled scheduler
- **WHEN** `tdt-scheduler status` is run and scheduling is enabled
- **THEN** it SHALL display enabled status, schedule count, and DBOS connection state

#### Scenario: Status with disabled scheduler
- **WHEN** `tdt-scheduler status` is run and scheduling is disabled
- **THEN** it SHALL display "disabled" and exit with code 0

### Requirement: Long-lived scheduler host (serve)
The system SHALL provide a `tdt-scheduler serve` command that runs a long-lived scheduler host. It SHALL initialize the `SchedulerEngine`, register the `scheduler_setup` workflows, call `apply_schedules()`, then block until terminated. This is the entrypoint for the Docker `scheduler` service (`command: ["uv", "run", "tdt-scheduler", "serve"]`).

#### Scenario: serve initializes, applies schedules, and stays running
- **WHEN** `tdt-scheduler serve` starts with scheduling enabled and a reachable DBOS DSN
- **THEN** the engine SHALL initialize, all registered schedules SHALL be activated via `apply_schedules()`, and the process SHALL remain running until terminated

#### Scenario: serve fails fast when the durable store is unreachable
- **WHEN** `tdt-scheduler serve` starts and the configured PostgreSQL DSN is unreachable
- **THEN** it SHALL exit non-zero with a clear error rather than running without a clock

#### Scenario: serve refuses passthrough mode
- **WHEN** `tdt-scheduler serve` starts with scheduling disabled (passthrough)
- **THEN** it SHALL exit non-zero, because a cron host with no DBOS clock cannot fire scheduled workflows (Decision 7)

#### Scenario: serve re-applies schedules on restart
- **WHEN** the `serve` process restarts after a crash or container recreation (PostgreSQL volume retained)
- **THEN** it SHALL call `apply_schedules()` again so all schedules are re-activated without manual intervention

#### Scenario: serve shuts down gracefully on SIGTERM
- **WHEN** the process receives `SIGTERM` (e.g. `docker stop`)
- **THEN** it SHALL call `shutdown()` to destroy the DBOS runtime and exit cleanly (exit code 0)
