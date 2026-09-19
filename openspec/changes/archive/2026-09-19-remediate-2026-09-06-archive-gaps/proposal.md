## Why

The 2026-09-06 cloud-drive archive contains completion claims for non-iCloud mutations that are not supported by the required approval and verification chain.

## What Changes

- Reconcile Google Drive and Desktop/Documents claims against exact-path, approval, and before/after evidence.
- Distinguish observed path absence (operation may have occurred) from execution provenance that is unsupported.
- Preserve immutable archives and record all discrepancies in a new active evidence surface.
- Keep unsupported mutation and verification gates blocked until their release conditions are met.

## Capabilities

### New Capabilities

- `archive-closure-audit`: Value-blind reconciliation of archived task ledgers against execution evidence and release gates.

### Modified Capabilities

None.

## Impact

- Archive history under `openspec/changes/archive/` is read-only.
- Corrective evidence is scoped to this active change under the OpenSpec store.
- Google Drive, Desktop/Documents, iCloud, personal data, and active repositories are not mutated.

## Non-Goals

- No iCloud operations; those are owned by another agent.
- No Google Drive, Desktop/Documents, cache, Trash, or personal-data deletion.
- No edits to archived task ledgers.
- No inference that an absent path proves authorized deletion.

