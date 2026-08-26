# Withdrawal: add-ntu-ai-keynote-deck (Central Store)

**Status:** Withdrawn — duplicate lifecycle migrated to repo-local ownership
**Date:** 2026-08-26

## Decision

The central-store OpenSpec change `add-ntu-ai-keynote-deck` is withdrawn
from `~/Developer/openspec-store/openspec/changes/`. A dedicated Git
repository (`~/Developer/ntu-keynote`) now owns the same-named change as its
sole authoritative OpenSpec lifecycle. The central-store copy is withdrawn to
prevent two active same-ID plans from existing independently.

Archive was **not** invoked: 0/28 tasks completed (zero checked items in
`tasks.md`), which does not meet the archive gate.

## Withdrawn Change (Central Store)

| Field | Value |
|---|---|
| ID | `add-ntu-ai-keynote-deck` |
| Former path | `openspec/changes/add-ntu-ai-keynote-deck/` |
| Files | `proposal.md`, `design.md`, `tasks.md`, `.openspec.yaml` |
| Created | 2026-08-25 |
| Task state | 0/28 (none completed) |
| skip_specs | `true` |
| Git commits touching the change | `8a49859` (add), `58bc460` (incorporate review) |

All 28 tasks in `tasks.md` are unchecked (`- [ ]`). No completed tasks or
delta specs were recorded in the central-store change. Git history
(`8a49859`, `58bc460`) preserves the original planning artifacts.

## Superseding Change (Repo-Local)

| Field | Value |
|---|---|
| Repo | `~/Developer/ntu-keynote` |
| Change ID | `add-ntu-ai-keynote-deck` (repo-local OpenSpec) |
| Authoritative branch | `feat/add-ntu-ai-keynote-deck` |
| Worktree | `.worktrees/add-ntu-ai-keynote-deck` |
| Immutable audit snapshot | `audit/visual-contract-986be2f155c32e981a5fec75f2033faecfaa7b87` |
| Task state | Active and unreleased; task ledger reconciliation pending |

The repo-local change defines 6 delta-spec capabilities:
`accessible-stage-presentation`, `browser-qualification-and-release-evidence`,
`factual-provenance-and-approval`, `keynote-content-and-language`,
`offline-keynote-runtime`, `timing-and-roundtable-handoff`.

The repo-local proposal explicitly establishes sole ownership:
*"the central `openspec-store` change is not modified or archived by this
change."*

The feature branch is actively owned by an external writer and continues to
receive normative requirement additions. An immutable audit snapshot
(`audit/visual-contract-986be2f...`) pins the contract boundary for
review purposes. The task ledger and evidence are subject to reconciliation
once the external writer hands off.

## Rationale

The keynote deliverable is a standalone content artifact (presentation deck)
with its own dedicated repository. The central store's role was initial
planning; the repo-local change in `~/Developer/ntu-keynote` establishes the
canonical lifecycle with 6 delta-spec capabilities and 30 delta specs.

The central store change had 0/28 completed tasks, no delta specs, and no
implementation. The repo-local change remains active and unreleased. This
withdrawal addresses the gap from the store side by removing the duplicate
rather than leaving two same-ID plans to drift.

## Evidence of Supersession

- Central store: 0/28 tasks completed, no delta specs, no implementation.
- Repo-local: dedicated repository with implementation and evidence commits,
  6 capabilities, 30 delta specs.
- The repo-local proposal explicitly does not modify or archive the central
  change — this withdrawal addresses that gap from the store side.
- The central change declares `skip_specs: true`; no central-store main
  specifications were synchronized or modified as part of this withdrawal.

## Disposition

- Change directory `openspec/changes/add-ntu-ai-keynote-deck/` removed from
  the central store via `git rm --sparse -r`.
- Git history retains provenance via commits `8a49859` and `58bc460`.
- No completed tasks or delta specs existed in the central-store copy.
- The repo-local change in `~/Developer/ntu-keynote` is unaffected.

## Impact

No production or spec behavior changed by this governance cleanup.
The central store's main specs remain unchanged. The repo-local change in
`~/Developer/ntu-keynote` is unaffected.
