# Tasks — Rule pattern FP reduction

## 1. Android L3 const-only companion post-filter

- [x] 1.1 Add `suppress_l3_const_companion(findings_per_file)` to `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py`. Function reads the file at `findings[0].absolute_file_path`, locates the matched `companion object {` line, and scans the next 30 lines for `lateinit var ...: (Context|Activity|Fragment|View)`. If none found, drop the finding.
- [x] 1.2 Register `suppress_l3_const_companion` in `ANDROID_RULE_POST_FILTERS` dict under the key `"L3"`.
- [x] 1.3 Add unit test `test_l3_const_only_companion_is_suppressed` to a new `code-daily-scan/tests/test_post_filters.py` using a tmp file with `companion object { const val FOO = 1 }`.
- [x] 1.4 Add unit test `test_l3_lateinit_activity_is_preserved` with `companion object { lateinit var activity: Activity }`.

## 2. Android C9 null-guarded `!!` post-filter

- [x] 2.1 Add `suppress_c9_guarded_notnull(findings_per_file)` to the same `post_filters.py` module. Function reads the file, locates the matched line (col 0), checks the 3 preceding lines for `if (.... != null)`. If found, drop the finding.
- [x] 2.2 Register `suppress_c9_guarded_notnull` in `ANDROID_RULE_POST_FILTERS` dict under the key `"C9"`.
- [x] 2.3 Add unit test `test_c9_guarded_bang_bang_is_suppressed` to `test_post_filters.py` with the `if (x != null) { x!!.field }` fixture.
- [x] 2.4 Add unit test `test_c9_unguarded_bang_bang_is_preserved` with `currentCurrencyConvert!!` and no preceding null guard.

## 3. iOS post-filters module

- [x] 3.1 Create `code-daily-scan/src/code_daily_scan/plugins/ios/post_filters.py` with module docstring (mirroring the Android module).
- [x] 3.2 Add `suppress_ios_a6_lifecycle_prints(findings_per_file)` that matches snippet against `re.compile(r'print\(\[.*\]\s*(deinit|init)\s*\)')` and the equivalent `debugPrint` regex. Drop findings that match.
- [x] 3.3 Export `IOS_RULE_POST_FILTERS: dict[str, RulePostFilter] = {"A6": suppress_ios_a6_lifecycle_prints}`.
- [x] 3.4 Add unit test `test_ios_a6_deinit_print_is_suppressed` with `print("[EWReviewBaseViewModel] deinit")`.
- [x] 3.5 Add unit test `test_ios_a6_production_error_print_is_preserved` with `print("❌ Provisioning start failed: \(error)")`.

## 4. iOS plugin wiring

- [x] 4.1 Edit `code-daily-scan/src/code_daily_scan/plugins/ios/plugin.py` to add the import `from . import post_filters`.
- [x] 4.2 Add `composite_rule_min_matches: dict[str, int] = {"C1": 2, "C5": 2, "C6": 2}` attribute to `IOSPlugin`.
- [x] 4.3 Add `cleanup_rule_pairs: dict[str, tuple[str, str]] = {"L2": (r"Timer\\.scheduledTimer\\s*\\(\\s*withTimeInterval:", r"timer\\??\\.invalidate\\s*\\(")}` attribute.
- [x] 4.4 Add `rule_post_filters: dict[str, Callable[[list[Finding]], list[Finding]]] = post_filters.IOS_RULE_POST_FILTERS` attribute.
- [x] 4.5 Add unit tests in `code-daily-scan/tests/test_ios_plugin.py`: `test_ios_plugin_has_composite_rule_min_matches`, `test_ios_plugin_has_cleanup_rule_pairs`, `test_ios_plugin_has_rule_post_filters`.

## 5. End-to-end validation

- [x] 5.1 Run the iOS EWallet scan with the new post-filters active. Confirm L2 ≤ 3, C1 ≤ 1, A6 ≤ 9 (from the proposal's expected counts).
- [x] 5.2 Run the Android EWallet scan. Confirm L3 ≤ 19, C9 ≤ 1.
- [x] 5.3 Spot-check 5 known-TP findings (M2 `EWProgressLoadingIndicator`, C7 `EWalletContactSupportScreen`, A3 `EWUpdateRFIScreenViewModel`, A6 `print("❌ Provisioning start failed")` in `EWPushProvisioningService.swift`, RCA-ARCH-002 in `EWalletCardDetailsScreen.kt`) — all should still be present.
- [x] 5.4 Spot-check 5 known-FP findings (`EWPINView.kt`, `pendingTransactionLimit!!`, `EWOnboardingScreen` C1, `EWPrepareKYCVM` L2, `EWReviewBaseViewModel` A6) — all should be suppressed.
- [x] 5.5 Run the full `code-daily-scan` test suite. Confirm `+8` tests in `test_post_filters.py` and `+3` tests in `test_ios_plugin.py`, all green.

## 6. Documentation

- [x] 6.1 Verify `openspec/changes/rule-pattern-fp-reduction/proposal.md` final form is committed to `tdt-meta`.
- [x] 6.2 Verify `design.md`, `specs/rule-pattern-fp-suppression/spec.md`, and `tasks.md` are all in place under `openspec/changes/rule-pattern-fp-reduction/`.
- [x] 6.3 Add a short summary comment to `code-daily-scan/src/code_daily_scan/plugins/ios/post_filters.py` linking to the OpenSpec change for future maintainers.

## Summary of Code Changes

| File | Change | Lines |
|------|--------|-------|
| `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py` | Add `suppress_l3_const_companion`, `suppress_c9_guarded_notnull` | +80 |
| `code-daily-scan/src/code_daily_scan/plugins/ios/post_filters.py` (new) | Define `suppress_ios_a6_lifecycle_prints`, export `IOS_RULE_POST_FILTERS` | +35 |
| `code-daily-scan/src/code_daily_scan/plugins/ios/plugin.py` | Add `composite_rule_min_matches`, `cleanup_rule_pairs`, `rule_post_filters` | +15 |
| `code-daily-scan/tests/test_post_filters.py` (new) | Unit tests for 3 new post-filters | +180 |
| `code-daily-scan/tests/test_ios_plugin.py` | Tests for new iOS plugin attributes | +40 |

Total: ~+350 lines.

## Expected Impact After Re-Scan

| Metric | Before | After (expected) | Delta |
|--------|--------|------------------|-------|
| iOS L2 findings | 6 | ~3 | -3 |
| iOS C1 findings | 6 | ~1 | -5 |
| iOS A6 findings | 19 | ~9 | -10 |
| Android L3 findings | 69 | ~19 | -50 |
| Android C9 findings | 2 | ~1 | -1 |
| **Combined FP reduction** | — | — | **~69** |
| **Combined precision** | ~54% | ~75% | **+21pp** |
| Test count | 132 | 143 (+11) | +11 |
