# Fix jira-daily-reports scheduler dispatch cwd

## Why

`jira_daily_reports.scheduler_setup.register_all_schedules()` registers 15
`jira-*` scheduled workflows on the shared DBOS engine owned by the Docker
`tdt-scheduler` container (`agent-core/compose.yaml`). Every workflow body
calls `jira_daily_reports.dbos_scheduling._run_report()`, which executes the
report CLI via `subprocess.run([uv, run, python, -m, jira_daily_reports,
…], cwd="/workspace/agent-core", env=env, check=True)`.

This dispatch is broken in the scheduler container:

1. `cwd="/workspace/agent-core"` resolves to `agent-core`'s `pyproject.toml`,
   not `jira-daily-reports`'s.
2. The scheduler Dockerfile pins `UV_PROJECT_ENVIRONMENT=/opt/scheduler/.venv`
   (`agent-core/deployments/scheduler/Dockerfile` line 16), so `uv run` from
   any cwd resolves to the scheduler venv regardless of which `pyproject.toml`
   it finds.
3. The scheduler venv (`/opt/scheduler/.venv`) is built from
   `agent-core/pyproject.toml` and has `jira-daily-reports/src` on `sys.path`
   (via `_add_workload_repos_to_sys_path` in
   `tdt-core/src/tdt_core/scheduler/cli.py`), but it does not have
   `jira_daily_reports` installed as a package — so
   `python -m jira_daily_reports` exits 1 with
   `No module named jira_daily_reports`.

Observed symptom: every `jira-sprint-sheet` cron tick has exited 1 since
2026-07-02 03:30 UTC (container start). The freshness state file
`~/.tdt/state/jira-daily-reports/freshness/1o5AJA589GElhqwACZn6v5uvFsVfruF25YS9Y_0LJhcw.json`
last refreshed `2026-06-30T17:00:33Z` — **48+ hours stale** as of this
change. The same failure applies to all 14 other jira-* workflows; only
`sprint-sheet` is visibly broken because it has a freshness state file we
can spot-check.

## What Changes

1. **`jira_daily_reports/dbos_scheduling.py::_run_report`** — replace the
   `uv run …` shortcut with `sys.executable -m jira_daily_reports …`,
   AND inject `PYTHONPATH=/workspace/jira-daily-reports/src` into the
   spawned environment. The scheduler venv (`/opt/scheduler/.venv`,
   built from `agent-core/pyproject.toml`) does NOT have
   `jira_daily_reports` installed as a package — the source is
   `COPY`ed into the image (`agent-core/deployments/scheduler/Dockerfile`
   line 42) but not registered with `uv` as an editable install, so it
   is not on `sys.path` by default. Without `PYTHONPATH` injection,
   `python -m jira_daily_reports` exits 1 with
   `No module named jira_daily_reports`. The `PYTHONPATH` injection
   mirrors the canonical pattern in
   `agent-core/scheduler_setup.py::_run_webhook_selftest` and siblings,
   which inject `PYTHONPATH` pointing at the workload repo's `src/`
   directory. Drop the now-unused `_find_uv` and `_repo_dir` helpers.
2. **Unit test** — `jira-daily-reports/tests/test_dbos_scheduling_dispatch.py`
   mocks `subprocess.run` and asserts `_run_report` builds the
   `sys.executable -m jira_daily_reports <cmd>` command, forwards env vars,
   and does NOT call `uv`. Locks in the contract so a future refactor can't
   reintroduce the broken `uv run … cwd=/workspace/agent-core` shortcut.
3. **Container rebuild** — the source mount for `jira-daily-reports/src` is
   `:ro` (`agent-core/compose.yaml` line 144), so the fix must be baked
   into the scheduler image via
   `docker compose -f agent-core/compose.yaml build scheduler`.
4. **Container restart + live trigger** — restart the scheduler container,
   then `POST /scheduler/schedules/jira-sprint-sheet/trigger` and verify
   the freshness state file updates.
5. **Degraded-state healthcheck follow-up** (separate task; not implemented
   in this change): the `/scheduler/health` endpoint currently returns 200
   even when the latest `jira-sprint-sheet` workflow is `FAILED`. Add a
   `latest_jira_sprint_sheet_status` field that surfaces
   `dbos.workflow_status.status` for the most recent run.

## Capabilities

### New Capabilities

- `jira-scheduler-dispatch-contract`: the canonical pattern for invoking
  `jira-daily-reports` CLIs from the `tdt-scheduler` container — use
  `sys.executable -m jira_daily_reports …` from the scheduler venv,
  injecting `PYTHONPATH=/workspace/jira-daily-reports/src` so the
  spawned process can resolve the module.

### Updated Capabilities (ADDED delta)

- `scheduler-engine`: `dbos.workflow_schedules` persistence gap is logged
  as a follow-up. (No code change in this delta — observation only.)

## Impact

- **Affected code**: `jira-daily-reports/src/jira_daily_reports/dbos_scheduling.py`
  (single function rewrite).
- **Affected tests**: new file
  `jira-daily-reports/tests/test_dbos_scheduling_dispatch.py` (3-4 scenarios).
- **Affected deploys**: scheduler image rebuild + container restart. The
  scheduler Dockerfile does not change — `jira-daily-reports/src` is already
  `COPY`-baked at line 42 of `agent-core/deployments/scheduler/Dockerfile`.
- **Affected specs**: `tdt-meta/openspec/specs/scheduler/spec.md` (engine
  contract) — gain a scenario covering the dispatch pattern.
- **No new secrets, no new env vars.**
- **No data migration**: DBOS state is unchanged.
- **No breaking change**: the wire-level behaviour of `jira-daily-reports`
  CLIs is unchanged — only how the scheduler container invokes them.

## Non-Goals

- Fixing the `dbos.workflow_schedules` persistence gap (cron specs are
  stored in the in-process registry only; not persisted to Postgres).
  Tracked as a separate observation; needs a deeper look at the DBOS
  engine version + `apply_schedules` path.
- Migrating the scheduler off the Docker container onto a host LaunchAgent.
  The Docker scheduler is the canonical owner per
  `centralized-scheduling-module` Decision 4; this change is a minimum
  patch to its dispatch layer.
- Restoring the `2026-06-30` freshness state — there is none to restore
  beyond what the next `sprint-sheet` run writes. Operators who need data
  between `2026-06-30` and now can re-trigger manually.
- Adding `schedules_applied` to the scheduler `/health` body (already
  present in `webhook-receiver` and `ai-review`; the scheduler is the
  owner so the field is redundant).

## Verification plan

1. `cd jira-daily-reports && uv run pytest tests/test_dbos_scheduling_dispatch.py -v`
   — new tests pass.
2. `uv run pytest tests/person_capacity/ -v` — 63 existing capacity tests
   still pass (no regressions).
3. `uv run ruff check src/jira_daily_reports/dbos_scheduling.py tests/test_dbos_scheduling_dispatch.py`
   — clean.
4. `uv run mypy src/jira_daily_reports/dbos_scheduling.py` — clean.
5. `docker compose -f agent-core/compose.yaml build scheduler` — image
   built with the new `dbos_scheduling.py`.
6. `docker compose -f agent-core/compose.yaml up -d scheduler` — container
   restarted.
7. Wait ≤120s for healthcheck (`start_period: 120s`).
8. `curl -X POST http://127.0.0.1:9100/scheduler/schedules/jira-sprint-sheet/trigger`
   — manual trigger.
9. Read back `~/.tdt/state/jira-daily-reports/freshness/1o5AJA589GElhqwACZn6v5uvFsVfruF25YS9Y_0LJhcw.json`
   — `refreshed_at` should be within the last 5 minutes.
10. `docker logs --tail 100 agent-core-local-scheduler-1 | grep
    'jira-sprint-sheet'` — last 3 entries should be
    `scheduler.workflow.succeeded` (or absence of `.failed`), not
    `scheduler.workflow.failed`.
11. `openspec validate fix-jira-scheduler-dispatch-cwd --strict` — exits 0.

## Rollback

The fix is one function in one file. Rollback = `git revert` of the
`dbos_scheduling.py` commit + scheduler image rebuild + container restart.
The previous behaviour (broken `uv run …`) returns immediately.