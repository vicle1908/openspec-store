# rca-taxonomy-v2 Specification

## ADDED Requirements

### Requirement: RCA pattern matching uses explicit word sequences, not greedy dot-star
The `detect_rca()` function SHALL use regex patterns with explicit word boundaries and non-greedy quantifiers to prevent over-matching across long ticket text.

#### Scenario: Regression pattern "was working" does not match across unrelated sentences
- **WHEN** ticket content is `"The was working on the fix."`
- **THEN** the RCA pattern SHALL NOT match (the phrase "was working" in this context is a grammatical fragment, not a regression indicator)

#### Scenario: Regression pattern "was working before" matches correctly
- **WHEN** ticket content is `"Bug: feature was working before release 3.0"`
- **THEN** the RCA pattern SHALL match `"was working before"` with category "Feature Not Working / Missing"

#### Scenario: "broke after" pattern does not greedily span the ticket
- **WHEN** ticket content is `"broke after review. Test broke after merge. This broke after deployment"`
- **THEN** the RCA pattern SHALL match each distinct occurrence, not a single span from the first "broke" to the last "after"

### Requirement: RCA categories do not produce false cross-category misclassification
The RCA pattern taxonomy SHALL minimize false positives where symptoms of one category are incorrectly matched as another category.

#### Scenario: Cache-related performance issues resolve to Performance category
- **WHEN** ticket content is `"Cache causes slow loading of market data"`
- **THEN** the matched category SHALL be "Performance / Slow Loading" (priority 5), not "Wrong Data / Incorrect Value" (priority 2)
- **AND** the matched text SHALL be `"slow loading"`, not `"cache"`

#### Scenario: Frozen spinner without "no response" resolves to Silent Exit
- **WHEN** ticket content is `"Loading spinner never stops, app becomes unresponsive"`
- **THEN** the matched category SHALL be "Silent Exit / No Feedback" (priority 3)
- **AND** if both Silent Exit and Performance patterns match, the lower priority (3) wins

#### Scenario: "overlap" in layout context resolves to UI Layout
- **WHEN** ticket content is `"Elements overlap on smaller screens"`
- **THEN** the matched category SHALL be "UI Layout / Visual Defect" (priority 4)

### Requirement: RCA taxonomy covers data race and concurrency bug patterns
The RCA taxonomy SHALL include patterns that detect data race and concurrency failures, mapping to the Crash/ANR category due to their severity.

#### Scenario: Race condition explicitly stated
- **WHEN** ticket content contains `"race condition"`, `"concurrent modification"`, `"thread safety"`, `"deadlock"`, or `"data corruption due to race"`
- **THEN** the matched category SHALL be "Crash / ANR / Force Close" (priority 1)

#### Scenario: Race condition causing wrong data prioritizes Crash
- **WHEN** ticket content is `"Race condition caused wrong portfolio balance"`
- **THEN** the matched category SHALL be "Crash / ANR / Force Close" (priority 1)

### Requirement: RCA taxonomy covers offline-first and sync failure patterns
The RCA taxonomy SHALL include patterns for offline-first failures and data synchronization issues.

#### Scenario: Offline mode failure detected
- **WHEN** ticket content contains `"offline"`, `"sync failed"`, `"data not syncing"`, `"local cache out of date"`, `"conflict resolution"`, or `"merge conflict on device"`
- **THEN** the matched category SHALL be "Network / API Connectivity" (priority 7)

#### Scenario: Background sync silently failing
- **WHEN** ticket content contains `"background sync"`, `"periodic sync"`, or `"auto-sync not working"`
- **THEN** the matched category SHALL be "Silent Exit / No Feedback" (priority 3) or "Network / API Connectivity" (priority 7)

### Requirement: RCA taxonomy covers notification delivery failure patterns
The RCA taxonomy SHALL include patterns for push notification and in-app notification failures.

#### Scenario: Push notification not received
- **WHEN** ticket content contains `"push notification not received"`, `"notification missing"`, `"silent push"`, `"notification delayed"`, or `"silent notification"`
- **THEN** the matched category SHALL be "Feature Not Working / Missing" (priority 8)

### Requirement: Code-hint confidence boost and prevention-action augmentation
The presence of any `code_hints` SHALL add a +0.1 confidence boost (capped at 0.95). Each hint token category SHALL add a corresponding prevention action:

- **`test` / `coverage` / `assert`** → "Add or strengthen automated regression tests around the affected code path" (applies to all RCA categories)
- **`guard` / `null` / `exception` / `timeout` / `retry`** → "Add defensive guards and explicit error handling in the affected branch code path"
- **`log` / `metric` / `trace` / `monitor`** → "Add monitoring or structured logging around the affected execution path"

#### Scenario: Null-pointer hint boosts crash RCA and adds guard action
- **WHEN** `detect_rca()` detects "Crash / ANR" category and `code_hints` contains `"NullPointerException"`, `"NPE"`, `"ArrayIndexOutOfBounds"`, or `"IndexError"`
- **THEN** confidence SHALL be boosted by 0.1
- **AND** the defensive-guard prevention action SHALL be added

#### Scenario: Guard/exception/timeout/retry hint boosts any RCA category and adds guard action
- **WHEN** `code_hints` contains `"guard"`, `"exception"`, `"timeout"`, `"retry"`
- **THEN** confidence SHALL be boosted by 0.1
- **AND** the defensive-guard prevention action SHALL be added

#### Scenario: Logging/metrics hint boosts any RCA category and adds monitoring action
- **WHEN** `code_hints` contains `"logging"`, `"metrics"`, `"trace"`, `"monitor"`
- **THEN** confidence SHALL be boosted by 0.1
- **AND** the monitoring/logging prevention action SHALL be added

#### Scenario: Test/coverage hint boosts all categories uniformly and adds regression-test action
- **WHEN** `code_hints` contains `"test"`, `"coverage"`, or `"assert"`
- **THEN** confidence SHALL be boosted by 0.1
- **AND** the regression-test prevention action SHALL be added regardless of RCA category

### Requirement: RCA priority-based confidence is weighted by category severity
The `detect_rca()` function SHALL use RCA priority (1-9) to influence the confidence score appropriately.

#### Scenario: Priority 1-4 categories have base confidence 0.7
- **WHEN** a ticket matches the "Crash / ANR / Force Close" category (priority 1)
- **THEN** base confidence SHALL be 0.7

#### Scenario: Priority 5-7 categories have base confidence 0.5
- **WHEN** a ticket matches the "Network / API Connectivity" category (priority 7)
- **THEN** base confidence SHALL be 0.5

#### Scenario: Priority 8-9 categories have base confidence 0.3
- **WHEN** a ticket matches the "General UI/UX Polish" category (priority 9)
- **THEN** base confidence SHALL be 0.3

### Requirement: Prevention actions are deduplicated without reordering
The prevention action list SHALL have duplicates removed while preserving insertion order.

#### Scenario: Duplicate prevention actions are collapsed
- **WHEN** prevention actions include `["Add crash reporting SDK", "Add crash reporting SDK", "Implement try-catch guards"]`
- **THEN** the returned list SHALL be `["Add crash reporting SDK", "Implement try-catch guards"]`

#### Scenario: Duplicates from code-hint augmentation are deduplicated
- **WHEN** a prevention action added by code-hint augmentation duplicates one already in the category default list
- **THEN** the deduplicated list SHALL contain each unique action exactly once

### Requirement: RCA confidence is capped at 0.95
The confidence score SHALL NOT exceed 0.95 even when multiple boosts are applied.

#### Scenario: Crash ticket with 3 categories matching and code hints caps at 0.95
- **WHEN** a ticket has base confidence 0.7, `match_count > 2` (+0.15), and `code_hints` (+0.1)
- **THEN** the returned confidence SHALL be `0.95`, not `0.95 + 0.1 = 1.05`

### Requirement: RCA matched_text captures the specific pattern match, not the full content
The `RootCauseSignal.matched_text` field SHALL contain only the substring matched by the regex pattern that triggered the chosen category.

#### Scenario: Long ticket, short match
- **WHEN** ticket content is `"The app crashed on startup with NullPointerException in the handler"`
- **THEN** `matched_text` SHALL be the regex match for the chosen category (e.g., `"crashed"` for "Crash / ANR / Force Close" via the priority-1 crash pattern), not the full content
- **AND** `matched_text` SHALL be non-empty whenever a category is detected
