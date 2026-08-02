## Why

The RCA and fix-status detection logic shipped in `jira-ticket-intelligence` (v1.0, 2026-06-15) contains multiple logic bugs that cause systematic misclassification of tickets. These bugs violate the existing `ticket-intelligence-core` spec contract — particularly the evidence-grounding and strong-fix-state requirements — and produce incorrect signals for downstream consumers (`jira-epic-report`, `jira-daily-reports`, `webhook-receiver`).

**Iteration D (2026-06-22):** Post-ship analysis of 752 mainflow v54 bugs found additional bugs: ADF comment text not normalized to plain text, worktree branch strings misclassified as MR FIXED evidence, description field never extracted, and severity rank thresholds miscalibrated vs. formula.

## What Changes

**Bug Fixes — Iteration C (2026-06-15):**
- Fix `detect_fix_status()` always returning `IN_REVIEW` for MR references due to incorrect `"review" in ref` substring check
- Fix `status_lower` variable computed but unused in Jira status keyword loop
- Fix canonical `status_mapping` short-circuited by keyword detection on Jira status string
- Fix `UNFIXED` rank > `UNKNOWN` rank in `_select_primary_fix_status_signal`
- Fix `mr_reference` parameter shadowed to `None` in early-return blocks, silently dropping MR evidence
- Normalize multi-exception handling in `analyzer.py` to parenthesized `except (TypeError, ValueError):` form for forward-compatible Python style
- Verify the existing `FixStatusSignal` vs `str` serialization contract: `IssueSummary.fix_status` remains `str | None`, while `TicketIntelligenceBundle.fix_status` remains `FixStatusSignal | None`

**Bug Fixes — Iteration D (2026-06-22):**
- Fix `SnapshotComment.body` storing raw ADF dict repr strings: `text_extractor.extract_text()` now detects and parses JSON-string representations of ADF objects before flattening. This prevents QA keyword patterns from matching ADF structural strings like `"merge_requests/123"`.
- Fix worktree branch strings (e.g. `"branch poems-mobile3-android:fix/PWM-1963"`) being treated as MR references in step 3 of `detect_fix_status()`: strings prefixed `"branch "` are now skipped in the MR reference loop and fall through to worktree evidence.
- Fix `_build_snapshot_issue()` never extracting the `description` field: description is now normalized to plain text (ADF → plain text) and stored in `raw_fields["description"]` for downstream consumers.
- Fix `_extract_scm_evidence()` using `len(evidence) <= 1` (incorrectly filling worktree data when step 1 produced 1 entry) instead of `len(evidence) == 0` (only when steps 1 and 2 produced nothing).
- Fix `_extract_scm_evidence()` worktree branch format mismatch: produced `"branch poems-mobile3-android"` but `_extract_code_hints()` produces `"branch poems-mobile3-android has 3 commits mentioning PWM-1963"`. The sheet-writer filter `"commits mention"` matched `_extract_code_hints()` output but not `_extract_scm_evidence()` output, leaving SCM Evidence empty.
- Fix severity rank thresholds (`_severity_rank_label()`) misaligned with achievable formula range: P0≥0.75 was unreachable (max formula output ≈ 0.58 without blocking signals). P0 reserved for issues with blocking signals; P1≥0.55, P2≥0.30, P3<0.30.

**Taxonomy Enhancements:**
- Add missing `CANCELED` value to `MergeRequestState` (contrast: `PipelineState` has it) and update GitLab state normalization so API `"canceled"` values do not collapse to `UNKNOWN`
- Fix greedy `.*` in priority-8 regression patterns that over-matches across long ticket text
- Add missing RCA categories for common bug patterns: data race / concurrency, offline-first / sync issues, notification failures
- Refine pattern precision to reduce cross-category overlap (e.g., "cache" appears in Wrong Data but also causes Performance issues)
- Refactor `FIX_KEYWORDS` reuse: separate `qa_patterns` from `jira_status_patterns` to eliminate cross-contamination

**Testing:**
- Add unit tests for `detect_rca()` covering all 9 RCA categories with representative inputs
- Add unit tests for `detect_fix_status()` covering all evidence-source paths (comments, SCM, MR references, Jira status)
- Add integration test for composite severity score edge cases

## Capabilities

### New Capabilities

- `rca-detection-fix`: Fixes confirmed bugs in `detect_rca()` and `detect_fix_status()` in `jira-skill/src/jira_skill/analysis/rca.py` and `analyzer.py`. Affected files: `rca.py`, `analyzer.py`, `signals.py`, `bundle.py`, `scm_evidence.py`, and `gitlab_evidence.py`. New test module: `tests/analysis/test_rca.py`.
- `rca-taxonomy-v2`: Enhances `rca_patterns.py` with refined patterns, new categories (data race, offline sync, notifications), and improved category disambiguation. Affected file: `rca_patterns.py`.

### Modified Capabilities

- `ticket-intelligence-core`: The spec's requirement "Strong fix-state claims require stronger evidence" (Scenario: Strong fix-state claims require stronger evidence) is violated by Bug B. The fix to `detect_fix_status()` restores the intended behavior. The spec does not need a delta file — this is a bug fix within existing requirements.

## Impact

**Owning repo:** `jira-skill`

**Affected files:**
- `src/jira_skill/analysis/rca.py` — detection logic (7 bugs)
- `src/jira_skill/analysis/extractors/rca_patterns.py` — taxonomy (precision + new categories)
- `src/jira_skill/analysis/analyzer.py` — Python 2 syntax errors, rank ordering
- `src/jira_skill/analysis/signals.py` — `FixStatusSignal` model (no model change, clarifying comment)
- `src/jira_skill/analysis/bundle.py` — `IssueSummary.fix_status` type annotation
- `src/jira_skill/analysis/scm_evidence.py` — `MergeRequestState` enum

**Consumers (read-only, no breaking contract change):**
- `jira-epic-report` — consumes `TicketIntelligenceBundle`
- `jira-daily-reports` — consumes `TicketIntelligenceBundle`
- `webhook-receiver` — consumes `RootCauseSignal` and `FixStatusSignal` via `build_freshness_bundle()`

**New test file:** `tests/analysis/test_rca.py`

**Non-goals:**
- No changes to the `TicketIntelligenceBundle` v1.0 contract shape
- No changes to the `RootCauseSignal` or `FixStatusSignal` Pydantic fields
- No new LLM/semantic enrichment (out of scope for this change)
- No changes to signal extraction ordering or composite score weights
