# Proposal: S2 Android XML-namespace FPs + Feature resolver Android coverage

## Why

The Android daily scan produces 3,347 S2 (cleartext HTTP) findings, of which 3,334 (99.6%) are false positives matching XML namespace declarations in layout XML files (`xmlns:android="http://schemas.android.com/apk/res/android"`). The remaining 13 are real `.kt` references.

In parallel, 57.4% of Android findings (3,039 of 5,299) fall into the "Others" feature bucket because the feature resolver only had patterns calibrated for the iOS layout (`Pmobile3/Modules/...`). The Android Kotlin package layout (`app/src/main/java/com/tdt/pmobile3/<module>/...`) was not properly normalized, so most files failed to match any feature.

## What Changes

### 1. S2 Rule Refinement (Android)

Update the S2 detection pattern from a raw `http://` substring to a URL pattern that excludes XML namespace URIs. The pattern is loaded by `AndroidMarkdownRuleParser` from `poems-mobile3-android/docs/rules/categories/security-network-hardening.md`. Until that file is updated, the fallback pattern in `code-daily-scan/config/rule_patterns.yaml` has been updated to:

```regex
\bhttps?://(?!schemas\.android\.com|www\.w3\.org)
```

This regex:
- Matches `http://...` and `https://...` URLs
- Skips the Android namespace (`schemas.android.com`)
- Skips XML namespace declarations (`www.w3.org`)
- Preserves detection of real cleartext URLs in code, network configs, and strings

The corresponding markdown file in the Android repo must be updated in lockstep to keep the source-of-truth rule consistent with the fallback.

### 2. Feature Resolver Android Coverage

Add a new `Common` feature bucket and a `Form` pattern extension in `code-daily_scan/feature_resolver.py` to cover Android-specific module paths that previously fell into `Others`:

- `Common` patterns: `ui/common`, `ui/customview`, `ui/dialog`, `extensions/`, `utils/`, `adapter/`, `model/`, `viewmodels/details`, `res/`
- `Form` additions: `screener`, `usso`, `phase1`, `conversation`

These patterns are scoped to a new `ANDROID_ONLY_RULES` list because:
- iOS paths (`Pmobile3/...`) would falsely match `extensions/`, `ui/common`, etc.
- The Android path normalizer strips `java/com/tdt/pmobile3/`, producing module-relative paths that don't conflict with iOS

The resolver signature now accepts a `platform` hint:

```python
def resolve_feature(file_path: str, platform: str | None = None) -> str
```

- `platform="android"` enables `ANDROID_ONLY_RULES`
- `platform="ios"` or `None` uses only the global `FEATURE_RULES`
- Callers (grep_scanner, ios/tabs.py, android/tabs.py) pass the platform hint

### 3. Path Normalizer

`_normalize_path()` now handles three Android-specific prefixes in order:

1. `java/com/tdt/pmobile3/` — strip package prefix to expose the module path
2. `java/com/tdt/poemsui/` — bucket the PoemsUIComponents module as `common/`
3. `app/src/main/res/` — bucket resource files (strings, themes, layouts) as `common/res/`

Previously, only `app/src/main/res/` was handled; Kotlin/Java files inside `pmobile3/` were left intact and rarely matched any feature.

## Impact

| Metric | Before | After (expected) | Delta |
|--------|--------|------------------|-------|
| Android S2 findings | 3,347 | ~13 (real `.kt` URLs) | -99.6% |
| Android "Others" | 3,039 (57%) | ~500-800 (10-15%) | -75% |
| iOS "Others" | 168 (12%) | 168 (12%) | unchanged |
| Android findings total | 5,299 | ~2,000 (after S2 fix) | -62% |
| Test count | 72 | 70 (2 stale test cases removed) | -2 |

## Verification

Run the Android scan with the new rules and compare against the previous `state/last-run-android.json`:
- S2 count should drop from 3,347 to < 20
- "Others" feature should drop from 3,039 to under 1,000
- No legitimate findings should be lost (only false positives should be removed)

Unit tests in `tests/test_feature_resolver.py` cover both the new `Common` and `Form` patterns, and the iOS leakage guard.
