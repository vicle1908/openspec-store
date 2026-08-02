# Proposal: `android-docs-mirror-retirement` — Retire local Android rule mirror

## Why

The `docs-repo-canonical-rule-source` change (v1) established `poems-mobile3-docs/50.RCA/20.AOS/rules/categories/` as the **canonical** source of truth. The local mirror at `poems-mobile3-android/docs/rules/categories/` became optional and is no longer required for scanning.

This change removes the local mirror and updates all references to it, completing the M-4 contract from the drift-detection spec.

## What Changes

### 1. Remove local mirror directory

Delete `poems-mobile3-android/docs/rules/categories/` (or archive it under `docs/.archived-rules-mirror/`).

### 2. Update `load-project-rulebook.mdc`

Update `poems-mobile3-android/.agents/load-project-rulebook.mdc` to point at the canonical docs repo path instead of the local mirror. The new reference path should be:
```
~/Developer/tdt/poems-mobile3-docs/20.Developments/40.AI/50.RCA/20.AOS/rules/categories/
```

### 3. Archive the mirror

Move the contents of `docs/rules/categories/` to `docs/.archived-rules-mirror/YYYY-MM-DD/` with a `README.md` inside noting that these files were retired in favor of the canonical docs repo.

## M-4 Contract

This change fulfills the M-4 retirement milestone: *"Local mirrors are deleted from platform repos once CI guard is in place and operator confirms no regressions."*

## Scope

- In scope: `poems-mobile3-android`.
- Out of scope: `code-daily-scan`, `poems-mobile3-ios`, `poems-mobile3-docs`.
