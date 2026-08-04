## Why

The archived migration-engine change was marked complete after a compatibility
implementation reintroduced pathname-based filesystem mutation, despite the
provider contract requiring descriptor-relative, root-bound, fail-closed
behavior. This correction restores the compatibility safety boundary and
finishes the strict executor as a separately reviewable, typed implementation
against synthetic roots.

## What Changes

- Keep the compatibility `tdt_core.migration_engine` mutators permanently
  fail-closed for arbitrary paths; the strict executor remains a separate
  typed entry point.
- Add regression tests proving that compatibility backup, apply, rollback, and
  journal persistence calls cannot mutate arbitrary paths or create staging
  artifacts.
- Preserve the strict planner, generation journal, and verified backup/staging
  modules as the implementation foundation for the next executor slice.
- Add a strict executor that uses the typed plan and journal to perform
  descriptor-relative switching, root-bound recovery, explicit rollback, and
  fresh-process SIGTERM recovery only under isolated roots.
- Keep a revision-bound task ledger and evidence report; compatibility tests
  alone never authorize migration completion.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdt-home-migration-engine`: compatibility entry points SHALL remain
  fail-closed, while the strict root-bound executor satisfies the archived
  capability contract only through its typed API.

## Impact

- Affected implementation: `migration_engine.py`, `migration_executor.py`, and
  the provider descriptor-relative migration helpers.
- Affected tests and docs: migration-engine safety, executor interruption and
  rollback suites, and `docs/migration-executor.md`.
- Affected planning surface: this corrective OpenSpec change only; archived
  changes remain immutable.
- No consumer repository, deployment configuration, live `~/.tdt`, or
  operator-owned filesystem is inspected or modified.
