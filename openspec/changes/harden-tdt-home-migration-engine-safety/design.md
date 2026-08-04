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

### Decision 3: Track the real executor separately

Descriptor-relative switching, recovery, rollback, signal interruption, and
isolated end-to-end verification remain open tasks. They require a strict
executor with explicit root identity, per-step intent/completion records,
verified postconditions, and durable backup metadata. The correction does not
mark those tasks complete merely because a compatibility test can copy a file.

## Non-Goals

- Editing or rewriting archived OpenSpec artifacts.
- Reading or mutating `/Users/androidteam/.tdt`.
- Modifying consumer repositories or deployment configuration.
- Adding a pathname-based compatibility fallback.
- Claiming strict switching, recovery, rollback, or SIGTERM evidence before it
  exists.

## Rollback

If the safety correction is rejected, revert only the corrective commit and
retain the archived artifacts for historical reference. Do not restore the
unsafe pathname-based implementation. Any future executor rollback remains
confined to synthetic roots and retained journal evidence.
