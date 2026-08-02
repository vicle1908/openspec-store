## Why

DBOS keeps ERROR and ENQUEUED workflow rows in the system database indefinitely. When a deployed workflow function is removed, renamed, or depends on a module absent from the running venv, every recovery attempt raises `ModuleNotFoundError` / `AttributeError` and transitions the row to ERROR — where it stays forever. These rows block the DBOS queue worker via per-key deduplication: any new dispatch with the same debounce key hits a live row for that key and either gets silently deduplicated (returning `DBOSQueueDeduplicatedError`) or creates a new ERROR row.

The manual workaround — running `tdt-scheduler cancel-stale-errors` — works but requires human intervention every 6–8 hours. This change automates that intervention by scheduling the cleanup as a DBOS cron workflow inside the existing Docker `tdt-scheduler:local` service, making the system self-healing.

## What Changes

A new DBOS `@scheduled_workflow` named `_stale_workflow_cleaner` is registered inside the Docker `tdt-scheduler` container, firing every 30 minutes. It runs `_cancel_stale_error_workflows` and `_cancel_stale_enqueued_workflows` against the shared system database (`tdt_scheduler_dbos_sys`) using the same logic as the existing `tdt-scheduler cancel-stale-errors` and `cancel-orphan-enqueued` CLI commands. The cleanup is idempotent — cancelling already-CANCELLED rows is a no-op.

No new CLI commands are needed. The existing `cancel-stale-errors` and `cancel-orphan-enqueued` commands are preserved for manual use.

## Capabilities

### New Capabilities
- `dbos-stale-workflow-auto-cleanup`: A DBOS `@scheduled_workflow` inside the Docker `tdt-scheduler` container that periodically cancels stale ERROR and ENQUEUED workflow rows from retired `application_version`s, preventing queue-worker hangs and per-key dedup blocks.

### Modified Capabilities
- `scheduler-engine`: The existing `scheduler-engine` capability (defined in `fix-app-services-apply-schedules`) is extended with a new scheduled workflow registration. The `apply_schedules()` ownership guard (only `app_name=tdt-scheduler` may call it) is respected.

## Impact

- **Added**: `_stale_workflow_cleaner` scheduled workflow in the Docker `tdt-scheduler:local` container.
- **No changes**: `webhook-receiver`, `ai-review`, `tdt-core` source code.
- **Database**: Reads `dbos.workflow_status`; updates `status` to `CANCELLED` for matching rows.
- **No new dependencies**: Uses existing `_cancel_stale_error_workflows` and `_cancel_stale_enqueued_workflows` internal functions already in `tdt-core/src/tdt_core/scheduler/cli.py`.
