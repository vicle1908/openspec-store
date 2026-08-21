## Why

A shared DBOS system database can retain a `webhook-selftest` schedule/workflow reference after that schedule has been removed from the current manifests, so the scheduler later emits `webhook-selftest is not a registered workflow function`; the fresh PostgreSQL control stayed healthy, proving the defect is persisted-state drift rather than a current manifest registration. The scheduler needs an ownership-aware, fail-safe reconciliation boundary before persisted DBOS state can enqueue work, with a reversible migration and real-runtime proof.

## What Changes

- Extend the existing `scheduler-engine` capability with startup/state reconciliation that compares persisted DBOS schedule and workflow state in `tdt_scheduler_dbos_sys` with the canonical schedules and registered workflow functions loaded by the scheduler.
- Reconcile only state that is demonstrably owned by the canonical `tdt-scheduler` process; remove or cancel confirmed stale references such as retired `webhook-selftest` rows, while preserving valid current schedules and unrelated consumer state.
- Make reconciliation idempotent and fail-safe: take no destructive action when ownership, registry resolution, schema compatibility, or database access cannot be established; prevent schedule activation/readiness when the scheduler cannot prove a safe state, and emit bounded diagnostics.
- Provide a versioned data-migration/operational path with pre-change snapshot, dry-run/report output, transactional or otherwise atomic mutation, and rollback that restores only the captured scheduler-owned rows. The path must be safe for shared-database deployments and repeatable after restart.
- Add focused regression coverage for stale schedule rows, stale workflow-status rows, unknown workflow references, valid retained schedules, repeated reconciliation, ownership boundaries, and reconciliation failures.
- Add real scheduler acceptance against (a) a deliberately stale shared DBOS database and (b) fresh `tdt_scheduler` plus `tdt_scheduler_dbos_sys` control databases, including bounded liveness, schedule counts, manifest absence/presence checks, and absence of the unregistered-workflow error.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `scheduler-engine`: add safe startup/state reconciliation for persisted DBOS schedules and workflow rows, plus migration/rollback and runtime acceptance requirements. Existing requirement and scenario identifiers remain unchanged; the delta adds only the new reconciliation contract.

## Impact

- **tdt-core scheduler ownership**: implementation is expected to inspect the current `SchedulerEngine.initialize()`, `apply_schedules()`, `ScheduleRegistryLoader.apply_from_yaml()`, and scheduler serve/bootstrap symbols before selecting the exact hook. The canonical scheduler must reconcile before DBOS schedule ticks can enqueue persisted stale references.
- **DBOS system database**: the affected shared database is `tdt_scheduler_dbos_sys`, including persisted schedule and workflow-status state. The change must not truncate or reset the database and must not mutate rows belonging to other DBOS consumers.
- **tdt-scheduler runtime acceptance**: the Docker `tdt-scheduler:local` service remains the real acceptance surface. The existing runbook records a healthy fresh control of `dbos_connected=true`, `schedule_count=20`, and `schedules_applied=19`; that baseline must remain intact while the stale-state case is repaired.
- **agent-core, tdt-observability, and other workload repositories**: no source change is authorized by this planning change unless a later implementation plan proves a symbol-level dependency after inspection. Declarative manifests remain owned by their implementing repositories.

## Non-Goals

- Do not restore, re-register, or silently execute the retired `webhook-selftest` schedule.
- Do not modify DBOS itself, truncate/reset either PostgreSQL database, or apply a blanket cleanup to all workflow rows.
- Do not delete or cancel current schedules, current-version work, or state that cannot be proven scheduler-owned.
- Do not treat network timeouts, optional telemetry notices, missing provider credentials, or an unhealthy external integration as this reconciliation defect.
- Do not change cron cadence, workload behavior, manifest ownership, or the scheduler's normal queue semantics.
- Do not edit source repositories during this planning change; implementation, migration execution, and runtime mutation belong to a later approved apply workflow.

## Evidence

- `tdt-scheduler/docs/tdt-scheduler-compose-verification.md` records the actionable persisted/scheduled `webhook-selftest` reference and the fresh-control baseline (`20` schedules, `19` applied) while distinguishing it from expected sandbox warnings.
- Current scheduler symbols include `SchedulerEngine.initialize()`/`apply_schedules()`, `ScheduleRegistryLoader.apply_from_yaml()`, and `tdt_core.scheduler.maintenance.stale_workflow_cleaner`; the implementation must verify their ordering and DBOS API compatibility rather than assume a specific code fix.
