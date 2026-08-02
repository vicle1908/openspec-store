# scheduler-entrypoint-manifest-generation

> **Capability:** `scheduler-entrypoint-manifest-generation` (NEW)
> **Owning change:** `scheduler-compose-self-bootstrap`

## Why

The `tdt-scheduler` Docker container currently depends on host-side `scripts/deploy.sh` invocations to populate `~/.tdt/schedules/*.yaml`. A fresh `docker compose up` on a clean host yields a scheduler with `code-daily-scan.yaml` and `tdt-observability.yaml` missing — only `jira-daily-reports.yaml` is generated in-container. This capability moves all manifest generation into the container's `entrypoint.sh` so the compose stack is self-bootstrapping.

---

## ADDED Requirements

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

#### Scenario: Generator raises, container exits

- **WHEN** `code_daily_scan_manifest()` raises (e.g., host config missing)
- **THEN** the entrypoint exits with code != 0
- **AND** the scheduler service is reported as `unhealthy` by `docker compose ps`
- **AND** the entrypoint log contains the exception traceback

### Requirement: Generator output format

Each generator function MUST return a Python `dict` matching the `tdt-schedule/v1` schema. The dict MUST be `model_dump()`-compatible with `tdt_core.scheduler.schedule_manifest.ScheduleManifest`. Cron, timezone, and `workflow.module/function` MUST be present for every schedule. `automatic_backfill` MUST be `False`.

#### Scenario: Generator output validates as ScheduleManifest

- **WHEN** any generator returns its dict
- **THEN** `ScheduleManifest.model_validate(dict)` returns a `ScheduleManifest` instance with `len(manifest.schedules) >= 1`

---

## Verification

| Mechanism | Command |
|-----------|---------|
| Unit tests | `pytest -x agent-core/tests/scheduler/test_entrypoint_manifest_generation.py -q` |
| Compose-up smoke test | `bash agent-core/scripts/verify_scheduler_compose_up.sh` |
| Live inspect | `curl -fsS http://127.0.0.1:9100/scheduler/health \| jq .reload.manifests_loaded` |

The smoke test verifies the **end-to-end path**: fresh image build, container start, manifests emitted, schedules registered, healthcheck green.
