# rule-pattern-fp-suppression Specification

## Purpose
TBD - created by archiving change rule-pattern-fp-reduction. Update Purpose after archive.
## Requirements
### Requirement: L3 Android const-only companion object findings are suppressed

The Android `L3` rule (`Static or singleton object retains Context/View/Fragment`) SHALL suppress a finding when the matched `companion object {` line in the source file is not followed by a `lateinit var` declaration of type `Context`, `Activity`, `Fragment`, or `View` within 30 lines of the match.

#### Scenario: Companion object with only const val is suppressed
- **WHEN** a Kotlin file has `companion object { const val FOO = "bar" }` and is matched by the L3 pattern
- **THEN** the L3 finding is dropped before being added to the result list

#### Scenario: Companion object with lateinit var Activity is preserved
- **WHEN** a Kotlin file has `companion object { lateinit var activity: Activity }` and is matched by the L3 pattern
- **THEN** the L3 finding is preserved (because `lateinit var` of type `Activity` is a real leak)

#### Scenario: Companion object with Context field is preserved
- **WHEN** a Kotlin file has `companion object { var ctx: Context? = null }` and is matched by the L3 pattern
- **THEN** the L3 finding is preserved

#### Scenario: Companion object with non-context lateinit var is suppressed
- **WHEN** a Kotlin file has `companion object { lateinit var config: AppConfig }` and is matched by the L3 pattern
- **THEN** the L3 finding is dropped (because `AppConfig` is not a `Context`/`Activity`/`Fragment`/`View`)

### Requirement: C1 iOS requires multiple matches per file

The iOS `C1` rule (`Unsafe SwiftUI/UIKit page selection without bounds check`) SHALL require a file to have at least 2 pattern matches before emitting a finding.

#### Scenario: Single TabView(selection:) match is suppressed
- **WHEN** a Swift file has exactly one `TabView(selection: $x) { ... }` block and is matched by the C1 pattern
- **THEN** the C1 finding is dropped (because the file has only 1 match)

#### Scenario: Two TabView(selection:) matches emit one finding
- **WHEN** a Swift file has two `TabView(selection: $x) { ... }` blocks and is matched by the C1 pattern
- **THEN** exactly one C1 finding is emitted (the second is suppressed as a duplicate within the same composite key)

#### Scenario: scrollToItem + TabView combination emits one finding
- **WHEN** a Swift file has one `TabView(selection:)` and one `scrollToItem(...)` call, both matching the C1 pattern
- **THEN** one C1 finding is emitted

### Requirement: L2 iOS Timer with deinit cleanup is suppressed

The iOS `L2` rule (`Timer without deinit cleanup`) SHALL suppress a finding when the source file contains both the trigger pattern `Timer.scheduledTimer(withTimeInterval:` AND the cleanup pattern `timer?.invalidate(`.

#### Scenario: Timer with [weak self] and deinit cleanup is suppressed
- **WHEN** a Swift file has `Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { [weak self] t in ... }` and a `deinit { timer?.invalidate() }` block
- **THEN** the L2 finding is dropped

#### Scenario: Timer without deinit cleanup is preserved
- **WHEN** a Swift file has `Timer.scheduledTimer(timeInterval: 0.08, target: self, selector: #selector(update))` and no matching `invalidate` call
- **THEN** the L2 finding is preserved

### Requirement: A6 iOS lifecycle deinit/init print statements are suppressed

The iOS `A6` rule (`Debug print statements leak into production`) SHALL suppress a finding when the matched snippet matches the pattern `print\(\[.*\]\s*(deinit|init)\s*\)` or `debugPrint\([^"]*\[.*\]\s*(deinit|init)` (i.e., a ViewModel lifecycle log line).

#### Scenario: deinit print is suppressed
- **WHEN** a Swift file has `print("[EWReviewBaseViewModel] deinit")` and is matched by the A6 pattern
- **THEN** the A6 finding is dropped

#### Scenario: init print is suppressed
- **WHEN** a Swift file has `debugPrint("[EWReviewConvertVM] init")` and is matched by the A6 pattern
- **THEN** the A6 finding is dropped

#### Scenario: production error print is preserved
- **WHEN** a Swift file has `print("❌ Provisioning start failed: \\(error)")` and is matched by the A6 pattern
- **THEN** the A6 finding is preserved (because the snippet is not a lifecycle log)

#### Scenario: arbitrary debugPrint is preserved
- **WHEN** a Swift file has `debugPrint("Trigger setFieldID [\\(field)] with fileID \\(fileId)")` and is matched by the A6 pattern
- **THEN** the A6 finding is preserved

### Requirement: C9 Android null-guarded `!!` is suppressed

The Android `C9` rule (`Non-null DTO fields and !! can crash when backend sends unexpected null values`) SHALL suppress a finding when the matched `!!` line is preceded by a `if (... != null)` check within 3 lines of the match.

#### Scenario: !! guarded by null check is suppressed
- **WHEN** a Kotlin file has:
  ```kotlin
  if (pendingTransactionLimit != null) {
      pendingTransactionLimit!!.amount.toString()
  }
  ```
- **THEN** the C9 finding for the `!!` line is dropped

#### Scenario: !! in async lambda with surrounding guard is suppressed
- **WHEN** a Kotlin file has a `!!` operator inside a block that is preceded by an `if (x != null) {` within 3 lines
- **THEN** the C9 finding is dropped

#### Scenario: !! in lifecycle method without guard is preserved
- **WHEN** a Kotlin file has `currentCurrencyConvert!!` on a line with no preceding `if` guard
- **THEN** the C9 finding is preserved

### Requirement: iOS plugin mirrors Android plugin post-filter structure

The `IOSPlugin` SHALL expose the same post-filter attributes as the `AndroidPlugin`:
- `composite_rule_min_matches: dict[str, int]` containing at least `{"C1": 2, "C5": 2, "C6": 2}`
- `cleanup_rule_pairs: dict[str, tuple[str, str]]` containing at least `{"L2": (r"Timer\\.scheduledTimer\\s*\\(\\s*withTimeInterval:", r"timer\\??\\.invalidate\\s*\\(")}`
- `rule_post_filters: dict[str, RulePostFilter]` containing at least the A6 lifecycle-print suppressor

#### Scenario: iOS plugin composite_rule_min_matches contains C1, C5, C6
- **WHEN** `ios_plugin.composite_rule_min_matches` is accessed
- **THEN** the value contains `{"C1": 2, "C5": 2, "C6": 2}`

#### Scenario: iOS plugin cleanup_rule_pairs contains L2
- **WHEN** `ios_plugin.cleanup_rule_pairs["L2"]` is accessed
- **THEN** the value is a tuple of (trigger_pattern, cleanup_pattern)

#### Scenario: iOS plugin rule_post_filters contains A6
- **WHEN** `ios_plugin.rule_post_filters["A6"]` is accessed
- **THEN** the value is a callable that accepts a list of Finding and returns a list of Finding

### Requirement: Post-filters are testable in isolation

Each new post-filter function SHALL be testable by passing a synthetic list of `Finding` objects to it and asserting the returned list.

#### Scenario: suppress_l3_const_companion drops a const-only finding
- **WHEN** a list of one L3 Finding is passed to `suppress_l3_const_companion`, where the file's companion object contains only `const val`
- **THEN** the returned list is empty

#### Scenario: suppress_c9_guarded_notnull drops a guarded !! finding
- **WHEN** a list of one C9 Finding is passed to `suppress_c9_guarded_notnull`, where the file has a `if (x != null) {` block within 3 lines preceding the match
- **THEN** the returned list is empty

#### Scenario: suppress_ios_a6_lifecycle_prints drops a deinit print finding
- **WHEN** a list of one A6 Finding is passed to `suppress_ios_a6_lifecycle_prints`, where the snippet is `print("[FooVM] deinit")`
- **THEN** the returned list is empty

