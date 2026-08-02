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
  contain that line
- **AND** the host bind-mounted file `$TDT_HOME/logs/scheduler-entrypoint.log`
  SHALL contain the same line (preserving the cross-restart persistence
  contract).

The dual-sink pattern is `exec > >(tee -a "${LOG_FILE}") 2>&1` in the
entrypoint script: this replaces PID 1's stdout with the read end of a
named pipe that `tee` writes to both the terminal (which becomes the
Docker json-file driver) and the file. The final `exec
uv run tdt-scheduler serve` inherits the tee-writer's stdout, so even
the post-fork server output is fanned to both sinks.