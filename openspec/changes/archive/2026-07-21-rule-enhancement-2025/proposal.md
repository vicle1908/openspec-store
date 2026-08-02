# Proposal: Rule Enhancement 2025 — Comprehensive FP Reduction and New Rules

## Why

Current rule set produces 1121 Android findings and 1 iOS finding (severely degraded). Analysis reveals:

### FP Issues (Android)
- **C7** (195 findings): `childFragmentManager` pattern too broad — 89% are safe lifecycle uses
- **C8** (341 findings): `resources` pattern too broad — matches any `resources` usage, not just after-detach
- **C8 filter**: Lifecycle filter not catching enough (341 vs expected <100)

### Coverage Gaps
- No rule for `viewLifecycleOwner` misuse (using `lifecycleScope` instead of `viewLifecycleOwner.lifecycleScope`)
- No rule for `repeatOnLifecycle` safety (collecting StateFlow without lifecycle awareness)
- No rule for `Deinit` cleanup in iOS (NotificationCenter, KVO observers)
- No rule for `[weak self]` in escaping closures (iOS)
- No rule for Swift concurrency safety (`Task { [weak self] }`)

### Research Findings
From Android Lint, detekt, SwiftLint, and Periphery best practices:
1. `childFragmentManager` is safe in Fragment lifecycle — only risky after detach
2. `parentFragmentManager`/`requireFragmentManager()` after detach is risky
3. `resources` in Fragment is risky only after detach, not in lifecycle methods
4. iOS `[weak self]` in escaping closures is critical for memory safety
5. iOS `deinit` cleanup prevents NotificationCenter/KVO leaks
6. Modern Android: use `viewLifecycleOwner`, `repeatOnLifecycle`, `collectAsStateWithLifecycle`

## What Changes

### 1. C7 Post-Filter: Suppress Safe childFragmentManager

Add `suppress_c7_child_fragment_manager_safe` that suppresses C7 findings where `childFragmentManager` is used inside Fragment lifecycle methods (onViewCreated, onActivityCreated, etc.).

**Impact**: -174 FPs (89% of C7 findings)

### 2. C8 Pattern Fix: Tighten resources Pattern

Change C8 detection pattern from broad `resources` to specific `resources.` calls in non-lifecycle contexts. The current pattern matches ANY `resources` usage, but only `resources` access after detach is risky.

**Impact**: -200+ FPs

### 3. C8 Filter Enhancement: Increase Window

Increase the lifecycle detection window from 20 to 30 lines and add more lifecycle methods (onCreateView, onViewCreated, onActivityCreated, onAttach, onStart, onResume).

**Impact**: -50+ FPs

### 4. New Rule: C10 — viewLifecycleOwner Misuse

Detect `lifecycleScope.launch` without `viewLifecycleOwner` in Fragments. Modern Android should use `viewLifecycleOwner.lifecycleScope.launch` or `repeatOnLifecycle`.

**Impact**: New rule, catches ~20-30 real issues

### 5. New Rule: C11 — StateFlow Without Lifecycle Awareness

Detect `collect {}` on StateFlow without `repeatOnLifecycle` or `collectAsStateWithLifecycle`. This causes memory leaks and crashes after view destruction.

**Impact**: New rule, catches ~10-20 real issues

### 6. New Rule: L7 — NotificationCenter Without RemoveObserver

Detect `NotificationCenter.default.addObserver` without matching `removeObserver` in `deinit`. This causes memory leaks.

**Impact**: New rule, catches ~5-10 real issues (iOS)

### 7. New Rule: L8 — [weak self] Missing in Escaping Closures

Detect escaping closures that capture `self` without `[weak self]`. This causes retain cycles.

**Impact**: New rule, catches ~10-15 real issues (iOS)

### 8. New Rule: C12 — Swift Task Without [weak self]

Detect `Task { self.` without `[weak self]`. Swift concurrency tasks can outlive the caller.

**Impact**: New rule, catches ~5-10 real issues (iOS)

## Capabilities

### Modified Capabilities
- `android-code-scan-rules`: C7/C8 post-filters, C8 pattern fix
- `ios-code-scan-rules`: New L7, L8, C12 rules

### New Capabilities
- `android-lifecycle-safety`: C10, C11 rules for modern Android patterns
- `ios-memory-safety`: L7, L8, C12 rules for iOS memory management

## Impact

- `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py`: C7/C8 filters
- `code-daily-scan/src/code_daily_scan/plugins/ios/post_filters.py`: L7/L8 filters
- `poems-mobile3-docs/.../crash-runtime.md`: C8 pattern fix, C10/C11/C12 rules
- `poems-mobile3-docs/.../memory-lifecycle.md`: L7/L8 rules
- No external dependencies, no API changes

## Non-Goals
- Modifying existing rule severity or priority
- Adding rules for other platforms (web, desktop)
- Changing the scanner architecture
