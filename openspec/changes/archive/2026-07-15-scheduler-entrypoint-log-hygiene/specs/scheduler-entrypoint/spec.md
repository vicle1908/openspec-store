# scheduler-entrypoint

## MODIFIED Requirements

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