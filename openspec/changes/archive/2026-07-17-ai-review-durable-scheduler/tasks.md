# ai-review Durable Scheduler Tasks

## Status

- `[ ]` pending
- `[x]` done

## Tasks

- [x] **T1**: Add `scheduler_enabled`, `scheduler_database_url`,
  `scheduler_app_name`, `review_debounce_seconds` fields to
  `ai-review/src/ai_review/config/settings.py`.

- [x] **T2**: Wire `SchedulerEngine` lifecycle into
  `ai-review/src/ai_review/api/app.py` lifespan: `from_env()`,
  `initialize()`, register `DebouncerWrapper`, `shutdown()` on
  exit.

- [x] **T3**: Add `_dispatch_review_workflow` async function in
  `app.py` that calls `orchestrator.run_sync` in a thread
  (matches the DBOS workflow contract).

- [x] **T4**: Update `ReviewOrchestrator.__init__` to accept
  `debouncer: DebouncerWrapper | None = None` kwarg.

- [x] **T5**: Update `ReviewOrchestrator.enqueue` to dispatch
  via `loop.run_in_executor(self.debouncer.debounce, ...)` when
  the debouncer is enabled, falling back to `asyncio.create_task`
  when disabled or None.

- [x] **T6**: Add `scheduler` and `review_debouncer` keys to
  the `/health` response.

- [x] **T7**: Update test fixtures in `tests/test_orchestrator.py`,
  `tests/test_health.py`, `tests/test_review_context.py` to set
  the four new `Settings` fields.

- [x] **T8**: Add three new tests in `tests/test_orchestrator.py`:
  - `test_enqueue_dispatches_via_dbos_debouncer_when_enabled`
  - `test_enqueue_falls_back_to_passthrough_when_debouncer_disabled`
  - `test_enqueue_falls_back_to_passthrough_when_no_debouncer`

- [x] **T9**: Verify `uv run pytest tests/ -q` passes (151 tests).

- [x] **T10**: Verify `uv run ruff check src/ tests/` passes.

- [x] **T11**: Verify `uv run mypy` passes.

- [x] **T12**: Commit `ai-review` (settings, app, orchestrator,
  tests).

- [x] **T13**: Commit `tdt-meta` (this OpenSpec change).

## Follow-up tasks (closed gap)

The first deploy surfaced a new gap that the spec did not anticipate:
**shared DBOS namespace between services causes cross-process
`ModuleNotFoundError`**. Closed in commits `0378e0e` (ai-review) and
`f53177d` (webhook-receiver).

- [x] **T14**: Set `SCHEDULER_APP_NAME` to a service-specific value
  in each runtime launcher (`tdt-ai-review`, `tdt-webhook-receiver`).
  Source change in `scripts/deploy.sh` heredoc template.

- [x] **T15**: Verify end-to-end dispatch via real GitLab webhook:
  `POST /gitlab-webhook → webhook-receiver mr_debounce_triggered →
  handoff_dispatch_accepted (HTTP 202) → ai-review intake_received →
  review_dbos_dispatched`. Confirmed via `e2e-dbos-fixed-*` test.

## Operational follow-up

- [x] **T16**: Add `tdt-scheduler cancel-stale-errors` CLI to
  `tdt-core/src/tdt_core/scheduler/cli.py`. Cancels ERROR rows from
  old application versions whose exception class is
  ModuleNotFoundError / AttributeError / ImportError / UnpicklingError
  OR whose workflow name is `_dbos_debouncer_workflow`,
  `_dispatch_review_workflow`, `_dispatch_mr_workflow`. Run after any
  deploy that renames or removes registered workflow functions.
  Implemented in commit `54f689c` (tdt-core).

- [x] **T17**: Fix DBOS queue cross-contamination. ai-review used
  `_dbos_internal_queue` (default), causing webhook-receiver's Docker
  scheduler process to pick up ai-review's `_dispatch_review_workflow`
  items and fail with "No module named 'webhook_receiver'". Fixed by
  giving ai-review its own named queue: `queue="tdt-ai-review-queue"`.
  webhook-receiver stays on the default queue (shared with Docker
  scheduler for internal scheduled tasks like scan-recent-mrs).
  Applied to source files and deployed venvs.
