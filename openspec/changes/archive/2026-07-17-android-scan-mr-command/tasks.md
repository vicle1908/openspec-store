# tasks.md

## Phase 0: Path format normalization (prerequisite — must be done before MR scanning)

- [x] **[HIGH] Normalize `Finding.file_path` to workspace-relative**
  - `GrepScanner._match_to_finding()` now uses `_workspace_rel_path(match.file_path, root)` for `file_path`
  - `root` is the worktree path, which mirrors the repo structure — paths are workspace-relative
  - Makes `Finding.file_path` workspace-relative for both daily scan and MR scan
  - **Verification:** Daily `scan` output in `last-run.json` must show workspace-relative paths

## Phase 1: Core scaffolding

- [x] **[HIGH] Add `changed_files: set[str] | None` to `GrepScanner` (R1)**
  - Added to `__init__`, post-filter applied in `scan()` when set
  - `MrScanOrchestrator` passes the set; scanner is filter-only, no `rg` change needed

- [x] **[HIGH] Create `code_daily_scan/gitlab_mr.py`**
  - `fetch_mr_changed_files(mr_iid, project) -> set[str]` — returns workspace-relative paths
  - `fetch_mr_info(mr_iid, project) -> MrInfo` dataclass (title, author, source_branch, target_branch, project_id)
  - `infer_project_from_git_remote(repo_path) -> str` (R5)
  - Uses `GitlabClientFactory.from_env()` — same factory as `ai-review`

- [x] **[HIGH] Create `code_daily_scan/orchestrator_mr.py`**
  - `MrScanOrchestrator(repo_path, patterns_path, changed_files)`
  - Same scanner list as `ScanOrchestrator`; passes `changed_files` to `GrepScanner`
  - Uses `WorktreeManager` to checkout source branch for accurate scanning
  - Returns findings with workspace-relative paths

- [x] **[HIGH] Create `code_daily_scan/gitlab_branch.py`**
  - `fetch_branch_info(source_branch, target_branch, project) -> BranchInfo` dataclass
  - Uses GitLab `repository_compare` API to get changed files between branches
  - Supports `--feature` filter for package-scoped scanning
  - Tab name: `BRANCH-{slug}` with optional `-{feature}` suffix

- [x] **[HIGH] Add `source_branch` parameter to `MrScanOrchestrator`**
  - `WorktreeManager` now accepts `branch` parameter to checkout correct branch
  - Fixes bug where scanning was done on wrong branch (defaulted to main)

- [x] **[HIGH] Add `feature` filter to `MrScanOrchestrator`**
  - `_filter_by_feature()` filters changed files by package/path prefix
  - Android: `--feature "com/tdt/pmobile3/ewallet"`
  - iOS: `--feature "Modules/Profile/Ewallet"`

## Phase 2: Sheet writing

- [x] **[HIGH] Modify `code_daily_scan/sheets/sheet_mr.py`**
  - `write_mr_findings()` now accepts both `MrInfo` and `BranchInfo` via Union type
  - Tab name from `ScanInfo.tab_name` (works for both types)

- [x] **[HIGH] Modify `cli.py` — add `scan-branch` command**
  - `@app.command("scan-branch")`
  - `--source-branch TEXT` (required), `--target-branch TEXT` (required), `--project TEXT`, `--feature TEXT`, `--dry-run`
  - Pipeline: `infer_project()` → `fetch_branch_info()` → `MrScanOrchestrator.run()` → `write_mr_findings()`

## Phase 3: CLI feature flag

- [x] **[MEDIUM] Add `--feature` option to both `scan-mr` and `scan-branch` commands**
  - `--feature TEXT` filters changed files to specific package/path
  - Tab name includes feature suffix when specified

## Phase 4: MR comment (optional)

- [x] **[MEDIUM] Add `--post-comment` flag to `scan-mr` command**
  - `_post_comment()` function imports `GitLabReviewPoster` from `ai_review.gitlab.review_posting` inside function body
  - Graceful fallback: `try/except ImportError` → log warning, skip

## Phase 5: Testing and verification

- [x] **[MEDIUM] Unit tests for `gitlab_mr.py`**
  - `test_fetch_mr_info_returns_mr_info`, `test_fetch_mr_info_not_found_raises_value_error`
  - `test_fetch_mr_info_api_error_raises_runtime_error`
  - `test_infer_project_from_git_remote`, `test_infer_project_raises_when_not_git_repo`
  - `test_changed_files_prefers_new_path`, `test_workspace_rel_path_*`

- [x] **[MEDIUM] Unit tests for `MrScanOrchestrator`**
  - `test_run_calls_phase3_process`, `test_run_uses_given_worktree_manager`
  - `test_phase3_called_with_findings`
  - `test_filter_by_feature`

- [x] **[MEDIUM] Unit tests for `sheet_mr.py`**
  - `test_build_mr_context_*`, `test_priority_counts_*`, `test_build_mr_tab_rows_*`
  - `test_write_mr_findings_dry_run_returns_preview`

- [x] **[MEDIUM] Unit tests for `gitlab_branch.py`**
  - `test_fetch_branch_info_returns_branch_info`, `test_fetch_branch_info_api_error`
  - `test_build_tab_name_with_feature`, `test_normalize_feature_name`

- [x] **[MEDIUM] Integration test — full `scan-branch` run**
  - CLI smoke test: `code-daily-scan scan-branch --help` confirms all options present

- [x] **[LOW] Verify `--dry-run` output**
  - `write_mr_findings()` returns `rows_preview` when `dry_run=True`

## Phase 6: Feature scans completed

- [x] **[HIGH] Android ewallet feature scan**
  - `scan-branch --source-branch modules/ewallet/develop_newdesignsystem --target-branch modules/ewallet/develop --feature "com/tdt/pmobile3/ewallet"`
  - Results: 169 findings (P0: 121, P1: 48)
  - Tab: `BRANCH-modules-ewallet-develop-newdesignsystem-ComTdtPmobile3Ewallet`
