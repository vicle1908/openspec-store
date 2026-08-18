## 1. tdt-core: Move stale_workflow_cleaner + Clean up scheduler CLI

- [ ] 1.1 Create `tdt-core/src/tdt_core/scheduler/maintenance.py` with `stale_workflow_cleaner` registered via `@_ENGINE.scheduled_workflow(cron="*/30 * * * *", cron_timezone="UTC", name="stale_workflow_cleaner")`, importing `cancel_stale_error_workflows` and `cancel_stale_enqueued_workflows` from `tdt_core.scheduler.cli`.
- [ ] 1.2 Ensure `maintenance.py` is imported during scheduler bootstrap (add to `tdt_core/scheduler/__init__.py` or the `serve()` entrypoint's import chain).
- [ ] 1.3 Update `tdt-core/scheduler/cli.py`: remove 3 hardcoded `"agent_core.scheduler_setup"` string literals (lines ~731, ~792, ~798) and 3 `sys.path.insert` blocks (lines ~763, ~770, ~785). The `serve` command should rely on the YAML manifest system for workflow discovery instead of dynamically importing a hardcoded module.
- [ ] 1.4 Update `tdt-core/scheduler/cli.py` docstrings that reference `agent_core.scheduler_setup`.
- [ ] 1.5 Update `tdt-core/scheduler/registry_loader.py` docstring referencing `agent-core/src/agent_core/scheduler_setup.py`.
- [ ] 1.6 Update `tdt-core/scheduler/README.md` referencing agent-core scheduler_setup.
- [ ] 1.7 Update `tdt-core/tests/scheduler/test_cli.py` if any test references `TDT_SCHEDULER_SETUP_MODULE`.
- [ ] 1.8 Run tdt-core test suite (`uv run pytest`) — confirm green.
- [ ] 1.9 Run ruff I001 + ruff format + mypy strict on tdt-core — confirm clean.

## 2. code-daily-scan: Create dbos_scheduling.py

- [ ] 2.1 Create `code-daily-scan/src/code_daily_scan/dbos_scheduling.py` with `register_all_schedules(engine, apply=False)` following the jira-daily-reports pattern: subprocess invocation of `daily_android_scan` and `daily_ios_scan`, retry logic for transient failures, idempotent registration cache.
- [ ] 2.2 Add unit tests for `register_all_schedules` (mock engine, verify workflow registration, verify idempotency).
- [ ] 2.3 Update `code-daily-scan/scripts/deploy.sh` line 61 to remove reference to `agent_core.scheduler_setup`.
- [ ] 2.4 Run code-daily-scan test suite — confirm green.

## 3. jira-epic-report: Create dbos_scheduling.py

- [ ] 3.1 Create `jira-epic-report/epic_report/dbos_scheduling.py` with `register_all_schedules(engine, apply=False)` wrapping the existing `daily_epic_report` subprocess invocation.
- [ ] 3.2 Add unit tests for `register_all_schedules` (mock engine, verify single schedule registration).
- [ ] 3.3 Update `jira-epic-report/epic_report/cli.py` line ~1478 docstring to remove reference to `agent_core.scheduler_setup.daily_epic_report`.
- [ ] 3.4 Run jira-epic-report test suite — confirm green.

## 4. Update manifest generators

- [ ] 4.1 Update `agent-core/deployments/scheduler/generators/code_daily_scan.py` to emit `register_fn: code_daily_scan.dbos_scheduling:register_all_schedules` instead of `module: agent_core.scheduler_setup` / `function: daily_android_scan`.
- [ ] 4.2 Update `agent-core/deployments/scheduler/generators/jira_epic_report.py` to emit `register_fn: jira_epic_report.dbos_scheduling:register_all_schedules` instead of `module: agent_core.scheduler_setup` / `function: daily_epic_report`.
- [ ] 4.3 Run a dry-run of the manifest generators against a temp dir to confirm correct YAML output for both repos.

## 5. Update YAML manifests (host-side)

- [ ] 5.1 Update `~/.tdt/schedules/code-daily-scan.yaml` to use `register_fn:` pointing to `code_daily_scan.dbos_scheduling:register_all_schedules` (two schedules: daily-android-scan, daily-ios-scan).
- [ ] 5.2 Update `~/.tdt/schedules/jira-epic-report.yaml` to use `register_fn:` pointing to `jira_epic_report.dbos_scheduling:register_all_schedules` (one schedule: daily-epic-report).
- [ ] 5.3 Validate both updated manifests with `tdt_core.scheduler.schedule_manifest.ScheduleManifest.model_validate()`.

## 6. Clean up agent-core (dead code + workflow removal)

- [ ] 6.1 Remove 8 dead functions from `agent-core/src/agent_core/scheduler_setup.py`: `_load_code_daily_scan_config`, `_get_android_config`, `_get_ios_config`, `_platform_scan_command`, `_run_platform_scan`, `daily_android_scan`, `daily_ios_scan`, `_PLATFORM_SHEET_ENV` dict, and `_android_config`/`_ios_config` globals. (~180 lines)
- [ ] 6.2 Remove `daily_epic_report` and `_run_epic_report` from `agent-core/src/agent_core/scheduler_setup.py` (moved to jira-epic-report).
- [ ] 6.3 Remove the `stale_workflow_cleaner` decorator and its function body from `agent-core/src/agent_core/scheduler_setup.py` (moved to tdt-core).
- [ ] 6.4 Remove `_current_application_version_for_cleanup` from `agent-core/src/agent_core/scheduler_setup.py` (moved to tdt-core maintenance).
- [ ] 6.5 Remove `sys.path.insert` blocks for code-daily-scan/jira-daily-reports from `agent-core/src/agent_core/scheduler_setup.py`.
- [ ] 6.6 Remove `cancel_stale_error_workflows` and `cancel_stale_enqueued_workflows` imports from `agent-core/src/agent_core/scheduler_setup.py`.
- [ ] 6.7 Remove `agent-core/scripts/generate_schedule_manifest.py` (the `@_ENGINE` decorator parser) — obsolete once stale_workflow_cleaner moves to tdt-core.
- [ ] 6.8 Update the module docstring in `agent-core/src/agent_core/scheduler_setup.py` to reflect reduced scope (YAML manifest bootstrap only).
- [ ] 6.9 Run ruff I001 + ruff format + mypy strict on agent-core — confirm clean.
- [ ] 6.10 Run agent-core test suite — confirm green.

## 7. Simplify Docker build

- [ ] 7.1 Review `agent-core/deployments/scheduler/Dockerfile` for COPY blocks that can be removed now that agent-core no longer imports sibling repos. Keep bind-mount volumes in compose.yaml (generators still need them).
- [ ] 7.2 Update `agent-core/deployments/scheduler/entrypoint.sh` if any PYTHONPATH adjustments are needed after the cleanup.
- [ ] 7.3 Build the scheduler Docker image (`docker compose build scheduler`) — confirm it builds successfully.

## 8. Update stale docstrings across repos

- [ ] 8.1 Update `jira-daily-reports/docs/dev-performance-rollout.md` lines ~20, ~33, ~82 to remove `agent_core.scheduler_setup` references.
- [ ] 8.2 Update `jira-daily-reports/src/jira_daily_reports/dbos_scheduling.py` lines ~108, ~127 comment referencing `agent_core.scheduler_setup._run_platform_scan`.
- [ ] 8.3 Update `jira-daily-reports/tests/test_dbos_scheduling_dispatch.py` line ~87 docstring.
- [ ] 8.4 Update `webhook-receiver/src/webhook_receiver/dbos_scheduling.py` line ~14 docstring.
- [ ] 8.5 Update `webhook-receiver/src/webhook_receiver/dlq_reaper_cli.py` line ~3 docstring.
- [ ] 8.6 Update `webhook-receiver/src/webhook_receiver/scan_recent_mr_cli.py` line ~3 docstring.
- [ ] 8.7 Update `webhook-receiver/src/webhook_receiver/selftest_cli.py` line ~3 docstring.
- [ ] 8.8 Update `ops-automation-suite/AGENTS.md` line ~8 referencing agent-core scheduler_setup patterns.
- [ ] 8.9 Cross-repo verification: `grep -rn "agent_core.scheduler_setup" /Users/androidteam/Developer/` (excluding .venv, __pycache__, node_modules, archived OpenSpec changes) to confirm zero stale references remain.

## 9. Integration verification

- [ ] 9.1 Start the scheduler container (`docker compose up -d scheduler`) and wait for health check.
- [ ] 9.2 Verify via `curl http://127.0.0.1:9100/scheduler/schedules` that all expected schedules are registered: `stale_workflow_cleaner`, `daily-android-scan`, `daily-ios-scan`, `daily-epic-report`, plus the existing jira-daily-reports schedules (`jira-standup`, `jira-run-all`, etc.) and other pre-existing schedules.
- [ ] 9.3 Verify that `stale_workflow_cleaner` fires correctly by checking DBOS logs for its next run time.
- [ ] 9.4 Run a manual scan test (`code-daily-scan scan --platform android`) to confirm the subprocess invocation still works through the register_fn path.

## 10. Commit and archive

- [ ] 10.1 Commit code-daily-scan changes with descriptive message.
- [ ] 10.2 Commit jira-epic-report changes with descriptive message.
- [ ] 10.3 Commit tdt-core changes with descriptive message.
- [ ] 10.4 Commit agent-core changes with descriptive message.
- [ ] 10.5 Commit docstring updates in jira-daily-reports, webhook-receiver, ops-automation-suite.
- [ ] 10.6 Commit openspec-store change (proposal, specs, design, tasks).
- [ ] 10.7 Validate the change: `openspec validate decouple-scheduler-workflows-from-agent-core --strict --store openspec-store`.
- [ ] 10.8 Archive the change.

## Dependency order

Groups have implicit ordering constraints. The recommended execution order is:

```
Group 1 (tdt-core: stale_workflow_cleaner + CLI)
  ↓
Group 2 (code-daily-scan: dbos_scheduling)  ─┐
Group 3 (jira-epic-report: dbos_scheduling) ─┤ (independent)
                                              ↓
Group 4 (manifest generators)              ← depends on 2-3
Group 5 (YAML manifests)                   ← depends on 4
Group 6 (agent-core cleanup)               ← depends on 1
Group 7 (Docker build)                     ← depends on 4-5-6
Group 8 (docstring updates)                ← independent
Group 9 (integration verification)         ← depends on 7
Group 10 (commit and archive)              ← depends on all
```

Critical path: 1 → 2/3 → 4 → 5 → 7 → 9 → 10
