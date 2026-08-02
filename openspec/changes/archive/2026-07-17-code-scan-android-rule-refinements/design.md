# Design — Android rule refinements

## S2 Pattern Design

The original pattern `http://` is a raw substring match. It catches:
1. Real `http://api.example.com` references in Kotlin/Java code (target)
2. XML namespace declarations `xmlns:android="http://schemas.android.com/apk/res/android"` (false positive)
3. W3C namespace declarations like `xmlns:app="http://schemas.android.com/apk/res-auto"` (false positive)

Replacement: a URL regex with negative lookahead:

```regex
\bhttps?://(?!schemas\.android\.com|www\.w3\.org)
```

This matches `http://` or `https://` followed by any host **except** the two XML namespace hosts. Verified with ripgrep: namespace strings in layout XML files (3,334 occurrences) are filtered out, while real URLs in `NetworkModule.kt`, `OkHttpClient.kt`, and similar files are preserved.

## Feature Resolver Architecture

```
feature_resolver.py
├── FEATURE_RULES          # Cross-platform: Trade, Auth, Home, WatchList, Form, ...
├── ANDROID_ONLY_RULES     # Android-only: Common (ui/common, extensions/, res/, ...)
└── resolve_feature(path, platform) → str
```

The `platform` hint is a string (`"android"`, `"ios"`, `None`) and is supplied by the calling scanner, which has access to the plugin object.

## Path Normalizer Flow

```
input path → lowercase
       │
       ├── starts with "java/com/tdt/pmobile3/" ?
       │       └─→ strip prefix → return module-relative path
       │           e.g. "ui/common/Dialog.kt" → "ui/common/Dialog.kt"
       │
       ├── starts with "java/com/tdt/poemsui/" ?
       │       └─→ strip prefix, prepend "common/" → return
       │           e.g. "Extensions.kt" → "common/Extensions.kt"
       │
       ├── starts with "app/src/main/res/" ?
       │       └─→ strip prefix, prepend "res/" → return
       │           e.g. "values/strings.xml" → "res/values/strings.xml"
       │
       └── fallback: try iOS base prefixes
                  ("Pmobile3/Modules/", "Pmobile3/", "ios/Pmobile3/Modules/")
```

## Files Touched

| File | Change | Lines |
|------|--------|-------|
| `code-daily-scan/src/code_daily_scan/feature_resolver.py` | Added ANDROID_ONLY_RULES, platform param, Android path normalization | +30 |
| `code-daily-scan/src/code_daily_scan/scanners/grep_scanner.py` | Pass platform hint to resolve_feature | +5 |
| `code-daily-scan/src/code_daily_scan/plugins/android/tabs.py` | Pass platform="android" | +1 |
| `code-daily-scan/src/code_daily_scan/plugins/ios/tabs.py` | Pass platform="ios" | +1 |
| `code-daily-scan/tests/test_feature_resolver.py` | Updated 2 stale assertions, count = 11 | +1 |
| `code-daily-scan/config/rule_patterns.yaml` | Refined S2 pattern (fallback) | +2 |

## Risks

1. **iOS leakage**: The `Common` patterns use generic substrings like `extensions/`, `utils/`, `model/`. If iOS paths normalize to a form containing these, iOS findings would be misclassified. Mitigation: ANDROID_ONLY_RULES only applies when `platform="android"`. Verified via 70/70 test cases.

2. **Stale markdown file**: The Android repo's `security-network-hardening.md` still has the old `http://` pattern. Until updated, the Android scanner will still produce 3,347 S2 findings. The yaml fallback is a defensive measure for non-Android-plugin scans.

3. **Resource files**: All Android `res/` files now bucket as `Common` regardless of feature. This is correct (resources are shared) but may surprise users expecting `Trade/res/...` to be classified as Trade.
