# Proposal: Reduce rule-pattern false positives in iOS and Android scanners

## Why

A spot-check of the latest EWallet scans (165 Android + 32 iOS findings) shows that **~50% of all findings are rule-pattern false positives** — they match real code that is benign by the rule's own documentation. The high FP rate dilutes the signal for code review, wastes triage time, and risks losing team trust in the scan output.

The previous OpenSpec change `code-scan-android-rule-refinements` addressed two large FP issues (S2 XML namespaces, "Others" feature bucket) but left five narrower patterns untouched. Each of these has 5–69 FPs that are easy to suppress with the existing post-filter infrastructure (`composite_rule_min_matches`, `cleanup_rule_pairs`, and per-plugin `post_filters`).

## What Changes

### 1. Suppress `L3` Android FPs in `companion object { const val ... }` blocks

The `L3` rule (Static or singleton object retains `Context`/`View`/`Fragment`) currently matches **any** `companion object {` line, including ones that only contain compile-time `const val` declarations. The documented detection requires "companion object **with** `lateinit var instance`" or "singleton fields of type `Context`/`Activity`/`Fragment`/`View`" — but the post-filter only suppresses the case where the file path contains `adapter`.

Add a new post-filter `suppress_l3_const_companion` that, given an L3 finding, suppresses it when:
- The matched snippet is `companion object {` and the file content within the next ~30 lines has no `lateinit var` or no fields of type `Context`/`Activity`/`Fragment`/`View`.

Expected impact: removes ~50 of the 69 Android L3 findings (those that are constants-only).

### 2. Suppress `C1` iOS FPs on single `TabView(selection:)` matches

The `C1` rule on iOS (`Unsafe SwiftUI/UIKit page selection without bounds check`) currently produces 6 P0 findings on files with a single `TabView(selection:)` — the same Android plugin config (`composite_rule_min_matches = {"C1": 2}`) is not applied to the iOS plugin.

Apply the existing Android `composite_rule_min_matches` config to the iOS plugin. This brings iOS in line with Android and requires a file to have ≥2 C1 matches (multiple `TabView` or combined with `scrollToItem`/`selectItem`) before emitting a finding.

Expected impact: removes ~5 of the 6 iOS C1 findings.

### 3. Suppress `L2` iOS FPs on `Timer.scheduledTimer` with `[weak self]` and `deinit` cleanup

The `L2` rule (Timer without deinit cleanup) currently matches all `Timer.scheduledTimer(withTimeInterval:)` calls, including ones that:
- Use `[weak self]` in the closure
- Have a `deinit { timer?.invalidate(); timer = nil }` cleanup

Add a new `cleanup_rule_pairs` entry to the iOS plugin:
```python
"L2": (r"Timer\\.scheduledTimer\\s*\\(\\s*withTimeInterval:", r"timer\\??\\.invalidate\\s*\\(")
```

This follows the existing `L4`/`L5` Android pattern. A finding is suppressed when the file contains both the trigger pattern (`Timer.scheduledTimer(withTimeInterval:`) AND the cleanup pattern (`timer?.invalidate(`).

Expected impact: removes 3 of the 3 sampled L2 iOS findings (all are weak-self + deinit cleaned up).

### 4. Suppress `A6` iOS FPs on `print`/`debugPrint` in `deinit` / `init` lifecycle logging

The `A6` rule (Debug print statements leak into production) currently matches every `print(...)` and `debugPrint(...)`. The iOS team uses `print("[VMName] deinit")` and `print("[VMName] init")` as an intentional VM-lifecycle debugging pattern.

Add a new post-filter `suppress_ios_a6_lifecycle_prints` that suppresses A6 findings where the snippet matches `print\(\[.*\]\s*(deinit|init)\s*\)` or `debugPrint\(\[.*\]\s*(deinit|init)\s*\)`.

This will leave real production-log noise (e.g. `print("❌ Provisioning start failed: \(error)")`) as a finding.

Expected impact: removes ~10 of the 19 iOS A6 findings (the lifecycle deinit/init pattern).

### 5. Suppress `C9` Android FPs on `!!` guarded by `if (x != null)` in same scope

The `C9` rule (Non-null DTO fields and `!!` can crash) currently matches every `!!` operator, including ones immediately preceded by a null check (`if (x != null) { x!!.field }`).

Add a new post-filter `suppress_c9_guarded_notnull` that, given a C9 finding, suppresses it when the matched line is preceded within 3 lines by an `if (... != null)` or `if (... == null) return` block.

Expected impact: removes ~1 of the 2 sampled C9 findings (the `pendingTransactionLimit!!` case).

### 6. Wire iOS plugin to use the new post-filters

The iOS plugin currently has empty `composite_rule_min_matches`, `cleanup_rule_pairs`, and no `post_filters` module. After this change, the iOS plugin mirrors the Android plugin's structure:
- `composite_rule_min_matches = {"C1": 2, "C5": 2, "C6": 2}` (from the Android precedent)
- `cleanup_rule_pairs` for L2
- New `plugins/ios/post_filters.py` for A6 lifecycle-print suppression

## Capabilities

### New Capabilities
- `rule-pattern-fp-suppression`: Per-plugin post-filter set that drops rule matches that are false positives by the rule's own documentation. Builds on the existing `composite_rule_min_matches`, `cleanup_rule_pairs`, and `post_filters` infrastructure.

### Modified Capabilities
None. The behavior of the rules themselves is unchanged; only their FP filtering is tightened. No existing OpenSpec specs are modified.

## Impact

| Area | Files / systems affected |
|------|--------------------------|
| `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py` | Add `suppress_l3_const_companion`, `suppress_c9_guarded_notnull` |
| `code-daily-scan/src/code_daily_scan/plugins/ios/post_filters.py` (new) | New module with `suppress_ios_a6_lifecycle_prints` |
| `code-daily-scan/src/code_daily_scan/plugins/ios/plugin.py` | Add `composite_rule_min_matches`, `cleanup_rule_pairs`, `rule_post_filters` |
| `code-daily-scan/tests/test_ios_plugin.py` | Tests for new iOS post-filter wiring |
| `code-daily-scan/tests/test_post_filters.py` (new) | Tests for each new post-filter |
| `openspec/changes/rule-pattern-fp-reduction/specs/rule-pattern-fp-suppression/spec.md` | New spec for the capability |

| Metric (expected after re-scan of EWallet branches) | Before | After | Delta |
|---------------------------------------------------|--------|-------|-------|
| Android L3 findings | 69 | ~19 | -50 (-72%) |
| iOS C1 findings | 6 | ~1 | -5 (-83%) |
| iOS L2 findings | 6 | ~3 | -3 (-50%) |
| iOS A6 findings | 19 | ~9 | -10 (-53%) |
| Android C9 findings | 2 | ~1 | -1 (-50%) |
| **Combined FP reduction** | — | — | **~69 FPs removed** |
| Android total findings | 165 | ~115 | -50 |
| iOS total findings | 32 | ~13 | -19 |
| **Combined precision (TP / Total)** | ~54% | ~75% | **+21pp** |

## Non-Goals

- **Do not** modify the rule patterns themselves in the Android/iOS rule markdown files. The patterns are correct as designed; the FPs come from missing context-aware post-filters.
- **Do not** introduce new dependency on a comment-stripping library. The post-filters use simple text-based heuristics within a bounded line window.
- **Do not** change rule priority (P0/P1/P2/P3). Re-prioritization is a separate change.

## Verification

1. Re-run the iOS scan (`poems-mobile3-ios` / `HuuThanh/Task/EW-Update-PUIComponent`) and confirm:
   - L2 count drops from 6 to ≤3
   - C1 count drops from 6 to ≤1
   - A6 count drops from 19 to ≤9
2. Re-run the Android scan (`poems-mobile3-android` / `modules/ewallet/develop_newdesignsystem`) and confirm:
   - L3 count drops from 69 to ≤19
   - C9 count drops from 2 to ≤1
3. Spot-check 5 known-TP findings (e.g. M2 `EWProgressLoadingIndicator`, C7 `EWalletContactSupportScreen`, A3 `EWUpdateRFIScreenViewModel`) to confirm they are preserved.
4. Run the full test suite — expect `+N` tests in `test_post_filters.py` and `test_ios_plugin.py`.
