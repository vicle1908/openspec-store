## Why

Two 2026-09-06 archived changes contain task ledgers that claim completion beyond the directly verified implementation state, weakening OpenSpec archive integrity and obscuring unresolved approval and test gates.

## What Changes

- Reconcile the archived cloud-drive and realtime Vitest ledgers against current evidence and predecessor active state.
- Record value-blind discrepancy evidence with exact paths, task counts, and gate classifications.
- Reopen unresolved cloud mutation and full-suite verification gates in an active corrective record.
- Preserve the archived changes as immutable history and avoid all unapproved cloud, personal-data, or repository mutations.

## Capabilities

### New Capabilities

- `archive-integrity-reconciliation`: Evidence-backed detection and correction planning for archived task ledgers that overstate completion.

### Modified Capabilities

None.

## Impact

- Affected boundary: `/Users/androidteam/Developer/openspec-store/openspec/changes/archive/` is read-only historical evidence; the new active change directory is the sole writable planning and evidence surface.
- No archived file, cloud path, personal data, active repository, or test configuration is modified by this corrective change.

## Non-Goals

- Do not edit, move, delete, or rewrite archived changes.
- Do not perform cloud-drive, Trash, cache, or personal-data mutations.
- Do not mark the blocked Vitest suite green without a successful full-suite run or an explicitly approved policy.
- Do not infer missing provenance or fabricate task execution evidence.
