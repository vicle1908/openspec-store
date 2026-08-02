# Design — Rule pattern FP reduction

## Context

The `code-daily-scan` system uses ripgrep-based scanners (`scanners/grep_scanner.py`) with rules loaded from per-repo Markdown files (`poems-mobile3-android/docs/rules/categories/*.md`, `poems-mobile3-ios/docs/technical-debt-scan/categories/*.md`). The scanner has three FP-suppression mechanisms:

1. `RulePostFilterConfig.composite_rule_min_matches` (rule_id → min matches per file) — applies during ripgrep result processing in `RipgrepRunner.search()`.
2. `RulePostFilterConfig.cleanup_rule_pairs` (rule_id → (trigger_pattern, cleanup_pattern)) — suppresses a finding when both patterns appear in the same file.
3. Per-plugin `rule_post_filters` dict (rule_id → callable[[list[Finding]], list[Finding]]) — runs AFTER ripgrep, gives full file access.

The Android plugin (`plugins/android/plugin.py`) already wires all three:
- `composite_rule_min_matches = {"C1": 2, "C5": 2, "C6": 2}`
- `cleanup_rule_pairs = {"L4": ..., "L5": ...}`
- `rule_post_filters = ANDROID_RULE_POST_FILTERS` (L2, L3, L6, P5)

The iOS plugin (`plugins/ios/plugin.py`) wires **none** of them — it has empty `composite_rule_min_matches = {}` and `cleanup_rule_pairs = {}`, and no `post_filters` module.

A spot-check of the latest EWallet scans (32 iOS + 165 Android) showed that 5 specific rules produce ~70 FPs that could be removed with the existing infrastructure.

## Goals / Non-Goals

**Goals:**

- Reduce FP rate from ~50% to ~25% on the EWallet test branches, bringing precision from ~54% to ~75%.
- Use only the existing three suppression mechanisms — no new infrastructure.
- Mirror the Android plugin structure to the iOS plugin (so the two scanners are symmetric in their FP-handling).
- Keep all changes within `code-daily-scan` — no edits to the iOS/Android rule markdown files in the source repos.

**Non-Goals:**

- Modify the rule regex patterns themselves. The patterns are correct; the issue is missing context.
- Introduce a comment-stripping library or AST-based analyzer. The post-filters use simple text heuristics within bounded line windows.
- Re-prioritize findings (P0 → P1, etc.). That is a separate change.
- Update the rule markdown docs in the iOS/Android repos. The rule docs are the **source of truth** for the patterns; the post-filters are scanner-level overrides.

## Decisions

### Decision 1: Use `composite_rule_min_matches` for C1 iOS (not a custom post-filter)

**Rationale:** Android already uses this exact mechanism for C1 (require ≥2 matches in a file). Mirroring it to iOS gives parity, requires zero new code, and follows the same semantics.

**Alternative considered:** A custom `suppress_ios_c1_tagged_tabview` post-filter that checks for `.tag(...)`/`.tagIndex(...)` usage. Rejected because: (a) the modifier names are team-specific, (b) composite filter is simpler and gets the same result for the 6/6 EWallet samples, (c) the post-filter would need to read the entire file anyway, so reading is not a concern.

### Decision 2: Use `cleanup_rule_pairs` for L2 iOS (not a custom post-filter)

**Rationale:** Android uses `cleanup_rule_pairs` for L4 (postDelayed ↔ removeCallbacks) and L5 (registerReceiver ↔ unregisterReceiver). The L2 iOS pattern fits the same shape: trigger is `Timer.scheduledTimer(...)`, cleanup is `timer?.invalidate()`.

**Alternative considered:** A custom post-filter that reads the file and looks for both `deinit { ... timer?.invalidate() }` and `[weak self]` in the closure. Rejected because the cleanup_rule_pairs infrastructure is simpler and covers the 3/3 EWallet samples correctly.

### Decision 3: Use a custom post-filter (not composite/cleanup) for L3 Android const-only companion

**Rationale:** The L3 false positive is "companion object exists but contains only `const val` and no `lateinit var` of type Context/View/Fragment". This is a file-content shape that neither `composite_rule_min_matches` (which is rule-level, not content-aware) nor `cleanup_rule_pairs` (which requires two independent patterns) can express.

The filter reads the file content, locates the matched `companion object {` line, and scans the next ~30 lines for a `lateinit var` declaration of type `Context`/`Activity`/`Fragment`/`View`. If none found, suppress the finding.

**Alternative considered:** Changing the rule pattern from `companion object {` to `companion object {[^}]*lateinit var`. Rejected because (a) the rule markdown is the source of truth and edits there affect both scanners, (b) the regex gets fragile with nested braces.

### Decision 4: Use a custom post-filter for A6 iOS lifecycle-prints

**Rationale:** A6 FPs are `print("[VMName] deinit")` / `debugPrint("[VMName] init")` — a deliberate team pattern. The suppression is a simple snippet regex match: `print\(\[.*\]\s*(deinit|init)\s*\)` or `debugPrint` variant.

**Alternative considered:** Re-prioritize A6 from P3 to a lower tier. Rejected because some A6 findings ARE real production noise (e.g. `print("❌ Provisioning start failed: \(error)")`) — those should stay as findings.

### Decision 5: Use a custom post-filter for C9 Android null-guarded `!!`

**Rationale:** C9 matches every `!!` operator. The FP is `!!` preceded by an `if (x != null)` check in the same scope. The filter checks the 3 lines preceding the match for `if (.... != null)` and suppresses if found.

**Alternative considered:** Exclude C9 from files where the matched line is inside an `if (x != null)` block. A line-by-line state machine is more complex; the 3-line window is sufficient for the 2/2 EWallet samples.

### Decision 6: iOS plugin gets a new `post_filters.py` module

**Rationale:** Mirror the Android plugin's structure. The new module exports `IOS_RULE_POST_FILTERS: dict[str, RulePostFilter]` with the A6 lifecycle-print suppressor. The iOS plugin's `plugin.py` adds a `rule_post_filters` attribute pointing at it.

This makes the two plugin structures symmetric and means future iOS-specific suppressors can be added without touching the scanner.

## File-Level Changes

| File | Change | Lines |
|------|--------|-------|
| `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py` | Add `suppress_l3_const_companion` and `suppress_c9_guarded_notnull`; register in `ANDROID_RULE_POST_FILTERS` | +60 |
| `code-daily-scan/src/code_daily_scan/plugins/ios/post_filters.py` (new) | Define `suppress_ios_a6_lifecycle_prints`, export `IOS_RULE_POST_FILTERS` | +35 |
| `code-daily-scan/src/code_daily_scan/plugins/ios/plugin.py` | Add `composite_rule_min_matches`, `cleanup_rule_pairs`, `rule_post_filters` attributes | +10 |
| `code-daily-scan/tests/test_post_filters.py` (new) | Unit tests for each new post-filter (real file fixtures) | +150 |
| `code-daily-scan/tests/test_ios_plugin.py` | Tests for the new iOS plugin attributes | +30 |

Total: ~+285 lines.

## Risks / Trade-offs

- **Risk:** Post-filter reads the file content, which is one I/O call per matched file. For very large files (rare in the EWallet scans), this could add latency. **Mitigation:** Cache `Path.read_text` results within a single scan run; the existing Android post-filters already do this.

- **Risk:** The 3-line window for C9 may miss some valid null-guards if they span more than 3 lines (e.g., `if (x == null) throw; if (y == null) return; // many lines; y!!.field`). **Mitigation:** Acceptable FP reduction; a 5-line window is a future tuning knob. The 2/2 EWallet samples use short guards.

- **Risk:** `[weak self]` is not in the L2 `cleanup_rule_pairs` — we only check for `timer?.invalidate(`. A file with `[weak self]` but no `invalidate` is still suppressed (because of `invalidate`), and a file with `invalidate` but no `[weak self]` is also suppressed. This is the desired behavior — both conditions are required for safe usage. **Mitigation:** Documented in the proposal as "weak-self + deinit cleaned up" — both conditions are present in the 3/3 EWallet samples.

- **Risk:** The iOS plugin change might affect other branches being scanned. **Mitigation:** All changes are FP-suppressions, meaning they only **reduce** finding counts, never add new ones. The risk is the opposite — losing a real finding. The 32 finding sample is small; the EWallet branch is the only validation set we have. We will validate against 2 branches and manually spot-check TPs.

- **Risk:** Code-style drift between Android and iOS plugin post-filters. **Mitigation:** Use the same type alias (`RulePostFilter = Callable[[list[Finding]], list[Finding]]`) and same module structure.

## Migration Plan

1. Land the `code-daily-scan` changes (post-filters + iOS plugin wiring + tests) on a feature branch.
2. Re-run the iOS EWallet scan: confirm counts drop as predicted.
3. Re-run the Android EWallet scan: confirm counts drop as predicted.
4. Spot-check 5 known-TP findings: confirm they are preserved.
5. Spot-check 5 known-FP findings: confirm they are now suppressed.
6. Merge to main; the next scheduled scan will pick up the new rules automatically.

**Rollback strategy:** Revert the merge commit. The only persistence point is the post-filter dict in the plugin; the rules markdown files are untouched, so reverting the merge fully restores the previous behavior.

## Open Questions

- Should the L3 Android filter also drop findings in `*ViewModel.kt` files where the `companion object` is used for `const val`? The current rule already has a `suppress_adapter_companion` for adapter files; ViewModel files have a different lifecycle. **Decision:** Out of scope for this change; can be a follow-up if the L3 count remains high after this change.

- Should A6 findings in `os.Logger` / `Logger.log` calls be excluded as proper logging? **Decision:** Out of scope — the team uses `print`/`debugPrint` for lifecycle; they would use `os.Logger` if they cared. No EWallet file uses `os.Logger`.

- Should the iOS plugin use `camelCase` for the new post-filter dict (e.g., `ios_rule_post_filters`) to match the Android naming (`ANDROID_RULE_POST_FILTERS`)? **Decision:** Use `IOS_RULE_POST_FILTERS` for symmetry.
