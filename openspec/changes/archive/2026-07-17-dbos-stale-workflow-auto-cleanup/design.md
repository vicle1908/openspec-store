## Context

The TDT ecosystem uses DBOS as its durable execution engine. Two classes of workflow rows accumulate over time and can block the queue worker:

1. **ERROR rows**: Created when a workflow from a previous `application_version` tries to recover but its function is no longer present in the current venv (e.g. `ModuleNotFoundError`, `AttributeError`). DBOS never clears these rows automatically.

2. **ENQUEUED rows**: Created when the scheduler container restarts with a new `application_version`. DBOS filters the queue worker to rows with `application_version = current OR IS NULL`; all rows from the previous version become invisible and accumulate.

Both types can trigger per-key deduplication blocks when a debounce key matches a stale row. The current workaround — running `tdt-scheduler cancel-stale-errors` manually — works but is fragile: the hang recurs every 6–8 hours without human intervention.

## Goals / Non-Goals

**Goals:**
- Eliminate the recurring `__psynch_cvwait` hang in `webhook-receiver` without manual intervention.
- Provide automated, scheduled cleanup of stale ERROR and ENQUEUED rows using the existing cleanup logic.
- Be idempotent: multiple runs with no stale rows should be no-ops.
- Require zero changes to `webhook-receiver`, `ai-review`, or the host launchd setup.

**Non-Goals:**
- Modifying the DBOS library itself.
- Creating new CLI commands (the existing `cancel-stale-errors` / `cancel-orphan-enqueued` CLI commands are preserved for manual use).
- Implementing a proactive health-check / service restart watchdog (separate concern; tracked as open follow-up).

## Decisions

### Decision 1: Run the cleaner as a DBOS `@scheduled_workflow` inside the Docker `tdt-scheduler` container

**Chosen approach**: Add `_stale_workflow_cleaner` as a `@scheduled_workflow` registered in the `tdt-scheduler` Docker container's startup, firing every 30 minutes.

**Rationale**: The Docker `tdt-scheduler:local` container is the canonical scheduler process — it is always-on (`restart: unless-stopped`), connects to the shared PostgreSQL, and is the only process that should call `apply_schedules()`. Registering the cleaner here keeps the concern co-located with other scheduled work. `webhook-receiver` and `ai-review` are not modified.

**Alternatives rejected**:
- *Launchd interval in host*: Duplicates scheduling infrastructure; not crash-recoverable.
- *Cron in host crontab*: Already removed from the host (Phase 0.7); inconsistent with DBOS-native approach.
- *In-process in `webhook-receiver`/`ai-review`*: Would require adding `apply_schedules()` call to those services, violating the ownership contract; also cross-service DBOS access would need separate engine instances.

### Decision 2: Reuse the existing `_cancel_stale_error_workflows` and `_cancel_stale_enqueued_workflows` functions from `tdt-core/scheduler/cli.py`

**Chosen approach**: Call these internal functions directly from the `_stale_workflow_cleaner` workflow.

**Rationale**: Both functions are already tested, handle the `application_version` comparison correctly, decode the pickled error blobs, and use `AUTOCOMMIT` isolation. No code duplication. The cleaner workflow wraps them with DBOS durability (retry, logging, crash-recovery).

**Alternative rejected**:
- *Re-implement cleanup logic in the workflow*: Would duplicate the error-decoding and SQL logic; risk of divergence.

### Decision 3: Cron interval of 30 minutes

**Chosen interval**: Every 30 minutes (`CRON_TZ=UTC`).

**Rationale**: The observed recurrence interval for the hang is 6–8 hours, so a 30-minute interval provides 12× redundancy against a single missed cleanup. A 5-minute interval would be too aggressive for a database write (UPDATE with no WHERE on potentially large tables). 1-hour would match the observed recurrence but 30 minutes is a safer default given the observed pattern.

## Risks / Trade-offs

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Cleanup is too slow on large `workflow_status` table | Low | Functions use targeted `WHERE application_version <> current` and `WHERE status = 'ERROR'` / `WHERE status = 'ENQUEUED' AND created_at < threshold`; both are indexed by design. |
| Cleanup cancels a legitimately ERROR workflow from the current version | Very Low | The function only cancels rows whose `application_version <> current_version` OR whose exception is in the known-stale class list. Legitimate errors (from current version) are preserved. |
| Docker `tdt-scheduler` is not running (e.g. host offline) | Low | The Docker container uses `restart: unless-stopped`. On host reboot, Docker Desktop auto-starts (Phase 0.2), container restarts, and the cleaner resumes. |
| Cleanup runs during active dispatch, creating race condition | Very Low | DBOS enqueues are idempotent; cancelling a row that has already been processed is harmless. Cleanup only targets stale `application_version`s or known-stale workflow names. |
