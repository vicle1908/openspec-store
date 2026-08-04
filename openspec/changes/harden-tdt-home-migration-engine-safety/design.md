# Design: TDT_HOME Migration Engine Safety Correction

## Context

The provider already has strict typed planning, a root-bound durable journal,
and verified backup/staging primitives. A later compatibility rewrite bypassed
those primitives with `Path` and `shutil` mutation. The correction must restore
the security boundary without rewriting archived artifacts or granting the
compatibility surface authority over arbitrary paths.

## Decisions

### Decision 1: Keep the compatibility facade fail-closed

`migration_engine.py` retains its historical plan and journal inspection API so
existing callers do not break, but all mutating compatibility functions raise
`ApplyError`. They must not create a backup directory, write a JSONL journal,
copy a source, replace a destination, or recursively remove staging data.

The strict implementation surface remains in `migration_plan.py`,
`migration_journal.py`, and `migration_backup.py`. A future executor must accept
their typed plan and `JournalStore`, not bypass them with compatibility paths.

### Decision 2: Test the negative boundary directly

Regression tests call every compatibility mutator against an isolated target
and assert the root remains byte-for-byte and entry-for-entry unchanged. A
source-inspection test rejects the forbidden pathname fallback imports and
operations. These tests are synthetic and do not resolve, inspect, or mutate
the real operator root.

### Decision 3: Keep strict execution separate and evidence-backed

The strict executor is now implemented as a separate, typed surface in
`migration_executor.py`; the compatibility facade remains fail-closed and is
not silently delegated to it. The executor accepts only `MigrationPlan`,
`JournalStore`, and explicit source roots. It derives the current operation
from the validated journal history, publishes durable `intent`/`completed`
pairs, and reopens every final object before `completed` or `committed`.

All target mutation is below a retained `RootAnchor`/`DirectoryHandle` using
no-follow inspection, exclusive staging, descriptor-relative `os.rename` or
`os.symlink`, `os.unlink` only for an authorized leaf, file synchronization,
and parent synchronization. A destination that is neither verified backup
state nor desired staged state is external interference and fails closed.

Recovery reloads the generation and uses the same deterministic operation
prefix in a fresh process. Rollback reverses only the affected prefix and
reopens the restored object against `BackupMetadata`; prior absence is an
explicit state. The optional boundary observer exists only for synthetic
subprocess tests and is called after the journal durability boundary.

## Non-Goals

- Editing or rewriting archived OpenSpec artifacts.
- Reading or mutating `/Users/androidteam/.tdt`.
- Modifying consumer repositories or deployment configuration.
- Adding a pathname-based compatibility fallback.
- Reading or mutating a live operator root; strict evidence remains synthetic.

## Rollback

If the safety correction is rejected, revert only the corrective commit and
retain the archived artifacts for historical reference. Do not restore the
unsafe pathname-based implementation. Any future executor rollback remains
confined to synthetic roots and retained journal evidence.
