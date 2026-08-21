## 1. Source ownership and pre-edit analysis

- [x] 1.1 Confirm the owning implementation surface in `tdt-core` and record exact immutable base, dirty fingerprint, dependency origins, and current scheduler/DBOS versions; verify `tdt-scheduler` remains the runtime acceptance host and `tdt-observability` is not edited.
- [x] 1.2 Run GitNexus impact analysis (or record the exact tooling failure and bounded direct-source fallback) for `SchedulerEngine.initialize`, `SchedulerEngine.apply_schedules`, `ScheduleRegistryLoader.apply_from_yaml`, and the stale-maintenance symbols; verify the report identifies the pre-edit blast radius before source changes.
- [x] 1.3 Add the smallest red tests/fixtures for an owned retired `webhook-selftest` schedule/workflow row, current rows, ambiguous ownership, and unavailable DBOS schema; verify the tests fail for the missing reconciliation behavior before implementation.

## 2. Reconciliation and readiness boundary

- [x] 2.1 Implement a normalized current registry/ownership snapshot at the canonical scheduler lifecycle boundary; verify decorator and YAML registrations are both included before persisted schedule activation.
- [x] 2.2 Implement a DBOS system-database adapter that detects schema/API capability, classifies stale versus current versus ambiguous scheduler-owned state, and redacts diagnostics; verify current and unrelated rows are never selected for mutation.
- [x] 2.3 Implement idempotent stale schedule/workflow cancellation or removal for confirmed scheduler-owned retired references; verify the seeded `webhook-selftest` row is quarantined before its next tick and a second run is a no-op.
- [x] 2.4 Add fail-closed lifecycle/readiness behavior for database, registry, schema, ownership, and mutation-recovery failures; verify persisted rows remain unchanged and cron/readiness do not activate on each failure path.

## 3. Reversible migration and rollback

- [x] 3.1 Add a versioned dry-run/apply path that reports candidate/protected rows, captures the exact selected scheduler-owned state, and applies changes transactionally or with an equivalent recoverable boundary; verify dry-run leaves selected tables unchanged.
- [x] 3.2 Implement rollback and conflict checks that restore only the captured scheduler-owned rows while preserving newer valid state and unrelated consumers; verify rollback succeeds for the fixture and refuses an ownership/version conflict.
- [x] 3.3 Add migration/rollback operational documentation with credential-free commands, bounded output, snapshot retention, and explicit no-truncate/no-reset safeguards; verify the runbook is consistent with the actual CLI/API surface.

## 4. Focused and real-runtime acceptance

- [x] 4.1 Run the focused scheduler regression suite covering stale schedule rows, stale workflow-status rows, current rows, ambiguity, idempotence, dry-run, rollback, and injected database/registry failures; verify all new tests pass.
- [x] 4.2 Build the real `tdt-scheduler:local` image and run a disposable seeded-stale PostgreSQL control; verify the scheduler remains healthy, current schedules apply, the retired reference is quarantined, and no new unregistered-workflow error appears.
- [x] 4.3 Re-run the fresh PostgreSQL control with both `tdt_scheduler` and `tdt_scheduler_dbos_sys` databases for at least 150 seconds; verify `dbos_connected=true`, the canonical 19/19 schedule baseline after retiring the legacy cleaner, no retired manifest entry, and no unregistered-workflow error.
- [x] 4.4 Independently monitor both runtime controls for restarts, OOM kills, health streak, bounded logs, and artifact preservation; verify ambient Compose projects and unrelated database state remain unchanged.

## 5. Quality, provenance, and OpenSpec completion

- [x] 5.1 Run the owning repositories' focused/full tests, Ruff/formatting, strict mypy, dependency/lock checks, and `git diff --check`; verify each exit code and classify pre-existing failures separately.
- [x] 5.2 Run `gitnexus detect_changes()` after implementation and before commit; verify the changed files/symbols and execution-flow risk match the approved scope, then commit only owned source/tests/docs.
- [x] 5.3 Re-run strict OpenSpec validation and doctor, update evidence/task checkboxes only from exact results, and verify the active change is not archived until implementation, rollback, and both runtime controls are accepted.
