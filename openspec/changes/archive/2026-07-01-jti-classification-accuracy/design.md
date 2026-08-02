# jti-classification-accuracy — Design

## Verified Call-Site Audit (Pre-Design Corrections)

Before writing implementation details, the following discrepancies between the original audit and the verified codebase are documented so the design is grounded in reality.

| Finding | Original Audit | Verified Reality |
|---------|---------------|-----------------|
| RCA-2: `_extract_code_hints` + `detect_rca` call sites | One call site (line 177) | **Two** call sites: `analyzer.py:177-179` AND `analyzer.py:656-1068` |
| RCA-3: `detect_rca(...) is None` assertions in tests | 3 assertions in 1 test function | **5 assertions across 3 test functions**: lines 121/122/124 (`TestDetectRcaEdgeCases.test_empty_content_returns_none`), 1197 (`TestRcaStemMatching.test_stuck_is_not_performance_alone`), 1313 (`TestRcaCoverage.test_app_stuck_becomes_unclassified`) |
| RCA-3: `analyzer.py:189` after RCA-3 change | "no behavior change" | The `if issue_root_cause else None` guard stays correct; no caller-side changes required beyond updating the 5 test assertions |
| RCA-2: `RootCauseSignal.category_priority` | Spec uses `<priority>` in `rca:match:N:...` prefix | **`RootCauseSignal` has no `priority`/`category_priority` field.** Use `RootCauseSignal.category` (the category name string) in the prefix → format is `rca:match:<category>:<matched_text>` |
| ~~RCA-1: priority not honored~~ | Priority-1 Crash displaced by Priority-4 UI Layout | **False alarm.** With `best_priority=inf` initialized, any match sets `best_priority`. All subsequent matches fail `priority < best_priority`. Priority IS correctly honored. RCA-1 is removed per proposal — no code change. |
| IMPACT-1: provenance module name | `impact_report.py:213` | `coverage_analyzer.py:91` (`FileAnalysis.path`) + `AnalysisResult.at_risk_modules` at line 113 |
| IMPACT-1: provenance data flow | assumed single-stage | **Three-stage flow:** `coverage_analyzer.AnalysisResult` → `impact_report.ImpactReport` (at `impact_report.py:213`) → `ImpactRow` (built at `impact/enrichment.py:138,150`). Each stage carries the dict additively. |
| IMPACT-1: actual sources of provenance | "gitnexus_impact.py tags" | **All three sources live in `coverage_analyzer.py`** (lines 240-290). Source A = `base_module_escalation` heuristic; Source B = `gitnexus_callgraph` (when `run_impact()` returns affected modules); Source C = `feature_map` (path → feature resolution). `enrichment.py` is the propagation step, not the tagging step. |
| IMPACT-1: `Analysis Evidence` column index | ambiguous (12 or 14) | **Zero-indexed 12, 1-indexed 13.** `CLASSIFICATION_COLUMNS[12]` in `sheets_writer.py:74`. Test confirms at `test_sheets_writer.py:362` (`classification[1][12]`). |
| RCA-4: nature of changes | "6 new pattern groups" | 6 new patterns **added to existing** priority groups; no new category rows are added to the taxonomy. Actual taxonomy is **10** categories (Crash p1, Wrong Data p2, Silent Exit p3, Text/Font p4, UI Layout p4, Performance p5, Auth p6, Network p7, Feature Not Working p8, General UI/UX Polish p9). After RCA-3 adds the unclassified sentinel, the taxonomy has 11 named categories. |
| RCA-4: actual category names | spec uses informal abbreviations | Verified names: `"Crash / ANR / Force Close"`, `"Wrong Data / Incorrect Value"`, `"Silent Exit / No Feedback"`, `"Text / Font Display"`, `"UI Layout / Visual Defect"`, `"Performance / Slow Loading"`, `"Authentication / Authorization"`, `"Network / API Connectivity"`, `"Feature Not Working / Missing"`, `"General UI/UX Polish — no specific pattern matched"` |
| Bundle version constant | `bundle_version.MINOR` | **`BundleVersion.MINOR` (IntEnum member) at `bundle.py:62-71`**. Increment in place. `BUNDLE_VERSION = BundleVersion.current()` at module load. |
| `test_sheets_writer.py` uses classes | `TestClassificationRows` | **No test classes exist** — only fakes (`FakeMetadata`, `FakeSheetsClient`) and **module-level functions** (e.g., `test_evidence_columns_distinct_when_both_empty`). Tests must be added as module-level functions. |
| `test_rca.py` Survey precision test | "test_rca_survey_precision test class" | **`TestRcaSurveyPrecision.test_survey_precision_target`** at line 1434; **65-ticket `SURVEY` list** with `(content, expected_category)` tuples. |

---

## 1. Evidence propagation to the sheet (RCA-2)

**Current state**: `RootCauseSignal.matched_text` (str) and `.evidence` (list[SignalEvidence]) exist in `signals.py:472-479` but the `matched_text` substring is never rendered by `sheets_writer.py`. The "Analysis Evidence" column (`CLASSIFICATION_COLUMNS[12]`, verified at `sheets_writer.py:74`; zero-indexed 12, 1-indexed 13) is populated from `IssueSummary.code_evidence`, sourced from `_extract_code_hints()` — which only inspects `raw_fields.code_context`, `worktree_commits`, and `mr_references`. None of those are populated for closed-bug backlog items.

**Two call sites confirmed** — the fix must apply to both:

| Call site | Location | Code path |
|-----------|----------|-----------|
| Primary | `analyzer.py:177-179` | `analyze_snapshot()` → `_extract_code_hints(issue)` then `issue_root_cause = sig_set.root_cause[0] if sig_set.root_cause else None` |
| Secondary | `analyzer.py:656-1068` | `_analyze_single_issue()` → `_extract_code_hints(issue)` then `rca_signal = detect_rca(rca_content, code_hints=code_hints)` |

**Fix (two-step):**

**Step A — extend `_extract_code_hints`** to accept an optional `rca_signal=` parameter. In both call sites, the resolved RCA signal is already available by the time `_extract_code_hints` is called — it just needs to be threaded through.

```python
# analyzer.py line 177 — primary call site
issue_code_hints = _extract_code_hints(issue, rca_signal=issue_root_cause)
```

```python
# analyzer.py line 656 — secondary call site
# issue_root_cause is NOT computed here; instead compute rca_content first,
# then detect_rca, then pass the result back to _extract_code_hints.
# See implementation task 2.2 for the full refactor.
rca_content = "\n\n".join(
    part for part in [issue.summary or "", description_text or "", *comment_bodies] if part
)
rca_signal = detect_rca(rca_content, code_hints=code_hints)
code_hints = _extract_code_hints(issue, rca_signal=rca_signal)  # append RCA evidence
```

The helper appends, when `rca_signal is not None`:

```python
if rca_signal is not None:
    # Use the category string from RootCauseSignal (which has no separate priority field).
    # This produces entries like: "rca:match:UI Layout / Visual Defect:tab isn't highlight"
    hints.append(f"rca:match:{rca_signal.category}:{rca_signal.matched_text}")
```

**Step B — sheet rendering.** No code change needed in `sheets_writer.py` — the existing `" | ".join(issue_code_evidence)` line (column at zero-indexed 12) automatically picks up the new entry. Operators see the audit trail inline: `rca:match:UI Layout / Visual Defect:tab isn't highlight | branch main has 3 commits mentioning AM-2343`.

**Unit test**: `tests/analysis/test_sheets_writer.py::test_rca_match_in_analysis_evidence` (module-level function; existing test file pattern uses no test classes — see `test_evidence_columns_distinct_when_both_empty` for the fixture pattern).

---

## 2. Unclassified fallback (RCA-3)

**Current state**: `detect_rca()` returns `RootCauseSignal | None`. When None, `analyzer.py:189` writes `rca_category=None`, the sheet writes `""`.

**Test blast radius** (5 assertions across 3 test functions):

| File | Line | Test function | Assertion |
|------|------|---------------|-----------|
| `test_rca.py` | 121 | `test_empty_content_returns_none` | `detect_rca("") is None` |
| `test_rca.py` | 122 | `test_empty_content_returns_none` | `detect_rca("   ") is None` |
| `test_rca.py` | 124 | `test_empty_content_returns_none` | `detect_rca(None) is None` |
| `test_rca.py` | 1197 | `test_stuck_is_not_performance_alone` | `sig is None` |
| `test_rca.py` | 1313 | `test_app_stuck_becomes_unclassified` | `sig is None` |

All 5 must be updated to assert `category == UNCLASSIFIED_CATEGORY` instead of `is None`.

**Fix** (three coordinated changes):

**Step A — sentinel constant.** New module-level constant in `rca.py`:

```python
UNCLASSIFIED_CATEGORY = "Other / Unclassified"
```

**Step B — `detect_rca()` always returns a signal.** Replace the `return None` at line 902 with:

```python
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
```

The sentinel is non-empty, semantically clear, and pivotable. Confidence 0.0 makes the unclassified bucket visible to downstream severity scoring.

**Step C — caller adaptation.** `analyzer.py:189` (`rca_category=issue_root_cause.category if issue_root_cause else None`) remains correct — the `else None` branch is now only reachable when `sig_set.root_cause` is empty (which should not happen after RCA-3, but the guard is harmless). Callers of `detect_rca()` in other code paths (e.g., any code that stores the result in a nullable variable) should be audited and updated.

**Step D — catalog update.** Add a new row to the RCA taxonomy documentation:

> 11. `Other / Unclassified` — assigned when no pattern from categories 1-10 matches. Confidence = 0.0. Operator signal: requires manual triage.

**Unit test**: `tests/analysis/test_rca.py::TestDetectRca.test_unclassified_fallback`. The existing `TestRcaSurveyPrecision` MUST still assert ≥85% precision (unclassified is excluded from the precision denominator).

---

## 3. Coverage gap closure (RCA-4)

Six new patterns are added to **existing** priority groups in `rca_patterns.py`. No new category rows or taxonomy entries are added. Each pattern goes through the existing `_stem_pattern()` wrapper at module load so inflections are matched automatically.

| Target group (priority) | New patterns | Live-run motivation |
|------------------------|--------------|---------------------|
| Auth / Authorization (p6) | `\bsso\b`, `\bsaml\b`, `\b(token)\s+(expired|expire|expires)\b`, `\bjwt\b.*\b(invalid|expired|missing)\b` | Mobile JWT refresh bugs; SSO silent failures |
| Network / API Connectivity (p7) | `\b(offline|queue|retry).{0,20}(fail|loop|stuck|storm)\b`, `\bcircuit.?breaker\b`, `\breconnect` | Captures offline-mode retry patterns |
| Feature Not Working / Missing (p8) | `\b(filter|pagination|sort|search)\s+(does not|doesn't|fails to|not)\s+(reset|apply|load|trigger)\b`, `\bscroll\s+to\s+(top|bottom)\s+(not|fails|broken)\b` | Captures filter-reset / pagination regressions explicitly |
| Wrong Data / Incorrect Value (p2) | `\bdecimal\b.*\b(precision|scaling|rounding|truncation)\b`, `\bcurrency\b.*\b(conversion|fx|exchange.?rate)\s+(wrong|stale|incorrect)\b` | Decimal precision in financial apps |
| Text / Font Display (p4) | `\b(locale|i18n|translation)\b.*\b(wrong|broken|missing|cut.?off|overflow)\b` | Catches i18n truncation that text-only QA might mark |
| Performance / Slow Loading (p5) | `\b(startup|launch)\s+time\b.*\b(slow|high|exceeded|timeout)\b`, `\bmemory\s+(leak|growth|usage)\b` | Captures cold-start regressions |

**Unit test**: one survey-positive fixture per new pattern group added to `tests/analysis/test_rca.py::TestRcaCoverage` (or a new test class). `TestRcaSurveyPrecision` regression gate must stay ≥85%.

---

## 4. `at_risk_modules` provenance (IMPACT-1)

**Spec source-of-truth**: `openspec/specs/impact-sheet-integration/spec.md` — Requirement: "Module provenance on at_risk_modules". This section documents the verified implementation path for that requirement.

**Verified provenance chain (THREE stages — additive throughout):**

```
FileChange objects (from gitlab_mr)
    ↓
coverage_analyzer.analyze_diff()   [coverage_analyzer.py:240-290]
    ├── per file: FileAnalysis { path: str, feature_resolution, lines_added/removed,
    │                    symbols_extracted, blast_radius }
    └── aggregate: AnalysisResult {
                    at_risk_modules: list[str],                  # line 113 (existing)
                    at_risk_modules_provenance: dict[str, str],  # NEW (additive)
                    ...
                  }
    ↓
impact_report.ImpactReport   [impact_report.py:121-213]
    at_risk_modules: list[str]                  # line 139 (existing)
    at_risk_modules_provenance: dict[str, str]  # NEW (additive, threaded from AnalysisResult)
    ↓
ImpactRow (built in ImpactEnricher._enrich_keys)  [enrichment.py:138,150]
    at_risk_modules: list[str]                  # existing
    at_risk_modules_provenance: dict[str, str]  # NEW (additive, threaded from ImpactReport)
    ↓
sheets_writer column at zero-indexed 24 "Module Source"  [new — CLASSIFICATION_COLUMNS[24]]
```

**Spec type**: `at_risk_modules_provenance: dict[str, str]` (module name → source label).

**Fix (3-stage, all additive)**:

**Stage 1 — `coverage_analyzer.py`**: tag each append with source. Three sources live here (lines 240-290):

```python
# Source A: base_module_escalation (line 247)
# When abs(net_lines) > BASE_MODULE_LINE_DELTA_THRESHOLD for a base module change,
# all platform features are added without GitNexus.
at_risk_modules.append(tag)
at_risk_modules_provenance[tag] = "base_module_escalation"

# Source B: gitnexus_callgraph (lines 278-287)
# When run_impact() returns affected_modules for changed symbols.
for mod in affected_modules:
    at_risk_modules_provenance[mod] = "gitnexus_callgraph"

# Source C: feature_map (feature_map.py)
# When a path is resolved via the YAML feature map (no GitNexus match).
# Tag with "feature_map".
```

**Stage 2 — `impact_report.py`**: `ImpactReport` (line 121) gains `at_risk_modules_provenance` field. `analyze_mr_to_report()` at line 213 copies `result.at_risk_modules_provenance` into the report alongside `at_risk_modules`.

**Stage 3 — `enrichment.py`**: `ImpactEnricher._enrich_keys()` at lines 138, 150 (where `ImpactRow` is constructed) propagates `report.at_risk_modules_provenance` into the row. **Critical:** `ImpactRow(at_risk_modules=sorted(at_risk))` at line 145 must also pass `at_risk_modules_provenance=report.at_risk_modules_provenance`. Any module that gets sorted out (e.g., deduped) MUST have its provenance preserved.

**Sheet**: new column "Module Source" at zero-indexed position 24. Rendered as:

```python
" | ".join(f"{module}({source.split('_')[0]})" for module, source in at_risk_modules_provenance.items())
# Example: "feature.common(gitnexus) | feature.search(feature)"
```

**Backward compat**: `at_risk_modules: list[str]` stays at line 336 of `bundle.py`. `at_risk_modules_provenance` defaults to `{}`. v1.1 consumers continue to work.

**Bundle version**: bump `BundleVersion.MINOR` from `1` to `2` at `bundle.py:71`. Since `BUNDLE_VERSION = BundleVersion.current()` is computed at import time, simply changing the constant propagates everywhere.

**Unit tests** (3 in `tests/impact/test_coverage_analyzer.py::TestAnalyzeDiff` — class exists at line 141):
- `test_gitnexus_source_tagged` — mock GitNexus returns `affected_modules=["feature.auth"]`; assert `result.at_risk_modules_provenance["feature.auth"] == "gitnexus_callgraph"`
- `test_feature_map_source_tagged` — mock feature map fallback; assert `source == "feature_map"`
- `test_base_module_escalation_source_tagged` — mock base module delta > 3; assert `source == "base_module_escalation"`

---

## Files Touched

| File | Action | Notes |
|------|--------|-------|
| `jira-skill/src/jira_skill/analysis/rca.py` | Replace `return None` at line 902 with sentinel signal; add `UNCLASSIFIED_CATEGORY` constant | No tie-break change (RCA-1 removed) |
| `jira-skill/src/jira_skill/analysis/analyzer.py` | 1. Extend `_extract_code_hints()` (line 1256) to accept `rca_signal=` param (2 call sites)<br>2. Refactor secondary call site (lines 656-1068) to compute RCA signal before re-calling `_extract_code_hints` | Primary: line 177-179; Secondary: line 656 + 1068 |
| `jira-skill/src/jira_skill/analysis/extractors/rca_patterns.py` | Add 6 patterns to existing priority groups (RCA-4) | No new category rows; 10 categories remain |
| `jira-skill/src/jira_skill/analysis/bundle.py` | 1. Bump `BundleVersion.MINOR` from `1` to `2` at line 71<br>2. Add `at_risk_modules_provenance: dict[str, str] = Field(default_factory=dict)` to `ImpactRow` at line 336 (additive) | Bundle becomes v1.2 |
| `jira-skill/src/jira_skill/impact/coverage_analyzer.py` | 1. Add `at_risk_modules_provenance: dict[str, str]` to `AnalysisResult` (line 113+)<br>2. Tag every `at_risk_modules.append(...)` with `at_risk_modules_provenance[module] = source` (3 sources) | Lines 240-290 |
| `jira-skill/src/jira_skill/impact/impact_report.py` | 1. Add `at_risk_modules_provenance` field to `ImpactReport` (line 121+)<br>2. In `analyze_mr_to_report()` at line 213: copy `result.at_risk_modules_provenance` → report | Threading stage 2 of 3 |
| `jira-skill/src/jira_skill/impact/enrichment.py` | In `_enrich_keys()` at lines 138, 145-150: propagate `report.at_risk_modules_provenance` into `ImpactRow.at_risk_modules_provenance` | Threading stage 3 of 3 — **the final consumer of provenance before the sheet** |
| `jira-skill/src/jira_skill/analysis/sheets_writer.py` | Extend `CLASSIFICATION_COLUMNS` (line 61) with new `"RCA Matched Text"` column (after index 9 "RCA") and `"Module Source"` column at zero-indexed position 24 (appended); update rendering loop in `_build_classification_rows` to populate the new columns | Total columns: 24 → 26 (or 23 → 25 depending on "RCA Matched Text" inclusion) |
| `jira-skill/tests/analysis/test_rca.py` | Update 5 `is None` assertions across 3 test functions → `category == UNCLASSIFIED_CATEGORY` (lines 121, 122, 124 in `TestDetectRcaEdgeCases`; line 1197 in `TestRcaStemMatching`; line 1313 in `TestRcaCoverage`); add `test_unclassified_fallback` to `TestDetectRca` | Existing 170+ tests must stay green |
| `jira-skill/tests/analysis/test_sheets_writer.py` | Add `test_rca_match_in_analysis_evidence` (module-level function, NOT inside a class — see existing `test_evidence_columns_distinct_when_both_empty` for pattern) | |
| `jira-skill/tests/impact/test_coverage_analyzer.py` | Add 3 subtests to existing `TestAnalyzeDiff` class (line 141) | `test_gitnexus_source_tagged`, `test_feature_map_source_tagged`, `test_base_module_escalation_source_tagged` |
| `.agents/skills/jira-ticket-intelligence/SKILL.md` | Add category 11 row to RCA taxonomy table; document `rca:match:<category>:<text>` in Analysis Evidence; document Module Source column | |
| `openspec/changes/jti-classification-accuracy/specs/jti-classification-accuracy/spec.md` | New spec, 4 requirements (RCA-2 to RCA-4 + IMPACT-1), 19 scenarios | |
| `openspec/specs/impact-sheet-integration/spec.md` | IMPACT-1 requirement already present at lines 81-104 | No edit needed; spec change is **additive provenance threading clarification only** |

**Total: 13 modified + 2 new = 15 files.**

---

## Verification Plan

1. `uv run pytest tests/analysis/ tests/impact/ -q` — all existing tests still pass + 8 new tests.
2. `uv run pytest tests/analysis/test_rca.py::TestRcaSurveyPrecision -q` — precision ≥85% (regression gate).
3. Re-run filter 15269 on live corpus. Bundle SHA changes; sheet shows the new columns. Verify:
   - 0 empty RCA cells (was 17)
   - Every row has `rca:match:<category>:<substring>` in Analysis Evidence column
   - Module Source column populated for all `at_risk_modules > 0` rows
4. Operator sanity check: pick 5 random issues, verify `matched_text` substring actually appears in the issue's narrative (eyeball verification).
5. Archive pre-flight: `openspec validate jti-classification-accuracy --strict`.
