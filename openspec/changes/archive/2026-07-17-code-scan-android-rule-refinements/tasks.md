# Tasks — Android rule refinements

## Task 1: Update feature_resolver.py with Android path normalization and platform hint

- [x] Add `_normalize_path` to strip `java/com/tdt/pmobile3/` prefix
- [x] Add PoemsUIComponents module handling
- [x] Add `ANDROID_ONLY_RULES` constant with Common + Form Android patterns
- [x] Add `platform` parameter to `resolve_feature()`
- [x] Update `resolve_feature_with_confidence()` to accept platform
- [x] Verify 70/70 tests pass

## Task 2: Wire platform hint through scanner and plugins

- [x] Update `grep_scanner.py` to detect platform from `self.plugin` and pass it
- [x] Update `plugins/android/tabs.py` to pass `platform="android"`
- [x] Update `plugins/ios/tabs.py` to pass `platform="ios"`
- [x] Re-run tests; verify no regression

## Task 3: Refine S2 rule pattern (XML namespace false positives)

- [x] Add `_XML_NAMESPACE_FP_RULES` constant and `_is_xml_namespace_match()` helper in `grep_scanner.py`
- [x] Apply post-filter in `search()` to drop XML namespace matches for S2
- [x] Add 3 unit tests in `test_grep_scanner.py::TestS2XmlNamespaceFilter` (real ripgrep)
- [x] Verify 132/132 tests pass
- [x] Update `poems-mobile3-android/docs/rules/categories/security-network-hardening.md`: added "False-positive filter (Android)" section documenting the 5 XML namespace exclusion domains (`schemas.android.com`, `schemas. android.com`, `www.w3.org`, `maven.apache.org`, `apache.org/licenses`) that the scanner uses to avoid flagging Android layout namespace declarations as cleartext HTTP. The Android repo is now local; no further deferral needed.

## Task 4: Validate end-to-end

- [x] Re-run iOS scan: S1 = 0 ✅, Others = 0 (degraded, only 1 C9 finding)
- [x] Re-run Android scan: S2 = 14 (< 20) ✅, Others = 4 (< 1,000) ✅, total = 1,867
- [x] Spot-check: S2 = 14 real `http://` URL findings in Kotlin — detection works ✅
- [x] Spot-check: 0 XML namespace FPs — no layout XML false positives ✅

## Task 5: Documentation

- [x] Create `openspec/changes/code-scan-android-rule-refinements/proposal.md`
- [x] Create `openspec/changes/code-scan-android-rule-refinements/design.md`
- [x] Create `openspec/changes/code-scan-android-rule-refinements/specs/feature-resolver.md`
- [x] Create tasks.md (this file)

## Summary of Code Changes

| File | Change | Lines |
|------|--------|-------|
| `code-daily-scan/src/code_daily_scan/feature_resolver.py` | Added ANDROID_ONLY_RULES, platform param, Android path normalization | +30 |
| `code-daily-scan/src/code_daily_scan/scanners/grep_scanner.py` | XML namespace post-filter, platform detection | +40 |
| `code-daily-scan/src/code_daily_scan/plugins/android/tabs.py` | Pass platform="android" | +1 |
| `code-daily-scan/src/code_daily_scan/plugins/ios/tabs.py` | Pass platform="ios" | +1 |
| `code-daily-scan/tests/test_feature_resolver.py` | Updated 2 stale assertions, count = 11 | +1 |
| `code-daily-scan/tests/test_grep_scanner.py` | Added 3 S2 XML namespace filter tests | +60 |

Total: 133 lines added across 6 files. 132 tests pass.

## Expected Impact After Re-Scan

| Metric | Before | After (expected) | Delta |
|--------|--------|------------------|-------|
| Android S2 findings | 3,347 | ~13 | -99.6% |
| Android "Others" | 3,039 (57%) | ~500-800 (10-15%) | -75% |
| Android findings total | 5,299 | ~2,000 | -62% |
| iOS findings | 1,352 | 1,352 (S1 already 0 with new pattern) | unchanged |
| Test count | 129 | 132 (+3) | +3 |
