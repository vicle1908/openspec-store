# Implementation Tasks

## 1. Foundation: YAML Schema and Pydantic Models (tdt-core)

- [x] 1.1 Create `tdt-core/src/tdt_core/scheduler/schedule_manifest.py`:
  - `ScheduleManifest` model: `apiVersion`, `owner`, `version`, `schedules[]`
  - `ScheduleSpec` model: `name`, `description`, `cron`, `timezone`, `automatic_backfill`, `workflow` (nested module/function), `queue`
  - `WorkflowRef` model: `module`, `function`
  - Use `pydantic.BaseModel` with field validators
  - `croniter` for cron expression validation
  - `zoneinfo.ZoneInfo` for timezone validation
  - `packaging.version.Version` for semver validation

- [x] 1.2 Add environment variable substitution in string fields using `os.path.expandvars`, supporting `${VAR}` and `${VAR:-default}` patterns. If a required variable (no default) is missing, log warning but leave unsubstituted.

- [x] 1.3 Write unit tests in `tdt-core/tests/scheduler/test_schedule_manifest.py` covering:
  - Valid manifest parsing with all fields
  - Missing required fields → validation error
  - Invalid cron expression → error
  - Invalid timezone → error
  - Unknown apiVersion → error
  - Env var substitution (set, unset, default)
  - Malformed YAML → error

- [x] 1.4 Run `ruff check tdt-core/src/tdt_core/scheduler/schedule_manifest.py --fix && ruff format tdt-core/src/tdt_core/scheduler/schedule_manifest.py && cd tdt-core && uv run mypy src/tdt_core/scheduler/schedule_manifest.py --strict`

## 2. Foundation: Registry Loader (tdt-core)

- [x] 2.1 Create `tdt-core/src/tdt_core/scheduler/registry_loader.py`:
  - `ScheduleRegistryLoader` class with `__init__(schedules_dir: Path = ~/.tdt/schedules)`
  - `discover_manifests() -> list[Path]`: scan for `*.yaml`, exclude hidden and `.reload`
  - `load_all() -> list[ScheduleManifest]`: parse all manifests, skip invalid with warning
  - `resolve_workflow(manifest: ScheduleManifest, schedule: ScheduleSpec) -> Callable`: use `importlib.import_module()` + `getattr()` to resolve module + function

- [x] 2.2 Implement `register_to_registry()`: convert `ScheduleManifest[]` to `ScheduledWorkflowSpec[]` and call `registry.register(spec)` for each. Use existing `ScheduledWorkflowSpec` from `tdt_core.scheduler.scheduling` — feed into the same registry that `apply_schedules()` consumes.

- [x] 2.3 Implement `apply_from_yaml(engine: SchedulerEngine)`: call `load_all()` → `resolve_workflow()` for each → `register_to_registry()` → `engine.apply_schedules()` once. If Phase 1 mode, log loaded manifests but skip `apply_schedules()`.

- [x] 2.4 Implement hot-reload detection:
  - `check_reload() -> bool`: compare `.reload` file mtime against last check
  - `_last_reload_check: float` instance variable
  - In `apply_from_yaml()`: after applying, update `_last_reload_check = time.time()`

- [x] 2.5 Implement SIGUSR1 handler:
  - `_trigger_reload_flag: bool` instance variable
  - `trigger_reload()`: set flag to True
  - In `apply_from_yaml()`: check flag, if set clear and reload
  - Register handler in `cli.py`'s `_serve()` using `signal.signal(signal.SIGUSR1, ...)` in the main thread

- [x] 2.6 Add structured logging using structlog:
  - `schedule.manifest_loaded`: owner, version, schedule_count
  - `schedule.manifest_skipped`: path, reason
  - `schedule.workflow_import_failed`: module, function, error
  - `schedule.reload_triggered`: manifests_count, source (healthcheck/signal)
  - `schedule.reload_completed`: schedules_applied, manifests_count, duration_ms
  - `schedule.reload_failed`: error, manifest_path

- [x] 2.7 Write unit tests in `tdt-core/tests/scheduler/test_registry_loader.py`:
  - Manifest discovery (mock filesystem)
  - Module import (mock importlib)
  - Reload detection (mock file mtime)
  - Graceful failure (skip invalid manifests, continue)

- [x] 2.8 Run `ruff check tdt-core/src/tdt_core/scheduler/registry_loader.py --fix && ruff format tdt-core/src/tdt_core/scheduler/registry_loader.py && cd tdt-core && uv run mypy src/tdt_core/scheduler/registry_loader.py --strict`

## 3. Phase 1: Integrate Loader into agent-core

- [x] 3.1 Modify `agent-core/scheduler_setup.py`:
  - After existing imports and `_cancel_stale_pending_workflows()` call
  - Add: `from tdt_core.scheduler.registry_loader import get_registry_loader`
  - Add: `loader = get_registry_loader()`
  - Add: Phase 1 mode — call `loader.apply_from_yaml(_ENGINE)` but in Phase 1: log loaded manifests only (do not call `engine.apply_schedules()`). Use env var `SCHEDULER_REGISTRY_PHASE=1` to toggle modes.

- [x] 3.2 Verify existing `@_ENGINE.scheduled_workflow` decorators still fire correctly:
  - `cd agent-core && uv run pytest tests/scheduler/ -v`

- [x] 3.3 Build and restart Docker scheduler: `docker compose -f agent-core/compose.yaml build scheduler && docker compose -f agent-core/compose.yaml up -d scheduler`

- [x] 3.4 Verify healthcheck: `curl -fsS http://127.0.0.1:9100/scheduler/health`

- [x] 3.5 Check logs show `schedule.manifest_loaded` events (Phase 1: manifests loaded but not applied)

## 4. Phase 1: Deploy Script YAML Generation

- [x] 4.1 Create `agent-core/scripts/generate_schedule_manifest.py`:
  - Parse `agent-core/scheduler_setup.py` source via `ast` or regex
  - Extract `@_ENGINE.scheduled_workflow(...)` call kwargs: `cron`, `name`, `cron_timezone`, `automatic_backfill`
  - Map function name to its `workflow.module` and `workflow.function` (module = `agent_core.scheduler_setup`)
  - Output: generate `~/.tdt/schedules/agent-core.yaml`
  - Include `apiVersion`, `owner: agent-core`, `version` (from git tag or `1.0.0`)
  - For `cron_timezone=workspace_timezone_name()`: resolve by importing `jira_daily_reports.config.workspace_timezone_name`

- [x] 4.2 Update `webhook-receiver/scripts/deploy.sh`:
  - After `uv sync`: `mkdir -p ~/.tdt/schedules`
  - Call `python3 agent-core/scripts/generate_schedule_manifest.py --repo webhook-receiver --output ~/.tdt/schedules/webhook-receiver.yaml` (generate from `webhook_receiver.selftest_cli`, `webhook_receiver.dlq_reaper_cli`, `webhook_receiver.scan_recent_mr_cli` — but these are wrappers, so the actual workflow functions live in `agent-core/scheduler_setup.py`. For Phase 1, generate manifest from a stub list of known schedule definitions in the deploy script.)

- [x] 4.3 Update `code-daily-scan/scripts/deploy.sh`:
  - Extract schedules from `~/.tdt/code-daily-scan.yaml` (cron/timezone are already in config)
  - Map to workflow: `code_daily_scan.__main__:main` (the scan CLI)
  - Generate `~/.tdt/schedules/code-daily-scan.yaml`

- [x] 4.4 Update `jira-skill/scripts/deploy.sh`:
  - Extract schedule from `JIRA_TICKET_ANALYSIS_FILTER_URL` env var and `jira_skill.cli` module
  - Generate `~/.tdt/schedules/jira-skill.yaml`

- [x] 4.5 Update `jira-daily-reports/scripts/deploy.sh`:
  - Extract schedules from `jira_daily_reports.scheduler_setup` (or stub list)
  - Generate `~/.tdt/schedules/jira-daily-reports.yaml`

- [x] 4.6 For each deploy: `mkdir -p ~/.tdt/schedules` before write, atomic write via temp file + rename.

- [x] 4.7 Test: `cd ~/Developer/tdt/webhook-receiver && bash scripts/deploy.sh`. Verify `~/.tdt/schedules/webhook-receiver.yaml` exists with correct content.

## 5. Phase 2: Enable Hot-Reload Apply

- [x] 5.1 Modify `agent-core/scheduler_setup.py`: set `SCHEDULER_REGISTRY_PHASE=2` (env-var controlled; Phase 1 = dry-run, Phase 2+ = apply)
- [x] 5.2 Register SIGUSR1 handler in `cli.py`'s `_serve()`: `_start_registry_reloader` daemon thread with `loader.register_sigusr1()`
- [x] 5.3 Update deploy scripts to touch `~/.tdt/schedules/.reload` after writing YAML: Phase 2+ scripts do this
- [x] 5.4 In `cli.py` `_serve()`: `_start_registry_reloader` daemon thread polls `.reload` mtime every 60s
- [x] 5.5 Update `/scheduler/health` endpoint to expose reload state: `health.py` calls `get_registry_loader().reload_state()`
- [x] 5.6 Restart scheduler: `docker compose -f agent-core/compose.yaml restart scheduler`
- [x] 5.7 Verify: `tdt-scheduler schedules list` shows all YAML-loaded schedules
- [x] 5.8 Test hot-reload: modify `~/.tdt/schedules/webhook-receiver.yaml` cron to `*/1 * * * *`, touch `.reload`. Verify change detected within 60s.
- [x] 5.9 Test SIGUSR1: `kill -USR1 $(pgrep -f tdt-scheduler)`. Verify immediate reload.

## 6. Phase 2: Migrate Schedules One by One

For each schedule, the migration is:
1. Remove `@_ENGINE.scheduled_workflow` decorator from `agent-core/scheduler_setup.py`
2. Ensure the YAML manifest for that repo is generated with correct values
3. Verify schedule fires from YAML
4. Check `tdt-scheduler schedules list` confirms the schedule is present

Migrate in this order (lowest risk first):
- [x] 6.1 `webhook-selftest` (YAML manifest in `webhook-receiver/scripts/deploy.sh`)
- [x] 6.2 `dlq-reaper` (YAML manifest in `webhook-receiver/scripts/deploy.sh`)
- [x] 6.3 `scan-recent-mr` (YAML manifest in `webhook-receiver/scripts/deploy.sh`)
- [x] 6.4 `coverage-scan` (YAML manifest in `ai-review/scripts/deploy.sh`)
- [x] 6.5 `daily-android-scan` (YAML manifest in `code-daily-scan/scripts/deploy.sh`)
- [x] 6.6 `daily-ios-scan` (YAML manifest in `code-daily-scan/scripts/deploy.sh`)
- [x] 6.7 `jira-status-audit` (YAML manifest in `jira-skill/scripts/deploy.sh`)
- [x] 6.8 jira-daily-reports schedules (15 schedules via `register_fn: jira_daily_reports.dbos_scheduling:register_all_schedules`, generated by `agent-core/deployments/scheduler/generate_jira_manifest.py` in Docker entrypoint)

## 7. Phase 3: Cleanup

- [x] 7.1 Remove `import jira_daily_reports.scheduler_setup` from `agent-core/scheduler_setup.py`
- [x] 7.2 Remove all `@_ENGINE.scheduled_workflow(...)` decorator functions from `agent-core/scheduler_setup.py`. Keep:
  - `_cancel_stale_pending_workflows()`
  - `ScheduleRegistryLoader` integration
  - SIGUSR1 handler registration
  - Hot-reload loop
- [x] 7.3 The `agent-core/scheduler_setup.py` module is now ~460 lines (workflow functions remain as they are importable by YAML manifests, but no DBOS decorators)
- [x] 7.4 Remove `SCHEDULER_REGISTRY_PHASE` env var: Phase 1/2 gating is removed — YAML is the canonical path
- [x] 7.5 Verify scheduler starts YAML-only: `tdt-scheduler schedules list` shows all schedules

## 8. Documentation

- [x] 8.1 Create `tdt-meta/docs/operations/schedule-registry.md`: directory structure, schema, hot-reload, troubleshooting
- [x] 8.2 Update `tdt-meta/docs/operations/scheduler-healthcheck.md`: add reload state to health endpoint response
- [x] 8.3 Update `tdt-core/src/tdt_core/scheduler/README.md`: note YAML-based schedule ownership, update process table

## 9. Verification

- [x] 9.1 Run tdt-core scheduler tests: 110/110 pass ✓
- [x] 9.2 Run linter: ruff check + format — clean
- [x] 9.3 Run type check: mypy --strict — clean (0 errors)
- [x] 9.4 Verify OpenSpec: `openspec validate --strict schedule-registry-independent-deployment` — valid ✓

## Rollback Plan

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 | Remove `ScheduleRegistryLoader` import + call from `scheduler_setup.py`. Remove YAML generation from deploy scripts. Restart scheduler. |
| Phase 2 | Set `SCHEDULER_REGISTRY_PHASE=1` (or remove Phase 2 code path). Remove `.reload` trigger from deploy scripts. Restart scheduler. YAML manifests exist but are ignored. |
| Phase 3 | Re-add `@scheduled_workflow` decorators to `scheduler_setup.py`. Re-add `import jira_daily_reports.scheduler_setup`. Remove generated YAML files (`~/.tdt/schedules/*.yaml`). Restart scheduler. |
