# Tasks

## 1. tdt-core: ownership guard on `apply_schedules()`

- [x] 1.1 Add `SchedulerContractViolationError(SchedulerError)` to
  `tdt-core/src/tdt_core/scheduler/types.py` (alongside `SchedulerError`).
- [x] 1.2 In `tdt-core/src/tdt_core/scheduler/engine.py::apply_schedules`, read
  `SCHEDULER_ENFORCE_OWNERSHIP` (default `true`) and the engine's configured
  `app_name`. If enforcement is on and `app_name != "tdt-scheduler"`, raise
  `SchedulerContractViolationError` with the message template:
  `apply_schedules() called by app_name={app_name!r}; only the canonical scheduler
  (app_name='tdt-scheduler') may register global schedules. Set
  SCHEDULER_ENFORCE_OWNERSHIP=false in test fixtures, or remove the
  apply_schedules() call from your service's lifespan.`
  Also exported `SchedulerError`, `SchedulerContractViolationError` in
  `tdt_core/scheduler/__init__.py`.
- [x] 1.3 Add a "Ownership contract" section to the `apply_schedules` docstring
  that describes the guard, the env override, and links to the OpenSpec change.
- [x] 1.4 Created `tdt-core/src/tdt_core/scheduler/README.md` with a
  "Who runs the scheduler?" table naming the Docker `tdt-scheduler:local`
  as canonical, listing which services are consumers (webhook-receiver, ai-review),
  and documenting the `SCHEDULER_ENFORCE_OWNERSHIP` env var.

## 2. tdt-core: `cancel-orphan-enqueued` CLI

- [x] 2.1 In `tdt-core/src/tdt_core/scheduler/cli.py`, added
  `_registered_versions(system_engine) -> set[str]` that returns
  `SELECT version_name FROM dbos.application_versions`.
- [x] 2.2 Added `_cancel_orphan_enqueued(system_engine, active_versions, older_than_ms)`
  that runs
  `UPDATE dbos.workflow_status SET status='CANCELLED' WHERE status='ENQUEUED'
  AND application_version NOT IN :active_versions AND created_at < :threshold_ms`
  and returns the rowcount.
- [x] 2.3 Added the `cancel-orphan-enqueued` Typer subcommand with
  `--older-than-hours` (default 24). Emits JSON on stdout with `action`,
  `cancelled`, `current_versions`, `threshold_hours`, `older_than_iso`. Exit 0 on success.
- [x] 2.4 Ran the CLI against the live DBOS system DB: returned
  `{"action": "cancel_orphan_enqueued", "cancelled": 0, ...}` — all 501 ENQUEUED
  rows reference a registered version and were created <24h ago; 0 cancelled (expected).

## 3. tdt-core: tests

- [x] 3.1 `tests/scheduler/test_engine.py::test_apply_schedules_rejects_non_owner_app_name`:
  with `app_name="tdt-ai-review"`, `apply_schedules()` raises
  `SchedulerContractViolationError`.
- [x] 3.2 `tests/scheduler/test_engine.py::test_apply_schedules_allows_tdt_scheduler`:
  with `app_name="tdt-scheduler"`, `apply_schedules()` proceeds.
- [x] 3.3 `tests/scheduler/test_engine.py::test_apply_schedules_opt_out_via_env`:
  with `app_name="tdt-test"` and `SCHEDULER_ENFORCE_OWNERSHIP=false`, the call
  proceeds.
- [x] 3.4 `tests/scheduler/test_cli.py::test_cancel_orphan_enqueued_removes_old_rows`:
  using fake SQLAlchemy engine, verifies orphan ENQUEUED rows are cancelled.
- [x] 3.5 `tests/scheduler/test_cli.py::test_cancel_orphan_enqueued_idempotent`:
  running the helper twice cancels 0 rows on the second run.
  **Result**: 28/28 tests passing.

## 4. ai-review: drop `apply_schedules()` from lifespan

- [x] 4.1 In `ai-review/src/ai_review/api/app.py::lifespan`, removed the
  `engine.apply_schedules()` call. The engine is initialized for debouncers only.
  Added `schedules_applied=False` to the `scheduler_engine_initialized` log event.
- [x] 4.2 In `ai-review/src/ai_review/api/app.py::health`, added
  `scheduler_status["schedules_applied"] = False` so operators can confirm
  the ownership contract via `curl /health | jq '.scheduler.schedules_applied'`.
- [x] 4.3 Added `test_lifespan_does_not_apply_schedules` in
  `ai-review/tests/test_api.py` asserting `apply_schedules` is never called
  and `schedules_applied=False` in `/health`.
- [x] 4.4 `uv run pytest tests/test_api.py` — **6/6 passing**.
  **Result**: 6/6 tests passing.

## 5. webhook-receiver: drop `apply_schedules()` from lifespan

- [x] 5.1 In `webhook-receiver/src/webhook_receiver/api/app.py::create_app`,
  removed the `_scheduler_engine.apply_schedules()` call. Added a comment
  explaining the ownership contract.
- [x] 5.2 (Skipped — webhook-receiver's `/health` scheduler status comes from
  `engine.get_status()` which reports `schedule_count`; adding `schedules_applied`
  is redundant since webhook-receiver never calls `apply_schedules`.)
- [x] 5.3 Added `test_create_app_does_not_call_apply_schedules` in
  `webhook-receiver/tests/unit/test_ingress_dispatch.py` asserting
  `apply_schedules` is never called.
- [x] 5.4 `uv run pytest tests/unit/test_ingress_dispatch.py` — **6/6 passing**.
  Full suite: **271/271 passing**.
  **Result**: 6/6 new tests passing, 271/271 total passing.

## 6. Documentation: scheduler ownership runbook

- [x] 6.1 Added "Scheduler ownership contract" section to
  `tdt-meta/docs/workflows/webhook-ai-review-dual-service-runbook.md` with:
  ownership table, detection commands (`grep SchedulerContractViolation`),
  cleanup commands (`cancel-stale-errors`, `cancel-orphan-enqueued`),
  verification commands (`curl /health | jq '.scheduler.schedules_applied'`).
- [x] 6.2 (Skipped — the webhook-failover doc is not applicable; the
  scheduler ownership section is in the primary dual-service runbook which
  is already the canonical ops doc.)

## 7. Verify in production

- [x] 7.1 Verified via `/health` endpoints:
  - `ai-review` (`8090`): `schedule_count: 0` — no global schedules owned.
  - `webhook-receiver` (`8080`): `schedule_count: 2` — local registry count
    (selftest + dlq-reaper decorators), not pushed to DBOS.
- [x] 7.2 Ran `tdt-scheduler cancel-stale-errors`: **19 stale ERROR workflows
  cancelled** — all `ModuleNotFoundError: No module named 'webhook_receiver'` or
  `'ai_review'` from old `971c48bb53fcf8be53ea4112ef0c6ef1`. Root cause is
  fixed by removing `apply_schedules()` from service lifespans.
- [x] 7.3 Ran `tdt-scheduler cancel-orphan-enqueued`:
  `{"action": "cancel_orphan_enqueued", "cancelled": 0, ...}` — no orphan
  ENQUEUED rows found.
- [x] 7.4 Grepped live logs: no `SchedulerContractViolationError` found in
  either `ai-review.stderr.log` or `webhook-receiver.stderr.log`.
- [x] 7.5 Confirmed: `ai-review` `/health` scheduler `app_name=tdt-ai-review`
  (not `tdt-scheduler`), confirming it is a consumer not an owner.

## 8. Mark change complete

- [x] [historical] 8.1 `openspec validate fix-app-services-apply-schedules` exits 0.
- [x] [historical] 8.2 `openspec archive fix-app-services-apply-schedules --yes` archives
  the change and promotes the new capabilities to
  `tdt-meta/openspec/specs/`.


---

> **Historical record:** This change was archived with 2 incomplete task(s) (28/30 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
