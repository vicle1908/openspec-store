## Context

The TDT ecosystem uses [DBOS](https://dbos.dev/) for durable workflow scheduling. The canonical scheduler runs in a Docker container managed by `agent-core`. Currently, all scheduled workflows are declared via Python `@_ENGINE.scheduled_workflow()` decorators in `agent-core/scheduler_setup.py`, which imports code from every scheduled repo.

This creates a coupling problem: any repo that wants to add, modify, or remove a scheduled workflow must modify `agent-core`, rebuild the Docker scheduler, and redeploy.

The solution is to introduce a declarative YAML-based schedule registry: each repo declares its schedules in a YAML manifest at `~/.tdt/schedules/<repo>.yaml`, and the scheduler discovers and applies them without hard imports.

### Current Architecture

```
agent-core/scheduler_setup.py  ← imports from every repo
    ├── jira_daily_reports.scheduler_setup
    ├── code_daily_scan (via config)
    ├── webhook_receiver (webhook-selftest, dlq-reaper, scan-recent-mr)
    ├── ai_review (coverage-scan)
    └── jira_skill (ticket-analysis)

# Every @scheduled_workflow decorator lives in agent-core
# To add a schedule: modify agent-core → rebuild Docker → redeploy
```

### Constraints

- Docker scheduler must continue running without restart when schedule YAMLs change
- Existing `@scheduled_workflow` decorators must continue working during migration (dual-write)
- The ownership contract (`apply_schedules()` restricted to `tdt-scheduler`) applies to YAML-loaded schedules
- `~/.tdt/schedules/` directory is shared between host and Docker container via `~/.tdt:/home/agent/.tdt` volume mount
- Python 3.14, uv packaging, launchd deployment model

## Goals / Non-Goals

**Goals:**
- Enable each repo to own its schedule definitions independently
- Zero-downtime schedule changes (hot-reload without scheduler restart)
- Declarative, version-controlled schedule manifests
- Minimal migration risk (existing decorators work during transition)
- Extends existing `ScheduleRegistry` and `ScheduledWorkflowSpec` — no new types needed

**Non-Goals:**
- Per-repo Docker scheduler containers (single scheduler remains)
- Kubernetes or cloud-native deployment support
- Configuration coupling resolution (`~/.tdt/config.yaml`)
- DBOS infrastructure changes (app_name isolation, version pinner)

## Decisions

### D1: YAML Manifest Location — `~/.tdt/schedules/` (shared volume)

**Decision:** Schedule YAML manifests live in `~/.tdt/schedules/` on the host, mounted into the Docker scheduler container at the same path.

**Rationale:** This matches the existing pattern for `~/.tdt/.env` (credentials), `~/.tdt/state/` (runtime state), and `~/.tdt/code-daily-scan.yaml` (per-repo config). The Docker compose already mounts `~/.tdt:/home/agent/.tdt` as a read-write volume. No compose changes needed.

### D2: Schema Maps Directly to `ScheduledWorkflowSpec`

**Decision:** The YAML schema fields map 1:1 to `ScheduledWorkflowSpec` fields. No new types are introduced.

| YAML field | `ScheduledWorkflowSpec` field |
|-----------|----------------------------|
| `name` | `schedule_name` |
| `cron` | `cron` |
| `timezone` | `cron_timezone` (null = UTC) |
| `automatic_backfill` | `automatic_backfill` |
| `queue` | `queue_name` |
| `workflow.module` + `workflow.function` | Resolved to `workflow_fn` via importlib |

**Rationale:** The loader converts YAML → `ScheduledWorkflowSpec` and feeds into the same `ScheduleRegistry` that decorator-based registration uses. The `apply_schedules()` call and DBOS upsert logic are unchanged.

### D3: Hot-Reload Trigger — `.reload` sentinel file

**Decision:** Deploy scripts write `~/.tdt/schedules/<repo>.yaml`, then write the current ISO timestamp to `~/.tdt/schedules/.reload`. The scheduler checks `.reload` mtime on every healthcheck cycle (60s) and on SIGUSR1.

**Rationale:** This is simpler than file-watcher libraries (watchdog, FSEvents) and avoids async complexity. The 60s polling interval is acceptable for schedule changes — they are event-driven, not latency-critical.

### D4: YAML Generation from Source Constants

**Decision:** Deploy scripts generate YAML from source code constants (AST parsing or hardcoded stub lists), not from pre-committed YAML files or config files.

**Rationale:** This avoids duplication — the cron expression, timezone, and workflow module are the source of truth in Python code. Generating from source ensures the YAML always reflects the current code. This mirrors the existing `uv-runtime-management` pattern where deploy copies source and builds from it.

### D5: DBOS Upsert for Schedule Updates

**Decision:** DBOS handles schedule updates via upsert semantics — calling `apply_schedules()` with a schedule name that already exists replaces the existing configuration.

**Rationale:** No explicit "delete old schedule" step needed. The `ScheduleRegistry` holds all registered specs; `apply_schedules()` pushes the full set to DBOS. If a schedule is removed from YAML, the next `apply_schedules()` simply doesn't include it.

### D6: Phase-Gated Migration

**Decision:** Three-phase migration with `SCHEDULER_REGISTRY_PHASE` env var toggle.

| Phase | Loader Behavior | Decorator Behavior | Deploy Script |
|-------|---------------|-------------------|---------------|
| 1 | Load YAML, log, **skip apply** | Active | Write YAML, **no .reload** |
| 2 | Load YAML, **apply via DBOS** | Active (dual-write) | Write YAML, **touch .reload** |
| 3 | Load YAML, apply via DBOS | **Removed** | Write YAML, touch .reload |

**Rationale:** Each phase is independently deployable and rollbackable. Phase 1 is zero-risk (existing system unchanged). Phase 2 enables hot-reload with fallback. Phase 3 completes the decoupling.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| YAML schema drift (v1 → v2) | Old manifests break | Version prefix; v1 supported indefinitely |
| Dynamic import failure (module not in sys.path) | Schedule doesn't fire | Deploy ensures repo source is on PYTHONPATH |
| YAML validation errors silently skipped | Schedule missing | Log warning + continue; alerts via observability |
| Race on hot-reload | Inconsistent state | DBOS upsert is atomic; at most one reload at a time |
| Scheduler startup before YAML files exist | No schedules applied | Schedules apply when YAMLs appear on hot-reload |

## Migration Plan

### Phase 1: Introduce Registry (zero risk)

1. Implement `ScheduleRegistryLoader` in `tdt-core`
2. Integrate into `agent-core/scheduler_setup.py` (Phase 1 mode: load YAML, skip apply)
3. Deploy scripts generate YAML manifests (scheduler ignores them)
4. Verify: existing decorators still fire, logs show `schedule.manifest_loaded`

### Phase 2: Dual-Write with Hot-Reload

1. Enable `apply_schedules()` call from loader
2. Register SIGUSR1 handler in `cli.py`
3. Deploy scripts touch `.reload` after writing YAML
4. Migrate schedules one by one from decorators to YAML
5. Verify: all schedules fire from YAML, hot-reload works

### Phase 3: YAML-Only

1. Remove `@_ENGINE.scheduled_workflow` decorators from `scheduler_setup.py`
2. Remove `import jira_daily_reports.scheduler_setup`
3. Remove `SCHEDULER_REGISTRY_PHASE` env var
4. Verify: scheduler starts YAML-only, all schedules present

### Rollback

| Phase | Rollback |
|-------|---------|
| Phase 1 | Remove loader integration from `scheduler_setup.py`, remove YAML generation from deploy scripts |
| Phase 2 | Set `SCHEDULER_REGISTRY_PHASE=1`, remove `.reload` trigger from deploy scripts |
| Phase 3 | Re-add decorators, remove YAML files, restart scheduler |

## Open Questions

1. **YAML generation from AST vs stub lists**: For Phase 1, the simplest approach is hardcoded stub lists in the deploy script (repo name → schedule definitions). AST parsing is more robust but more complex. Decision: Phase 1 uses stub lists, Phase 2+ may migrate to AST if time permits.

2. **Schedule deletion when YAML removed**: If a deploy script deletes its YAML manifest (repo no longer has schedules), the schedule remains in DBOS until next `apply_schedules()` call. The next hot-reload will remove it via DBOS upsert. Acceptable.

3. **Concurrent schedule updates**: If two repos deploy simultaneously, both trigger hot-reload. The scheduler re-applies all schedules twice within 60s. DBOS upsert is idempotent — no issue.
