## MODIFIED Requirements

### Requirement: The scheduler container emits all manifests at startup

The Docker `scheduler` service's `entrypoint.sh` MUST invoke a manifest generator for each `(repo, output_path)` pair before executing `tdt-scheduler serve`. The entrypoint SHALL live at `tdt-scheduler/entrypoint.sh` (moved from `agent-core/deployments/scheduler/entrypoint.sh`).

#### Scenario: All three manifests written on container start

- **WHEN** the scheduler container is started via `docker compose up -d` from `tdt-scheduler/`
- **THEN** `entrypoint.sh` exits 0 only AFTER all manifest files exist and parse via `tdt_core.scheduler.schedule_manifest.ScheduleManifest.model_validate`
- **AND** the container's `tdt-scheduler serve` process starts with the manifests already on disk

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
