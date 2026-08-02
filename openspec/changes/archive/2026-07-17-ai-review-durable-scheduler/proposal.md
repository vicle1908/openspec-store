# ai-review Durable Scheduler (DBOS alignment)

## Why

The `ai-review` FastAPI service is the only Python service in the TDT
ecosystem that does not use DBOS for review dispatch. It currently
uses `asyncio.create_task` in `ReviewOrchestrator.enqueue()` to fire
the review, which means:

- Tasks are lost on process crash (no durability)
- No dedup-key semantics (DBOS debouncer has built-in dedup)
- Inconsistent with the ecosystem-wide standard established by
  `tdt-core[scheduler]` and used by `webhook-receiver`
- The `centralized-scheduling-module` openspec explicitly directs
  every Python service to migrate to DBOS-backed scheduling.

This change aligns `ai-review` to the DBOS standard so that reviews
dispatched to it are durable and the service behaves consistently
with the rest of the ecosystem.

## What Changes

1. **Add `scheduler_*` and `review_debounce_seconds` fields to
   `Settings`**: read from `SCHEDULER_ENABLED`, `SCHEDULER_DBOS_DATABASE_URL`,
   `SCHEDULER_APP_NAME`, `AI_REVIEW_REVIEW_DEBOUNCE_SECONDS`.

2. **Wire `SchedulerEngine` into the FastAPI lifespan**:
   - Try `SchedulerEngine.from_env().initialize()` at startup
   - Register a `DebouncerWrapper` keyed by `mr-{mr_iid}` for the
     review dispatch path
   - Log success/failure to the `scheduler_engine_initialized` /
     `scheduler_engine_init_failed` events (same as webhook-receiver)
   - Shutdown the engine gracefully on lifespan exit

3. **Replace `asyncio.create_task` in `ReviewOrchestrator.enqueue`**
   with the canonical DBOS pattern: when the debouncer is enabled
   and initialized, dispatch via `loop.run_in_executor` (because
   DBOS's `Debouncer.debounce()` is sync and refuses to run inside
   an active asyncio loop); when disabled, fall back to the legacy
   `asyncio.create_task` passthrough so the service still works
   without DBOS configured.

4. **Expose scheduler state in `/health`**: add `scheduler` and
   `review_debouncer` keys to the health JSON so operators can see
   whether DBOS is active.

5. **Tests**: three new tests in `tests/test_orchestrator.py`
   covering the DBOS-enabled path, the DBOS-disabled passthrough
   path, and the no-debouncer fallback.

## Goals

1. When `SCHEDULER_ENABLED=true` and `SCHEDULER_DBOS_DATABASE_URL`
   is set, `ai-review` MUST dispatch reviews via DBOS debouncer
   with the debounce key `mr-{mr_iid}`.
2. When DBOS is not available (disabled or init failed), the
   service MUST fall back to the in-process `asyncio.create_task`
   passthrough and continue to serve reviews.
3. The lifespan MUST shut down the engine on exit so DBOS does not
   leak resources.
4. The service MUST report its scheduler state in `/health`.

## Non-Goals

- This change does NOT add new scheduled workflows (cron jobs) to
  `ai-review`. Periodic work (coverage scan, freshness refresh) is
  handled by the Docker `scheduler` service per the
  `centralized-scheduling-module` Phase 4 migration.
- This change does NOT change the idempotency mechanism
  (`IdempotencyRegistry`). DBOS debouncer dedup is a *complement*
  to idempotency, not a replacement.
- This change does NOT add a `tdt-core[scheduler]` dependency —
  the dependency is already declared in `ai-review/pyproject.toml`.

## Success Criteria

- All 151 unit tests pass (`uv run pytest tests/ -q`).
- `uv run ruff check src/ tests/` and `uv run mypy` pass clean.
- The new tests in `tests/test_orchestrator.py` verify both the
  DBOS dispatch path and the passthrough path.
- After a clean `bash scripts/deploy.sh` from the dev tree, both
  `com.tdt.ai-review` and `com.tdt.webhook-receiver` are healthy
  and accept review requests.
- DBOS Conductor logs show service-specific appnames:
  `appname=tdt-ai-review` for ai-review,
  `appname=tdt-webhook-receiver` for webhook-receiver.
- `tdt-scheduler cancel-stale-errors` cancels stale ERROR rows
  from a previous `application_version`, releasing per-key
  debouncer locks held by removed/renamed workflow functions.

## Operational Follow-up (Post-deploy discoveries)

Two gaps surfaced only after the first real-deploy and end-to-end
verification; both are closed by commits in this change's
`tasks.md`:

* **SCHEDULER_APP_NAME cross-service isolation** (REQ-5): both
  services shared the default `tdt-scheduler` namespace, causing
  cross-process `ModuleNotFoundError` when DBOS tried to rehydrate
  workflows in a service that lacked the originating module.
  Fixed in commits `0378e0e` (ai-review) and `f53177d`
  (webhook-receiver) by exporting a per-service
  `SCHEDULER_APP_NAME` in each runtime launcher.

* **`tdt-scheduler cancel-stale-errors` CLI** (REQ-6): DBOS
  does not auto-clean ERROR rows; after a deploy that renames or
  removes a registered workflow function, every recovered
  workflow errors at module import time and holds the per-key
  debouncer lock indefinitely. Fixed in commit `54f689c`
  (tdt-core) by adding a one-shot cleanup CLI.

* **DBOS queue isolation** (REQ-7): ai-review used the default
  DBOS `_dbos_internal_queue`, causing cross-contamination when
  webhook-receiver's Docker scheduler process picked up ai-review's
  `_dispatch_review_workflow` items and failed with
  "No module named 'webhook_receiver'". Attempted fix by giving ai-review
  its own named queue: `queue="tdt-ai-review-queue"`. This caused DBOS
  "Invalid queue name provided to debouncer" errors because named queues
  must be pre-registered in every DBOS process consuming from the shared
  system DB. Root fix: ensure each service only registers queues it
  owns, and the Docker scheduler does not consume other services' queues.
  Mitigation: `SCHEDULER_APP_NAME` isolation ensures services have
  distinct app namespaces.
