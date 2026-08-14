# Tasks: Android Rule Pattern Accuracy

## 1. C2 Pattern Fix

- [x] [historical] 1.1 Update C2 detection pattern in `poems-mobile3-android/docs/rules/categories/crash-runtime.md` from `class .*Fragment\(.*\)` to `class \w+\([^)]+\)\s*:\s*(Base)?Fragment`
- [x] [historical] 1.2 Verify C2 pattern change doesn't break existing test cases
- [x] [historical] 1.3 Run Android scan and confirm C2 findings drop from 550 to <150

## 2. C8 Post-Filter

- [x] [historical] 2.1 Add `suppress_c8_lifecycle_safe` to `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py`
- [x] [historical] 2.2 Register in `ANDROID_RULE_POST_FILTERS` under key `"C8"`
- [x] [historical] 2.3 Add unit tests for lifecycle-safe suppression
- [x] [historical] 2.4 Run Android scan and confirm C8 findings drop from 330 to <100

## 3. P5 Post-Filter Enhancement

- [x] [historical] 3.1 Add `suppress_p5_small_adapter` to `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py`
- [x] [historical] 3.2 Enhance existing `suppress_diffing_p5` to also check adapter size
- [x] [historical] 3.3 Add unit tests for small adapter suppression
- [x] [historical] 3.4 Run Android scan and confirm P5 findings drop from 233 to <140

## 4. Validation

- [x] [historical] 4.1 Run full test suite
- [x] [historical] 4.2 Run `ruff check`, `ruff format --check`, `mypy --strict`
- [x] [historical] 4.3 Run Android scan and verify total findings drop from 1860 to <1100
- [x] [historical] 4.4 Spot-check 5 known TP findings are preserved
- [x] [historical] 4.5 Spot-check 5 known FP findings are suppressed

## 5. Documentation & Archive

- [x] [historical] 5.1 Run `openspec validate --strict android-rule-pattern-accuracy`
- [x] [historical] 5.2 Commit changes
- [x] [historical] 5.3 Archive change


---

> **Historical record:** This change was archived with 19 incomplete task(s) (0/19 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
