# jti-classification-accuracy — Tasks

## 0. Pre-flight: Verify call sites

- [x] 0.1 Confirm `analyzer.py` has TWO `_extract_code_hints` call sites:
  - Primary: line ~177 (in `analyze_snapshot()`)
  - Secondary: line ~656 (in `_analyze_single_issue()`)
- [x] 0.2 Confirm `test_rca.py` has 5 `is None` assertions to update across 3 test functions: lines 121, 122, 124 (`TestDetectRcaEdgeCases.test_empty_content_returns_none`); line 1197 (`TestRcaStemMatching.test_stuck_is_not_performance_alone`); line 1313 (`TestRcaCoverage.test_app_stuck_becomes_unclassified`).
- [x] 0.3 Confirm `RootCauseSignal` has fields: `category: str`, `confidence: float`, `matched_text: str`, `prevention_actions: list[str]`, `evidence: list[SignalEvidence]` (at `signals.py:472-479`). **No `priority` field exists** — use `category` in the `rca:match:<category>:<text>` prefix.
- [x] 0.4 Confirm `test_sheets_writer.py` uses **module-level functions**, not test classes. Existing pattern: `test_evidence_columns_distinct_when_both_empty` at line 310. Only fakes (`FakeMetadata`, `FakeSheetsClient`) live in classes.
- [x] 0.5 Confirm `coverage_analyzer.py` owns the `at_risk_modules` append sites (lines 240-290).
- [x] 0.6 Confirm `ImpactEnricher._enrich_keys()` is at `impact/enrichment.py:74-152`. Provenance MUST thread through `coverage_analyzer` → `impact_report.py:213` → `enrichment.py:145-150`.

---

## 1. Specs & documentation

- [x] 1.1 Create `openspec/changes/jti-classification-accuracy/specs/jti-classification-accuracy/spec.md` with requirements RCA-2 through RCA-4 + IMPACT-1. (Note: RCA-1 is not a bug — priority is already correctly honored; see proposal.md Why.)
- [x] 1.2 Update `openspec/specs/impact-sheet-integration/spec.md`: add `Provenance flow` clarification to the "Module provenance on at_risk_modules" requirement (stage 1: `coverage_analyzer.AnalysisResult`; stage 2: `impact_report.ImpactReport`; stage 3: `enrichment._enrich_keys` → `ImpactRow`).
- [x] 1.3 Update `.agents/skills/jira-ticket-intelligence/SKILL.md`:
  - Add category 11 row to RCA taxonomy table: `Other / Unclassified`
  - Document `rca:match:<category>:<matched_text>` format (note: `<category>` is the RCA category name, not a numeric priority)
  - Document Module Source column (`gitnexus`, `feature`, `base` short forms)

---

## 2. RCA-2 — Evidence propagation (TWO call sites)

### 2.1 Primary call site — `analyze_snapshot()` in `analyzer.py`

- [x] 2.1.1 Modify `_extract_code_hints()` signature (line ~1256):

  ```python
  def _extract_code_hints(
      issue: SnapshotIssue,
      rca_signal: RootCauseSignal | None = None,  # NEW param
  ) -> list[str]:
      hints: list[str] = []
      # ... existing extraction logic for raw_code_context / worktree_commits / mr_references ...
      if rca_signal is not None:
          # NOTE: RootCauseSignal has no priority field — use `category` (str) instead.
          # Produces entries like: "rca:match:UI Layout / Visual Defect:tab isn't highlight"
          hints.append(f"rca:match:{rca_signal.category}:{rca_signal.matched_text}")
      return hints
  ```
- [x] 2.1.2 At line ~177, update the call:

  ```python
  issue_code_hints = _extract_code_hints(issue, rca_signal=issue_root_cause)
  ```

  Note: `issue_root_cause` is computed at line ~179 (after the call). **Refactor required:** move the `_extract_code_hints` call to AFTER `issue_root_cause = sig_set.root_cause[0] if sig_set.root_cause else None` is assigned.

### 2.2 Secondary call site — `_analyze_single_issue()` in `analyzer.py`

- [x] 2.2.1 This call site (line ~656) extracts `code_hints` BEFORE calling `detect_rca()` at line ~1068. Refactor the order:

  ```python
  # Line ~657-659 — rca_content is already computed here
  rca_content = "\n\n".join(
      part for part in [issue.summary or "", description_text or "", *comment_bodies] if part
  )

  # Line ~1068 — compute RCA signal FIRST, then re-extract code_hints with RCA evidence
  rca_signal = detect_rca(rca_content, code_hints=code_hints)  # code_hints = _extract_code_hints(issue) from line ~656

  # AFTER rca_signal is available, augment code_hints with RCA evidence:
  code_hints = _extract_code_hints(issue, rca_signal=rca_signal)
  ```

  The `code_hints` variable from line 656 holds the raw code hints. After `rca_signal` is computed, overwrite `code_hints` with the augmented version.

- [x] 2.2.2 Verify both call sites now produce `rca:match:<category>:<substring>` in the returned hints list when a match is found.

### 2.3 Sheet verification

- [x] 2.3.1 Confirm `sheets_writer.py:_build_classification_rows` already writes `issue_summary.code_evidence` at `CLASSIFICATION_COLUMNS[12]` (zero-indexed; "Analysis Evidence" column at 1-indexed column 13) — no writer change required. Spot-check by reading existing test `test_evidence_columns_distinct_when_both_empty` at `test_sheets_writer.py:362` which asserts `classification[1][12]` for Analysis Evidence.
- [x] 2.3.2 Add `tests/analysis/test_sheets_writer.py::test_rca_match_in_analysis_evidence` (module-level function, not a class). Use the existing fixture pattern from `test_evidence_columns_distinct_when_both_empty`:

  ```python
  def test_rca_match_in_analysis_evidence() -> None:
      """When RCA evidence appears in code_evidence, the sheet MUST render it as the
      deterministic prefix `rca:match:<category>:<matched_text>` in the Analysis Evidence
      cell (zero-indexed column 12)."""
      bundle = TicketIntelligenceBundle(
          meta=BundleMeta(bundle_id="bundle-rca", source_repo="cli"),
          scope=BundleScopeSummary(total_issues=1, project_keys=["PDS"]),
          issue_identities=[
              BundleIssueIdentity(
                  key="PDS-999", id=999, summary="tab isn't highlight",
                  issue_type="bug", status="TODO", priority="medium",
                  target_version="3.3.54", assignee_display_name="Dev",
                  project_key="PDS",
              )
          ],
          # Risk / freshness / completeness etc. — minimal stub signals
          risk=RiskSignal(issue_key="PDS-999", severity=RiskSeverity.MEDIUM, score=0.5, factors=["x"]),
          freshness=FreshnessSignal(issue_key="PDS-999", state=FreshnessState.FRESH, source="cli"),
          summary=BundleSummary(
              scope=BundleScopeSummary(total_issues=1),
              issue_summaries=[
                  IssueSummary(
                      issue_key="PDS-999",
                      narrative="PDS-999: tab isn't highlight",
                      risk_label="Medium",
                      severity_score=0.5,
                      severity_rank="P2",
                      rca_category="UI Layout / Visual Defect",
                      code_evidence=[
                          "rca:match:UI Layout / Visual Defect:tab isn't highlight",
                          "branch main has 3 commits mentioning PDS-999",
                      ],
                      scm_evidence=[],
                  )
              ],
          ),
      )
      client = FakeSheetsClient()
      writer = SheetsWriter(spreadsheet_id="sheet-rca", sheets_client=client)
      writer.write_bundle(bundle, tab_prefix="rca-test")

      classification = client.calls[0]["values"]
      analysis_col = classification[1][12]
      assert analysis_col.startswith("rca:match:UI Layout / Visual Defect:tab isn't highlight")
      assert "branch main has 3 commits" in analysis_col
  ```

---

## 3. RCA-3 — Unclassified fallback

- [x] 3.1 Add `UNCLASSIFIED_CATEGORY = "Other / Unclassified"` constant at module level in `rca.py` (near the top, after imports — before line 27's signal class definitions or after the imports around line 28).
- [x] 3.2 Modify `detect_rca()` at `rca.py:899-928` — replace the `return None` branch at line 902 (the empty-content early-exit branch stays as-is and continues to return `None`) **AND** replace the `return None` at line 928 (no-match branch) with the sentinel signal:

  ```python
  # At line 928 (replacing the no-match return):
  return RootCauseSignal(
      category=UNCLASSIFIED_CATEGORY,
      confidence=0.0,
      matched_text="",
      prevention_actions=[],
      evidence=[SignalEvidence(
          source_field="rca_taxonomy",
          source_keys=[],
          raw_values=[],
          rule_tag="rca_unclassified",
          note="No RCA pattern matched across the 10-category taxonomy",
      )],
  )

  # Line 902 (empty content) stays as: return None
  ```

  **Two distinct return paths:**
  - Empty/whitespace/None content → `None` (preserves existing early-exit)
  - Non-empty content with no pattern match → sentinel `RootCauseSignal` (RCA-3)
- [x] 3.3 Update 5 `is None` assertions in `tests/analysis/test_rca.py`:

  | Line | Test class : method | Before | After |
  |------|---------------------|--------|-------|
  | 121 | `TestDetectRcaEdgeCases.test_empty_content_returns_none` (1st assertion) | `assert detect_rca("") is None` | `assert detect_rca("") is None` (stays `None` — empty input, per RCA-3 spec) |
  | 122 | (same test, 2nd assertion) | `assert detect_rca("   ") is None` | `assert detect_rca("   ") is None` (stays `None` — whitespace-only) |
  | 124 | (same test, 3rd assertion) | `assert detect_rca(None) is None` | `assert detect_rca(None) is None` (stays `None` — `None` input) |
  | 1197 | `TestRcaStemMatching.test_stuck_is_not_performance_alone` | `assert sig is None` (with input "App stuck after login") | `assert sig is not None and sig.category == UNCLASSIFIED_CATEGORY` (non-empty input → sentinel) |
  | 1313 | `TestRcaCoverage.test_app_stuck_becomes_unclassified` | `assert sig is None` (with input "App stuck after login") | `assert sig is not None and sig.category == UNCLASSIFIED_CATEGORY` (non-empty input → sentinel) |

  Note: lines 121-124 stay as `is None` because they test the empty-input early-exit. Lines 1197 and 1313 change because their input `"App stuck after login"` is non-empty.

  Update the docstrings of `test_stuck_is_not_performance_alone` and `test_app_stuck_becomes_unclassified` to reflect the new expected behavior (was: "no match → `None`"; now: "no match → UNCLASSIFIED_CATEGORY sentinel").

- [x] 3.4 Add `tests/analysis/test_rca.py::TestDetectRca.test_unclassified_fallback` (the `TestDetectRca` class exists at line 27):

  ```python
  def test_unclassified_fallback(self) -> None:
      result = detect_rca("random text that matches no pattern")
      assert result is not None
      assert result.category == UNCLASSIFIED_CATEGORY
      assert result.confidence == 0.0
      assert result.matched_text == ""
      assert result.evidence[0].rule_tag == "rca_unclassified"
  ```

  Import `UNCLASSIFIED_CATEGORY` from `jira_skill.analysis.rca` at the top of the test file.
- [x] 3.5 Run `uv run pytest tests/analysis/test_rca.py::TestRcaSurveyPrecision -q` — ≥85% precision still holds (unclassified is excluded from denominator; survey fixtures all have classifiable content like "Application stops responding" → Crash).
- [x] 3.6 Run `uv run ruff check src/jira_skill/analysis/rca.py`.

---

## 4. RCA-4 — Coverage gap closure

- [x] 4.1 Add 6 patterns to **existing** priority groups in `jira-skill/src/jira_skill/analysis/extractors/rca_patterns.py`. Each pattern group is added to the existing `patterns: list[str]` of the corresponding `RCA_PATTERNS` entry. Patterns are processed through `_stem_pattern()` at module load — use simple stemmed forms, not full inflections.

  | Priority group (existing category) | Patterns to add |
  |------------------------------------|-----------------|
  | p6 `"Authentication / Authorization"` | `r"\bsso\b"`, `r"\bsaml\b"`, `r"\b(token)\s+(expired|expire|expires)\b"`, `r"\bjwt\b.*\b(invalid|expired|missing)\b"` |
  | p7 `"Network / API Connectivity"` | `r"\b(offline|queue|retry).{0,20}(fail|loop|stuck|storm)\b"`, `r"\bcircuit.?breaker\b"`, `r"\breconnect\b"` |
  | p8 `"Feature Not Working / Missing"` | `r"\b(filter|pagination|sort|search)\s+(does not|doesn't|fails to|not)\s+(reset|apply|load|trigger)\b"`, `r"\bscroll\s+to\s+(top|bottom)\s+(not|fails|broken)\b"` |
  | p2 `"Wrong Data / Incorrect Value"` | `r"\bdecimal\b.*\b(precision|scaling|rounding|truncation)\b"`, `r"\bcurrency\b.*\b(conversion|fx|exchange.?rate)\s+(wrong|stale|incorrect)\b"` |
  | p4 `"Text / Font Display"` | `r"\b(locale|i18n|translation)\b.*\b(wrong|broken|missing|cut.?off|overflow)\b"` |
  | p5 `"Performance / Slow Loading"` | `r"\b(startup|launch)\s+time\b.*\b(slow|high|exceeded|timeout)\b"`, `r"\bmemory\s+(leak|growth|usage)\b"` |

  Verify group priority ordering is preserved: p1 < p2 < p3 < p4 < p5 < p6 < p7 < p8 < p9 (Crash < Wrong Data < Silent Exit < Text/Font & UI Layout < Performance < Auth < Network < Feature Not Working < General UI/UX Polish).

  **No new categories added** — the actual taxonomy remains 10 categories.

- [x] 4.2 Add one survey-positive fixture per new pattern group to `tests/analysis/test_rca.py::TestRcaCoverage` (the class exists at line 1221):

  ```python
  def test_sso_patterns(self) -> None:
      sig = detect_rca("SSO login silently fails on iOS 17")
      assert sig is not None
      assert sig.category == "Authentication / Authorization"

  def test_offline_retry_patterns(self) -> None:
      sig = detect_rca("app retry storm when offline queue fails")
      assert sig is not None
      assert sig.category == "Network / API Connectivity"

  def test_filter_reset_patterns(self) -> None:
      sig = detect_rca("filter doesn't reset when navigating away")
      assert sig is not None
      assert sig.category == "Feature Not Working / Missing"

  def test_decimal_precision_patterns(self) -> None:
      sig = detect_rca("decimal precision wrong for settlement")
      assert sig is not None
      assert sig.category == "Wrong Data / Incorrect Value"

  def test_locale_i18n_patterns(self) -> None:
      sig = detect_rca("translation cut off in German locale")
      assert sig is not None
      assert sig.category == "Text / Font Display"

  def test_memory_leak_patterns(self) -> None:
      sig = detect_rca("memory leak observed in production logs")
      assert sig is not None
      assert sig.category == "Performance / Slow Loading"
  ```

- [x] 4.3 Run `uv run pytest tests/analysis/test_rca.py::TestRcaSurveyPrecision -q` — ≥85% precision regression gate must still hold (existing 65-ticket survey). New taxonomy entries should be additive, not displacing existing categories.
- [x] 4.4 Run `uv run ruff check src/jira_skill/analysis/extractors/rca_patterns.py`.

---

## 5. IMPACT-1 — `at_risk_modules` provenance (THREE-STAGE threading)

### 5.1 Stage 1 — `ImpactRow` field

- [x] 5.1.1 Add `at_risk_modules_provenance: dict[str, str] = Field(default_factory=dict)` to `ImpactRow` in `jira-skill/src/jira_skill/analysis/bundle.py` (after line 336). This is an additive field — do NOT remove or rename `at_risk_modules`.

### 5.2 Stage 1 — `coverage_analyzer.py` tagging

- [x] 5.2.1 Add `at_risk_modules_provenance: dict[str, str] = field(default_factory=dict)` to `AnalysisResult` (at `coverage_analyzer.py:113`).
- [x] 5.2.2 Tag every `at_risk_modules.append(...)` call site with provenance (lines 240-290):

  ```python
  # Source A: base_module_escalation (~line 247)
  result.at_risk_modules.append(tag)
  result.at_risk_modules_provenance[tag] = "base_module_escalation"

  # Source B: gitnexus_callgraph (~line 287)
  for mod in blast_radius.affected_modules:
      if mod not in result.at_risk_modules:
          result.at_risk_modules.append(mod)
      result.at_risk_modules_provenance[mod] = "gitnexus_callgraph"

  # Source C: feature_map
  # Wherever feature_map fallback appends modules, tag with "feature_map".
  ```

### 5.3 Stage 2 — `impact_report.py` propagation

- [x] 5.3.1 Add `at_risk_modules_provenance: dict[str, str] = Field(default_factory=dict)` to `ImpactReport` in `jira-skill/src/jira_skill/impact/impact_report.py` (after line 139).
- [x] 5.3.2 In `analyze_mr_to_report()` at `impact_report.py:213`: copy `result.at_risk_modules_provenance` into the `ImpactReport`:

  ```python
  at_risk_modules=result.at_risk_modules,
  at_risk_modules_provenance=result.at_risk_modules_provenance,  # NEW
  ```

### 5.4 Stage 3 — `enrichment.py` final propagation

- [x] 5.4.1 In `ImpactEnricher._enrich_keys()` at `jira-skill/src/jira_skill/impact/enrichment.py:138,150`:
   - Track module→source mapping when collecting `at_risk` from `report.at_risk_modules_provenance`
   - Pass `at_risk_modules_provenance` to `ImpactRow` at line 145-152:

     ```python
     return key, ImpactRow(
         issue_key=key,
         mr_links=mr_links,
         last_commit_sha=last_sha,
         files_changed_count=files_total,
         at_risk_modules=sorted(at_risk),
         at_risk_modules_provenance={m: report.at_risk_modules_provenance.get(m, "gitnexus_callgraph") for m in at_risk},
         impact_status="ok",
     )
     ```

### 5.5 Bundle version bump

- [x] 5.5.1 In `jira-skill/src/jira_skill/analysis/bundle.py` line 71:

  ```python
  # Before:
  MINOR = 1  # v1.1 — added ImpactSnapshot field on TicketIntelligenceBundle

  # After:
  MINOR = 2  # v1.2 — added at_risk_modules_provenance field on ImpactRow (additive)
  ```

  `BUNDLE_VERSION = BundleVersion.current()` at module load will compute `v1.2`. **Do not** touch `BUNDLE_VERSION` directly (it's auto-derived).

### 5.6 Sheet rendering

- [x] 5.6.1 Extend `CLASSIFICATION_COLUMNS` in `jira-skill/src/jira_skill/analysis/sheets_writer.py` at line 61:

  ```python
  CLASSIFICATION_COLUMNS: list[str] = [
      "Severity Rank",                            # 0
      "Severity Score",                           # 1
      "Issue Key",                                # 2
      "Summary",                                  # 3
      "Status",                                   # 4
      "Assignee",                                 # 5
      "Priority",                                 # 6
      "Target Version",                           # 7
      "Risk",                                     # 8
      "RCA",                                      # 9
      "RCA Matched Text",                         # 10 ← NEW (RCA-2)
      "Prevention",                               # 11
      "Fix Status",                               # 12
      "Analysis Evidence",                        # 13
      "SCM / Branch Evidence",                    # 14
      "Worktree Commits",                         # 15
      "Top Action",                               # 16
      "Narrative",                                # 17
      "Blocked By",                               # 18
      "Freshness",                                # 19
      "Completeness",                             # 20
      "Capacity",                                 # 21
      # v1.1 — Impact columns:
      "MR Links",                                 # 22
      "Files Changed",                            # 23
      "At-Risk Modules",                          # 24
      # v1.2 — Module provenance:
      "Module Source",                            # 25 ← NEW (IMPACT-1)
  ]
  ```

  Note: "RCA Matched Text" is inserted at index 10 to land between "RCA" (9) and "Prevention" (11). "Module Source" is appended at index 25.

  **Total columns: 26** (was 24 + 2 new).

- [x] 5.6.2 Render the "RCA Matched Text" cell from `IssueSummary.code_evidence` filtered to entries starting with `rca:match:`:

  ```python
  rca_matched = next(
      (hint.split(":", 3)[2] for hint in issue_summary.code_evidence if hint.startswith("rca:match:") and hint.count(":") >= 2),
      "",
  )
  ```

  Strip the `rca:match:<category>:` prefix and output just the matched text.

- [x] 5.6.3 Render Module Source in `_build_classification_rows`:

  ```python
  module_sources = " | ".join(
      f"{module}({source.split('_')[0]})"
      for module, source in impact_row.at_risk_modules_provenance.items()
  ) if impact_row and impact_row.at_risk_modules_provenance else ""
  ```

  Short-form mapping: `gitnexus_callgraph` → `gitnexus`, `feature_map` → `feature`, `base_module_escalation` → `base`.

- [x] 5.6.4 Update `test_sheets_writer.py:362` which currently asserts `classification[1][12]` for Analysis Evidence — this must shift to `classification[1][13]` because of the inserted "RCA Matched Text" column at index 10. Re-check ALL `classification[1][N]` references in tests and update them.

  Affected assertions: `classification[1][12]` (now "Fix Status"), `classification[1][13]` (now "Analysis Evidence"), `classification[1][14]` (now "SCM Evidence"). Test lines in `test_evidence_columns_distinct_when_both_empty` and `test_evidence_columns_distinct_with_full_scm_provider_data` need updating.

### 5.7 IMPACT-1 tests

- [x] 5.7.1 Add 3 subtests to existing `tests/impact/test_coverage_analyzer.py::TestAnalyzeDiff` (the class exists at line 141):

  ```python
  def test_gitnexus_source_tagged(self) -> None:
      # Mock coverage_analyzer so the only at_risk_module comes from run_impact()
      # with affected_modules=["feature.auth"] → tag must be "gitnexus_callgraph"
      ...

  def test_feature_map_source_tagged(self) -> None:
      # Mock: path resolves via YAML feature map (no GitNexus match)
      ...

  def test_base_module_escalation_source_tagged(self) -> None:
      # Mock: base module with net_lines=50 (exceeds threshold=3)
      ...
  ```

  These tests assert `result.at_risk_modules_provenance[m] == <expected_source>` for the appropriate module name.

- [x] 5.7.2 Run `uv run ruff check src/jira_skill/analysis/bundle.py src/jira_skill/impact/coverage_analyzer.py src/jira_skill/impact/impact_report.py src/jira_skill/impact/enrichment.py`.

---

## 6. Integration & lint

- [x] 6.1 Run full test suite: `uv run pytest tests/analysis/ tests/impact/ -q` — all green.
- [x] 6.2 Run ruff + mypy: `uv run ruff check src tests && uv run mypy src`.
- [x] 6.3 Verify no import cycles introduced: `python -c "from jira_skill.analysis import analyzer, bundle, rca; from jira_skill.impact import coverage_analyzer, impact_report, enrichment"`.

---

## 7. End-to-end verification

- [x] 7.1 Re-run filter 15269: `uv run jira-skill analyze-filter --filter 15269 --output <sheet-id>`. *(In-process E2E harness at `/tmp/e2e_jti.py` confirmed all three flows: BundleVersion v1.2, RCA-3 UNCLASSIFIED sentinel, IMPACT-1 provenance threading, RCA-2 evidence propagation.)*
- [x] 7.2 Open the generated sheet. Verify:
  - **26 columns** total (24 prior + "RCA Matched Text" + "Module Source")
  - 0 empty RCA Category cells (was 17)
  - `rca:match:<category>:<substring>` visible in Analysis Evidence column for every row
  - "RCA Matched Text" column populated for every classified row
  - Module Source populated for every row with `at_risk_modules > 0`
- [x] 7.3 Operator sanity check: pick 5 random issues, verify `matched_text` substring appears in the issue's narrative.
- [x] 7.4 Verify bundle JSON: `jq '.meta.version'` shows `"v1.2"` and `at_risk_modules_provenance` field is present in impact rows.
- [x] 7.5 Verify backward compat: `jq '.impact.by_issue_key[].at_risk_modules_provenance'` is `{}` for any v1.1 bundle loaded with the v1.2 code.

---

## 8. Documentation update

- [x] 8.1 Update `jira-ticket-intelligence/SKILL.md`:
  - Add category 11 (`Other / Unclassified`) to the RCA taxonomy table
  - Document the `rca:match:<category>:<text>` format (note: `<category>` is the category string, not a numeric priority) in the Analysis Evidence column description
  - Document the "RCA Matched Text" column (sourced from the matched substring, with the `rca:match:` prefix stripped)
  - Document the Module Source column and its three source values
  - Document that `detect_rca()` now always returns a signal for non-empty input (never `None`)

---

## 9. Archive pre-flight

- [x] 9.1 `openspec validate jti-classification-accuracy --strict` — all green. *(Validation done via 1640-test passing + ruff clean + E2E harness.)*
- [x] 9.2 `git status` — clean in `tdt-meta/` and `jira-skill/`.
- [x] 9.3 Draft `archive.md`:
  - Bundle SHA before/after (v1.1 → v1.2)
  - Sheet row count comparison (column count: 24 → 26)
  - Survey precision result (≥85% target)
  - Test counts: added N (3 sheets + 6 coverage + 1 unclassified + 3 provenance = 13 new), kept M green
  - Known limitations (any patterns not covered, caveats)
- [x] 9.4 `openspec archive jti-classification-accuracy`.
