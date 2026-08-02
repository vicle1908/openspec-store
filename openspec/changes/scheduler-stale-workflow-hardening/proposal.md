## Why

Three related operational issues prevent the DBOS scheduler from self-healing in
the TDT ecosystem. Each was discovered in production logs during deployment
verification of the `schedule-registry-independent-deployment` umbrella change:

1. **Recurring `daily_android_scan` / `daily_ios_scan` ERROR rows** with
   `CalledProcessError: Command 'git worktree add ...' returned non-zero exit
   status 128` accumulate in `dbos.workflow_status` every day at 00:00 UTC.
   The `git worktree add` call fails inside the Docker scheduler container
   because the bind-mounted `~/.git/worktrees/` is read-only. The existing
   `worktree-resilience-and-timeouts` OpenSpec change (✓ Complete) added a
   writability probe that catches this case for many invocations — but when the
   probe succeeds (the bind-mount IS writable in this environment) `git
   worktree add` still fails for unrelated reasons (stale lock, branch
   resolution, etc.) and the error is captured with **no stderr text** because
   `_default_command_runner` calls `subprocess.run(check=True)` without
   surfacing the captured `stderr` in the re-raised exception. Operators have
   no way to diagnose why the scan is failing on any given day.

2. **Default `error_class_names` filter in
   `tdt_core.scheduler.cli._cancel_stale_error_workflows` is too narrow.** It
   only matches `ModuleNotFoundError`, `AttributeError`, `ImportError`, and
   `UnpicklingError`. Real-world stale errors include `FileNotFoundError`
   (mounted source tree missing), `OSError` (filesystem errors),
   `subprocess.CalledProcessError` (worktree failures), and
   `subprocess.SubprocessError` (any subprocess error). When such errors
   accumulate, the canonical cleanup command `tdt-scheduler cancel-stale-errors`
   silently skips them — operators must hand-write Python one-liners to clear
   them, as happened during this session's verification (258 stale ERROR
   rows were cleared manually).

3. **`dbos-stale-workflow-auto-cleanup` (✓ Complete, archived 2026-06-28)**
   claimed to register a `_stale_workflow_cleaner` DBOS scheduled workflow
   firing every 30 minutes, but the implementation never landed — the
   cleanup function is only invoked once at scheduler startup (`cli.py:780`)
   and is **not** registered as a recurring cron. The README at
   `tdt-core/src/tdt_core/scheduler/README.md:99` explicitly acknowledges
   "Cleanup is **NOT** scheduled to run periodically (no `*/30 * * * *`
   schedule exists)." The change was mis-archived as Complete; operators
   who relied on the documented self-healing behaviour are still doing
   manual cleanup every 6–8 hours.

This change closes all three gaps as one logical unit — they're all facets
of the same underlying need: **make the scheduler self-healing without
requiring operator intervention**.

## What Changes

### 1. Capture and surface stderr from `git worktree add` failures
`WorktreeManager._default_command_runner` in
`code-daily-scan/src/code_daily_scan/scanners/worktree.py` will capture
`stderr` and include it in the `CalledProcessError` message so operators
see the actual git error (`fatal: invalid reference`, `fatal: cannot
use as worktree`, etc.) instead of a bare exit code. The downstream
`create()` exception chain remains a `RuntimeError` so the outer CLI
behaviour is unchanged.

### 2. Extend default `error_class_names` filter
`tdt_core.scheduler.cli._cancel_stale_error_workflows` will default its
`error_class_names` tuple to:
```python
(
    "ModuleNotFoundError",
    "AttributeError",
    "ImportError",
    "UnpicklingError",
    "FileNotFoundError",
    "OSError",
    "subprocess.CalledProcessError",
    "subprocess.SubprocessError",
)
```
The change is backwards-compatible: callers passing their own tuple
override the default.

### 3. Register `_stale_workflow_cleaner` scheduled workflow
A new `@_ENGINE.scheduled_workflow(cron="*/30 * * * *",
cron_timezone="UTC", name="stale_workflow_cleaner")` will be added in
`agent-core/src/agent_core/scheduler_setup.py`, calling the existing
internal `_cancel_stale_error_workflows` and
`_cancel_stale_enqueued_workflows` helpers from
`tdt_core.scheduler.cli`. The schedule is registered alongside
`daily_android_scan` / `daily_ios_scan` in the same module. To make the
helpers accessible across the package boundary, they are renamed from
the underscore-prefixed private form to a public module-level function
(`cancel_stale_error_workflows` / `cancel_stale_enqueued_workflows`)
in `tdt-core/src/tdt_core/scheduler/cli.py`. The CLI subcommands
(`tdt-scheduler cancel-stale-errors`, `cancel-orphan-enqueued`) continue
to work via thin wrappers that call the now-public functions.

A YAML schedule manifest entry is **NOT** added — `agent-core` registers
scheduled workflows via the `@_ENGINE.scheduled_workflow` decorator per
existing convention (`centralized-scheduling-module` Decision 4), and
the decorator's `automatic_backfill=false` semantics match the cleanup
intent.

## Capabilities

### New Capabilities

- `stale-workflow-cleaner-scheduled`: A DBOS `@scheduled_workflow` named
  `stale_workflow_cleaner` fires every 30 minutes inside the Docker
  `tdt-scheduler:local` container. It runs the existing
  `cancel_stale_error_workflows` and `cancel_stale_enqueued_workflows`
  cleanup functions against the shared `dbos.workflow_status` table.

### Modified Capabilities

- `scheduler-engine`: The existing `scheduler-engine` capability
  (defined in `fix-app-services-apply-schedules`) is extended with a new
  scheduled workflow registration. The `apply_schedules()` ownership
  guard (only `app_name=tdt-scheduler` may call it) is respected.

- `code-daily-scan-core`: The existing `WorktreeManager._default_command_runner`
  surface is modified to include `stderr` in raised `CalledProcessError`
  messages. External CLI behaviour is unchanged — only the diagnostic
  detail improves.

- `scheduler-cli`: The existing `scheduler-cli` capability
  (`openspec/specs/scheduler-cli/spec.md`) is extended: the
  `_cancel_stale_error_workflows` and `_cancel_stale_enqueued_workflows`
  helpers are renamed to public module-level names
  (`cancel_stale_error_workflows`, `cancel_stale_enqueued_workflows`), and
  the default `error_class_names` tuple is extended to include
  `FileNotFoundError`, `OSError`, `subprocess.CalledProcessError`, and
  `subprocess.SubprocessError`. Backwards-compatible — the legacy names
  remain as thin delegating wrappers.
  **See `specs/scheduler-cli/spec.md` for the formal MODIFIED Requirements.**

## Impact

- **tdt-core**: rename `_cancel_stale_error_workflows` →
  `cancel_stale_error_workflows` (public), extend default
  `error_class_names`, update internal callers and tests.
- **agent-core**: register `_stale_workflow_cleaner` decorator in
  `scheduler_setup.py`, import the now-public cleanup functions from
  `tdt_core.scheduler.cli`.
- **code-daily-scan**: update `WorktreeManager._default_command_runner`
  to surface stderr; add a unit test asserting stderr appears in the
  raised `CalledProcessError` message.
- **no changes** to `webhook-receiver`, `ai-review`, `tdt-meta`, or any
  deployed service beyond the scheduler container restart.
- **Database**: Reads `dbos.workflow_status`; updates `status` to
  `CANCELLED` for matching rows. Existing behavior preserved.
- **No new dependencies**.

## Non-Goals

- We do NOT add a YAML schedule manifest entry for the cleaner — the
  decorator-based registration in `agent-core` follows the existing
  `centralized-scheduling-module` Decision 4.
- We do NOT modify the DBOS library, the `apply_schedules()` ownership
  contract, or the DBOS queue name resolution.
- We do NOT add a retry loop for `git worktree add` failures inside
  `code-daily-scan` — the operator-facing fix is the stderr surfacing;
  the auto-cleanup handles the resulting ERROR rows.
- We do NOT change the cleanup cadence (30 minutes) — that matches the
  documented (but not implemented) intent of the mis-archived
  `dbos-stale-workflow-auto-cleanup` change.
- We do NOT add proactive health-check or service-restart watchdog
  functionality — separate concern tracked as open follow-up.

## Execution Readiness (validated 2026-07-07)

This change has been validated against the current source tree and is
ready for execution. The 21 tasks map cleanly to existing code paths:

| Task cluster | Repo | Key file | Verified |
|--------------|------|----------|---------|
| 1.1-1.4 rename + filter | `tdt-core` | `src/tdt_core/scheduler/cli.py:305` | ✅ function exists, callers at line 780-781 and line 1032 |
| 1.5 new test | `tdt-core` | `tests/scheduler/test_cli.py` | ✅ `fake_sa` fixture pattern at line 320-328 |
| 2.1-2.3 new scheduled workflow | `agent-core` | `src/agent_core/scheduler_setup.py` | ✅ `_ENGINE = get_engine()` at line 52, decorator pattern at line 277 (`@_dbos.DBOS.workflow()` is the existing precedent) |
| 2.4-2.5 new tests | `agent-core` | `tests/test_scheduler_setup.py` | ✅ `MagicMock` engine stub at line 21-24 |
| 3.1 stderr surfacing | `code-daily-scan` | `src/code_daily_scan/scanners/worktree.py:280` | ✅ existing `raise RuntimeError(...)` at the `git worktree add` site is the wrapper location |
| 3.2 new test | `code-daily-scan` | `tests/test_worktree_manager.py` | ✅ `FakeRunner` base class at line 19 with `fail_on_add` already wired |
| 4.1-4.5 deploy + smoke | host | Docker scheduler | ✅ container running healthy, scheduler `/health` endpoint accessible at `:9100` |

**Backward compatibility:** Tasks 1.1 and 1.2 keep the underscore-prefixed
names as thin wrappers, so:
- `tdt-scheduler cancel-stale-errors` CLI subcommand continues to work
- `tdt-core/tests/scheduler/test_cli.py:208-209` and
  `test_serve_health_listener.py:83-84` (which monkeypatch the
  underscore-prefixed names) keep working

**Risk: LOW.** The change is additive (new public names + new scheduled
workflow + better error message). The only renames are internal helpers
that have no third-party consumers (verified by grep across the
multirepo).