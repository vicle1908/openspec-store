# DBOS Stale Workflow Auto-Cleanup

## Purpose

Automate the periodic cleanup of stale DBOS ERROR and ENQUEUED workflow rows
using a DBOS `@scheduled_workflow` registered in the Docker `tdt-scheduler`
container. This prevents queue-worker hangs caused by per-key deduplication
blocks from old `application_version` rows.

## ADDED Requirements

### Requirement: Scheduled cleanup workflow fires every 30 minutes

The Docker `tdt-scheduler:local` container SHALL run a DBOS `@scheduled_workflow`
named `_stale_workflow_cleaner` on a cron of `*/30 * * * *` (UTC timezone).
The workflow SHALL call both `_cancel_stale_error_workflows` and
`_cancel_stale_enqueued_workflows` from `tdt_core.scheduler.cli`.

#### Scenario: Cleaner fires on schedule

- **WHEN** the cron fires at :00 or :30 past the hour (UTC)
- **THEN** the `_stale_workflow_cleaner` workflow SHALL execute
- **AND** SHALL emit a log line to `sys.stderr` (via `print()`) containing the
  counts of cancelled ERROR, ENQUEUED, and PENDING rows so the output is visible
  in `docker logs` regardless of the stdlib logging pipeline configuration

### Requirement: Only stale rows from old application versions are cancelled

The cleaner SHALL NOT cancel ERROR, ENQUEUED, or PENDING rows whose `application_version`
equals the current recorded version in `dbos.application_versions`. Cancellation
is limited to:
- ERROR rows with `application_version <> current_version` AND whose
  exception class is one of `ModuleNotFoundError`, `AttributeError`,
  `ImportError`, `UnpicklingError`, OR whose workflow name is one of
  `_dbos_debouncer_workflow`, `_dispatch_review_workflow`,
  `_dispatch_mr_workflow`.
- ENQUEUED rows older than 48 hours AND with `application_version <> current_version`.
- PENDING rows with `application_version <> current_version` AND whose
  workflow name is one of the stale debouncer names above. No age threshold
  is applied because a PENDING row from the current version may be legitimately
  in-flight; only cross-version PENDING rows are orphaned.

#### Scenario: Cleanup preserves current-version ERROR rows

- **WHEN** a workflow from the current `application_version` raises an exception
  and transitions to ERROR
- **THEN** the cleaner SHALL NOT cancel that row on the next cleanup run
- **AND** the row SHALL remain visible in `dbos.workflow_status` for inspection

### Requirement: Cleanup is idempotent

Running the cleaner when no stale rows exist SHALL be a no-op (zero rows cancelled).
Re-running immediately after a cleanup SHALL also be a no-op.

#### Scenario: Double-run is idempotent

- **WHEN** the cleaner is triggered manually immediately after a normal run
- **THEN** the second run SHALL report `cancelled: 0` for both ERROR and ENQUEUED

### Requirement: No changes to webhook-receiver or ai-review

The auto-cleanup mechanism SHALL NOT require any code changes, configuration
changes, or redeployment of `webhook-receiver` or `ai-review`.

#### Scenario: No impact on consumer services

- **WHEN** the cleaner runs in the Docker `tdt-scheduler` container
- **THEN** `webhook-receiver` and `ai-review` SHALL continue operating normally
- **AND** their DBOS queue workers SHALL process dispatches without interruption

## Out of Scope

- Proactive service restart watchdog (detecting `/health` timeouts and force-restarting services). This is a separate concern from database cleanup.
- Modifying `webhook-receiver` or `ai-review` to call `apply_schedules()`.
- Creating new CLI commands for manual cleanup (existing commands are preserved).
