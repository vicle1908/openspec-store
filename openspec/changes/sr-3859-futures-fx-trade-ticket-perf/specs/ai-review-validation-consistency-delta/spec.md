# Delta Spec: ai-review-validation-consistency — Add Trade/PMP hot-path invariant check

## Change Rationale

SR-3859 is the fourth recurrence of the `MutableLiveData`/`@Published` self-reinforcing observer loop bug class in the POEMS Mobile 3 codebase. Code review alone has not prevented recurrence (SR-3323, SR-3223, SR-3319, SR-3859). This delta extends the `ai-review-validation-consistency` capability to surface the SR-3859 invariants automatically when a diff touches the Trade/PMP hot-path files, making the regression visible at PR time rather than at QA round test.

## MODIFIED Requirements

### Requirement: AI review validation consistency checks

The system MUST surface SR-3859 invariants when an ai-review diff touches any Trade/PMP hot-path file pattern. The detailed check is in the Scenario below.

The existing requirements are unchanged. The following check is **added**:

#### Scenario: Diff touching Trade/PMP hot-path files triggers SR-3859 invariant checklist

- **WHEN** the `ai-review` orchestrator evaluates a diff where one or more files match any of these patterns:
  - `**/TradeFutures*/**` (any file in TradeFutures module)
  - `**/TradeBuySellScreen/Futures/**` (iOS Futures buy/sell screen)
  - `**/TopPriceDetailCounter*` (Android counter detail header)
  - `**/PMP*ViewModel*` (Android PMP ViewModels)
  - `**/PMPEventListener*` (Android PMP event listener)
  - `**/PMPUtilViewModel*` (Android PMP util ViewModel)
  - `**/TBSFuturesViewModel*` (iOS Futures order ticket VM)
  - `**/TradeFuturesViewModel*` (iOS Futures position/order VM)
- **THEN** the review output SHALL prepend a section titled `SR-3859 Invariants — Trade/PMP Hot-Path`
- **AND** SHALL list each of the following checks that are relevant to the changed files:
  - `SHALL NOT: objectWillChange.send()` in any `TradeFuturesViewModel` or `TBSFuturesViewModel` file (iOS)
  - `SHALL NOT: MutableLiveData.value = X` inside `updateTopDetailWithPMP`, `updateUICounterInfo`, or any `setOnResponseListener` callback (Android)
  - `SHALL: deduplicate PMP subscriptions per counter per screen stack` (both platforms)
  - `SHALL: distinctUntilChanged on price stream before dispatching to UI` (both platforms)
  - `SHALL: coalesce to ≤ 1 main-thread mutation per frame (16 ms)` (both platforms)
  - `SHALL: format prices off main thread` (both platforms)
  - `SHALL: bounded retry with backoff on PMP reconnect` (Android)
  - `SHALL: pre-computed PMP field lookup map in PMPUtilViewModel` (Android)
- **AND** if the diff introduces any `objectWillChange.send()` or `MutableLiveData.value = X` in a hot-path file, the review output SHALL add a `REGRESSION WARNING` annotation with the text: `This change re-introduces the SR-3859 anti-pattern (MutableLiveData/objectWillChange self-fire loop). Reference: https://psplit.atlassian.net/browse/SR-3859`

#### Scenario: Diff does not match hot-path patterns

- **WHEN** a diff does not match any of the file patterns above
- **THEN** the `SR-3859 Invariants` section SHALL NOT be emitted
- **AND** no other behavior of `ai-review-validation-consistency` is affected
