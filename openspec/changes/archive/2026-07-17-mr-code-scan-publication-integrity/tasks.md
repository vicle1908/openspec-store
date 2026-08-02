# MR Code Scan Publication Integrity Tasks

## 1. Authoritative MR diff snapshot (`ai-review`)

- [x] 1.1 Add `MrDiffSnapshot` dataclass in `ai-review/src/ai_review/models.py` carrying `project_id`, `mr_iid`, `target_branch`, `source_branch`, `head_sha`, `base_sha`, `diff_version_id`, `changed_files` (list of `MrDiffFile` with `old_path`, `new_path`, `status` [added/modified/renamed/deleted], and `changed_ranges`), and a `changed_lines_for(path)` helper returning the union of all changed ranges for that path.
- [x] 1.2 Extend `ReviewContextResolver.resolve` (`ai-review/src/ai_review/review_flow/context.py`) to resolve an `MrDiffSnapshot` once per intake through the existing `GitlabClientFactory` client and GitLab v4 merge-request versions/diffs APIs (`gl.http_list('/projects/{pid}/merge_requests/{iid}/versions')` for version list, `gl.http_get(...)` for diff details per version). Cache the resolved diff-version ID per `(project_id, mr_iid)` for 60 seconds to avoid burst rate-limiting (D-7). Cache the result on `ReviewContext.snapshot` and retain `ReviewDiff` compatibility values derived from it.
- [x] 1.3 Add a `head_sha_drift` degradation path: when the prepared worktree HEAD does not equal `snapshot.head_sha`, set `degraded_reason="head_sha_drift"` and skip scanning.
- [x] 1.4 Propagate `snapshot.base_sha`, `snapshot.diff_version_id`, and per-file `changed_ranges` through `ai-review/src/ai_review/prompts/builder.py` metadata and through the code-scan metadata sidecar read in `ai-review/src/ai_review/reviewers/code_scan_reviewer.py`.

## 2. Shared changed-hunk relevance gate (`ai-review`)

- [x] 2.1 Extract the existing `EnhancedValidationContext` file/line decision into a reusable code-scan relevance helper (under `ai-review/src/ai_review/validation/` or the review-flow package) returning filtered findings and reason counters; use `ReviewDiff` values derived from the snapshot rather than duplicating hunk parsing in the orchestrator.
- [x] 2.2 Apply the shared code-scan relevance gate before `CodeScanReviewer._post_comment`, and pass the same filtered code-scan findings into aggregate orchestration so the dedicated `<!-- code-scan-review -->` note and `<!-- mr-auto-review -->` summary cannot diverge. Replace the orchestrator's existing per-finding `EnhancedValidationContext.validate()` call for code-scan findings (orchestrator.py ~line 675) with the shared gate output so code-scan findings are validated exactly once (D-8). LLM reviewer findings continue to use the existing `EnhancedValidationContext` path.
- [x] 2.3 Extend the existing `codescan_execution_summary` event with `hunk_filtered` and `suppressed` skip-reason counters and `diff_version_id`.

## 3. Note identity and stale-note handling (`ai-review`)

- [x] 3.1 Update the dedicated note template in `ai-review/src/ai_review/reviewers/code_scan_reviewer.py` to include a stable footer line containing `head_sha=<sha>`, `base_sha=<sha>`, and `diff_version_id=<id>` (REGEX-friendly for parsing back).
- [x] 3.2 Update the aggregate note template in `ai-review/src/ai_review/review_flow/orchestrator.py` to add `Reviewed head SHA`, `Base SHA`, and `Diff version ID` fields.
- [x] 3.3 Add a precondition compare in the intake dispatcher on every intake action (`open`, `reopen`, AND `update`): when the MR already has a dedicated note, parse its `diff_version_id` from the footer; if it differs from the resolved `snapshot.diff_version_id`, mark the note stale via `GitLabReviewPoster` once a fresh scan completes, or post a short stale-marker comment.
- [x] 3.4 Reuse the existing post_or_update machinery so an unchanged diff-version ID results in update rather than duplication.

## 4. Android receiver-state detection (`code-daily-scan`)

- [x] 4.1 Add parser-compatible `L-RX-001` and `L-RX-002` definitions to the canonical Android `memory-lifecycle.md` rules source and update the local mirror only if this workspace owns that mirror; verify `AndroidRulesLoader` loads both IDs with the existing category mapping.
- [x] 4.2 Extend `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py` to support context-aware detectors that read full file content (same pattern as existing `suppress_viewholder_context`) and emit new `Finding` objects for L-RX rules. Register the new detectors in `ANDROID_RULE_POST_FILTERS` and update `plugin.py` `rule_post_filters` mapping. The detectors MUST use the existing `Finding` model (with `rule_id`, `file_path`, `line`, `message`, `priority`) so `FindingParser` can consume them downstream. No new scanner type is needed.
- [x] 4.3 Implement `L-RX-001`: locate paired receiver registration/unregistration in one compilation unit, identify the registration Boolean, and emit the finding when a nullable registration input can bypass the call before the flag becomes `true`.
- [x] 4.4 Implement `L-RX-002`: locate `runCatching` or empty-catch unregister paths that clear the registration flag regardless of failure and emit the finding at the unregister/state-update site.
- [x] 4.5 Add regression fixtures for valid `onStart`/`onStop`, non-null object-expression receivers, thrown registration calls, and files without paired unregister; none may produce an `L-RX` finding.

## 5. Tests (`ai-review` and `code-daily-scan`)

- [x] 5.1 In `ai-review/tests/test_review_flow/test_context.py`, add tests that the resolved `snapshot` carries `head_sha`, `base_sha`, and `diff_version_id`, and that a HEAD drift triggers `head_sha_drift` degradation.
- [x] 5.2 In `ai-review/tests/test_review_flow/test_orchestrator.py`, add tests proving the dedicated note and the aggregate summary publish identical `count` and that out-of-hunk findings are dropped with `hunk_filtered` reasons.
- [x] 5.3 In `ai-review/tests/test_reviewers/test_code_scan_reviewer.py`, add tests proving the dedicated note footer contains `head_sha`, `base_sha`, and `diff_version_id` and that stale notes are replaced or marked.
- [x] 5.4 In `code-daily-scan/tests/test_android_l_rx.py`, add fixtures covering: valid `onStart` registration with successful flag update (no finding); flag assignment outside `?.let` (L-RX-001); `runCatching` around `unregisterReceiver` followed by unconditional flag clear (L-RX-002); object-expression receiver with paired unregister but no flag mutation (no finding).

## 6. Live MR validation

- [x] 6.1 Re-trigger MR !23843 against diff version 644137 on `pspl/poems-mobile3-android`; verify the dedicated note carries the snapshot footer, the dedicated note and aggregate summary publish identical finding counts, and the receiver-state detector emits `L-RX-001` and `L-RX-002` on the added helper. Fallback: if MR !23843 is inaccessible or its diff versions are stale, select any Android MR with >=10 files where target-branch was advanced mid-review.
- [x] 6.2 Re-trigger one additional large Android MR (>=20 files) end-to-end; verify the shared gate publishes zero whole-file findings when the snapshot matches GitLab and refreshes the prior note when the diff-version ID differs.
- [x] 6.3 Run `cd ai-review && uv run pytest` and `cd code-daily-scan && uv run pytest`; confirm the new tests pass.
- [x] 6.4 Run `ruff check . --fix && ruff format .` and `mypy src/ --strict` in each modified Python repository; confirm clean exit.

## 7. Documentation and rollout

- [x] 7.1 Update `ai-review/README.md` with the new diff snapshot, footer format, and stale-note behaviour; reference the OpenSpec change.
- [x] 7.2 Update `code-daily-scan/README.md` and the Android rules markdown to document the `L-RX` category.
- [x] 7.3 After tests and an explicitly authorized deployment, redeploy ai-review via `cd ai-review && bash scripts/deploy.sh --require-clean`; restart the scheduler from `cd agent-core && docker compose up --build -d scheduler`; verify `curl -fsS http://127.0.0.1:8090/health`, `curl -fsS http://127.0.0.1:9100/scheduler/health`, `docker compose ps scheduler`, and `bash scripts/verify_scheduler_compose_up.sh` when compose/Dockerfile/entrypoint files changed. Prerequisite: the `L-RX` rules must be committed to the canonical `poems-mobile3-docs` rules repo BEFORE the scheduler restart, since `AndroidRulesLoader` loads rules at scan time.

## 8. Rollback

- [x] 8.1 If live validation fails, redeploy the prior known-good ai-review and code-daily-scan revisions, rebuild the scheduler, and verify module paths under `deployments/ai-review/app/.venv` plus `/health/full` plus `/scheduler/health` all return healthy.
- [x] 8.2 If only the Android detector misfires, roll back the scanner source/deployment revision and rebuild the scheduler; do not add a new environment flag unless implementation proves a runtime kill switch is required and the setting is documented in the canonical config contract.
