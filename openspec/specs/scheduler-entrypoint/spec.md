# scheduler-entrypoint Specification

## Purpose
Defines the scheduler container entrypoint: atomic manifest generation, hot-reload signaling, fast-fail on generator errors, dual-sink logging, and startup log rotation.
## Requirements
### Requirement: The scheduler container emits all manifests at startup

The Docker `scheduler` service's `entrypoint.sh` MUST invoke a manifest generator for each `(repo, output_path)` pair before executing `tdt-scheduler serve`. The list of `(repo, output_path)` pairs MUST include at minimum:

- `("jira-daily-reports", "/home/agent/.tdt/schedules/jira-daily-reports.yaml")`
- `("code-daily-scan", "/home/agent/.tdt/schedules/code-daily-scan.yaml")`
- `("tdt-observability", "/home/agent/.tdt/schedules/tdt-observability.yaml")`

#### Scenario: All three manifests written on container start

- **WHEN** the scheduler container is started via `docker compose up -d scheduler`
- **THEN** `entrypoint.sh` exits 0 only AFTER all three manifest files exist and parse via `tdt_core.scheduler.schedule_manifest.ScheduleManifest.model_validate`
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

If any generator function raises an exception, the entrypoint MUST exit with a non-zero status, log the failure to `/home/agent/.tdt/logs/scheduler-entrypoint.log`, and **NOT** proceed to `tdt-scheduler serve`. The container's `restart: unless-stopped` policy MAY restart the container; each restart MUST re-attempt the same generators.

The entrypoint MUST also make PID 1's stdout and stderr reachable through
the Docker log driver (json-file by default) so that `docker logs`,
`docker compose logs`, and any container-level log rotation or shipping
pipeline can observe what the scheduler is emitting. The mechanism MUST
write to both the host bind-mounted log file and the container stdout
without introducing a single point of failure — the file write MUST NOT
silently consume output that the container stdout would otherwise show.

#### Scenario: Generator raises, container exits

- **WHEN** `code_daily_scan_manifest()` raises (e.g., host config missing)
- **THEN** the entrypoint exits with code != 0
- **AND** the scheduler service is reported as `unhealthy` by `docker compose ps`
- **AND** the entrypoint log contains the exception traceback

#### Scenario: Scheduler stdout is reachable via docker logs

- **WHEN** the scheduler process emits any line to stdout or stderr (DBOS
  startup banners, structlog events, dependency-integrity gate output, etc.)
- **THEN** `docker logs agent-core-local-scheduler-1 --since <since>` SHALL
  contain that line within milliseconds
- **AND** the host bind-mounted file `$TDT_HOME/logs/scheduler-entrypoint.log`
  SHALL contain the same line (preserving the cross-restart persistence
  contract).

The dual-sink pattern is `exec > >(stdbuf -oL tee -a "${LOG_FILE}") 2>&1`
in the entrypoint script. `stdbuf -oL` forces line-buffering on tee so that
every single-line output (structlog events, subprocess stdout/stderr, etc.)
is flushed to both the terminal (which becomes the Docker json-file driver)
and the file immediately — without it, tee's default 8 KB block buffer would
delay all non-flush output until ~40 structlog lines accumulate.

#### Scenario: Scheduler log is rotated at startup if over 50 MB

- **WHEN** the container starts and `~/.tdt/logs/scheduler-entrypoint.log`
  exists with a size greater than 52,428,800 bytes (50 MB)
- **THEN** the entrypoint SHALL rename the existing file to
  `scheduler-entrypoint.log.1` before starting tee
- **AND** tee SHALL start with a fresh (empty or zero-sized) file at the
  original path
- **AND** the entrypoint SHALL print a "Rotated" notice to stdout (which
  reaches both docker logs and the new file).

This matches the 50 MB cap used by `~/.tdt/scripts/rotate-logs.sh` for
other service logs, making the rotation policy consistent. The `.1` file
is kept on the host bind mount for manual cleanup; no automatic deletion
policy is added here.

### Requirement: Generator output format

Each generator function MUST return a Python `dict` matching the `tdt-schedule/v1` schema. The dict MUST be `model_dump()`-compatible with `tdt_core.scheduler.schedule_manifest.ScheduleManifest`. Cron, timezone, and `workflow.module/function` MUST be present for every schedule. `automatic_backfill` MUST be `False`.

#### Scenario: Generator output validates as ScheduleManifest

- **WHEN** any generator returns its dict
- **THEN** `ScheduleManifest.model_validate(dict)` returns a `ScheduleManifest` instance with `len(manifest.schedules) >= 1`

---

