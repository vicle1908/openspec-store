# Design — fix-jira-scheduler-dispatch-cwd

## Context

`jira-daily-reports` is the only workload repo in the TDT ecosystem whose
scheduled-workflow dispatcher uses a `uv run` shortcut. Every other
workload dispatcher (`agent-core/scheduler_setup.py::_run_webhook_selftest`,
`_run_dlq_reaper`, `_run_coverage_scan`, `_run_jira_ticket_analysis`,
`_run_platform_scan`, `_run_scan_recent_mrs`) uses the canonical pattern:

```python
cmd = [sys.executable, "-m", "<package>", "..."]
env = os.environ.copy()
env["PYTHONPATH"] = ":".join([str(src_dir), env.get("PYTHONPATH", "")])
subprocess.run(cmd, cwd=str(src_dir), env=env, check=True)
```

The jira-daily-reports dispatcher was a `uv run` shortcut that worked
under the host workstation (where `uv` resolves to the local project
`.venv`), but it breaks inside the Docker scheduler container because:

1. The Dockerfile pins `UV_PROJECT_ENVIRONMENT=/opt/scheduler/.venv`.
2. That venv is built from `agent-core/pyproject.toml`, with
   `jira-daily-reports/src` injected via `sys.path` from
   `_add_workload_repos_to_sys_path` — not installed as a package.
3. `cwd="/workspace/agent-core"` makes `uv run` walk up to
   `agent-core/pyproject.toml`, but `UV_PROJECT_ENVIRONMENT` overrides the
   resulting venv path, so the subprocess boots
   `/opt/scheduler/.venv/bin/python3 -m jira_daily_reports sprint-sheet`,
   which exits 1 with `No module named jira_daily_reports`.

## Goals / Non-Goals

**Goals:**
- One function rewrite in `jira_daily_reports/dbos_scheduling.py` that
  uses the canonical pattern (`sys.executable -m jira_daily_reports …`).
- Lock the contract with a unit test that mocks `subprocess.run` and
  asserts the command shape, env forwarding, and absence of `uv`.
- Rebuild the scheduler image, restart the container, and verify the
  freshness state file updates.

**Non-Goals:**
- Changing `tdt-core` scheduler code.
- Changing the scheduler Dockerfile (no new COPY instructions; the
  source mount is unchanged).
- Changing how schedules are registered (the registration code is
  correct; only the workflow body invocation is broken).

## Decisions

### D1: Use `sys.executable -m jira_daily_reports` + PYTHONPATH injection

**Choice:** Match the canonical pattern in `agent-core/scheduler_setup.py`:
invoke `sys.executable -m jira_daily_reports <cmd>` and inject
`PYTHONPATH=/workspace/jira-daily-reports/src` into the spawned env.

**Why:** The scheduler venv (`/opt/scheduler/.venv`) is built from
`agent-core/pyproject.toml`. `jira-daily-reports/src` is `COPY`ed into
the image (line 42 of `agent-core/deployments/scheduler/Dockerfile`)
but is NOT registered as an editable install, so it is not on the
venv's `sys.path` by default. Without `PYTHONPATH` injection,
`python -m jira_daily_reports` exits 1 with
`No module named jira_daily_reports`.

**Alternatives considered:**
- `pip install -e /workspace/jira-daily-reports` into the scheduler venv
  at build time: rejected — duplicates state. The source mount is
  already in place at runtime; an editable install would force a
  re-install on every rebuild and bloat the image.
- Add `jira-daily-reports` as a `uv` dependency of `agent-core`:
  rejected — cross-cutting change that affects every consumer of
  `agent-core` (webhook-receiver, ai-review). Higher blast radius
  for a single workload's scheduler dispatch fix.
- Fix `cwd` to `/workspace/jira-daily-reports` and keep `uv run`:
  rejected — `UV_PROJECT_ENVIRONMENT` still overrides the resolved venv
  path; we'd just shift the failure mode. The fact that `uv run` would
  need to be paired with `unset UV_PROJECT_ENVIRONMENT` is a fragile
  workaround compared to using `sys.executable` directly with an
  explicit `PYTHONPATH`.

### D2: Drop `_find_uv` and `_repo_dir` helpers

**Choice:** Remove `_find_uv` (no longer called) and `_repo_dir`
(unused outside this path).

**Why:** Both helpers exist solely to support the `uv run …` shortcut.
After D1 they're dead code. Keeping them invites future regressions.

### D3: Test with `subprocess.run` mock

**Choice:** Mock `subprocess.run` and assert the call shape.

**Why:** The contract is "build this exact command list, forward these
exact env vars, don't shell out via uv". A mock-based test pins the
contract without needing a live venv or jira-daily-reports install.

**Alternatives considered:**
- End-to-end test that runs `_run_report` against a real Jira API:
  rejected — that's an integration test, lives elsewhere (manual
  verification in the `Verification plan` of the proposal).
- Subprocess test that asserts a `jira_daily_reports` import resolves
  inside the spawned process: rejected — environment-dependent,
  flaky in CI.

### D4: Add a degraded-state healthcheck follow-up

**Choice:** Log it as Task 5 in `tasks.md`; do not implement in this
change.

**Why:** The `/scheduler/health` endpoint returns 200 even when the
latest `jira-sprint-sheet` workflow is `FAILED`. That's a real operator
blind spot, but it's a separate concern from the dispatch fix. Mixing
them would obscure the root-cause story and inflate the change scope.

## Risks / Trade-offs

- **[Risk] Other workflows may also break in production** → **Mitigation:**
  All 15 jira-* workflows share `_run_report`; the fix repairs all of
  them in one shot. Manual trigger of each schedule will be exercised
  in the verification plan.
- **[Risk] Container restart interrupts in-flight webhook coverage scan**
  → **Mitigation:** The coverage-scan workflow is registered with
  `automatic_backfill=False` and is non-blocking; the next 10-minute
  tick resumes normal operation. Acceptable.
- **[Trade-off] Test for `_run_report` lives next to the function it
  tests, not in `tests/test_dbos_scheduling.py`** → Decision: create
  `tests/test_dbos_scheduling_dispatch.py` for clarity, since the test
  is specifically about the dispatch contract (not scheduling
  registration, which has its own tests in `tests/cli/test_schedule.py`).
- **[Risk] Future refactor reintroduces `uv run …`** → **Mitigation:**
  D3 test asserts absence of `uv` in the command list.

## Migration Plan

1. Merge this OpenSpec change into the repo (proposal + design + tasks
   + spec delta).
2. Apply the code fix in `dbos_scheduling.py::_run_report`.
3. Add the unit test in `tests/test_dbos_scheduling_dispatch.py`.
4. Run pytest locally — new test passes; existing 63 capacity tests
   still pass.
5. `docker compose -f agent-core/compose.yaml build scheduler` (rebuilds
   the scheduler image with the new `dbos_scheduling.py`).
6. `docker compose -f agent-core/compose.yaml up -d scheduler` (restarts
   the container; new dispatch code is loaded).
7. Wait ≤120s for healthcheck.
8. `curl -X POST http://127.0.0.1:9100/scheduler/schedules/jira-sprint-sheet/trigger`.
9. Read freshness state file — confirm `refreshed_at` is within the
   last 5 minutes.
10. `docker logs --tail 100 agent-core-local-scheduler-1 | grep
    jira-sprint-sheet` — confirm `.succeeded` (or no `.failed`).

## Open Questions

- **Resolved:** Use `sys.executable -m jira_daily_reports` (D1).
- **Resolved:** Mock-based test for the dispatch contract (D3).
- **Resolved:** Degraded-state healthcheck is a separate change (D4).
- **Deferred:** DBOS `workflow_schedules` persistence gap — needs
  separate investigation; not blocking this change.