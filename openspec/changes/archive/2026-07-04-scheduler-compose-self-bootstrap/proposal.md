# scheduler-compose-self-bootstrap

> **Status:** Proposed
> **Generated:** 2026-07-04
> **Context:** Follow-up to `schedule-registry-independent-deployment` (✓ Complete) and `scheduler-stale-workflow-hardening` (in progress). Both shipped the schedule-registry data plane but the bootstrap plane still depends on host-side `scripts/deploy.sh` invocations and ad-hoc `cp` writes. This change moves manifest generation into the container so a fresh `docker compose up` on a clean host produces a self-consistent deployment.

## Why

The `agent-core` Docker scheduler service (`compose.yaml` service `scheduler`) currently cannot produce a fully bootstrapped deployment from `docker compose up` alone:

1. **`code-daily-scan.yaml` is written by `code-daily-scan/scripts/deploy.sh`** running on the **host** BEFORE the container starts. The host script reads host `~/.tdt/code-daily-scan.yaml`, generates the manifest, atomically writes to `~/.tdt/schedules/code-daily-scan.yaml`, and touches `~/.tdt/schedules/.reload` to trigger hot-reload. If an operator clones the workspace on a fresh machine and runs `bash scripts/docker-dev.sh up`, the scheduler starts but `code-daily-scan` schedules are missing.

2. **`tdt-observability.yaml` is written manually** — there is no deploy script at all. The manifest in `~/.tdt/schedules/tdt-observability.yaml` was created on 2026-07-03 by hand and has not been regenerated. If `tdt_observability.retention:daily_observability_retention` is moved, renamed, or its cron changed in source, the live manifest goes stale.

3. **Only `jira-daily-reports.yaml` is generated inside the container** (`generate_jira_manifest.py` invoked by `entrypoint.sh`). The container-as-source-of-truth pattern is implemented for one repo but not the other two. This inconsistency makes "the container is the source of truth" a partial claim.

4. **Host-side deploy scripts cannot run inside the container** because:
   - They assume `~/deployments/<repo>/app` paths that don't exist inside the container (`/workspace/<repo>` is the canonical path inside).
   - They install Python into `$HOME/deployments` (not `/opt/scheduler/.venv`).
   - They are not idempotent on container restart — running `deploy.sh` twice produces no-op writes but the **`.reload` touch always fires**, possibly out-of-order.

5. **Live debugging via `apt-get install ripgrep` inside a running container** (during this session) is an anti-pattern: it mutates a single ephemeral instance, diverges from `Dockerfile` content, and is lost on next `docker compose up --build`. The right fix is to bake dependencies into the image via `apt-get install` in the Dockerfile.

The desired end-state is that **`docker compose up --build` on a fresh host produces a working scheduler** that has loaded all three manifests, registered all schedules, and is ready to fire on the next cron tick — without anyone running a host-side deploy script or `exec`-ing into the container.

## What Changes

1. **Generic in-container manifest generator**: Replace the special-case `generate_jira_manifest.py` with a generic `generate_schedule_manifest.py` (in `agent-core/deployments/scheduler/`) that emits `tdt-schedule/v1` YAML manifests for any repo registered with the bootstrap. Each repo declares its manifest shape in a **Python function inside the agent-core scheduler deployment directory** that returns the manifest dict given the current source/config snapshot. The jira case becomes one such function.

2. **`code-daily-scan` manifest moved into container**: A new function `generate_code_daily_scan_manifest(output_path: Path)` reads `~/.tdt/code-daily-scan.yaml` (already bind-mounted at `/home/agent/.tdt/code-daily-scan.yaml`) via `code_daily_scan.config.load_config()` and writes `~/.tdt/schedules/code-daily-scan.yaml` using the same atomic temp+rename pattern as `jira`. Both legacy host-side heredoc in `code-daily-scan/scripts/deploy.sh` and the manifest-section of that script are deprecated.

3. **`tdt-observability` manifest moved into container**: A new function `generate_tdt_observability_manifest(output_path: Path)` reads constants from `tdt_observability.retention.daily_observability_retention` (already bind-mounted at `/workspace/tdt-observability/src/`) and writes the manifest. This makes the static hand-written file unnecessary.

4. **`entrypoint.sh` orchestrates all generators**: A single entrypoint that:
   - Generates `jira-daily-reports.yaml`, `code-daily-scan.yaml`, `tdt-observability.yaml` (in that order)
   - Touches `~/.tdt/schedules/.reload` once, atomically, with the current ISO timestamp
   - Execs `tdt-scheduler serve`
   - On any generator error, exits non-zero (early-fail — operators must see the bug, not a silent fallback)
   - Logs to `~/.tdt/logs/scheduler-entrypoint.log` for post-mortem

5. **Existing `code-daily-scan/scripts/deploy.sh` reduced to a config-touch shim**: It only updates the host-side config (`~/.tdt/code-daily-scan.yaml`) and touches `~/.tdt/schedules/.reload` to trigger hot-reload. **The 60-line Python heredoc that emits `code-daily-scan.yaml` is removed.** A `DeprecationWarning` log line in the removed section tells users where the manifest now comes from.

6. **Bake `ripgrep` into the Dockerfile**: Add `ripgrep` to the `apt-get install` list in `agent-core/deployments/scheduler/Dockerfile`. Removes the need for live `docker exec ... apt-get install` debugging. Same for any other system binaries the scheduler indirectly invokes (currently: `git`, `curl`, `psql`-adjacent — list verified via `shellcheck`-equivalent grep during implementation).

7. **Smoke test added**: `tests/scheduler/test_entrypoint_manifest_generation.py` runs each generator function against a fixture directory and asserts:
   - The output YAML parses via `tdt_core.scheduler.schedule_manifest.ScheduleManifest.model_validate`
   - The expected schedules (cron, timezone, workflow module/function) are present
   - The atomic write pattern is used (no partial writes, no leftover `.tmp` files)
   - Dry-run mode does NOT touch `~/.tdt/schedules/.reload`

8. **End-to-end compose-up smoke test**: `scripts/verify_scheduler_compose_up.sh` (NEW) tears down the running scheduler, runs `docker compose down -v`, rebuilds from scratch (`docker compose build scheduler`), starts it (`docker compose up -d scheduler`), waits for healthcheck, then asserts the health endpoint reports the expected number of manifests and schedules. CI integration is documented in `tdt-meta/docs/workflows/scheduler-compose-up-smoke.md` but the test itself runs locally — full CI requires a Linux agent.

## Capabilities

### New Capabilities

- `scheduler-entrypoint-manifest-generation`: The agent-core Docker scheduler's `entrypoint.sh` MUST generate all `~/.tdt/schedules/<repo>.yaml` manifests at container startup using commit-time generator functions declared alongside the Dockerfile. The entrypoint MUST be the source of truth for manifest content; operator `deploy.sh` invocations on the host MUST NOT be required for the scheduler to have a complete schedule set.

- `scheduler-generic-manifest-generator-framework`: A registry-style framework inside `agent-core/deployments/scheduler/` mapping `(repo, callable)` to a generator function. Adding a new scheduled repo requires (1) the framework registering the callable and (2) `compose.yaml` mounting the repo source. Adding a new manifest block MUST NOT require editing `tdt_core` or `agent_core.scheduler_setup`.

- `scheduler-compose-up-smoke-test`: An executable script + Python unit test that verifies the scheduler container, started fresh via `docker compose up -d --build`, loads all expected manifests and reports a healthy healthcheck within `start_period + 60s`. The test MUST run against a non-local Postgres (compose-provided) and MUST NOT depend on the prior state of `~/.tdt/`.

### Modified Capabilities

- `agent-core-docker-local-development`: The Dockerfile now installs `ripgrep` alongside `git`, `curl`, `gcc`, `libpq-dev`, `tzdata`. The test `test_dockerfile_matches_compose_versions` is extended to assert `ripgrep` is installed.

- `code-daily-scan-deployment`: The host-side `deploy.sh` is reduced to a config-touch shim. The Python heredoc that wrote `~/.tdt/schedules/code-daily-scan.yaml` is removed and replaced with a `INFO` log line pointing operators at the container's entrypoint.

## Non-Goals

- **No new schedulers** — this change is purely about how existing `code-daily-scan`, `tdt-observability`, and `jira-daily-reports` schedules get registered. Adding a new scheduled repo is a separate concern.
- **No changes to the schedule registry data plane** (registry loader, hot-reload, SIGUSR1, health endpoint) — those are owned by the `schedule-registry-independent-deployment` change.
- **No migration of `code-daily-scan` to a standalone container** — the scheduler remains the single Docker host for all DBOS schedules per `centralize-scheduling` Decision 4.
- **No changes to the manifest schema (`tdt-schedule/v1`)** — generators emit the same YAML format the loader already accepts.
- **No changes to host-side `.env` or `.env.docker`** files — those continue to define `SCHEDULER_POSTGRES_DSN` and similar knobs.

## Impact

**Affected repos:**
- `agent-core`: `compose.yaml`, `Dockerfile`, `deployments/scheduler/entrypoint.sh`, `deployments/scheduler/generate_*.py` (split), `tests/scheduler/test_entrypoint_manifest_generation.py` (NEW), `tests/test_docker_local_dev.py` (extended)
- `code-daily-scan`: `scripts/deploy.sh` (reduced)
- `tdt-observability`: no code change — its manifest now comes from the entrypoint

**Affected docs:**
- `tdt-meta/docs/workflows/scheduler-compose-up-smoke.md` (NEW)
- `tdt-meta/docs/operations/schedule-registry.md` — add a "Manifest Bootstrap" section explaining that all manifests are now generated by the container's `entrypoint.sh`
- `tdt-observability/CLAUDE.md` / `tdt-observability/README.md` — note that its schedule manifest is owned by the scheduler container; the manual manifest file is removed

**Affected specs:**
- `agent-core-docker-local-development` (extended)
- `scheduler-engine` (no functional change — capability added at the deployment layer, not the data plane)

**Backward compatibility:**
- Existing `~/.tdt/schedules/<repo>.yaml` files written by `deploy.sh` continue to work. After the operator rebuilds and restarts the container, the entrypoint rewrites them with the new generator's content. Hot-reload (`.reload` sentinel) ensures DBOS re-registers without operator intervention.
- The `code-daily-scan/scripts/deploy.sh` removal of the heredoc is a `DeprecationWarning` first; in a follow-up change it can become a hard error.
