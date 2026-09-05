## 1. Evidence & Preconditions

- [x] 1.1 Write evidence/evidence-identity.md recording: branch tip SHA `69bf758`, the 8 unique commits, and the content-diff proof that the reviews/ evidence equals main's archived `2026-08-25-repair-hermes-cron-run-reliability` (3 files 0 diff lines, agy.md whitespace-only). Verify: evidence file committed with matching diff output.
- [x] 1.2 Write evidence/symlink-correction.md correcting the prior dry-run: the 6 `~/orca/workspaces/agent-core/*` paths are symlinks to canonical repos (0 bytes), PROTECTED as live Orca registrations (referenced by orchestration.db worktree_ids). Verify: `readlink` output for all 6 recorded.
- [x] 1.3 Verify no live Orca session/process on the worktree: no processes matching `review-hermes-cron`, terminal records wtr_90bc36be1d8c/wtr_b42cde3b7cfb are stale (last update 2026-08-24). Verify: `ps` grep empty; DB check recorded.

## 2. Retirement Transaction (spec Decision 4 order)

- [x] 2.1 Remove the worktree: `git -C ~/Developer/openspec-store worktree remove ~/orca/workspaces/openspec-store/review-hermes-cron --force` (force justified: generated graphify-out dirt). Verify: `git worktree list` no longer shows it; directory gone.
- [x] 2.2 Delete the branch: `git -C ~/Developer/openspec-store branch -D review-hermes-cron`. Verify: `git branch` has no review-hermes-cron; deletion message records was=69bf758.

## 3. Empty Orca Dir Cleanup (DB-gated)

- [x] 3.1 Query orchestration.db for references to `~/orca/workspaces/tdt-core` and `~/orca/workspaces/tdt-scheduler` paths. Remove the dirs only if zero references; if referenced, record why they stay. Verify: query output + removal result (or retention reason) in evidence.

## 4. Final Verification

- [x] 4.1 Re-run the lifecycle dry-run with an updated observation set (review-hermes-cron now absent, symlink facts corrected) and confirm orca-space classification: symlinks PROTECTED, review-hermes-cron gone from scan, remaining paths unchanged. Verify: new manifest in evidence with classifications.
- [x] 4.2 Confirm store clean and archived: tasks ticked, `openspec validate` passes, archive and commit. Verify: `git status` clean in openspec-store after archive.
