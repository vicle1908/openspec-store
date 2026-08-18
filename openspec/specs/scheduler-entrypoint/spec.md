# scheduler-entrypoint Specification

## Purpose
Defines the scheduler container entrypoint: atomic manifest generation, hot-reload signaling, fast-fail on generator errors, dual-sink logging, and startup log rotation.
## Requirements
### Requirement: The scheduler container emits all manifests at startup

The Docker `scheduler` service's `entrypoint.sh` MUST invoke a manifest generator for each `(repo, output_path)` pair before executing `tdt-scheduler serve`. The entrypoint SHALL live at `tdt-scheduler/entrypoint.sh` (moved from `agent-core/deployments/scheduler/entrypoint.sh`).

#### Scenario: All three manifests written on container start

- **WHEN** the scheduler container is started via `docker compose up -d` from `tdt-scheduler/`
- **THEN** `entrypoint.sh` exits 0 only AFTER all manifest files exist and parse via `tdt_core.scheduler.schedule_manifest.ScheduleManifest.model_validate`
- **AND** the container's `tdt-scheduler serve` process starts with the manifests already on disk

### Requirement: Manifest writes are atomic

Each manifest write MUST use the pattern `write tmp + rename`. After the rename, no `<output>.yaml.tmp` files MAY remain in `/home/agent/.tdt/schedules/`.

#### Scenario: Atomic write leaves no .tmp leftover

- **WHEN** the generator writes a manifest to `/home/agent/.tdt/schedules/<repo>.yaml`
- **THEN** a `Path(...).with_suffix(".yaml.tmp")` is created and renamed
- **AND** after the rename, `glob("/home/agent/.tdt/schedules/*.tmp")` returns no matches for that repo

### Requirement: Hot-reload is triggered exactly once after all manifests are written

After all manifests are written successfully, the entrypoint MUST touch `/home/agent/.tdt/schedules/.reload` exactly once (atomic write + rename). The scheduler observes this in its next healthcheck poll and re-applies the schedule set in one cycle.

#### Scenario: Single .reload touch after all manifests

- **WHEN** all three manifests are written successfully
- **THEN** the `.reload` file's mtime is updated once
- **AND** the scheduler's healthcheck reports `manifests_loaded == 3` and `schedules_applied == <expected_count>`

### Requirement: Generator failures fail the entrypoint fast

If any manifest generator exits non-zero, the entrypoint SHALL exit non-zero immediately. The Docker `restart: unless-stopped` policy restarts the container, re-running the full generation sequence.

#### Scenario: Generator raises, container exits

- **WHEN** a manifest generator raises (e.g., host config missing)
- **THEN** the entrypoint exits with code != 0
- **AND** the scheduler service is reported as `unhealthy` by `docker compose ps`
- **AND** the entrypoint log contains the exception traceback

#### Scenario: Scheduler stdout is reachable via docker logs

- **WHEN** the scheduler process emits any line to stdout or stderr
- **THEN** `docker logs <scheduler-container> --since <since>` SHALL contain that line within milliseconds
- **AND** the host bind-mounted file `$TDT_HOME/logs/scheduler-entrypoint.log` SHALL contain the same line

#### Scenario: Scheduler log is rotated at startup if over 50 MB

- **WHEN** the container starts and `~/.tdt/logs/scheduler-entrypoint.log` exists with a size greater than 52,428,800 bytes (50 MB)
- **THEN** the entrypoint SHALL rename the existing file to `scheduler-entrypoint.log.1` before starting tee
- **AND** tee SHALL start with a fresh file at the original path

### Requirement: Generator output format

Each generator function MUST return a Python `dict` matching the `tdt-schedule/v1` schema. The dict MUST be `model_dump()`-compatible with `tdt_core.scheduler.schedule_manifest.ScheduleManifest`. Cron, timezone, and `workflow.module/function` MUST be present for every schedule. `automatic_backfill` MUST be `False`.

#### Scenario: Generator output validates as ScheduleManifest

- **WHEN** any generator returns its dict
- **THEN** `ScheduleManifest.model_validate(dict)` returns a `ScheduleManifest` instance with `len(manifest.schedules) >= 1`

---
