## MODIFIED Requirements

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
- **THEN** it SHALL drain in-flight workflows and exit cleanly
