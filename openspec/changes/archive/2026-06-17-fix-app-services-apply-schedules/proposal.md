# Stop App Services From Re-Registering Global DBOS Schedules

## Why

`webhook-receiver` and `ai-review` each call `engine.apply_schedules()` in their FastAPI
lifespan. The DBOS `workflow_schedules` table is **global per Postgres database**, not
partitioned by `app_name`, so every TDT service that boots and runs `apply_schedules()`
re-registers the same cron set (webhook-selftest, coverage-scan, scan-recent-mrs,
dlq-reaper, all jira-* schedules) under its own process `app_version`.

The intended owner of the global schedule set is the **Docker `tdt-scheduler` service**
in `agent-core/compose.yaml` (`tdt-scheduler:local`, `uv run tdt-scheduler serve`,
`TDT_SCHEDULER_SETUP_MODULE=scheduler_setup`). It is healthy and has been up 24h+, firing
all cron workflows correctly. The `webhook-receiver` and `ai-review` processes are
duplicating that work — and failing, because the workflow *functions* they register
(`webhook_receiver.scan_recent_mrs`, `webhook_receiver.selftest`, etc.) are not on their
own `sys.path`.

Observed symptoms on 2026-06-17:

- 39 ERROR rows in `dbos.workflow_status` for `_dbos_debouncer_workflow`, all
  `ModuleNotFoundError: No module named 'webhook_receiver'` (and one
  `No module named 'ai_review'`, the symmetric case from a previous rotation).
- 5 cancelled by `tdt-scheduler cancel-stale-errors`; the remaining 122 orphan
  ENQUEUED rows from old `application_version`s (22ed88a9…, 6cde92a2…) were cancelled
  manually.
- `ai-review.stderr.log` repeats the same `ModuleNotFoundError` lines on every restart
  since the per-service `app_name` was introduced in `f53177d` / `0378e0e`.
- 324 `degraded=True` markers in `ai-review.stdout.log` over the same window — the
  ai-review pipeline itself is fine, but its `OrchestrationResult.degraded` flag is set
  when a debounced review runs alongside the failing schedule-load and inherits noise
  from the same process.

`webhook-receiver` is the worst offender in practice because it is the *oldest* of the
duplicating processes; `ai-review` only joined the schedule-double-registration club
after `a5ea1dc`. Both must stop calling `apply_schedules()`.

## What Changes

1. **`ai-review`**: in `ai_review/api/app.py::lifespan`, drop the
   `engine.apply_schedules()` call. Keep `engine.initialize()` (so its debouncer still
   works) and `engine.debouncer(...)` registration. Log
   `scheduler_engine_initialized` with a new field `schedules_applied=False` so operators
   can confirm at a glance that ai-review is *not* running cron.

2. **`webhook-receiver`**: symmetric change in its `lifespan` — keep the debouncer, drop
   `apply_schedules()`. Same new log field.

3. **Document the contract** in `tdt-core`'s `SchedulerEngine.apply_schedules` docstring
   and `README`: only the canonical scheduler (Docker container or the future host
   `tdt-scheduler` LaunchAgent) may call `apply_schedules()`. Application services must
   only call `initialize()` + `debouncer()` / `queue()`. Add an assert
   (`scheduler_settings.app_name == "tdt-scheduler"`) at the top of
   `apply_schedules()` to make this contract enforceable — any non-scheduler call raises
   `SchedulerContractViolation` with a clear message. Keep the assert behind a
   `SCHEDULER_ENFORCE_OWNERSHIP` env var (default `True`) so test fixtures can opt out.

4. **Operational runbook** update: `tdt-meta/openspec/changes/coverage-sweep/docs/operations/webhook-failover.md`
   (or a new `docs/operations/tdt-scheduler-ownership.md`) gets a "Who runs the
   scheduler?" section that names the Docker `tdt-scheduler:local` as canonical and
   points at the new assert.

5. **`tdt-scheduler` cancel-stale-errors is now sufficient on its own** for cleanup of
   future drift — but a one-shot helper `tdt-scheduler cancel-orphan-enqueued` is added
   (alongside `cancel-stale-errors`) that cancels `ENQUEUED` rows whose
   `application_version` is no longer in `dbos.application_versions` and that have not
   fired in >24h. Idempotent. Replaces the manual `UPDATE` we ran on 2026-06-17.

## Capabilities

### New Capabilities

- `tdt-scheduler-ownership-contract`: rules for which processes may register global
  schedules, the `app_name=tdt-scheduler` invariant, the `SchedulerContractViolationError`
  exception, and the `SCHEDULER_ENFORCE_OWNERSHIP` env var.

- `tdt-scheduler-cancel-orphan-enqueued-cli`: the `cancel-orphan-enqueued` command
  that cancels ENQUEUED rows whose `application_version` is no longer active.

### Updated Capabilities (ADDED delta)

- `scheduler-engine`: `apply_schedules()` gains the ownership guard. This is an
  ADDED delta (the base `scheduler-engine` capability is implicitly created here).

## Impact

- **Affected services**: `ai-review` (FastAPI lifespan), `webhook-receiver` (FastAPI
  lifespan), `tdt-core` (engine + new CLI + assert).
- **Affected specs**:
  `tdt-meta/openspec/specs/scheduler/spec.md` (engine contract),
  `tdt-meta/openspec/specs/ai-review/spec.md` (lifespan),
  `tdt-meta/openspec/specs/webhook-receiver/spec.md` (lifespan).
- **Affected workflows**: none — the schedules are still registered by the Docker
  scheduler; we only stop the application services from racing it.
- **No new secrets, no new env vars beyond `SCHEDULER_ENFORCE_OWNERSHIP`** (default-on).
- **No data migration**: DBOS schedules table is the source of truth, unchanged.
- **No breaking change to MR review flow**: ai-review's debouncer continues to dispatch
  reviews on MR webhooks; the change is purely "stop also running the cron set."

## Non-Goals

- Migrating the cron set off the Docker scheduler to a host LaunchAgent. The Docker
  scheduler is healthy and this change is intentionally a *minimum* patch. A future
  change (`host-scheduler-launchagent`) can mirror the Docker setup onto launchd for
  environments where Docker is unavailable.
- Removing the `app_name` per-service isolation. That commit (`f53177d` / `0378e0e`) is
  correct and necessary; the bug is that the app services were *also* running
  `apply_schedules()` after the isolation was added.
- Cleaning the running DBOS schedule table itself. The Docker scheduler is the only
  writer that matters going forward; old rows from `971c48bb…` and `68f54a61…` are
  handled by `cancel-stale-errors` + the new `cancel-orphan-enqueued` CLI.
