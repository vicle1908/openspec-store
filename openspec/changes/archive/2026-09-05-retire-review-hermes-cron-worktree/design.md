## Context

The gated-cleanup spec (archived 2026-08-25) defines retirement as a gated transaction: Orca activity check → worktree removal → branch deletion, with OpenSpec paths handled by OpenSpec commands. This change is the first application of that transaction to a real path. Prior dry-run evidence for this path (`reclaimability_not_proven`) was based on the 8 unmerged commits; follow-up research proved those commits' final state is content-identical to main's archive of the underlying change, removing the blocker.

## Goals / Non-Goals

**Goals:**
- Retire the `review-hermes-cron` worktree and branch with a durable audit record
- Correct the prior dry-run's symlink mis-observation in evidence
- Stay strictly inside the gated-cleanup transaction order

**Non-Goals:**
- No deletion of the 6 orca symlinks (live registrations referenced by orchestration.db)
- No retention-inventory changes
- No touching of the archived change directory (immutable archive history)

## Decisions

### 1. Evidence-preservation method: record SHA, don't merge

**Decision:** Record branch tip `69bf758` and the identity proof in this change's evidence, then delete the branch. Do not merge into main.

**Rationale:** Merging 8 commits whose final state equals existing archive content would duplicate history with no information gain; the recorded SHA + identity diff is sufficient audit. Alternative considered (merge-then-delete) rejected: archive dirs are immutable and the commits touch only the archived change's files.

### 2. Empty orca dirs removed only with DB-reference proof

**Decision:** Check `orchestration.db` (`worker_terminal_resources.worktree_id`) for the two empty dirs before removal; remove only on zero references.

**Rationale:** They sit under `~/.orca` (retention: runtime state, PROTECTED); a DB-free proof that they are unregistered husks is the minimum bar for exception. The earlier research already showed `tdt-main`/`tdt-main-yaml-bootstrap` terminal records exist under `orca/workspaces/tdt-core/` — so these need the DB check, and if referenced, they stay.

### 3. Worktree removal before branch deletion

**Decision:** Follow spec transaction order exactly: verify no live terminal/process, `git worktree remove`, then `git branch -D`.

**Rationale:** Spec Decision 4 ordering; also matches the recorded lesson that worktree removal and branch deletion are separate transitions.

## Risks / Trade-offs

- **[Risk] Evidence value overlooked** → Mitigation: identity proof by content diff (3/4 files 0 diff lines, 4th trailing-whitespace only) recorded in evidence before any deletion; branch SHA recoverable until gc.
- **[Risk] Orca re-creates the worktree** → Mitigation: the two stale "owned" terminal records (wtr_90bc36be1d8c, wtr_b42cde3b7cfb) are noted; if Orca later errors on a missing worktree, the DB records name this change as the retirement authority.
- **[Risk] Empty-dir removal conflicts with Orca** → Mitigation: DB-reference check gates it; any reference means the dir stays.
