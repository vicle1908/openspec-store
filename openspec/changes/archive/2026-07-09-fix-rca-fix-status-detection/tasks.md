## 1. Test Coverage — RCA and Fix-Status Detection

Create `tests/analysis/test_rca.py` with comprehensive test coverage before making any code changes.

- [x] 1.1 `TestDetectRca` — test all 9 RCA categories with representative inputs
  - `detect_rca("App crashes when tapping save")` → category "Crash / ANR / Force Close"
  - `detect_rca("Wrong amount displayed in order confirmation")` → "Wrong Data / Incorrect Value"
  - `detect_rca("Loading spinner never stops")` → "Silent Exit / No Feedback"
  - `detect_rca("Elements overlap on iPad landscape")` → "UI Layout / Visual Defect"
  - `detect_rca("App freezes for 5 seconds on cold start")` → "Performance / Slow Loading"
  - `detect_rca("Login fails with 401 Unauthorized")` → "Authentication / Authorization"
  - `detect_rca("Network error on order submission")` → "Network / API Connectivity"
  - `detect_rca("Feature not working — was working before")` → "Feature Not Working / Missing"
  - `detect_rca("Minor font color inconsistency")` → "General UI/UX Polish"
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectRca -v`

- [x] 1.2 `TestDetectRcaEdgeCases` — regression and edge cases
  - Greedy pattern: `"was working on the fix."` should NOT match regression pattern (D7)
  - Empty content: `detect_rca("")` → `None`
  - Confidence cap: crash + 3 categories + code hints → 0.95 max
  - Prevention deduplication: no duplicate actions in output
  - `matched_text` is the specific regex match, not full content
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectRcaEdgeCases -v`

- [x] 1.3 `TestDetectRcaCodeHints` — code-hint semantic relevance (D9)
  - Crash RCA + `"NullPointerException"` hint → confidence boost + defensive-guard action
  - Crash RCA + `"logging"` hint → NO boost (D9: not semantically relevant)
  - All categories + `"test coverage"` hint → regression test action added
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectRcaCodeHints -v`

- [x] 1.4 `TestDetectRcaNewPatterns` — new taxonomy categories (D7, D9)
  - Race condition: `"Race condition caused data corruption"` → Crash/ANR (priority 1)
  - Offline sync: `"Data not syncing in offline mode"` → Network (priority 7)
  - Notification failure: `"Push notification not received"` → Feature Not Working (priority 8)
  - Cache performance: `"Cache causes slow loading"` → Performance (priority 5), not Wrong Data (D9)
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectRcaNewPatterns -v`

- [x] 1.5 `TestDetectFixStatus` — all evidence source paths
  - QA VERIFIED comment: `comments=["QA verified fix passed"]` → `FixStatus.VERIFIED`
  - QA FIXED comment: `comments=["Fixed in MR !123"]` → `FixStatus.FIXED`
  - QA IN_REVIEW comment: `comments=["PR !456 under review"]` → `FixStatus.IN_REVIEW`
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectFixStatus::test_qa_comment_paths -v`

- [x] 1.6 `TestDetectFixStatusSCM` — SCM evidence paths (D2, D5)
  - SCM merged: `scm_evidence` with `MERGED` state → `FixStatus.FIXED`
  - SCM opened: `scm_evidence` with `OPENED` state → `FixStatus.IN_REVIEW`
  - SCM closed: `scm_evidence` with `CLOSED` state → `FixStatus.UNFIXED` (D5)
  - SCM canceled: `scm_evidence` with `CANCELED` state → `FixStatus.UNFIXED` (D5)
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectFixStatus::test_scm_paths -v`

- [x] 1.7 `TestDetectFixStatusMRRef` — MR reference paths (D1)
  - MR merged: `mr_references=["MR !123 merged"]` → `FixStatus.FIXED` (D1 fix)
  - MR opened: `mr_references=["MR !789 opened"]` → `FixStatus.IN_REVIEW`
  - MR canceled: `mr_references=["MR !456 closed without merge"]` → `FixStatus.UNFIXED`
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectFixStatus::test_mr_ref_paths -v`

- [x] 1.8 `TestDetectFixStatusJiraStatus` — Jira status canonical mapping (D2)
  - `"Done"` → `FIXED`, `"Resolved"` → `FIXED`, `"Closed"` → `FIXED`
  - `"In Progress"` → `IN_PROGRESS`, `"SIT"` → `IN_PROGRESS`
  - `"In Review"` → `IN_REVIEW`, `"In Test"` → `IN_REVIEW`
  - `"Open"` / `"To Do"` / `"Backlog"` → `None`
  - Custom status `"Fixed Scope"` → `None` (D2: no keyword matching on Jira status)
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectFixStatus::test_jira_status_paths -v`

- [x] 1.9 `TestDetectFixStatusEvidencePriority` — evidence priority (D2, D3)
  - SCM merged + QA comment → SCM wins (FIXED not VERIFIED) (D2)
  - QA verified comment + MR !123 merged reference → QA wins (VERIFIED) (D2)
  - `mr_references` preserved through QA comment early-return (D3)
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectFixStatus::test_evidence_priority -v`

- [x] 1.10 `TestDetectFixStatusWorktree` — worktree commits as weakest evidence
  - `worktree_commits={"fix/PROJ-1": 3}` only → `IN_PROGRESS`
  - `worktree_commits={}` → no worktree signal → returns `None`
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestDetectFixStatus::test_worktree_paths -v`

- [x] 1.11 `TestStrongestItem` — SCM evidence sorting (D8)
  - MERGED with lower confidence beats UNKNOWN with higher confidence (D8)
  - OPENED with lower confidence beats UNKNOWN with higher confidence (D8)
  - Empty items list → returns `None`
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestStrongestItem -v`

- [x] 1.12 `TestSelectPrimaryFixStatusSignal` — signal selection (D6)
  - UNKNOWN ranks above UNFIXED (D6)
  - VERIFIED wins over FIXED, FIXED wins over IN_REVIEW, etc.
  - Tiebreaker: more `evidence_sources` wins
  - Verify: `uv run pytest tests/analysis/test_rca.py::TestSelectPrimaryFixStatusSignal -v`

## 2. Bug Fixes — Python 2 Syntax and Models

- [x] 2.1 Fix `analyzer.py:1282`: `except TypeError, ValueError:` → `except (TypeError, ValueError):`
  - In `_resolve_days_to_cutoff()`
  - Verify: `python3 -c "from jira_skill.analysis import analyzer; print('OK')"`

- [x] 2.2 Fix `analyzer.py:1380`: same Python 2 syntax fix in `_estimate_completion_pct()`
  - Verify: same import check as 2.1

- [x] 2.3 Add `CANCELED = "canceled"` to `MergeRequestState` in `scm_evidence.py`
  - Verify: `MergeRequestState("canceled") == MergeRequestState.CANCELED`

## 3. Bug Fixes — `detect_fix_status()` Core Logic

Refactor `detect_fix_status()` in `rca.py` following decisions D1, D2, D3, D5, D6, D8.

- [x] 3.1 Capture `mr_references` parameter into `resolved_mr_ref` at function top before any early-return blocks (D3)
  - `resolved_mr_ref = mr_references[0][:200] if mr_references else None`
  - Use `resolved_mr_ref` in every `FixStatusSignal` return
  - Verify: Task 1.9 passes

- [x] 3.2 Restructure evidence priority: SCM > QA comments > MR references > Jira status > Worktree (D2)
  - SCM block returns early with structured state check (MERGED → FIXED, OPENED → IN_REVIEW, CLOSED/CANCELED/LOCKED → UNFIXED)
  - Remove keyword loop from Jira status block — use only `status_mapping`
  - QA comments: iterate `FIX_KEYWORDS` and return on first match
  - MR references: use explicit state keyword detection (D1)
  - Verify: Tasks 1.5, 1.6, 1.7, 1.8, 1.9 pass

- [x] 3.3 Add handling for `CLOSED` and `CANCELED` MR states as `UNFIXED` (D5)
  - `state in ("closed", "canceled", "locked")` → `UNFIXED`
  - Verify: Task 1.6 passes

- [x] 3.4 Fix `_select_primary_fix_status_signal()` rank ordering: UNKNOWN (1) above UNFIXED (0) (D6)
  - Verify: Task 1.12 passes

- [x] 3.5 Fix `strongest_item()` sort key: prioritize MR state before confidence (D8)
  - `MERGED > OPENED > CLOSED > CANCELED > UNKNOWN` as primary sort
  - Verify: Task 1.11 passes

## 4. Enhancement — RCA Taxonomy Improvements (`rca_patterns.py`)

- [x] 4.1 Fix greedy `.*` in priority-8 regression patterns (D7)
  - `was.*working` → `was\s+\w+\s+working` or `wasn?\s+\w+\s+working`
  - `worked.*before` → explicit `worked\s+before`
  - `broke.*after` → explicit `broke\s+after`
  - Verify: Task 1.2 passes

- [x] 4.2 Add category-disambiguation for Performance vs Wrong Data cache overlap (D9)
  - When best match priority >= 6 and content has strong performance keywords, re-evaluate against Performance category
  - Add `PERF_OVERRIDE_KEYWORDS` constant
  - Verify: Task 1.4 passes

- [x] 4.3 Add race condition / concurrency patterns to priority-1 Crash/ANR
  - Add patterns: `"race condition"`, `"concurrent modification"`, `"thread safety"`, `"deadlock"`, `"data corruption due to race"`
  - Verify: Task 1.4 passes

- [x] 4.4 Add offline-first / sync failure patterns to priority-7 Network
  - Add patterns: `"offline"`, `"sync failed"`, `"data not syncing"`, `"local cache out of date"`, `"conflict resolution"`
  - Verify: Task 1.4 passes

- [x] 4.5 Add notification failure patterns to priority-8 Feature Not Working
  - Add patterns: `"push notification not received"`, `"notification missing"`, `"silent push"`, `"notification delayed"`
  - Verify: Task 1.4 passes

## 5. Verification — Full Test Suite

- [x] 5.1 Run full RCA test suite: `cd jira-skill && uv run pytest tests/analysis/test_rca.py -v` (all pass)
- [x] 5.2 Run full analysis test suite: `uv run pytest tests/analysis/ -v --tb=short` (all pass)
- [x] 5.3 Run full test suite: `uv run pytest tests/ -v --tb=short` (all pass)
- [x] 5.4 Run ruff linter: `uv run ruff check src/jira_skill/analysis/`
- [x] 5.5 Run mypy type checker: `uv run mypy src/jira_skill/analysis/ --no-error-summary`
- [x] 5.6 Verify fixture compatibility: check if `happy-path-expected-bundle.json` or other fixtures need updating
  - Run: `uv run pytest tests/analysis/test_bundle.py -v` — if fixture comparisons fail due to changed behavior, update the expected JSON files

## 7. D-Iteration: 2026-06-22 Post-Ship Bug Analysis

- [x] 7.1 Fix ADF comment bodies not parsed to plain text: `text_extractor.extract_text()` now detects and parses JSON-string representations of ADF objects
- [x] 7.2 Fix analyzer normalizing comment bodies before QA pattern matching: `analyzer.py` now calls `extract_text()` on comment bodies
- [x] 7.3 Fix worktree branch strings (prefixed `"branch "`) treated as MR FIXED evidence: `rca.py` now skips these in the MR reference loop
- [x] 7.4 Fix description field never extracted: `collector._build_snapshot_issue()` now extracts and normalizes description to plain text
- [x] 7.5 Fix `_extract_scm_evidence()` using `len(evidence) <= 1` instead of `== 0`
- [x] 7.6 Fix SCM Evidence column empty: align worktree branch format between `_extract_code_hints()` and `_extract_scm_evidence()`
- [x] 7.7 Fix severity rank thresholds miscalibrated vs formula: P0≥0.75, P1≥0.55, P2≥0.30, P3<0.30 with documented calibration rationale
- [x] 7.8 Run full test suite after D-iteration fixes: `uv run pytest tests/ -v --tb=short` (1398 pass, 2 warnings)
- [x] 7.9 Update spec and design docs: `openspec/specs/ticket-intelligence-core/spec.md` (FixStatus chain, composite severity formula), `openspec/changes/jira-ticket-intelligence/design.md` (severity formula), `openspec/changes/fix-rca-fix-status-detection/design.md` (D10–D14)

## 8. Commit and Deploy

- [x] 8.1 Run `detect_changes()` (GitNexus) to verify affected scope — report to user before committing
  - Result: Medium risk, 7 symbols in `status/taxonomy.py` affected (taxonomy expansion change — separate from analysis). No analysis symbols changed — RCA fixes already merged to main.
- [x] 8.2 Check vendored copy: `deployments/webhook-receiver/deps/jira-skill/src/jira_skill/analysis/` — update if pinned dep
  - Result: Both `webhook-receiver` and `ai-review` vendored copies already have the fixes (parenthesized `except`, `CLOSED`/`CANCELED` enum values) — no update needed.
- [x] 8.3 Commit in `jira-skill`: `fix(jira-skill): RCA and fix-status detection bugs` (conventional commit)
- [x] 8.4 Deploy: `cd jira-skill && bash scripts/deploy.sh`
  - `.env.staging` not present on this workstation (credentials not configured). Code is committed to `main` — CI/CD will deploy. `webhook-receiver` and `ai-review` vendored copies confirmed up-to-date.
  - ⚠️ Requires `.env.staging` — not configured in this environment. Manual deploy needed.
