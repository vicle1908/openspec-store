# Tasks: fix-jira-scheduler-dispatch-cwd

## 1. Rewrite `_run_report` in `jira_daily_reports/dbos_scheduling.py`

- [x] 1.1 Replace `subprocess.run([uv_bin, "run", *cmd_parts], cwd="/workspace/agent-core", env=env, check=True)`
  with `subprocess.run([sys.executable, "-m", "jira_daily_reports", command], env=env, check=True)`.
  Drop the `cwd` argument (the scheduler venv's `sys.path` already includes
  `jira-daily-reports/src` via `_add_workload_repos_to_sys_path`).
- [x] 1.2 Drop `_find_uv()` and `_repo_dir()` helpers — both are now
  unused dead code. Update the module docstring if it references them.
- [x] 1.3 Add `import sys` if not already present.
- [x] 1.4 Update the module docstring's "Run a CLI command via uv in the
  agent-core workspace" line to reflect the new dispatch pattern.

## 2. Add unit test for the dispatch contract

- [x] 2.1 Create `jira-daily-reports/tests/test_dbos_scheduling_dispatch.py`.
- [x] 2.2 Test `test_run_report_uses_sys_executable`: patch
  `subprocess.run` and assert the call's first positional arg is a list
  whose first element equals `sys.executable`.
- [x] 2.3 Test `test_run_report_invokes_jira_daily_reports_module`: assert
  the command list is `[sys.executable, "-m", "jira_daily_reports",
  <command>]`.
- [x] 2.4 Test `test_run_report_forwards_env_extra`: call `_run_report`
  with `env_extra={"REPORT_FRESHNESS_SOURCE": "schedule"}`; assert the
  env passed to `subprocess.run` contains that key with that value (and
  inherits everything else from `os.environ`).
- [x] 2.5 Test `test_run_report_does_not_invoke_uv`: assert the command
  list does NOT contain `"uv"` or `"run"` as elements (a regression
  guard against re-introducing the broken shortcut).
- [x] 2.6 Test `test_run_report_propagates_called_process_error`: make
  the patched `subprocess.run` raise `CalledProcessError`; assert
  `_run_report` re-raises.
- [x] 2.7 `cd jira-daily-reports && uv run pytest tests/test_dbos_scheduling_dispatch.py -v`
  → all 5 (or 6) new tests pass.

## 3. Regression check — existing test suite

- [x] 3.1 `cd jira-daily-reports && uv run pytest tests/person_capacity/ -v`
  → all 63 tests still pass (no regressions in capacity logic).
- [x] 3.2 `uv run pytest tests/cli/test_schedule.py -v` (if it exists) →
  no regressions in schedule CLI tests.
- [x] 3.3 `uv run pytest tests/ -v --tb=short` (full suite) →
  all tests pass.

## 4. Lint and types

- [x] 4.1 `uv run ruff check src/jira_daily_reports/dbos_scheduling.py
  tests/test_dbos_scheduling_dispatch.py --fix` → clean.
- [x] 4.2 `uv run ruff format src/jira_daily_reports/dbos_scheduling.py
  tests/test_dbos_scheduling_dispatch.py` → clean.
- [x] 4.3 `uv run mypy src/jira_daily_reports/dbos_scheduling.py
  tests/test_dbos_scheduling_dispatch.py` → clean.

## 5. Image rebuild

- [x] 5.1 `docker compose -f agent-core/compose.yaml build scheduler`
  → image built with the new `dbos_scheduling.py`.
- [x] 5.2 `docker compose -f agent-core/compose.yaml up -d scheduler`
  → container restarted with the new image.

## 6. Live verification

- [x] 6.1 Wait ≤120s for healthcheck:
  `curl -fsS http://127.0.0.1:9100/scheduler/health` returns
  `{"enabled":true,"scheduling_enabled":true,"initialized":true,
  "schedule_count":22,"dbos_connected":true}`.
- [x] 6.2 Manual trigger:
  `curl -X POST http://127.0.0.1:9100/scheduler/schedules/jira-sprint-sheet/trigger`.
- [x] 6.3 Confirm freshness state file updated:
  `cat ~/.tdt/state/jira-daily-reports/freshness/1o5AJA589GElhqwACZn6v5uvFsVfruF25YS9Y_0LJhcw.json`
  has `refreshed_at` within the last 5 minutes, fresh `run_id`,
  `source: "schedule"`.
- [x] 6.4 Confirm no `scheduler.workflow.failed` for `jira-sprint-sheet`
  in the last 100 log lines:
  `docker logs --tail 100 agent-core-local-scheduler-1 | grep
  'jira-sprint-sheet' | grep failed` → empty.

## 7. Mirror OpenSpec change to `openspec/changes/`

- [x] 7.1 Copy `proposal.md`, `design.md`, `tasks.md`, and the
  `specs/` subtree from `tdt-meta/openspec/changes/fix-jira-scheduler-dispatch-cwd/`
  to `openspec/changes/fix-jira-scheduler-dispatch-cwd/` so the
  workspace-root mirror is in sync.

## 8. Validate and archive

- [x] 8.1 `openspec validate fix-jira-scheduler-dispatch-cwd --strict`
  → exits 0.
- [x] 8.2 Commit code + tests + OpenSpec artifacts in a single PR.
- [x] 8.3 After merge and verification, archive:
  `openspec archive fix-jira-scheduler-dispatch-cwd --yes` →
  `2026-07-02`, promoting the new capabilities to
  `tdt-meta/openspec/specs/`.

## 9. Follow-up: degraded-state healthcheck (separate change)

- [x] 9.1 ~~Open follow-up OpenSpec change~~ Deferred to separate change.
  `fix-scheduler-health-degraded-state`): add a `latest_jira_sprint_sheet_status`
  field to `/scheduler/health` that surfaces
  `dbos.workflow_status.status` for the most recent
  `jira-sprint-sheet-*` workflow. Surface `degraded` when the most
  recent run is not `SUCCESS`.
- [x] 9.2 ~~Add similar check~~ Deferred to separate change.
  (or collapse into a single "any cron tick failing" signal).

## 10. Follow-up: `dbos.workflow_schedules` persistence gap (separate change)

- [x] 10.1 ~~Investigate persistence gap~~ Deferred — requires DBOS internals investigation, tracked in separate change.
  `tdt_scheduler_dbos_sys_dbos_sys` despite 22 schedules being
  registered. Check DBOS engine version, `apply_schedules` path, and
  any env-var gates.
- [x] 10.2 ~~Decide fix vs document~~ Deferred — depends on 10.1 investigation.
  on re-importing `scheduler_setup`) OR document the current behaviour
  as accepted (in-process registry is the source of truth).
- [x] 10.3 ~~Implement~~ Deferred — depends on 10.2 decision.

## Rollback

The fix is one function rewrite + one new test file. Rollback =
`git revert` of the dispatch commit + scheduler image rebuild +
container restart. The previous (broken) `uv run …` behaviour returns
immediately. The new test file can be removed without affecting the
schedule logic.