# ai-review-enhanced-scan Tasks

## 1. Configuration & Dependencies

- [x] 1.1 Add `enable_codescan: bool` field to `Settings` dataclass in `ai-review/src/ai_review/config/settings.py`
- [x] 1.2 Add `enable_codescan` loading in `Settings.from_env()`:

    ```python
    enable_codescan=get_bool_env(
        "AI_REVIEW_ENABLE_CODESCAN",
        get_bool_env("ENABLE_CODE_SCAN", True)
    ),
    ```

- [x] 1.3 Add `"codescan"` to `Settings.get_enabled_clis()` return list
- [x] 1.4 Add `code-daily-scan` dependency to `ai-review/pyproject.toml`:

    ```toml
    dependencies = [
        # ... existing deps ...
        "code-daily-scan",
    ]
    [tool.uv.sources]
    code-daily-scan = { path = "../code-daily-scan", editable = true }
    ```

- [x] 1.5 Add `ENABLE_CODE_SCAN=true` to `~/.tdt/.env` (or document in README)
  - **Resolution:** Documented in README per task 8.1-8.4 (complete)

## 2. Create CodeScanReviewer Module

- [x] 2.1 Create `ai-review/src/ai_review/reviewers/code_scan_reviewer.py`
- [x] 2.2 Implement `CodeScanReviewer(BaseReviewer)` class with:
  - `name: str = "codescan"`
  - `check_availability()` — verify `code_daily_scan` package is importable
  - `run(prompt_file, mode, cwd)` — invoke `MrScanOrchestrator` and return `ReviewResult`
- [x] 2.3 Add `platform: str` and `patterns_path: Path | None` to constructor
- [x] 2.4 Implement `_serialize_finding()` for Finding → markdown conversion
- [x] 2.5 Implement `_get_platform_from_project_id()` using `local_repo_paths` mapping

## 3. Finding Serialization

- [x] 3.1 Create severity mapping: P0/P1 → critical, P2 → high, P3 → medium, info → suggestion
- [x] 3.2 Format findings as markdown list: `- [{severity}] {file}:{line} - {message}`
- [x] 3.3 Include `rule_id` as prefix if available
- [x] 3.4 Handle empty findings → return "No code scan issues found"

## 4. GitLab Integration

- [x] 4.1 Create `GitLabReviewPoster` instance with marker `<!-- code-scan-review -->`
- [x] 4.2 Post findings comment after scan completes successfully
- [x] 4.3 Post error comment if scan fails (with error details)
- [x] 4.4 Handle "no issues" case with informational comment

## 5. Orchestrator Integration

- [x] 5.1 Import `CodeScanReviewer` in `ai-review/src/ai_review/reviewers/__init__.py`
- [x] 5.2 Update `ReviewOrchestrator._build_reviewers()`:

    ```python
    if settings.enable_codescan:
        repo_path = self._get_repo_path(payload.project_id)
        platform = self._get_platform_from_project_id(payload.project_id)
        reviewers["codescan"] = CodeScanReviewer(
            repo_path=repo_path,
            platform=platform,
            timeout_seconds=settings.review_timeout,
        )
    ```

- [x] 5.3 Add `_get_repo_path(project_id)` helper using `settings.local_repo_paths`
- [x] 5.4 Add `_get_platform_from_project_id(project_id)` helper:
  - Project 231 → "ios"
  - Project 232 → "android"

## 6. Error Handling

- [x] 6.1 Wrap `MrScanOrchestrator.run()` in try/except
- [x] 6.2 Catch `RuntimeError` (worktree failures) → `ReviewResult(status=FAILED, error=...)`
- [x] 6.3 Catch `ValueError` (invalid MR) → `ReviewResult(status=FAILED, error=...)`
- [x] 6.4 Catch `subprocess.TimeoutExpired` → `ReviewResult(status=FAILED, error=...)`
- [x] 6.5 Catch generic `Exception` → `ReviewResult(status=FAILED, error=str(exc))`
- [x] 6.6 Log errors at ERROR level with full traceback

## 7. Testing

- [x] 7.1 Create `ai-review/tests/reviewers/test_code_scan_reviewer.py`
- [x] 7.2 Test `check_availability()` with/without code-daily-scan installed
- [x] 7.3 Test `run()` with mock `MrScanOrchestrator` returning findings
- [x] 7.4 Test `run()` with empty findings → "No issues found"
- [x] 7.5 Test error handling: worktree failure, invalid MR, timeout
- [x] 7.6 Test `_serialize_finding()` with various severity levels
- [x] 7.7 Test `_get_platform_from_project_id()` mapping
- [x] 7.8 Test integration with orchestrator (mock settings)
- [x] 7.9 Run full test suite: `cd ai-review && uv run pytest`

## 8. Documentation

- [x] 8.1 Update `ai-review/README.md` with:
  - `ENABLE_CODE_SCAN` / `AI_REVIEW_ENABLE_CODESCAN` env var
  - `<!-- code-scan-review -->` comment marker
  - Example scan output
- [x] 8.2 Document platform detection (project ID 231/232)
- [x] 8.3 Add troubleshooting section for common errors
- [x] 8.4 Update health check to include `codescan` in `reviewer_enablement`

## 9. Bug Fixes

- [x] 9.1 Fix duplicate codescan reviewer execution (was added both in `_build_reviewers` loop AND separately in `_build_reviewer_plans`)
- [x] 9.2 Add `metadata_path` to `ReviewerPlan` for codescan to read JSON context
- [x] 9.3 Write `metadata.json` sidecar file alongside prompt files for codescan
- [x] 9.4 Update `BaseReviewer.run()` signature to accept optional `metadata_path`
- [x] 9.5 Update `CodeScanReviewer` to read metadata from sidecar JSON instead of markdown prompt
- [x] 9.6 Fix `_read_metadata()` to use the provided `metadata_path` parameter
- [x] 9.7 Update all reviewers and tests to match new `run()` signature

## 10. Exact Revision Context

- [x] 10.1 In `ai-review/src/ai_review/prompts/builder.py`, propagate `worktree_path` and `commit_sha` into the code-scan metadata sidecar
- [x] 10.2 In `ai-review/src/ai_review/reviewers/code_scan_reviewer.py`, require both fields and remove silent fallback to the long-lived repository checkout for MR scans
- [x] 10.3 Verify the prepared checkout exists and `git rev-parse HEAD` equals the reviewed SHA before invoking `MrScanOrchestrator`
- [x] 10.4 Return a failed reviewer result and post a non-clean error comment for missing or mismatched revision context
- [x] 10.5 Replace the current `worktree_path.parent` repository assumption with explicit prepared checkout and repository-root semantics; do not infer a bare repository from the worktree directory layout

## 11. Scan Execution Evidence

- [x] 11.1 In `code-daily-scan/src/code_daily_scan/orchestrator_mr.py`, compute requested, supported-extension, existing, and missing file sets before scanning
- [x] 11.2 Record loaded-rule counts by category and total without changing individual rule detection semantics
- [x] 11.3 Add a namespaced execution-evidence section containing requested-file, eligible-file, existing-file, scanned-file, loaded-rule, pre-Phase-3 finding, post-Phase-3 finding, skip-reason, and degradation fields to the existing report dictionary
- [x] 11.4 Preserve the exact `(findings, report)` return shape and existing Phase 3 report keys for standalone MR/branch CLI compatibility
- [x] 11.5 Preserve Phase 3 degradation reasons separately from detector execution status in the returned MR scan report
- [x] 11.6 Keep unsupported assets such as Android JSON files visible as ineligible rather than counting them as scanned

## 12. Outcome Classification and Logging

- [x] 12.1 In `CodeScanReviewer`, publish "No code scan issues found" only for an exact-SHA, non-degraded run with at least one existing eligible file and at least one loaded rule
- [x] 12.2 Publish an informational skipped result when there are no changed files or when changed files exist but none are eligible for the platform scanner
- [x] 12.3 Publish a degraded result when some eligible files are missing or Phase 3 is degraded, preserving findings and identifying the degraded stage; fail when all eligible files are missing
- [x] 12.4 Publish a failed result when no rules load or revision integrity cannot be established
- [x] 12.5 Emit one structured `codescan_execution_summary` log event with MR identity, revision identity, all execution counts, outcome, and reasons

## 13. Regression Tests

- [x] 13.1 Add `PromptBuilder` tests proving `worktree_path` and `commit_sha` survive metadata serialization
- [x] 13.2 Add `CodeScanReviewer` tests for exact-SHA success, missing metadata, mismatched HEAD, and no repository fallback
- [x] 13.3 Add `MrScanOrchestrator` tests for mixed Kotlin/JSON changes, all-unsupported changes, partially and wholly missing eligible files, zero loaded rules, and clean zero-finding execution
- [x] 13.4 Add compatibility tests proving existing CLI callers still unpack `(findings, report)` and existing Phase 3 report keys remain available
- [x] 13.5 Add integration coverage proving an empty finding list cannot produce a clean comment without eligible-file, loaded-rule, exact-SHA, and non-degraded Phase 3 evidence
- [x] 13.6 Run focused tests in both repos, then `uv run pytest` for `ai-review` and `code-daily-scan`
- [x] 13.7 Run `ruff check . --fix`, `ruff format .`, and strict mypy checks in both repos

## 14. Deployment and Operational Verification

- [x] 14.1 Deploy the MR-review runtime with `cd ai-review && bash scripts/deploy.sh --require-clean`; this copies both `ai-review` and `code-daily-scan` into the launchd runtime and must not be replaced by `code-daily-scan/scripts/deploy.sh`
- [x] 14.2 Under `deployments/ai-review/app/.venv`, verify imported `ai_review` and `code_daily_scan` module paths resolve inside `deployments/ai-review`, dependency snapshots match source, `/health/full` is healthy, and exactly one launchd listener serves port 8090
- [x] 14.3 Rebuild/restart the separate scheduler runtime with `cd agent-core && docker compose up --build -d scheduler`; verify `/scheduler/health` and in-container `code_daily_scan` module provenance because the long-running process must reload bind-mounted source
- [x] 14.4 Re-trigger MR 23833 at commit `db04a3df71e4bc24f841cd410d862db112625420` and verify logs show eligible Kotlin files, loaded rules, exact checkout SHA, and detector/Phase 3 status
- [x] 14.5 Verify the GitLab code-scan comment reports findings, verified clean, skipped, degraded, or failed without conflating outcomes
- [x] 14.6 Confirm launchd logs contain one `codescan_execution_summary` event for the retriggered MR and no silent clean result
- [x] 14.7 Roll back by redeploying the prior known-good ai-review and scanner source revisions, then rebuilding/restarting the scheduler; verify both runtime module paths and health checks after rollback
