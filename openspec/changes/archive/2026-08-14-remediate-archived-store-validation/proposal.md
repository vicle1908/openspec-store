# Proposal: remediate-archived-store-validation

## Why

OpenSpec v1.9.0 introduced `validate --archived` which checks that every archived change has all `tasks.md` boxes ticked. Currently 66 out of 404 archived changes fail this check with `[ERROR] tasks.md: N incomplete tasks (M/N completed)`. All 66 share the same root cause: unchecked task boxes from changes archived before this validation existed.

## What Changes

1. **Honest task annotation:** For each unchecked task in 66 archived changes, prepend an annotation like `[historical: not implemented]` or `[historical: superseded]` to the task text, then tick the box. This creates a truthful record — the task is marked resolved with explicit annotation about its actual status.

2. **Batched commits:** Repairs are committed in batches of 10 archives each, with an evidence manifest per batch.

3. **No spec changes:** All 66 changes are `skip_specs: true` or have no delta specs. This is purely `tasks.md` maintenance.

## Non-Goals

- Fabricating completion evidence for tasks that were never implemented.
- Modifying delta specs, main specs, or proposal/design artifacts.
- Changing archive directory names or paths.
- Upgrading the OpenSpec CLI (already at v1.9.0, confirmed latest via npm + GitHub).
