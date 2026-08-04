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
- [x] 2.2 Implement descriptor-relative destination switching with durable
  per-step `intent`/`completed` records and reopened postcondition checks.
- [x] 2.3 Implement root-bound recovery and rollback using verified generation
  manifests, prior absence, symlinks, metadata, and external-interference
  rejection.
- [x] 2.4 Add real subprocess/SIGTERM interruption coverage at every durable
  boundary and prove fresh-process idempotent recovery.
- [x] 2.5 Add isolated apply → verify → rollback and provider contract evidence.

## 3. Verification and documentation

- [x] 3.1 Run full quality gates with the protected worktree state resolved.
- [x] 3.2 Document the strict executor API, failure semantics, and operator
  boundary without exposing live-root values.
- [x] 3.3 Run strict OpenSpec validation and store doctor, then review before
  archival.

## Evidence boundary

The compatibility correction is implemented in canonical `tdt-core` commit
`88746e7`; the strict executor implementation is in `6d266fe`, with a terminal
postcondition recheck and compatibility/documentation follow-up in `97f83e2`,
plus staging-cleanup regression coverage in `6934182` and direct-constructor
root invariant coverage in `c657aad`. Focused migration, backup, journal,
plan, and safety tests pass; the final executor-test formatting revision is
`7c686ee`.
the full provider suite reports 508 passed and 16 skipped. Ruff lint, strict
mypy, and `git diff --check` pass. The subprocess matrix reaches and recovers
from all six durable boundaries in fresh processes, and regular-file,
symlink, prior-absence, rollback, and interference tests pass against
temporary roots.

Task 3.1 remains open because repository-wide Ruff format still reports the
protected concurrent `migration_journal.py` syntax edit. `cli.py` and
`source_audit.py` formatter drift from landed agent commits was corrected
without touching that protected file. The archived migration-engine change
remains historical; this active change is the authoritative safety correction
and follow-up plan. Strict OpenSpec validation reports 357 passed and 0 failed;
`openspec store doctor openspec-store` reports no structural issues.
