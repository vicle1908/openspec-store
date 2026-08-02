## Why

The `agent-core/scheduler_setup.py` is the central coupling point for all scheduled workflows in the TDT ecosystem. Every time a repo wants to add, modify, or remove a scheduled workflow, it must modify `agent-core`, rebuild the Docker scheduler, and redeploy. This blocks independent evolution and slows down the team.

The goal is to enable each repo to own its own schedule definitions independently — declared as YAML manifests in `~/.tdt/schedules/` — while the scheduler discovers and applies them without central coordination.

## What Changes

1. **YAML Manifest Schema (`tdt-schedule/v1`)**: Define a declarative YAML schema for schedule definitions: cron expression, timezone, workflow module/function, timeout, queue. Each scheduled repo ships its manifest.

2. **ScheduleRegistryLoader**: Add `ScheduleRegistryLoader` to `tdt-core` that reads `~/.tdt/schedules/*.yaml` manifests and feeds them into the existing `ScheduleRegistry` (from `tdt_core.scheduler.scheduling`). The loader extends — not replaces — the existing decorator-based registration.

3. **Hot-Reload Mechanism**: The scheduler checks `~/.tdt/schedules/.reload` sentinel on every healthcheck cycle (60s) and on SIGUSR1. DBOS handles schedule upsert idempotently — re-registering replaces the existing config.

4. **Deploy Script YAML Generation**: Each repo's deploy script generates its `~/.tdt/schedules/<repo>.yaml` manifest from source code constants (AST parsing or hardcoded stub lists), then touches `.reload` to trigger hot-reload.

5. **Migration Path**: Phase 1 (YAML generated but ignored), Phase 2 (YAML applied, hot-reload active, dual-write), Phase 3 (decorators removed, YAML-only).

## Capabilities

### New Capabilities

- `schedule-registry-loader`: Reads `~/.tdt/schedules/*.yaml` manifests, resolves workflow modules, registers `ScheduledWorkflowSpec` objects into the existing `ScheduleRegistry`, and calls `engine.apply_schedules()`. Feeds into the same registry that decorator-based schedules use.

- `schedule-manifest-schema`: Declarative YAML schema (`tdt-schedule/v1`) with fields that map directly to `ScheduledWorkflowSpec`. Env-var substitution via `${VAR}` and `${VAR:-default}`. Pydantic validation.

- `schedule-deploy-integration`: Each repo's deploy script generates its YAML manifest from source constants and writes to `~/.tdt/schedules/<repo>.yaml`. Atomic writes via temp file + rename. Triggers hot-reload via `.reload` sentinel in Phase 2+.

- `schedule-hot-reload`: Scheduler detects `.reload` changes on healthcheck cycles and on SIGUSR1. Re-applies all schedules via DBOS upsert. Structured logging for reload events.

### Modified Capabilities

- `scheduler-engine` (existing `ScheduleRegistry` class): Extended to accept YAML-loaded `ScheduledWorkflowSpec` objects alongside decorator-based ones. The ownership contract (`apply_schedules()` restricted to `tdt-scheduler`) applies to both paths. No changes to `ScheduledWorkflowSpec` fields — YAML schema maps directly.

- `scheduler-cli` (existing `serve` command): Extended to call `ScheduleRegistryLoader.apply_from_yaml(engine)` during startup and to register SIGUSR1 handler. Health endpoint extended to expose reload state.

## Non-Goals

- This change does NOT address configuration coupling (`~/.tdt/config.yaml` shared across services) — separate concern.
- This change does NOT migrate the Docker scheduler to per-repo containers — single Docker scheduler remains.
- This change does NOT modify the DBOS app_name isolation or version pinner mechanism.
- This change does NOT add Kubernetes or cloud-native deployment support.
- This change does NOT require pre-committed YAML files in source repos — manifests are generated at deploy time from source constants.

## Impact

- **New code**: `tdt-core/src/tdt_core/scheduler/schedule_manifest.py` — Pydantic models for YAML schema
- **New code**: `tdt-core/src/tdt_core/scheduler/registry_loader.py` — YAML loader, module resolver, hot-reload
- **Modified code**: `agent-core/src/agent_core/scheduler_setup.py` — integrate loader, Phase 1/2/3 toggle
- **Modified code**: `tdt-core/src/tdt_core/scheduler/cli.py` — register SIGUSR1, expose reload state in health
- **New code**: `agent-core/scripts/generate_schedule_manifest.py` — AST-based YAML generation
- **Modified code**: `webhook-receiver/scripts/deploy.sh`, `ai-review/scripts/deploy.sh`, `jira-daily-reports/scripts/deploy.sh`, `code-daily-scan/scripts/deploy.sh`, `jira-skill/scripts/deploy.sh` — generate YAML + trigger `.reload`
- **New file**: `~/.tdt/schedules/*.yaml` (generated, not committed)
- **Database**: None — DBOS schema unchanged
- **Dependencies**: `pyyaml` (already via pydantic), `croniter` (already present), `packaging` (already present)
