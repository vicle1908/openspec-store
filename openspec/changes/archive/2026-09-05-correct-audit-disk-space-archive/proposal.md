## Why

The archived `2026-09-05-audit-disk-space-cleanup` change contains three documentation claims that are ambiguous or historically stale even though its operational evidence and task ledger are complete. A corrective change is needed because archived OpenSpec history is immutable and must be reconciled without rewriting it.

## What Changes

- Add value-blind evidence reconciling the three archived documentation warnings.
- Clarify that the archived Trash statement describes the pre-approval inventory, while later approved cleanup is recorded separately.
- Clarify that the original non-goal prohibited unapproved automatic mutation; approved cleanup execution is recorded in the implementation evidence.
- Narrow the no-unrelated-modification claim to the implementation scope of this change.
- Preserve the archived change unchanged and do not modify active unrelated changes.
- Non-goals: editing archived files, deleting or restoring files, changing application state, rewriting Git history, or archiving incomplete changes.

## Capabilities

### New Capabilities

- `archive-claim-reconciliation`: Value-blind corrective evidence for stale or ambiguous archived cleanup claims.

### Modified Capabilities

None.

## Impact

- Affected ownership boundaries: OpenSpec archive governance, workstation cleanup evidence, Docker, Trash, npm/pnpm, and the pre-existing workspace dirty state.
- The archive remains immutable; only this corrective active change is written until its own completion and archival.
