# Tasks: TDT_HOME Migration Engine Safety Correction

## 1. Restore the compatibility boundary

- [x] 1.1 Restore `migration_engine.py` compatibility mutators to explicit
  fail-closed behavior.
- [x] 1.2 Add regression tests for no mutation, no pathname fallback, and
  read-only recovery classification.
- [x] 1.3 Run focused migration-engine and provider quality gates.

## 2. Implement the strict executor safely

- [x] 2.1 Define an executor API that accepts only the typed
  `tdt_core.migration_plan.MigrationPlan`, `JournalStore`, and explicit source
  roots; reject compatibility-path plans.
- [ ] 2.2 Implement descriptor-relative destination switching with durable
  per-step `intent`/`completed` records and reopened postcondition checks.
- [ ] 2.3 Implement root-bound recovery and rollback using verified generation
  manifests, prior absence, symlinks, metadata, and external-interference
  rejection.
- [ ] 2.4 Add real subprocess/SIGTERM interruption coverage at every durable
  boundary and prove fresh-process idempotent recovery.
- [ ] 2.5 Add isolated apply → verify → rollback and provider contract evidence.

## 3. Verification and documentation

- [ ] 3.1 Run full quality gates with the protected worktree state resolved.
- [ ] 3.2 Document the strict executor API, failure semantics, and operator
  boundary without exposing live-root values.
- [ ] 3.3 Run strict OpenSpec validation and store doctor, then review before
  archival.

## Evidence boundary

The compatibility correction is implemented in canonical `tdt-core` commit
`88746e7`; the strict executor boundary and prepare/stage wiring are in
`cf7ff14`. Focused migration-engine, safety, and executor tests pass, and the
full provider suite reports 508 passed and 16 skipped with Ruff lint and strict
mypy green.
The repository-wide format check still reports only the protected concurrent
`migration_journal.py` syntax edit. This evidence does not claim the strict
executor tasks in section 2 are complete. The archived migration-engine change
remains historical; this active change is the authoritative safety correction
and follow-up plan.
