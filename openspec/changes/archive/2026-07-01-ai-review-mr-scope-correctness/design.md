# MR Review Diff Scope Correctness — Design

## Context

The 2026-06-16 review of MR `pspl/poems-mobile3-android!23389` revealed that
`ai-review` can post reviews with wildly wrong diff scope. GitLab shows 1
file changed for the MR, but the AI review ran against a 52-file diff
because the worktree prepare step timed out and the resolver silently
fell back to the local source repo. The local tracking branch was 57
commits behind origin, so the diff against the stale local tracking
branch returned 52 files.

This is a correctness bug. The AI reviewers (claude, codescan) reported
false findings on files unrelated to the MR. We have no way to know how
many other MRs have been reviewed with the same bug; the symptom is
silent.

## Goals / Non-Goals

**Goals:**

- Correct diff scope in all review paths (worktree, local, GitLab API).
- Detect and address the root cause: macOS worktree slowness on
  repos with many stale worktree entries.
- Lock in the fix with regression tests that exercise the failure mode.
- Preserve existing behavior when the worktree prepare succeeds
  (local_git is still preferred; it's faster than the API).

**Non-Goals:**

- Switching the default diff source to GitLab API (it costs API quota).
- Auto-cleaning up `_remove_existing` worktrees on a periodic basis
  (out of scope; the per-prepare pruning is enough for the observed
  scale of 25+ entries).
- Adding a CLI to manually trigger a worktree cleanup.

## Decisions

### D1. Skip local_git when worktree prepare fails

- **Decision**: When `GitWorktreeManager.prepare()` raises, the
  `ReviewContextResolver` MUST set `worktree_failed=True` and skip
  `_load_local_diffs`. The `if not diffs:` block at the bottom of
  `resolve()` then consults `_load_gitlab_compare` as the only
  fallback.
- **Why**: The local source repo's tracking branches can be many
  commits behind origin. A diff against the stale local tracking
  branch produces a flood of false changes. The GitLab API is the
  source of truth for MR scope.
- **Alternatives considered**:
  - Always use GitLab API as fallback (rejected: doubles API quota
    on every degraded review; the slow `git diff` is still cheaper
    than a network round-trip when the tracking branch is up to date).
  - Re-fetch the target branch before running local_git (rejected:
    adds latency; the GitLab API path is already the proven correct
    fallback).

### D2. Auto-prune stale worktrees when count > threshold

- **Decision**: When `GitWorktreeManager.prepare()` is called and the
  parent repo has more than `STALE_WORKTREE_PRUNE_THRESHOLD` (default
  16) worktrees registered, run `git worktree remove --force` on any
  whose path no longer exists on disk, then `git worktree prune`.
- **Why**: This is the dominant contributor to the 60s timeout. macOS
  `git worktree add` is slow when there are many stale entries in
  `.git/worktrees/`. Pruning them keeps the operation fast.
- **Threshold choice**: 16 is empirically above the expected steady-
  state count (2 prior worktrees per active MR * ~8 active MRs) and
  well below the 25+ count that triggered the timeout. Operators can
  raise or lower it as a class attribute.
- **Best-effort**: All prune operations are wrapped in
  `try/except (CalledProcessError, TimeoutExpired, OSError)`. A prune
  failure MUST NOT block the new worktree add — it just means the
  next add will be slow.
- **Alternatives considered**:
  - Periodic background cleanup task (rejected: more moving parts;
    per-prepare is sufficient at our MR volume).
  - Drop the threshold and always prune (rejected: adds latency to
    the happy path; we don't want every review to pay the prune cost).

### D3. Additive `pruned_stale_count` field on `WorktreeCheckout`

- **Decision**: Add an optional `pruned_stale_count: int = 0` field to
  the `WorktreeCheckout` dataclass. Callers can log or alert on a
  non-zero value as a signal that the parent repo has accumulated
  stale worktree entries.
- **Why**: Without observability, a slow `git worktree add` that
  succeeds in 5s today might silently regress to 60s+ next week. The
  field makes the trend visible.
- **No breaking change**: existing call sites that destructure only
  `path` and `created` continue to work.

### D4. Prefer `origin/<branch>` over bare local tracking branch

- **Decision**: `_resolve_branch_ref` first tries `origin/<branch>`
  via `git rev-parse --verify origin/<branch>`. If that resolves, the
  `origin/...` ref is returned. Only if the `origin/...` ref does not
  exist does the resolver fall back to the bare branch name.
- **Why**: Even within a successfully prepared worktree, the bare
  `release/v3.3.54_develop_27_06_2026` ref can be many commits behind
  `origin/release/...`. A diff against the stale bare ref produces a
  flood of false changes. The `origin/...` ref is updated by every
  `git fetch` and is the correct base for MR diffs.
- **Source fallback chain**: `_resolve_source_ref` first tries the
  branch ref chain, then falls back to the literal `commit_sha` so
  that MRs whose source branch was force-pushed or deleted still get a
  valid diff.
- **Regression test**:
  `test_review_context_resolver_prefers_origin_ref_over_stale_local_tracking`
  in `tests/test_review_context.py` exercises this path with a bare
  repo where `main` and `origin/main` resolve to different SHAs.

### D5. Cross-check local_git diff against GitLab API diff

- **Decision**: After `_load_local_diffs` returns, the resolver also
  calls `_load_gitlab_compare` and compares the file lists. When the
  local_git diff has strictly more files than the GitLab API diff and
  the inflation factor is at least `_MIN_INFLATION_FACTOR` (default
  2.5), the resolver switches to the GitLab API result, sets
  `diff_source=GITLAB_COMPARE`, and marks the context as
  `degraded_step="local_diff_stale"`.
- **Why**: `_fetch_branch` inside `GitWorktreeManager.prepare()` uses
  `check=False` and a 60s timeout. When the fetch fails silently (e.g.
  the parent repo has 25+ stale worktree entries, the network is
  slow, or the remote ref is locked), the `origin/<target>` ref
  remains stale, and D4 alone cannot catch it. The cross-check turns
  the silent fetch failure into a visible degradation.
- **Why not always use GitLab API?** GitLab API returns the diff as
  plain text without rename detection or hunks suitable for
  hunk-level review prompts. Local_git is preferred when correct
  because it produces higher-quality diffs and is cheaper.
- **Symptom observed**: MR 23318 (poems-mobile3-android, 2026-06-16)
  had 46 files per GitLab API but local_git produced 4592 files
  because the local tracking branch was 3000+ commits behind origin.
  After D5, the resolver correctly returns the 46-file diff and marks
  the run as `degraded_step=local_diff_stale`.
- **Regression tests**:
  `test_local_diff_looks_stale_detects_inflated_local_count` and
  `test_review_context_resolver_prefers_gitlab_when_local_diff_is_stale`
  in `tests/test_review_context.py`.

## Architecture

### Before (broken)

```
ReviewContextResolver.resolve()
  ↓
GitWorktreeManager.prepare()  ← times out > 60s
  ↓ (degraded_step = "worktree_prepare", but...)
  ↓
_load_local_diffs(repo_path=source_repo)  ← USES STALE LOCAL TRACKING BRANCH
  ↓
diff_source = LOCAL_GIT (WRONG)
  ↓
Reviewers see 52 files instead of 1
```

### After (fixed)

```
ReviewContextResolver.resolve()
  ↓
GitWorktreeManager.prepare()
  ├─ _maybe_prune_stale_worktrees(repo)  ← NEW: prune if > threshold
  ↓
  ├─ if succeeds: load local diffs from worktree (correct)
  └─ if fails:
       ├─ log "worktree_fallback_skipping_local_git"
       └─ skip _load_local_diffs entirely
  ↓
_load_local_diffs()
  ├─ _resolve_branch_ref() prefers origin/<branch>  ← D4
  └─ cross-check vs GitLab API                       ← D5
       └─ if local_git has 2.5x+ more files → use GitLab API
  ↓
if not diffs:  _load_gitlab_compare()  ← CORRECT FALLBACK
  ↓
diff_source = GITLAB_COMPARE (when fallback used)
```

## Test Plan

1. **Unit test**: `test_worktree_fallback_skips_local_git_to_avoid_stale_branch_diffs`
   - Patch `worktree_manager.prepare` to raise
   - Spy on `_load_local_diffs` to assert it is NEVER called
   - Mock `_load_gitlab_compare` to return a 1-file diff
   - Assert `diff_source == GITLAB_COMPARE` and `changed_files == [the right file]`
2. **Unit test**: `test_prepare_prunes_stale_worktrees_above_threshold`
   - Lower the threshold to 2
   - Create a worktree, delete its directory on disk
   - Create a fresh worktree
   - Trigger another prepare() and assert that `git worktree remove`
     was called for the orphan
3. **Existing tests**: after Tier 1/2/3, the suite grew to 16 worktree
   tests + 13 review_context tests (29 total; originally 9 + 11 = 20).
   Tier 1/2/3-specific tests are listed in `tasks.md` §6.4, §7.4,
   and §8.4.
4. **Unit test**: `test_review_context_resolver_prefers_origin_ref_over_stale_local_tracking`
   - Build a bare repo where `main` is 1 commit and `origin/main` is
     2 commits ahead
   - Create a feature branch from `origin/main` with 1 new file
   - Resolve context and assert `changed_files == [feature.py]`
5. **Unit test**: `test_local_diff_looks_stale_detects_inflated_local_count`
   - Direct tests of the staticmethod that decides when local_git
     looks stale relative to the GitLab API
6. **Unit test**: `test_review_context_resolver_prefers_gitlab_when_local_diff_is_stale`
   - Mock `_load_local_diffs` to return 52 files
   - Mock `_load_gitlab_compare` to return 2 files
   - Assert resolver switches to `diff_source=GITLAB_COMPARE` and
     `degraded_step=local_diff_stale`
7. **End-to-end verification** (post-deploy):
   - MR 23396 (poems-mobile3-android): was 60+ files, now 2 files
     (`local_git`, not degraded)
   - MR 23397 (poems-mobile3-android): was 76 files, now 6 files
     (`local_git`, not degraded)
   - MR 23318 (poems-mobile3-android): was 4592 files, now 46 files
     (`gitlab_compare`, degraded_step=local_diff_stale)

### D6. Observable fetch failures via structlog warnings

- **Decision**: `_fetch_branch` and `_fetch_commit` now capture the
  `subprocess.run` result and emit `logger.warning` with `argv`,
  `returncode`, `stderr`, and relevant identifiers when the fetch fails.
- **Why**: `check=False` silently swallowed errors. With Tier 2 adding
  target-branch fetches and Tier 3 adding retry fetches, operators need
  to see which fetches fail and why — network auth, timeout, locked ref,
  or unknown. This is the observability signal that justifies the more
  invasive Tier 3 retry logic.
- **Log events**: `worktree_fetch_branch_failed`, `worktree_fetch_commit_failed`.
- **Behavior unchanged**: callers still receive no exception. This is pure
  observability.

### D7. Proactive target-branch fetch in `prepare()`

- **Decision**: `GitWorktreeManager.prepare()` now accepts an optional
  `target_branch` parameter. When provided and different from the source
  branch, `_fetch_branch` is called for the target ref as well.
- **Why**: `_resolve_branch_ref` prefers `origin/<branch>` over the bare
  ref, but `origin/<target>` was never fetched in the original design.
  On poems-mobile3-android, a typical MR targets
  `release/v3.3.54_develop_27_06_2026` which may not have been fetched
  since the last time *any* MR targeted it — potentially days ago. The
  stale target ref produces a diff of all changes since that point, not
  just the MR's changes.
- **Cost**: one additional `git fetch` per handoff (~1-2s wall clock).
  At ~25 MRs/day, this adds ~30s/day — negligible.
- **Skip condition**: when `target_branch == source_branch`, the target
  fetch is skipped to avoid a redundant fetch.

### D8. Retry-with-refresh when local diff is stale

- **Decision**: When `_local_diff_looks_stale` fires (local_git has 2.5x+
  more files than GitLab API), the resolver calls
  `worktree_manager.refresh_target_ref()` and re-runs `_load_local_diffs`
  once. If the retry succeeds (local diff is now clean), the result is
  `diff_source=LOCAL_GIT` and the context is **non-degraded**. If the
  refresh fails or the retry still shows staleness, fall back to GitLab
  API and mark degraded.
- **Why**: Tier 2 eliminates the common case (target ref was never
  fetched). But a race remains: between `prepare()` and the first
  `_load_local_diffs` call, new commits can land on the target branch,
  making `origin/<target>` stale again. The retry recovers from this
  transient condition without requiring a second full `git fetch` upfront.
- **Retry cap**: `_STALE_RETRY_MAX = 1`. One retry is sufficient; more
  retries indicate a persistent condition (network, auth, or extremely
  active target branch) that GitLab API will handle correctly.
- **Log events**: `local_git_diff_stale_retrying_with_refresh` (info),
  `local_git_diff_stale_using_gitlab` (warning, only on exhausted retry).
- **Regression tests**:
  `test_review_context_resolver_retries_with_refresh_on_stale_diff` and
  `test_review_context_resolver_falls_back_after_failed_refresh`.

## Architecture (post-Tier-3)

```
ReviewContextResolver.resolve()
  ↓
GitWorktreeManager.prepare()
  ├─ _fetch_branch(source_branch)         ← Tier 1: logs on failure
  ├─ _fetch_commit(commit_sha)            ← Tier 1: logs on failure
  ├─ _fetch_branch(target_branch)         ← Tier 2: new, avoids stale target
  ├─ _maybe_prune_stale_worktrees()       ← D2
  └─ git worktree add [source, origin/src, ...]
       └─ if fails: degraded_step = "worktree_prepare"
  ↓
_load_gitlab_compare()                    ← called first in Tier 3 retry loop
  ↓
while True:
  _load_local_diffs(worktree, source, target)
  ├─ _resolve_branch_ref() prefers origin/<target>  ← D4
  └─ _local_diff_looks_stale() ?
       ├─ No  → LOCAL_GIT, non-degraded ✓
       └─ Yes → refresh_target_ref(target)  ← Tier 3 retry
                    ├─ Success → retry _load_local_diffs
                    └─ Failure → break → GITLAB_COMPARE, degraded ✓
```

## Risks / Trade-offs

- **Tier 2 latency**: +1 fetch (~1-2s) per handoff. Below noise threshold.
- **Tier 3 retry latency**: worst case adds one extra `_load_local_diffs`
  call (~100-500ms) on degraded reviews. Not significant.
- **Tier 1 log volume**: one warning per failed fetch. At steady state
  with no failures, zero extra log lines. With failures, the signal is
  valuable for diagnosis.
- **Non-breaking API**: `target_branch` defaults to `None`. Existing
  callers of `prepare()` (tests, any direct callers) are unaffected.

## Verification Results (2026-06-27)

Post-deploy production verification confirmed the three-tier design works
end-to-end. Full results in `tasks.md § 10`.

| Metric | Pre-deploy | Post-deploy |
|--------|-----------|-------------|
| Degraded rate (last 7 days) | 46% (327/698) | 5% (1/17) |
| local_git diff_source % (post-deploy) | n/a | 94% (16/17) |
| local_git vs GitLab API file counts | n/a | 6/6 match exactly |
| Worktrees on disk after 35 reviews | 0 | 0 |
| Tier 1 warning logs in production | 0 | 4 (all from synthetic tests) |

The `ai-review-mr-scope-correctness` change is verified complete.
Ongoing task 9.3 is the only remaining item: monitor
`worktree_fetch_branch_failed` and `worktree_refresh_target_ref_failed`
in production logs for 48 hours.

