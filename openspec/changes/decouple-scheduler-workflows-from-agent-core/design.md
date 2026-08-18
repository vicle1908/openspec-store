## Context

The `centralized-scheduling-module` (2026-07-17, 100/100) established the YAML manifest system (`tdt-schedule/v1`) and proved the `register_fn` pattern with jira-daily-reports and webhook-receiver. However, two repos (code-daily-scan, jira-epic-report) still route workflow registration through `agent-core/scheduler_setup.py` via `module:function` YAML wiring. This creates cross-repo `sys.path.insert` coupling and requires the Docker build context to span the entire workspace. The `stale_workflow_cleaner` — a DBOS maintenance workflow — is also registered from agent-core despite belonging to tdt-core's scheduler framework.

A comprehensive audit (GitNexus + cross-repo grep + code reading) revealed additional legacy:

1. **8 dead functions (~180 lines)** in `agent-core/scheduler_setup.py` — `_load_code_daily_scan_config`, `_get_android_config`, `_get_ios_config`, `_platform_scan_command`, `_run_platform_scan`, `daily_android_scan`, `daily_ios_scan`, and associated globals. These are unreachable because YAML manifests now own schedule registration.
2. **`tdt-core/scheduler/cli.py`** hardcodes `"agent_core.scheduler_setup"` as the default module at 3 locations (lines ~731, ~792, ~798) with 3 `sys.path.insert` blocks — creating a runtime coupling that survives beyond agent-core cleanup.
3. **Stale docstrings/comments** in 5 repos referencing `agent_core.scheduler_setup` patterns.
4. **`scripts/generate_schedule_manifest.py`** — a special `@_ENGINE` decorator parser that becomes obsolete once `stale_workflow_cleaner` moves to tdt-core.

## Goals / Non-Goals

**Goals:**
- Zero `sys.path.insert` hacks in agent-core
- Each repo owns its own workflow registration via `register_fn`
- `stale_workflow_cleaner` lives in tdt-core alongside the DBOS engine
- Dockerfile build context scoped to agent-core only
- All 5 repos in `~/.tdt/schedules/` use the same `register_fn` or `module:function` pattern consistently

**Non-Goals:**
- Changing the tdt-scheduler ownership contract
- Modifying jira-daily-reports or webhook-receiver (already migrated)
- Changing the Docker image base, Python version, or DBOS engine
- Migrating other agent-core concerns (tool registry, skill system, etc.)

## Decisions

### D1: stale_workflow_cleaner moves to tdt-core/scheduler/maintenance.py

**Decision:** The cleaner becomes a framework-level built-in, registered during scheduler engine bootstrap rather than by an application-layer module.

**Rationale:** The cleaner knows about DBOS workflow states (error rows, enqueued rows, application versions) — this is scheduler infrastructure, not business logic. tdt-core already owns the engine, CLI, and registry. Putting the cleaner here follows single-responsibility and eliminates the agent-core→tdt-core circular dependency for these functions.

**Alternative considered:** Keep in agent-core but register via YAML manifest → rejected because the cleaner is framework-level and should always be active; YAML manifests are for repo-specific workflows that can be disabled.

### D2: code-daily-scan creates dbos_scheduling.py with register_all_schedules

**Decision:** Follow the jira-daily-reports pattern exactly — a `dbos_scheduling.py` module with `register_all_schedules(engine, apply=False)` that uses the subprocess invocation pattern (`_run_report` equivalent) to run `daily_android_scan` and `daily_ios_scan`.

**Rationale:** The pattern is proven (jira-daily-reports: 16 schedules, idempotent, retry logic). Consistency reduces cognitive load and review burden.

### D3: jira-epic-report creates dbos_scheduling.py with register_all_schedules

**Decision:** Same pattern as code-daily-scan. The existing `daily_epic_report` function (which calls `epic-report scheduled-run`) is wrapped in a `register_all_schedules` that the YAML manifest calls.

**Rationale:** The epic report already has a standalone CLI (`epic-report scheduled-run`) that handles its own config, retry, and error propagation. The register_all_schedules wrapper is thin.

### D4: Manifest generators update output, not structure

**Decision:** The existing `generators/code_daily_scan.py` and `generators/jira_epic_report.py` are modified to emit `register_fn:` instead of `module:function` in the YAML. The generator infrastructure (dispatcher, atomic write, hot-reload) is unchanged.

**Rationale:** The generators live in agent-core/deployments/scheduler because they produce manifests during Docker entrypoint. Moving them would complicate the build; updating their output is simpler.

### D5: Dockerfile simplifies but retains workspace-context safety net

**Decision:** The Dockerfile can reduce COPY scope, but the compose.yaml volumes still bind-mount sibling repos for runtime. The `sys.path` insertions in scheduler_setup.py are removed, but the Docker PYTHONPATH for generators is retained as defense-in-depth.

**Rationale:** The generators still import sibling-repo modules at call time; removing the bind mounts would break them. The simplification is in agent-core's own code, not the Docker orchestration.

## Risks / Trade-offs

- **[Generator output mismatch]** → The YAML manifest for code-daily-scan must match the register_fn's expected interface. Mitigated by: the register_fn pattern is identical to jira-daily-reports (same engine parameter contract).
- **[Docker rebuild required]** → All 4 repos need rebuild. Mitigated by: no behavioral change; only wiring changes.
- **[Stale manifests on disk]** → If the container starts before the entrypoint regenerates manifests, old module:function YAML remains. Mitigated by: the entrypoint always regenerates before starting; the .reload sentinel forces re-read.
- **[spec drift]** → Two specs are modified (agent-core-scheduler-setup, scheduled-epic-report); the specs must stay in sync with the code changes. Mitigated by: delta specs are created in this change.

## Migration Plan

1. Create `tdt-core/scheduler/maintenance.py` with stale_workflow_cleaner
2. Create `code_daily_scan/dbos_scheduling.py` with register_all_schedules
3. Create `jira_epic_report/dbos_scheduling.py` with register_all_schedules
4. Update `generators/code_daily_scan.py` and `generators/jira_epic_report.py`
5. Update YAML manifests for both repos
6. Remove workflow functions from `agent-core/scheduler_setup.py`
7. Remove sys.path.insert blocks from agent-core
8. Update `tdt-core/scheduler/cli.py` (hardcoded module refs + sys.path)
9. Update stale docstrings in 5 repos
10. Simplify Docker build
11. Rebuild Docker image, restart scheduler, verify all schedules registered
12. Run full test suites across all 4 code repos

**Rollback (comprehensive):**
1. `git checkout` all 4 code repo working trees (agent-core, tdt-core, code-daily-scan, jira-epic-report) to pre-change commits
2. Revert `~/.tdt/schedules/code-daily-scan.yaml` and `~/.tdt/schedules/jira-epic-report.yaml` to old `module:function` format
3. Revert `generators/code_daily_scan.py` and `generators/jira_epic_report.py`
4. Rebuild Docker image: `docker compose build scheduler && docker compose up -d scheduler`
5. Verify: `curl http://127.0.0.1:9100/scheduler/schedules` shows all schedules
No data loss — manifests are regenerated at container start.
