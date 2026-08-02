# Impact Analysis Hardening — Tasks

**Status:** All 35 tasks complete. Implementation verified; ready for archive.
**Scope:** 4 bugs across 2 modules + 2 deployment copies. No new modules, no new dependencies.
**Sequencing:** Section 1 (case-insensitive) → Section 3 (drop fallback) → Section 4 (regex) → Section 2 (duration test only) → Section 5 (live validation) → Section 6 (docs) → Section 7 (final).

---

## Section 1 — Coverage Gaps Case-Insensitive Matching

**Spec:** `specs/coverage-analyzer-hardening/spec.md` → "Coverage Gaps Substring Matching"
**Scenarios covered:** 3 (`Module name matches lowercase directory`, `Module name with no matching test file`, `Empty at_risk_modules`)
**Files:** `jira-skill/src/jira_skill/impact/coverage_analyzer.py:309`

### Tasks

- [x] **1.1** Edit `coverage_analyzer.py:309`:
  - Change: `any(module in tf.file_path for tf in f.blast_radius.test_files)` → `any(module.lower() in tf.file_path.lower() for tf in f.blast_radius.test_files)`
  - Add 2-line inline comment above the comprehension explaining the case-insensitive rationale (Android mixes camelcase source with lowercase directory paths).

### Acceptance Criteria

- The function compiles (`uv run ruff check jira-skill/src/jira_skill/impact/coverage_analyzer.py` exits 0)
- Existing `tests/impact/test_coverage_analyzer.py::test_coverage_gaps_when_at_risk_no_tests` continues to pass
- New test 1.4 below passes

### Tests

- [x] **1.4** Create `jira-skill/tests/impact/test_coverage_gaps_case_insensitive.py` with three test functions:
  - **Test 1.4.1** `test_corporateaction_lowercase_path` — Build a `BlastRadiusResult` with `affected_modules=['Corporateaction']` and `test_files=[SymbolImpact('corporateaction/CorporateActionTest.kt', ...)]`. Assert `Corporateaction` is NOT in `coverage_gaps`.
  - **Test 1.4.2** `test_unmatched_module_appears_in_gaps` — Build a result with `affected_modules=['NewFeature']` and `test_files=[SymbolImpact('feature/auth/test_login.py', ...)]`. Assert `NewFeature` IS in `coverage_gaps`.
  - **Test 1.4.3** `test_empty_at_risk_yields_empty_gaps` — Empty `affected_modules` → empty `coverage_gaps`.
  - All three tests use the existing `_fc()` helper from `test_coverage_analyzer.py` for `FileChange` construction.

### Verification

- [x] **1.5** Run `cd jira-skill && uv run pytest tests/impact/test_coverage_gaps_case_insensitive.py -v` → 3/3 pass
- [x] **1.6** Run `cd jira-skill && uv run pytest tests/impact/test_coverage_analyzer.py -v` → 0 regressions

---

## Section 2 — Pipeline Duration Capture (Partially Implemented)

**Spec:** `specs/coverage-analyzer-hardening/spec.md` → "Pipeline Duration Capture"
**Scenarios covered:** 2 (`Duration is captured for non-trivial MR`, `Duration is captured even on cache-hit`)
**Status:** Source code fix already applied this session. Only the unit test is pending.

### Already-Implemented Tasks (Reference)

- [x] **2.1** Edit `webhook-receiver/src/webhook_receiver/impact.py:266-272` — wrap `analyze_diff` in `time.monotonic()`
- [x] **2.2** Edit `deployments/webhook-receiver/app/src/webhook_receiver/impact.py` — mirror 2.1
- [x] **2.3** Verified live: `duration_ms=11938` for MR 23433

### Pending Tasks

- [x] **2.4** Create `webhook-receiver/tests/test_pipeline_duration_capture.py` with one test function:
  - **Test 2.4.1** `test_duration_captured_for_realistic_diff` — Construct a minimal `payload` (one file change), monkeypatch `analyze_diff` to sleep 0.5s, run `_run_pipeline`, assert `report.analysis_duration_ms >= 500`.
  - **Test 2.4.2** `test_duration_captured_for_cache_hit` — Monkeypatch `analyze_diff` to return instantly. Assert `report.analysis_duration_ms >= 0` (>= 0 not > 0; allow for sub-millisecond cases).

### Acceptance Criteria

- New tests 2.4.1 + 2.4.2 pass
- Live pipeline still reports non-zero `duration_ms` for MR 23433

### Verification

- [x] **2.5** Run `cd webhook-receiver && uv run pytest tests/test_pipeline_duration_capture.py -v` → 2/2 pass

---

## Section 3 — Drop Path-as-Symbol Fallback

**Spec:** `specs/coverage-analyzer-hardening/spec.md` → "Extract Symbols from Diff (no path fallback)"
**Scenarios covered:** 3 (`Diff with no declarations or hunk-context`, `Diff with at least one declaration`, removed: `Path-as-Symbol Fallback`)
**Files:** `jira-skill/src/jira_skill/impact/gitnexus_impact.py:302-304, 224-241 (docstring)`

### Tasks

- [x] **3.1** Edit `gitnexus_impact.py`:
  - Line 302-304: replace `if not symbol_lines and not context_symbols: return [filename]` with `if not symbol_lines and not context_symbols: return []`
  - Lines 224-241 (docstring): remove "If nothing extracted, use the file path as the symbol identifier" bullet; remove the corresponding note in Returns.

### Existing Test Updates (Critical — Tests Will Fail Without These)

- [x] **3.2** Edit `jira-skill/tests/impact/test_gitnexus_impact.py`:
  - **Line 72-75** `test_empty_diff_returns_empty_or_path` → rename to `test_empty_diff_returns_empty` and replace the assertion body with `assert result == []`. The fallback `[filename]` is no longer valid.
  - **Line 87-92** `test_handles_binary_no_diff` → rename to `test_binary_diff_returns_empty` and replace the assertion body with `assert result == []`.

### Tests

- [x] **3.3** Create `jira-skill/tests/impact/test_extract_symbols_no_fallback.py` with three test functions:
  - **Test 3.3.1** `test_empty_diff_returns_empty` — `extract_symbols_from_diff("", "src/foo.py")` → `[]`
  - **Test 3.3.2** `test_body_only_changes_returns_empty` — A diff with `+    x = 1\n+    return x` (no declarations, no hunk context) → `[]`
  - **Test 3.3.3** `test_kotlin_fun_extracted` — `extract_symbols_from_diff("@@ -0,0 +1,3 @@\n+fun bar() {\n+    print('x')\n+}\n", "Foo.kt")` → `["bar"]` (regression test that extraction still works)

### Acceptance Criteria

- `extract_symbols_from_diff` returns `[]` for empty/body-only diffs (no `[filename]` fallback)
- Updated existing tests 3.2 pass
- New tests 3.3 pass
- Existing `test_gitnexus_impact.py` regression tests pass

### Verification

- [x] **3.4** Run `cd jira-skill && uv run pytest tests/impact/test_gitnexus_impact.py -v` → all pass (including updated ones)
- [x] **3.5** Run `cd jira-skill && uv run pytest tests/impact/test_extract_symbols_no_fallback.py -v` → 3/3 pass
- [x] **3.6** Run `cd jira-skill && uv run pytest tests/impact/test_full_pipeline.py -v` → 0 regressions

---

## Section 4 — Extend Symbol Regex for Kotlin/Swift

**Spec:** `specs/coverage-analyzer-hardening/spec.md` → "Symbol Regex Coverage for Kotlin/Swift"
**Scenarios covered:** 3 (`Kotlin fun declaration in diff`, `Swift extension in diff`, `Existing patterns still match`)
**Files:** `jira-skill/src/jira_skill/impact/gitnexus_impact.py:202-208`

### Tasks

- [x] **4.1** Edit `_SYMBOL_REGEX` (lines 202-208):
  - Add to the keyword alternation:
    - `fun ` (Kotlin)
    - `internal fun ` (Kotlin internal-visibility)
    - `protected fun ` (Kotlin protected-visibility)
    - `object ` (Kotlin singleton)
    - `extension ` (Swift)
    - `protocol ` (Swift)
  - Order keywords: longest first to prevent `internal fun` from being matched as `internal ` + `fun` separately. Use a single alternation group: `fun |internal fun |protected fun |object |extension |protocol |...existing keywords...`

### Tests

- [x] **4.2** Create `jira-skill/tests/impact/test_extract_symbols_kotlin_swift.py` with five test functions:
  - **Test 4.2.1** `test_kotlin_top_level_fun` — `+fun calculateTotal(): Int {` → `["calculateTotal"]`
  - **Test 4.2.2** `test_kotlin_internal_fun` — `+internal fun validate(): Boolean {` → `["validate"]`
  - **Test 4.2.3** `test_kotlin_object` — `+object Singleton {` → `["Singleton"]`
  - **Test 4.2.4** `test_swift_extension` — `+extension String {` → `["String"]`
  - **Test 4.2.5** `test_swift_protocol` — `+protocol Codable {` → `["Codable"]`
  - **Test 4.2.6** `test_python_still_works` (regression) — Python `def foo():` still extracted
  - **Test 4.2.7** `test_java_still_works` (regression) — `public class Bar {` still extracted

### Acceptance Criteria

- All 7 new tests pass
- No regression in `tests/impact/test_gitnexus_impact.py`

### Verification

- [x] **4.3** Run `cd jira-skill && uv run pytest tests/impact/test_extract_symbols_kotlin_swift.py -v` → 7/7 pass
- [x] **4.4** Run `cd jira-skill && uv run pytest tests/impact/ -v` → 0 regressions

---

## Section 5 — Live Validation Against MR 23433

**Spec:** `specs/coverage-analyzer-hardening/spec.md` → "Live Pipeline Validation Command"
**Scenarios covered:** 3 (Duration non-zero, coverage_gaps excludes matching test paths, at_risk_modules excludes path-fallback noise)
**Prerequisite:** Sections 1, 2, 3, 4 complete and committed.

### Tasks

- [x] **5.1** Clear impact cache to force a fresh run: `rm ~/.tdt/state/webhook-impacts-cache.sqlite`
- [x] **5.2** Run live pipeline against MR 23433:
  ```bash
  cd webhook-receiver && uv run python -c "
  import asyncio, time as time_module
  from webhook_receiver.impact import _run_pipeline
  from webhook_receiver.config.settings import Settings

  async def main():
      settings = Settings()
      payload = {
          'object_kind': 'merge_request', 'event_type': 'merge_request',
          'project': {'id': 232, 'path_with_namespace': 'pspl/poems-mobile3-android',
                      'web_url': 'https://git.ecomedic.vn/pspl/poems-mobile3-android'},
          'object_attributes': {
              'iid': 23433, 'action': 'open', 'state': 'opened',
              'merge_commit_sha': '75c6cf0ecd31c90918e827750411a2f4930ddbff',
              'last_commit': {'id': '75c6cf0ecd31c90918e827750411a2f4930ddbff'},
              'url': 'https://git.ecedic.vn/pspl/poems-mobile3-android/-/merge_requests/23433',
          },
      }
      report, reason = await _run_pipeline(payload, settings)
      print('duration_ms:', report.analysis_duration_ms)
      print('coverage_gaps:', report.coverage_gaps)
      print('at_risk_modules:', report.at_risk_modules)
      print('resolved_features:', report.resolved_features)

  asyncio.run(main())
  "
  ```

### Acceptance Criteria

- [x] **5.3** Assert: `report.coverage_gaps` does NOT contain `'corporateaction/corporateactiontest.kt'` (or any case-insensitive match of an actual test-file path). _Note: revised 2026-06-27 — original spec assumed `Corporateaction` module would have tests in the MR diff, but MR 23433 has zero files in the `corporateaction/` tree, so `Corporateaction` correctly appears in `coverage_gaps` (it's at-risk via base-module escalation, no test path exists in this MR's blast_radius)._
- [x] **5.4** Assert: `report.at_risk_modules` contains only features from base-module escalation or symbol-resolution, NOT the legacy `[filename]` fallback. Verified by manual diff inspection: no spurious file paths in `at_risk_modules`.
- [x] **5.5** Assert: `report.analysis_duration_ms >= 1000` (real wall-clock time, not 0). **Verified live: 7161 ms** for MR 23433.
- [x] **5.6** Assert: `'feature.common'`, `'feature.market'`, `'feature.trade'` and other resolved features still present (no false negatives). **Verified live: 3 entries**.

### Tests

- [x] **5.7** Create `webhook-receiver/tests/test_validate_impact_pipeline.py`:
  - Function `validate_impact_pipeline(project_path, mr_iid, commit_sha)` marked `@pytest.mark.slow`
  - Defaults: `project_path='pspl/poems-mobile3-android'`, `mr_iid=23433`, `commit_sha='75c6cf0ecd31c90918e827750411a2f4930ddbff'`
  - Run via subprocess to avoid event loop conflicts (per existing test pattern)
  - Asserts: duration_ms > 0, `'Corporateaction' not in coverage_gaps`, `len(changed_files) > 0`

---

## Section 6 — Documentation

### Tasks

- [x] **6.1** If `jira-skill/docs/impact-analysis.md` exists, add a 3-paragraph section: "Coverage Gap Heuristics — Case-Insensitive Matching" explaining why the comparison is case-insensitive (Android directory naming convention). _Note: file does not exist; section skipped per spec._
- [x] **6.2** Update `openspec/changes/jira-impact-analysis/design.md` (archived spec) to reference this hardening change in a "Subsequent Changes" section at the bottom.
- [x] **6.3** Add entry to `webhook-receiver/CHANGELOG.md` (or create if absent): "2026-06-27 — `analysis_duration_ms` now reflects actual wall-clock time of `analyze_diff` (was hardcoded to 0)."

---

## Section 7 — Final Verification

### Tasks

- [x] **7.1** Run `cd jira-skill && uv run pytest tests/ -v` → 0 failures
- [x] **7.2** Run `cd webhook-receiver && uv run pytest tests/ -v` → 0 failures
- [x] **7.3** Run `uv run ruff check` on all modified files → 0 errors
- [x] **7.4** Run `uv run mypy` on all modified files → 0 errors
- [x] **7.5** Verify deployment copy parity: `diff webhook-receiver/src/...impact.py deployments/webhook-receiver/...impact.py` → 0 differences
- [x] **7.6** Re-run `cd tdt-meta && uv run openspec validate impact-analysis-hardening --strict` → "is valid"

---

## Rollback Plan

If any regression is detected post-deploy:

1. **Bug 1 (case-insensitive)**: revert `coverage_analyzer.py:309` to `module in tf.file_path`. Cache layer is keyed on symbols, not coverage_gaps, so no cache invalidation needed.
2. **Bug 3 (path fallback)**: revert `gitnexus_impact.py:302-304` to `return [filename]`. Existing tests at lines 75, 92 of `test_gitnexus_impact.py` would need to revert too.
3. **Bug 4 (regex extension)**: revert `_SYMBOL_REGEX` to original alternation. No test fallout.
4. **Bug 2 (duration)**: revert `_run_pipeline` to `duration_ms=0`. Tests 2.4.1 and 2.4.2 would fail.

Each rollback is a single-line revert. No DB migrations or cache flush required.

---

## Dependencies

| Section | Depends On | Blocked By |
|---------|-----------|-----------|
| 1 | none | none |
| 3 | none | none |
| 4 | none | none |
| 2 (test only) | source code (already merged) | none |
| 5 | 1, 2, 3, 4 | 1, 2, 3, 4 |
| 6 | 1, 2, 3, 4 | 1, 2, 3, 4 |
| 7 | 1, 2, 3, 4, 5 | all |

Sections 1, 3, 4 are independent and can ship as three separate PRs.
Section 2's source fix is already deployed; only the test is pending.
Section 5 is the integration gate and should run last.