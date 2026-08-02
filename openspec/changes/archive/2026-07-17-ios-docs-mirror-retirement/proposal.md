# Proposal: `ios-docs-mirror-retirement` — Retire local iOS rule mirror + restructure

## Why

The `docs-repo-canonical-rule-source` change (v1) established `poems-mobile3-docs/50.RCA/10.iOS/rules/categories/` as the **canonical** source of truth. The local mirror at `poems-mobile3-ios/docs/technical-debt-scan/categories/` (legacy path) became optional and is no longer required for scanning.

This change removes the legacy mirror, migrates iOS to the 9-file `docs/rules/categories/` layout (aligned with Android), and updates all references to it — completing the M-4 contract from the drift-detection spec.

## What Changes

### 1. Remove legacy local mirror directory

Delete `poems-mobile3-ios/docs/technical-debt-scan/categories/` (or archive it under `docs/.archived-rules-mirror/YYYY-MM-DD/`).

### 2. Restructure to `docs/rules/categories/`

Migrate iOS to the 9-file layout matching Android's canonical structure:

- Create `poems-mobile3-ios/docs/rules/categories/` as the canonical local reference path.
- Sync all 9 canonical category files from `poems-mobile3-docs/50.RCA/10.iOS/rules/categories/` into this directory.
- This is the **last sync** before the local mirror is retired entirely (per the M-1 contract from `docs-repo-mirror-sync`).

### 3. Update `load-project-rulebook.mdc`

Update `poems-mobile3-ios/.agents/load-project-rulebook.mdc` to reference `docs/rules/categories/` instead of `docs/technical-debt-scan/categories/`.

### 4. Archive the legacy mirror

Move the contents of `docs/technical-debt-scan/categories/` to `docs/.archived-rules-mirror/YYYY-MM-DD/` with a `README.md` noting the retirement date and the new path.

## M-4 Contract

This change fulfills the M-4 retirement milestone for iOS.

## Scope

- In scope: `poems-mobile3-ios`.
- Out of scope: `code-daily-scan`, `poems-mobile3-android`, `poems-mobile3-docs`.
