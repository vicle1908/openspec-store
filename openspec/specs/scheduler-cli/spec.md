# scheduler-cli Specification

## Purpose

The tdt-scheduler CLI provides a command-line interface for managing scheduled workflows: listing, pausing, resuming, triggering, and deleting schedules, as well as querying scheduler health status.

## Requirements

_(Baseline: no requirements defined. All requirements are introduced by the `centralized-scheduling-module` change.)_

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

The system SHALL provide a `tdt-scheduler serve` command that runs a long-lived scheduler host. It SHALL initialize the `SchedulerEngine`, load schedule manifests from `~/.tdt/schedules/` via the YAML manifest registry loader, call `apply_schedules()`, then block until terminated. The `serve` command SHALL NOT hardcode a specific module path as the default schedule source; all workflow registration is driven by YAML manifests. This is the entrypoint for the Docker `scheduler` service (`command: ["uv", "run", "tdt-scheduler", "serve"]`).

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

### Requirement: Public module-level cleanup helpers

The system SHALL provide public module-level functions `cancel_stale_error_workflows`
and `cancel_stale_enqueued_workflows` in `tdt_core.scheduler.cli`. The original
underscore-prefixed names SHALL remain as thin delegating wrappers so existing
internal callers and tests continue to work without modification.

#### Scenario: Public helpers exist and are callable

- **WHEN** `from tdt_core.scheduler.cli import cancel_stale_error_workflows` is
  executed
- **THEN** the import SHALL succeed and the function SHALL be callable with
  `(engine: SchedulerEngine, *, current_version: str | None = None, ...)`

#### Scenario: Legacy underscore-prefixed names still work

- **WHEN** `from tdt_core.scheduler.cli import _cancel_stale_error_workflows` is
  executed
- **THEN** the import SHALL succeed and the function SHALL behave identically to
  the new public `cancel_stale_error_workflows` (delegation, not a copy)

### Requirement: Default error_class_names tuple

The system SHALL default `_cancel_stale_error_workflows` (and its public alias
`cancel_stale_error_workflows`) to match the following exception classes:

```python
(
    "ModuleNotFoundError",
    "AttributeError",
    "ImportError",
    "UnpicklingError",
    "FileNotFoundError",
    "OSError",
    "subprocess.CalledProcessError",
    "subprocess.SubprocessError",
)
```

#### Scenario: Default tuple catches real-world stale exceptions

- **WHEN** the cleanup function encounters an `ERROR` row whose pickled
  exception decodes to `subprocess.CalledProcessError` with `returncode=128`
- **THEN** the row SHALL be cancelled (class name matches the default tuple)

- **WHEN** the cleanup function encounters an `ERROR` row whose pickled
  exception decodes to `FileNotFoundError(2, "No such file or directory")`
- **THEN** the row SHALL be cancelled

#### Scenario: Callers may override the default tuple

- **WHEN** `cancel_stale_error_workflows(engine, current_version=None, error_class_names=("MyError",))` is called
- **THEN** the function SHALL use ONLY the caller-provided `("MyError",)` tuple,
  not the default — overrides are explicit and complete
