# mr-review-orchestration — Diff Scope Correctness

> **Capability**: `mr-review-orchestration`
> **Status**: Modified
> **Change**: `ai-review-mr-scope-correctness`

## Purpose

Ensures the AI review's diff source always reflects the actual MR scope
(GitLab's view of what changed in the MR), never the local source repo's
view of the source-vs-target-branch divergence.

## ADDED Requirements

### Requirement: Worktree fallback MUST use GitLab API, not local_git

The `ReviewContextResolver` MUST skip the local `git diff` path when the
worktree manager's `prepare()` method raises an exception. When the worktree
prepare fails, the resolver SHALL set `worktree_failed = True` and MUST NOT
call `_load_local_diffs()`. The fallback to `_load_gitlab_compare()` (at the
bottom of `resolve()`) SHALL be the only diff source consulted. The system
MUST emit a structlog event with the key `worktree_fallback_skipping_local_git`
and the fields `handoff_id`, `mr_iid`, and `degraded_reason` for every
worktree fallback.

#### Scenario: worktree prepare raises

- **WHEN** `GitWorktreeManager.prepare()` raises `RuntimeError`
- **AND** `ReviewContextResolver.resolve()` is called with that payload
- **THEN** `_load_local_diffs()` is NOT called
- **AND** `diff_source = DiffSource.GITLAB_COMPARE`
- **AND** `degraded_step = "worktree_prepare"`
- **AND** a `worktree_fallback_skipping_local_git` log event is emitted

### Requirement: Stale worktree auto-pruning

The `GitWorktreeManager.prepare()` method MUST prune stale worktree entries
from the parent repo before running `git worktree add` when the count of
registered worktrees exceeds `STALE_WORKTREE_PRUNE_THRESHOLD` (default 16).
A "stale worktree" is defined as a worktree whose registered path no longer
exists on disk. The pruning step MUST be best-effort: a failure to remove a
single stale worktree or to run `git worktree prune` MUST NOT block the new
`git worktree add` invocation. The `WorktreeCheckout` dataclass MUST include
a `pruned_stale_count: int = 0` field.

#### Scenario: prune runs above threshold

- **GIVEN** the parent repo has > 16 registered worktrees
- **AND** at least one registered worktree path no longer exists on disk
- **WHEN** `GitWorktreeManager.prepare()` is called
- **THEN** `git worktree remove` is called for each stale path
- **AND** `git worktree prune` is called after
- **AND** `WorktreeCheckout.pruned_stale_count` reflects the count removed

### Requirement: Branch ref resolution MUST prefer `origin/<branch>`

The `_resolve_branch_ref` helper MUST first try to resolve `origin/<branch>`
and only fall back to the bare branch name when `origin/<branch>` does not
exist. The bare local tracking branch can be many commits behind
`origin/<branch>`, and a diff against a stale bare ref produces a flood of
false-positive file changes not part of the MR. The source ref resolver MUST
additionally fall back to the literal `commit_sha` when neither
`origin/<source>` nor `<source>` resolve.

#### Scenario: origin/ref takes precedence over bare ref

- **GIVEN** a local repo where bare `main` and `origin/main` resolve to different SHAs
- **WHEN** `_resolve_branch_ref(repo, "main")` is called
- **THEN** `"origin/main"` is returned (not bare `"main"`)

#### Scenario: commit_sha fallback when branch does not exist

- **GIVEN** `origin/feature/x` and `feature/x` both fail `git rev-parse`
- **WHEN** `_resolve_source_ref(repo, "feature/x", "abc1234")` is called
- **THEN** `"abc1234"` is returned

### Requirement: Cross-check local_git diff against GitLab API

When `_load_local_diffs()` returns a non-empty diff, the resolver MUST also
call `_load_gitlab_compare()` and compare the two file lists. The resolver
MUST prefer the GitLab API result and set `diff_source = GITLAB_COMPARE`
with `degraded_step = "local_diff_stale"` when: the GitLab API returned a
non-empty file list, AND the local_git file list has strictly more entries,
AND the inflation factor is at least `_MIN_INFLATION_FACTOR` (default 2.5).
The resolver MUST emit `local_git_diff_stale_using_gitlab` with `handoff_id`,
`mr_iid`, `local_count`, and `gitlab_count` whenever this switch occurs.

#### Scenario: inflated local diff triggers GitLab API fallback

- **GIVEN** `_load_local_diffs()` returns 50 changed files
- **AND** `_load_gitlab_compare()` returns 2 changed files
- **WHEN** `_local_diff_looks_stale([50 files], [2 files])` is evaluated
- **THEN** `True` is returned (inflation factor = 25 >= 2.5)
- **AND** the resolver switches to GitLab API result

#### Scenario: matching diff does not trigger fallback

- **GIVEN** `_load_local_diffs()` returns 2 changed files
- **AND** `_load_gitlab_compare()` returns 2 changed files
- **WHEN** `_local_diff_looks_stale([2 files], [2 files])` is evaluated
- **THEN** `False` is returned (no inflation)

### Requirement: Fetch failures MUST be observable

The `GitWorktreeManager._fetch_branch()` and `_fetch_commit()` methods MUST
emit a structlog warning event when the underlying `git fetch` subprocess returns
a non-zero exit code. The event MUST include the `argv` list, `returncode`,
`stderr` output, `repo_path`, and the relevant branch or commit identifier.

#### Scenario: fetch failure emits warning log

- **GIVEN** `git fetch origin refs/heads/nonexistent:refs/remotes/origin/nonexistent` exits 128
- **WHEN** `_fetch_branch(repo, "nonexistent")` is called
- **THEN** a structlog warning with key `worktree_fetch_branch_failed` is emitted
- **AND** the event includes `argv`, `returncode`, `stderr`, `repo_path`, `branch`

### Requirement: prepare() MUST fetch the target branch ref

The `GitWorktreeManager.prepare()` method MUST accept an optional `target_branch`
parameter. When provided and different from the source branch, `prepare()` MUST
call `_fetch_branch()` for the target ref, ensuring `origin/<target>` is current
before `_resolve_branch_ref` uses it as the diff base.

#### Scenario: target_branch causes additional fetch

- **WHEN** `prepare(repo, "feature/x", handoff_id, target_branch="main")` is called
- **THEN** `origin/main` exists in `repo` (fetch succeeded)
- **AND** `origin/feature/x` exists in `repo` (fetch succeeded)

### Requirement: Stale diff detection MUST retry with ref refresh

The resolver MUST attempt to recover from a stale local diff by refreshing the
target ref and retrying `_load_local_diffs()` once before falling back to the
GitLab API. When `_local_diff_looks_stale()` detects that the local_git diff
has 2.5x+ more files than the GitLab API diff, the resolver SHALL call
`worktree_manager.refresh_target_ref()` with the target branch and retry
`_load_local_diffs()` once. If the retry counter exceeds `_STALE_RETRY_MAX`
(default 1) or `refresh_target_ref()` returns False, the resolver SHALL fall
back to GitLab API and mark the context degraded. If the retry succeeds, the
resolver SHALL set `diff_source = DiffSource.LOCAL_GIT` and MUST NOT mark the
context degraded. The resolver SHALL emit `local_git_diff_stale_retrying_with_refresh`
(info) when entering the retry path, and `local_git_diff_stale_using_gitlab`
(warning) only when exhausted.

#### Scenario: retry succeeds — LOCAL_GIT, non-degraded

- **GIVEN** first `_load_local_diffs()` returns 50 files (stale)
- **AND** `_load_gitlab_compare()` returns 2 files
- **AND** `refresh_target_ref()` returns `True`
- **WHEN** the retry `_load_local_diffs()` returns 2 files (now clean)
- **THEN** `diff_source = DiffSource.LOCAL_GIT`
- **AND** `degraded = False`
- **AND** `local_git_diff_stale_retrying_with_refresh` info log is emitted

#### Scenario: retry exhausted — GITLAB_COMPARE, degraded

- **GIVEN** first `_load_local_diffs()` returns 50 files (stale)
- **AND** `_load_gitlab_compare()` returns 2 files
- **AND** `refresh_target_ref()` returns `False`
- **WHEN** `resolve()` completes
- **THEN** `diff_source = DiffSource.GITLAB_COMPARE`
- **AND** `degraded = True`
- **AND** `degraded_step = "local_diff_stale"`
- **AND** `local_git_diff_stale_using_gitlab` warning log is emitted

### Requirement: Diff source MUST reflect MR scope

The `ReviewContextResolver` MUST only set `diff_source = DiffSource.LOCAL_GIT` when the worktree prepare succeeded AND the local diff is not stale relative to the GitLab API. When the worktree prepare fails, the only valid diff sources are `DiffSource.GITLAB_COMPARE` (from `_load_gitlab_compare()`) and `DiffSource.UNAVAILABLE` (if the GitLab API also fails). `DiffSource.LOCAL_GIT` MUST NOT be set when the worktree prepare failed.

#### Scenario: LOCAL_GIT forbidden after worktree failure

- **WHEN** `GitWorktreeManager.prepare()` raises and `resolve()` completes
- **THEN** `context.diff_source` is NEVER `DiffSource.LOCAL_GIT`
