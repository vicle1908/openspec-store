# proposal.md

## Why

Android scan findings from `code-daily-scan` currently run daily across the entire codebase. When a developer opens a merge request (MR) or works on a feature branch, there is no lightweight way to:

1. Get a quick code quality signal on **just the changed files** before review
2. Focus on a **specific feature/module** (e.g., ewallet) without scanning everything
3. Write findings to a **dedicated, ephemeral spreadsheet tab** that doesn't pollute daily scan tabs
4. Optionally post a **summary comment on the MR itself** without triggering a full LLM-powered review

The `scan` command is repo-wide and slow; `ai-review` does LLM reasoning over diffs but doesn't write structured findings to sheets. There is a gap between "full daily scan" and "LLM review" — `scan-mr` and `scan-branch` fill it.

## What Changes

1. **`scan-mr` CLI command**: given a GitLab MR IID, fetch the changed files, run scanners scoped to those files, and write results to a `MR-{IID}` tab in the configured spreadsheet.

2. **`scan-branch` CLI command**: given source and target branch names, compare them using GitLab's `repository_compare` API, run scanners on changed files in a git worktree of the source branch, and write results to a `BRANCH-{slug}` tab.

3. **`--feature` option** (both commands): filter changed files to a specific package/path (e.g., `com/tdt/pmobile3/ewallet` for Android, `Modules/Profile/Ewallet` for iOS).

4. **Git worktree integration**: `MrScanOrchestrator` creates a detached worktree for the source branch, ensuring scans run on the correct code state.

5. **Feature tab naming**: when `--feature` is specified, the tab name includes the feature suffix (e.g., `BRANCH-modules-ewallet-develop-newdesignsystem-ComTdtPmobile3Ewallet`).

## Capabilities

### scan-mr
- `code-daily-scan scan-mr --mr-iid 23318 [--post-comment]` — fetch MR diff, scan changed files, write to tab
- `code-daily-scan scan-mr --mr-iid 23318 --feature "com/tdt/pmobile3/ewallet"` — scan only ewallet files
- `code-daily-scan scan-mr --mr-iid 23318 --dry-run` — preview findings without writing

### scan-branch
- `code-daily-scan scan-branch --source-branch develop_newdesign --target-branch develop [--feature "ewallet"]` — compare branches, optionally filter by feature
- `code-daily-scan scan-branch --source-branch develop_newdesign --target-branch develop --dry-run` — preview findings

## Impact

**Scope:** `code-daily-scan` repo only.

- Adds `gitlab_branch.py` — branch compare using `repository_compare` API
- Adds `source_branch` parameter to `MrScanOrchestrator` for worktree checkout
- Adds `feature` parameter to `MrScanOrchestrator` for package filtering
- Modifies `cli.py` — adds `scan-branch` command, `--feature` option to both commands
- Modifies `sheet_mr.py` — accepts both `MrInfo` and `BranchInfo` via Union type

**No impact on:**
- `ai-review` (shares SDK usage but no code changes)
- `tdt-core` (uses existing `GitlabClientFactory`)
- Daily `scan` command behavior
