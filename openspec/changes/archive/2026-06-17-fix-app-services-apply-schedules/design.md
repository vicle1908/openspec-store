# Design — Stop App Services From Re-Registering Global DBOS Schedules

## Root Cause (recap)

`DBOS` model: there is **one** `workflow_schedules` table per Postgres database.
`apply_schedules()` is the only way to register a cron. There is no built-in ownership
mechanism; the same cron can be registered N times by N processes, and on every tick
**all of them** try to enqueue a workflow instance. Each enqueued instance is tagged with
the originating process's `application_version` (a content hash of the running code) so
DBOS can recover from crashes — but it does not deduplicate across registrations.

Today, three processes call `apply_schedules()`:

| Process | Where | `app_name` | Outcome |
|---------|-------|------------|---------|
| Docker `tdt-scheduler:local` | `agent-core/compose.yaml` | `tdt-scheduler` | ✅ executes all workflows correctly |
| `webhook-receiver` (host) | `com.tdt.webhook-receiver` | `tdt-webhook-receiver` | ❌ registers cron but workflow functions are in `webhook_receiver.*` which IS on its path; succeeds; but creates duplicate ENQUEUED rows |
| `ai-review` (host) | `com.tdt.ai-review` | `tdt-ai-review` | ❌ registers cron; workflow functions like `webhook_receiver.scan_recent_mrs` are NOT on its path → ModuleNotFoundError, marks `degraded=True` on parallel debouncer dispatches |

`webhook-receiver` and `ai-review` are *competing* with the Docker scheduler for the
right to run the same cron set. The Docker scheduler wins the race for *successful*
execution, but the losing registrations still show up as ERROR/ENQUEUED rows in the DBOS
system database and degrade the *application-level* reviews running in ai-review.

The original architectural intent (per `tdt-meta/openspec/changes/centralized-scheduling-module/`)
was: one process owns schedules; the others consume via debouncers. That intent was
correctly implemented in the Docker container, but the *host* services were never told
to stop applying schedules. They kept doing it from before the migration (when
`centralized-scheduling-module` was a draft) and the `app_name` per-service isolation
commit (`f53177d` / `0378e0e`) fixed the *cross-process* dispatch collision but did not
fix the *schedule-owner* collision.

## Design

### 1. Application services: drop `apply_schedules()` from FastAPI lifespan

**`ai-review/src/ai_review/api/app.py`** — current `lifespan` (lines ~70–120) calls
`engine.apply_schedules()` implicitly via the `SchedulerEngine` initialization. We will:

- Keep `engine = SchedulerEngine.from_env()` and `engine.initialize()`.
- Add `if scheduler_settings.app_name == "tdt-scheduler": engine.apply_schedules()` —
  no-op for ai-review (its `app_name` is `tdt-ai-review`).
- Add a structured log `scheduler_engine_initialized` with new field
  `schedules_applied: bool` so operators can confirm at runtime.
- Keep `engine.debouncer(...)` registration unchanged.

**`webhook-receiver/src/webhook_receiver/api/app.py`** — symmetric change.

**Why this shape**: the lifespan code already reads `SchedulerSettings.from_env()` to
make the enabled/disabled decision; extending the same path is one line. We do not
remove the call to `apply_schedules()` — we gate it on `app_name`, so a service that
*is* `tdt-scheduler` (the future host LaunchAgent) can still use the same code path
with no extra code.

### 2. tdt-core: ownership contract + assert

**`tdt-core/src/tdt_core/scheduler/engine.py`** — `apply_schedules()` gains an
ownership guard at the top:

```python
def apply_schedules(self) -> None:
    if get_bool_env("SCHEDULER_ENFORCE_OWNERSHIP", default=True):
        if self._config.app_name != "tdt-scheduler":
            raise SchedulerContractViolation(
                f"apply_schedules() called by app_name={self._config.app_name!r}; "
                f"only the canonical scheduler (app_name='tdt-scheduler') may "
                f"register global schedules. Set SCHEDULER_ENFORCE_OWNERSHIP=false "
                f"in test fixtures, or remove the apply_schedules() call from your "
                f"service's lifespan."
            )
    # ... existing logic ...
```

The check is **fail-closed** in production. The env var escape hatch keeps the existing
`tdt-scheduler tests/` fixtures working. `SchedulerContractViolation` is a new
`SchedulerError` subclass in the same module.

The Docker `tdt-scheduler:local` is the only process whose `app_name` is
`tdt-scheduler` by default; the host services' launchers set
`SCHEDULER_APP_NAME=tdt-webhook-receiver` and `SCHEDULER_APP_NAME=tdt-ai-review`
respectively (already in their launcher scripts after commit `f53177d` / `0378e0e`).

### 3. tdt-core: new `cancel-orphan-enqueued` CLI

**`tdt-core/src/tdt_core/scheduler/cli.py`** — alongside `cancel-stale-errors`:

```python
@app.command("cancel-orphan-enqueued")
def cancel_orphan_enqueued(
    older_than_hours: int = typer.Option(24, help="..."),
) -> None:
    """Cancel ENQUEUED rows whose application_version is no longer registered.

    Useful after a deploy that retires a code path: DBOS keeps the ENQUEUED
    rows forever and re-fires them on every scheduler tick, even after the
    originating process is gone. This CLI removes them in bulk.
    """
    engine = SchedulerEngine.from_env()
    if not engine.enabled:
        _fail("Scheduler is disabled. Set SCHEDULER_ENABLED=true.")
    system_engine = _create_system_db_engine(engine)
    current_versions = _registered_versions(system_engine)
    count = _cancel_orphan_enqueued(
        system_engine,
        active_versions=current_versions,
        older_than_ms=int((time.time() - older_than_hours * 3600) * 1000),
    )
    _echo({"action": "cancel_orphan_enqueued", "cancelled": count, ...})
```

The new helper `_registered_versions(engine)` returns
`SELECT version_name FROM dbos.application_versions`; `_cancel_orphan_enqueued` runs
the same shape of `UPDATE` we ran by hand on 2026-06-17, parameterized by
`active_versions` and a `created_at` threshold. This is what we should have had
yesterday.

### 4. Tests

`tdt-core/tests/scheduler/test_engine.py` gains:

- `test_apply_schedules_rejects_non_owner_app_name`: with
  `SCHEDULER_ENFORCE_OWNERSHIP=true` and `SCHEDULER_APP_NAME=tdt-ai-review`, calling
  `engine.apply_schedules()` raises `SchedulerContractViolation`.
- `test_apply_schedules_allows_tdt_scheduler`: with `app_name=tdt-scheduler`, the call
  proceeds (against a real or in-memory test DSN).
- `test_apply_schedules_opt_out_via_env`: with
  `SCHEDULER_ENFORCE_OWNERSHIP=false`, the call proceeds regardless of `app_name`.
- `test_cancel_orphan_enqueued_removes_old_rows`: a fixture inserts ENQUEUED rows for
  an unknown `application_version` and verifies they are cancelled while rows for
  registered versions survive.

`ai-review/tests/` gains:

- `test_lifespan_does_not_apply_schedules`: import the lifespan, call it, assert that
  `engine.apply_schedules` is *not* called and that the new `schedules_applied=False`
  log line is emitted.

`webhook-receiver/tests/` gains the symmetric test.

### 5. Observability

Add the `schedules_applied: bool` field to the existing
`scheduler_engine_initialized` structlog event in both `ai-review` and
`webhook-receiver`. The `/health` endpoint in both services surfaces
`scheduler.schedules_applied` alongside the existing `scheduler.enabled`,
`scheduler.initialized`, `scheduler.dbos_connected` fields.

The Docker scheduler's `/health` already reports the right value (always `True` for
`tdt-scheduler`).

## Trade-offs

| Option | Pros | Cons |
|--------|------|------|
| **Stop calling `apply_schedules()` from app services** (chosen) | One-line fix per service; preserves Docker scheduler ownership; zero risk of breaking cron firing | App services must coordinate with the scheduler in production; if Docker scheduler is down, app services still do nothing |
| **Move all schedules to a host LaunchAgent, drop Docker scheduler** | No Docker dependency; one less moving part | Larger deploy-surface change; out of scope per `Non-Goals` |
| **Add a "skip if not owner" guard inside `apply_schedules()` only** | Smaller code change | Silent: nothing tells you the app service is *trying* to apply schedules and is being ignored; you only find out when a workflow silently doesn't fire |
| **Make `app_name=tdt-scheduler` a hard requirement for all schedule registration, period** | Strictest | Breaks legitimate single-process schedulers (test fixtures, future LaunchAgent) |

The chosen option is the **fail-closed guard + skip-by-default** combo: production
fails loudly if an app service tries to apply schedules; opt-out is one env var. Test
fixtures and the future host LaunchAgent both fit cleanly.

## Risk

- **Low**. The Docker scheduler is already running all schedules. Stopping the app
  services from competing *adds* nothing wrong; it only stops noise.
- **The ownership assert is fail-closed in production** — if a deployer forgets to set
  `SCHEDULER_APP_NAME=tdt-ai-review` in a new host service's launcher, that service
  will fail to start with a clear error message instead of silently dropping cron
  workflows. This is the desired behavior.
- **No data migration**. No rollback plan needed beyond `git revert`; the previous
  state (services calling `apply_schedules()` and producing ERROR rows) is recoverable
  by reverting.
