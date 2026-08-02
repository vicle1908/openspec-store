# MR Review Diff Scope Correctness

## Why

The `ai-review` service has a silent failure mode that produces wrong diff scope
on every review when the worktree preparation step times out. Symptom observed
on 2026-06-16 for MR `!23389` in `pspl/poems-mobile3-android`:

- GitLab API: 1 file changed (`MeSettingsEnterNewEmail.kt`)
- ai-review logged diff: 10 files (orchestration handoff `daff3a29ee7f4505`)
  → 52 files (later handoff `dff024c3dbcd4d4f`) when worktree preparation
  fell back to the local source repo.

Root cause: when `git worktree add` times out (60s default), the resolver
silently falls back to using the **source repo** for `git diff`. The
`release/v3.3.54_develop_27_06_2026` local tracking branch on
`poems-mobile3-android` was 57 commits behind
`origin/release/v3.3.54_develop_27_06_2026`, so the diff returned 52 files
(divergence between stale local tracking branch and the source branch),
not the 1 file the MR actually changed. The 52-file diff was sent to
reviewers and surfaced as 4 false findings (e.g. comments about
`AccountDetailScreen.kt` lines 188/228/283, none of which the MR changed).

Two contributing factors:

1. **Worktree prepare frequently times out on macOS** when there are
   20+ stale `.git/worktrees/<n>` directories left over from prior
   handoffs. macOS `git worktree add` becomes slow on big repos.
2. **Fallback to local repo is unsafe** because the local tracking branch
   can be stale, and the source branch is fetched into a worktree only,
   not the parent repo.

## What Changes

1. **When worktree prepare fails, skip local_git entirely** and go straight
   to the GitLab API (`merge_request.changes()`). The GitLab API is the
   source of truth for MR scope and is not subject to local-branch drift.
2. **Prune stale worktrees** in the parent repo automatically when the
   number of registered worktrees exceeds a threshold (default 16). This
   addresses the timeout root cause and keeps `git worktree add` fast.
3. **Add a regression test** that asserts `_load_local_diffs` is never
   called when the worktree prepare raises.
4. **Add a regression test** for the worktree manager's stale-pruning path.

## Capabilities

### Modified Capabilities

- `mr-review-orchestration`: When worktree preparation fails, the diff
  source MUST be the GitLab compare API, not the local source repo. When
  the GitLab API is also unavailable, the context MUST be marked
  `degraded` with `diff_source=unavailable` (not silently using a stale
  local diff).
- `git-worktree-management`: When the number of registered worktrees
  exceeds a configurable threshold, the manager MUST prune stale entries
  (paths that no longer exist on disk) before adding a new one. The
  number of pruned worktrees MUST be recorded in the
  `WorktreeCheckout.pruned_stale_count` field for observability.

## Impact

- **Files affected**:
  - `ai-review/src/ai_review/review_flow/context.py` — new skip branch
  - `ai-review/src/ai_review/worktree/manager.py` — new `_maybe_prune_stale_worktrees` helper
  - `ai-review/tests/test_review_context.py` — regression test
  - `ai-review/tests/test_worktree_manager.py` — regression test
- **No breaking changes**: `WorktreeCheckout` gets an additive field
  (`pruned_stale_count`) with a default of 0.
- **Behavior change**: reviews produced from a degraded worktree path
  will now use the GitLab API for the diff (correct) instead of the
  local repo (often wrong). This may slightly increase GitLab API
  rate-limit pressure when the primary path fails; we accept this
  trade-off because correctness is more important than API quota.
- **Test coverage**: 2 new regression tests added. Existing 9+8
  tests still pass.
