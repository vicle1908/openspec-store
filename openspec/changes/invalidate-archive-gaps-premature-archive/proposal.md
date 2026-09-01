## Why

The corrective change `invalidate-archive-gaps-closure-fabrications` was moved to `openspec/changes/archive/2026-09-01-invalidate-archive-gaps-closure-fabrications/` (commit claim `d247e76`) while its own archived ledger records the opposite of archive-readiness: task 2.2 (omp `~/.omp/agent/models.yml` 0644→0600 ratify-or-revert) and task 2.3 (cline live sentinel) are UNCHECKED, and task 3.3's decision text states "leave the change ACTIVE … Archive is not permitted while 2.2 and 2.3 remain unresolved." The archive is therefore invalid per the change's own closure contract and the store's precedent (`invalidate-ntu-keynote-closure-fabrications`); the commit message's claims ("2.2 RATIFIED", "all gates closed") are contradicted by the archived bytes it shipped.

This change records the invalidity read-only. The archived directory stays byte-identical.

## What Changes

- Records a value-blind invalidity note (`evidence/premature-archive-record.json`) citing the archived ledger lines (2.2 unchecked, 2.3 unchecked, 3.3 "leave ACTIVE / archive not permitted") against the archived directory's location and the contradicting commit message.
- Restates, as the current authoritative gate state (carried from the archived ledger, unchanged):
  - 2.1: authorization verified (genuine user accepted-risk message, independently hash-verified against the primary Prime session), gate verification still pending — no live sentinel is independently verified in this lineage; archived live-sentinel claims and results remain untrusted and void pending fresh verification.
  - 2.2: OPEN — awaiting the owner's explicit ratify-or-revert decision; best-practice research is retained as a pending recommendation to RATIFY (keep 0600).
  - 2.3: OPEN/blocked — requires a user-owned cline auth session if a live sentinel is ever required.
- Adds one ADDED requirement to the existing `omniroute-closure-integrity` capability (synced from the same lineage): the archive-while-open void rule. That capability already forbids closing ticks citing unverifiable authorization and closure without recorded gate verification; the ADDED requirement extends it to the lifecycle contradiction, and the remaining existing requirements are cited rather than duplicated.

## Capabilities

### Modified Capabilities

- `omniroute-closure-integrity`: one ADDED requirement — a change SHALL NOT be archived while its ledger records open owner gates (void-if-archived rule); the delta also cites the existing requirements as the violated contract.

## Non-Goals

- Editing any archived byte.
- Releasing or verifying any gate, running any live probe, or deciding 2.2/2.3 on the owner's behalf.
- Re-litigating the 2.1 authorization (verified genuine by independent recomputation).
