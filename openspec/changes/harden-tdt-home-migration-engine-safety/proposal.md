## Why

The archived migration-engine change was marked complete after a compatibility
implementation reintroduced pathname-based filesystem mutation, despite the
provider contract requiring descriptor-relative, root-bound, fail-closed
behavior. This correction restores the safety boundary immediately and keeps
the still-unimplemented strict executor explicitly tracked.

## What Changes

- Restore the compatibility `tdt_core.migration_engine` mutators to a
  fail-closed surface until they can delegate to a verified strict executor.
- Add regression tests proving that compatibility backup, apply, rollback, and
  journal persistence calls cannot mutate arbitrary paths or create staging
  artifacts.
- Preserve the strict planner, generation journal, and verified backup/staging
  modules as the implementation foundation for the next executor slice.
- Add a follow-up task ledger for descriptor-relative switching, recovery,
  rollback, interruption, and isolated-root evidence; do not claim those tasks
  complete from superficial compatibility tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdt-home-migration-engine`: compatibility entry points SHALL remain
  fail-closed until a strict root-bound executor satisfies the archived
  capability contract.

## Impact

- Affected implementation: `/Users/androidteam/Developer/tdt-core/src/tdt_core/migration_engine.py`.
- Affected tests: migration-engine compatibility and safety regression suites.
- Affected planning surface: this corrective OpenSpec change only; archived
  changes remain immutable.
- No consumer repository, deployment configuration, live `~/.tdt`, or
  operator-owned filesystem is inspected or modified.
