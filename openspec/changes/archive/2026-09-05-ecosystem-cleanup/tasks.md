## 1. Audit Worktrees

- [x] 1.1 Audit agent-core worktrees: list all 14, identify which are orphaned (inside `.git/`, orca workers) vs active feature work. Verify with `git log main..branch` for each. Record findings. Verify: list produced with disposition per worktree.
- [x] 1.2 Audit webhook-receiver worktrees: list all 9, identify 4 detached-HEAD deploy sources and 3 nested worktrees. Verify with branch check. Record findings. Verify: list produced.
- [x] 1.3 Audit ai-review worktrees: list all 5, identify detached-HEAD and deploy source worktrees. Record findings. Verify: list produced.
- [x] 1.4 Audit tdt-scheduler worktrees: list all 5, check branch status. Record findings. Verify: list produced.
- [x] 1.5 Audit remaining repos (agent-harness, tdt-core, ops-automation-suite): check worktrees. Record findings. Verify: list produced.

## 2. Resolve tdt-core Branch

- [x] 2.1 Check if `fix/remove-api-key-env-loader-exemption` has unmerged commits vs main. If merged, delete branch. If unmerged, merge to main or preserve. Verify: `git -C ~/Developer/tdt-core branch --show-current` returns `main`.

## 3. Delete Stale Worktrees

- [x] 3.1 Delete all detached-HEAD worktrees (webhook-receiver × 4, ai-review × 1). Verify: `git worktree list` no longer shows detached HEAD entries.
- [x] 3.2 Delete orphaned agent-core worktrees (inside `.git/` dir, orca worker remnants). Verify: agent-core worktree count reduced to ≤2.
- [x] 3.3 Delete completed/stale webhook-receiver worktrees (deploy sources, health checks). Verify: webhook-receiver worktree count reduced to ≤1.
- [x] 3.4 Delete stale ai-review deploy worktrees. Verify: ai-review worktree count reduced to ≤1.
- [x] 3.5 Delete stale tdt-scheduler worktrees. Verify: tdt-scheduler worktree count reduced to ≤1.
- [x] 3.6 Delete stale agent-harness and ops-automation-suite worktrees if branches are merged. Verify: worktree counts at minimum.

## 4. Clean Uncommitted Changes

- [x] 4.1 Commit graphify-out changes in repos where they're dirty (agent-docs-sync, ai-harness-skills, code-daily-scan, jira-daily-reports, jira-epic-report, jira-skill, tdt-scheduler). Verify: `git status` clean for each.
- [x] 4.2 Remove orphaned untracked deploy source directories from webhook-receiver and ai-review main worktrees. Verify: `git status` no deploy directories listed.

## 5. Sync Missing Virtual Environments

- [x] 5.1 Run `uv sync` in ai-harness-skills. Verify: `.venv/` directory exists.
- [x] 5.2 Run `uv sync` in browser-cli. Verify: `.venv/` directory exists.
- [x] 5.3 Run `uv sync` in code-daily-scan. Verify: `.venv/` directory exists.

## 6. Verify tdt-scheduler Embedded Copies

- [x] 6.1 Compare embedded agent-core, jira-skill, code-daily-scan, jira-daily-reports directories in tdt-scheduler against their upstream repos. If stale, update or document divergence. Verify: comparison output produced.

## 7. Final Verification

- [x] 7.1 Run `git status` on all 19 Python repos — all should be on main/master with clean status (except harmless `.claude/` dirs). Verify: all repos report clean.
- [x] 7.2 Run `git worktree list` across all repos — total worktree count should be ≤10 (down from 35). Verify: count confirmed.
- [x] 7.3 Verify all repos with pyproject.toml have `.venv/`. Verify: no MISSING venvs (except tdt-scheduler which is Docker-built).
