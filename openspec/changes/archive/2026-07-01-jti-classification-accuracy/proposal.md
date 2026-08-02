# jti-classification-accuracy — Proposal

## Why

A live-run correctness audit of filter `15269` (bundle `v1.1`, 738 issues, 615 MR-bearing rows, 0 schema violations) followed by code-level verification against `rca.py`, `analyzer.py`, `sheets_writer.py`, and `coverage_analyzer.py` surfaced **four real defects** that affect operator trust in the JTI classification sheet:

1. **RCA matches are unauditable.** `RootCauseSignal.matched_text` is computed at `rca.py:918-925` and stored on the signal, but `IssueSummary.code_evidence` (rendered in the sheet's "Analysis Evidence" cell — zero-indexed column 12 in `CLASSIFICATION_COLUMNS`, which corresponds to 1-indexed column 13) is sourced from `_extract_code_hints()` which only inspects `raw_fields.code_context`, `raw_fields.worktree_commits`, and `raw_fields.mr_references`. None of those are populated for closed-bug backlog issues — for all 738 issues, `code_evidence = []`. The RCA matched substring is computed but discarded before it reaches the operator, so a misclassification cannot be debugged without rerunning the analyzer.
2. **17 of 738 issues render an empty RCA cell.** `detect_rca()` returns `None` when no pattern matches (`rca.py:927-928`), and `analyzer.py:189` propagates `None` into `rca_category`. The sheet fallback chain `sheets_writer.py:254-260` writes `""`. These issues are ungroupable in pivot views and the operator has no signal that anything is wrong.
3. **Coverage gaps in priority-6..9 buckets.** Priority-8/9 buckets (`Feature Not Working`, `Auth`, `Network`, `Performance`) cover only 35/738 (4.7%) of the live corpus. Missing patterns identified during the audit: SSO/SAML, token expiry, offline queue/retry, JWT validation, locale/i18n truncation, decimal precision in financial transactions.
4. **`at_risk_modules` is a flat `list[str]` with no provenance.** The sheet renders `"feature.common"` at zero-indexed column 24 (`CLASSIFICATION_COLUMNS[24]`, the "At-Risk Modules" column) but the operator cannot tell whether the module came from a GitNexus call-graph match (`run_impact`), a YAML feature-map substring lookup, or a base-module escalation heuristic (`is_base_module AND abs(net_lines) > 3`). All three paths produce identical-looking strings in the column.

**Defect that is NOT real (verified against implementation):**

5. ~~**RCA priority not honored.**~~ The audit originally claimed priority-1 Crash could be displaced by priority-4 UI Layout. Walking through the algorithm at `rca.py:918-925` confirms: with `best_priority` initialized to `inf`, a priority-1 match sets `best_priority=1`. All subsequent matches (priority 2, 3, 4, 4, 5, ...) fail the `priority < best_priority` guard (`4 < 1` is False). Priority is correctly honored today. The audit's apparent misclassifications (e.g. `AM-2322` "Eye icon missing" → `Wrong Data`, `PDS-365` "tab isn't highlight" → `Crash`) actually came from full Jira description+comment content (not the issue title alone) where patterns like `shows wrong` and `crashes` legitimately match at priorities 2 and 1 respectively. No bug. **RCA-1 is therefore removed from this change.** The audit's false alarm is documented here for traceability.

## What Changes

Create a new OpenSpec spec `jti-classification-accuracy` with three RCA requirements plus IMPACT-1 (extends `impact-sheet-integration`):

- **RCA-2 — Evidence propagation:** When `detect_rca()` returns a signal with a non-empty `matched_text`, the bundle MUST include that substring in `IssueSummary.code_evidence` with the deterministic prefix `rca:match:<category>:<matched_text>` (where `<category>` is the RCA category string, since `RootCauseSignal` does not carry a separate priority field). The sheet's existing "Analysis Evidence" column at zero-indexed position 12 renders this verbatim (no writer-side change needed). RCA evidence MUST appear before any worktree-commit evidence in the joined cell.
- **RCA-3 — Unclassified fallback:** When no pattern matches across the 10-category taxonomy on **non-empty** input, `detect_rca()` MUST return a `RootCauseSignal` with `category="Other / Unclassified"`, `confidence=0.0`, `matched_text=""`, and `evidence=[SignalEvidence(rule_tag="rca_unclassified", ...)]`. When the input IS empty (`""`, whitespace-only, or `None`), `detect_rca()` MUST continue returning `None` (preserves existing behavior). The sheet MUST render the literal string `"Other / Unclassified"` (not empty, not `"None"`).
- **RCA-4 — Coverage gap closure:** The `RCA_PATTERNS` taxonomy MUST add six new pattern groups addressing the audit's identified gaps. Each pattern goes through the existing `_stem_pattern()` inflection expansion. Each new pattern gets a survey-positive fixture in `tests/analysis/test_rca.py`. The 65-ticket precision survey regression gate (≥85%) MUST remain satisfied.
- **IMPACT-1 — `at_risk_modules` provenance:** Extend `ImpactRow` additively with `at_risk_modules_provenance: dict[str, str]` (module name → source label). Three sources: `"gitnexus_callgraph"` (call-graph match), `"feature_map"` (YAML resolution), `"base_module_escalation"` (heuristic). Render a new sheet column "Module Source" at column 24 (zero-indexed) as `module(source_short)` joined by `" | "`. The existing `at_risk_modules: list[str]` field is preserved verbatim — additive change.

## Capabilities

### New Capabilities

- `jti-classification-accuracy`: pin down three deterministic RCA contracts (evidence propagation, unclassified fallback, coverage gap closure) and one impact-analysis contract (`at_risk_modules` provenance with a new sheet column). 4 requirements total: RCA-2, RCA-3, RCA-4, IMPACT-1.

### Modified Capabilities

- `impact-sheet-integration`: extend `ImpactRow` with the additive `at_risk_modules_provenance: dict[str, str]` field, add the IMPACT-1 requirement for sheet-level rendering of a new "Module Source" column, **and** add four new requirements: HYPERLINK-1 (Issue-Key hyperlinks), HYPERLINK-2 (MR-link hyperlinks), RCA-5 (comment-noise stripping), RCA-6 (issue-key stripping to prevent status-code false positives in narrative prefixes, multi-ticket branch names, and cross-references), and RCA-7 (high-precision new patterns for Wrong Data, Authentication, and UI Layout addressing genuine classification gaps discovered in live-data audit of filter 15269). Bump the bundle version from `v1.1` to `v1.2`. All existing v1.1 requirements are preserved verbatim — this is purely additive.

## Impact

- **Operator-visible:**
  - Sheet `Analysis Evidence` column (zero-indexed 12, 1-indexed 13) gains `rca:match:<category>:<text>` entries for every RCA-classified row — auditable trail.
  - 17 currently-empty RCA cells (2.3% of corpus) will render `"Other / Unclassified"`.
  - Sheet `Module Source` column (column 24) shows the provenance of each `at_risk_modules` entry.
  - Coverage gap closure will reroute some unclassified issues into p6..p8 buckets — exact count depends on the audit sample but the live corpus has clear SSO, retry, and pagination gaps.
- **Risk:**
  - **Backwards-compatible for v1.1 bundles.** `at_risk_modules_provenance` defaults to `{}`; consumers that don't read the new field continue to work.
  - **Test breakage.** Five existing assertions in `test_rca.py` (`test_empty_content_returns_none` line 120-124, plus two `'stuck'` no-match assertions at lines 1197 and 1313) MUST be updated: `None` becomes `signal with category="Other / Unclassified"`.
  - **`match_count > 2` confidence boost guard.** `rca.py:934-942` iterates patterns separately from `best_match`, so the boost calculation works correctly even when no pattern matches. No change needed, but documented for future maintainers.
  - **Survey precision regression gate.** The 65-ticket `TestRcaSurveyPrecision.test_rca_survey_precision` MUST remain ≥85% after the RCA-4 taxonomy additions. New pattern groups MUST add survey-positive fixtures.
- **Out of scope:**
  - LLM-based classification (RCA is fully deterministic today — kept that way).
  - Risk-factor weights, severity thresholds, recommendation engine — separate work streams.
  - The audit's false-positive finding about priority ordering (see Why §5) — not a bug, no change.

## Success Criteria

- All 29 scenarios in the new spec pass (RCA-2: 3, RCA-3: 4, RCA-4: 6, IMPACT-1: 6, RCA-5: 2, RCA-6: 3, RCA-7: 5). Count verified against `openspec/changes/jti-classification-accuracy/specs/jti-classification-accuracy/spec.md` (base 19 scenarios) and `openspec/specs/impact-sheet-integration/spec.md` (RCA-5/6/7: 10 scenarios).
- Existing 170+ RCA tests still pass; updated 5 `None` assertions for the new sentinel return.
- The 65-ticket survey precision ≥ 85% (regression gate).
  - Re-run filter 15269 on the live corpus: 0 empty RCA cells, `Analysis Evidence` shows `rca:match:*` for every classified row, `Module Source` column populated for all `at_risk_modules > 0` rows.
- Operator confusion in the field about "why is this categorized as X" is reduced — they can now read the matched substring in the sheet.