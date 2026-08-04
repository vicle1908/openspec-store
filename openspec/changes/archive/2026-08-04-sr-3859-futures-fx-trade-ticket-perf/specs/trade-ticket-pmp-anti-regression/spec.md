# Spec: Trade Ticket PMP Anti-Regression

## Purpose

Define the regression-test contract that prevents the Futures/FX order ticket / order detail performance bug class from being reintroduced. SR-3859 is the fourth occurrence of this bug class (SR-3323, SR-3223, SR-3319, SR-3859), so the contract must (a) capture the specific anti-patterns as CI-gated invariants, (b) ship reproducible test fixtures that future engineers can re-run, and (c) feed the AI review pipeline so that future diffs touching the same files are flagged at PR time.

---

## ADDED Requirements

### Requirement: No `objectWillChange.send()` on the iOS Trade hot path

The iOS Trade hot-path files SHALL NOT call `objectWillChange.send()` in any code path reachable from a PMP tick handler.

#### Scenario: Static check on iOS source

- **GIVEN** the iOS module is built for the v3.3.54 release
- **WHEN** the CI gate runs the static check `rg "objectWillChange\.send" Pmobile3/Modules/Trade/TradeFutures/ Pmobile3/Modules/Trade/TradeBuySellScreen/Futures/`
- **THEN** the check SHALL return zero matches
- **AND** the build SHALL fail if any match is found

#### Scenario: Runtime check during replay

- **GIVEN** `PmpCoalescingTests` replays the recorded 50-tick/sec burst for 5 seconds
- **WHEN** the test instrumented `objectWillChange.send` and `willSet` hooks
- **THEN** the total count of `objectWillChange.send` invocations across the Trade hot-path view models SHALL be 0
- **AND** the total count of `@Published.willSet` invocations SHALL be ≤ 30 in 5 seconds (≤ 6/sec)

### Requirement: No `MutableLiveData.value = X` self-mutation on the Android Trade hot path

The Android Trade hot-path files SHALL NOT write back to a `MutableLiveData` whose observers consume the same LiveData upstream source (no self-reinforcing observer loops).

#### Scenario: Static check on Android source

- **GIVEN** the Android module is built for the v3.3.54 release
- **WHEN** the CI gate runs the static check `rg "\.value\s*=\s*\w" app/src/main/java/com/tdt/pmobile3/ui/screens/watchlists/counterdetail/common/TopPriceDetailCounterFutureFX.kt app/src/main/java/com/tdt/pmobile3/ui/screens/trade/tradeticket/`
- **THEN** the check SHALL return zero matches inside PMP-driven `updateTopDetailWithPMP`, `updateUICounterInfo`, and any callback registered via `setOnResponseListener`
- **AND** the build SHALL fail if any match is found

#### Scenario: Runtime check during replay

- **GIVEN** `TradeTicketFutureFXPerformanceTest` replays the recorded 50-tick/sec burst via `FakePmpEventListener` for 5 seconds
- **WHEN** the test instruments the `MediatorLiveData.setValue` calls
- **THEN** the total count of PMP-driven `setValue` invocations on `mCounterInForDetailFutures` SHALL be ≤ 30 in 5 seconds (≤ 6/sec)
- **AND** the total count of `updateTopDetailWithPMP` invocations SHALL be ≤ 30 in 5 seconds

### Requirement: Recorded burst fixture format

A recorded PMP burst fixture SHALL be available at `tests/fixtures/pmp-burst-50hz-5s.jsonl` in both `poems-mobile3-ios` and `poems-mobile3-android` repositories, with one JSON object per line representing a single tick.

#### Scenario: Fixture schema

- **GIVEN** a line in `pmp-burst-50hz-5s.jsonl`
- **WHEN** the line is parsed as JSON
- **THEN** it SHALL match the schema: `{"ts_ms": <int>, "counter": <string>, "bid": <string>, "ask": <string>, "last_done": <string>, "volume": <string|null>}`
- **AND** the file SHALL contain exactly 250 lines (50 ticks/sec × 5 sec)

#### Scenario: Fixture reproducibility

- **GIVEN** the fixture file is committed to the repo
- **WHEN** the regression test reads the fixture and feeds it through the deduplicator
- **THEN** the test SHALL produce the same `dispatched_count`, `dropped_count`, and `coalesce_ratio` on every run
- **AND** the test SHALL fail if those numbers deviate by more than 5%

### Requirement: iOS regression test bundle

A new XCTest bundle `PmpCoalescingTests` SHALL exist in `poems-mobile3-ios` with the test cases enumerated below.

#### Scenario: `test_dedupAcrossListeners_dispatchesOncePerPriceChange`

- **GIVEN** two listeners attached to `PmpSubscriptionCoordinator` for the same counter
- **WHEN** the recorded burst is replayed
- **THEN** each listener SHALL observe exactly N dispatches where N equals the number of *distinct* (bid, ask, last_done) tuples in the burst
- **AND** SHALL NOT observe more than 6 dispatches per second

#### Scenario: `test_noObjectWillChangeSend_duringReplay`

- **GIVEN** the burst replay is running with `objectWillChange.send` instrumented
- **WHEN** the replay completes
- **THEN** the instrumented counter SHALL be 0

#### Scenario: `test_mapTradeInfo_throttledToOnePerFrame`

- **GIVEN** `TBSFuturesViewModel.mapTradeInfo` is instrumented
- **WHEN** the burst replay fires 4 ticks within 8 ms
- **THEN** `mapTradeInfo` SHALL execute at most once for that frame

### Requirement: Android regression test

A new test class `TradeTicketFutureFXPerformanceTest` SHALL exist in `poems-mobile3-android` with the test cases enumerated below.

#### Scenario: `test_liveData_observerFiresAtMostOncePerDistinctTick`

- **GIVEN** `mCounterInForDetailFutures` has two observers attached
- **WHEN** the recorded burst is replayed via `FakePmpEventListener`
- **THEN** each observer SHALL observe at most 30 emissions in 5 seconds (≤ 6/sec)
- **AND** the count SHALL equal the number of distinct price tuples

#### Scenario: `test_updateTopDetailWithPMP_throttledToOnePerFrame`

- **GIVEN** the burst replay fires 4 ticks within 8 ms
- **WHEN** `updateTopDetailWithPMP` is instrumented
- **THEN** it SHALL execute at most once for that frame

#### Scenario: `test_pmpFieldLookup_isPreComputed`

- **GIVEN** `PMPUtilViewModel` is constructed
- **WHEN** the test inspects `mPmpFieldLookup`
- **THEN** it SHALL be a non-empty `Map<String, String>`
- **AND** `getFinalHashMapPmpResponse()` SHALL complete in < 1 ms per tick

### Requirement: AI review invariant check

When the `ai-review` orchestrator reviews a diff that touches any of the file patterns `**/TradeFutures*/**`, `**/TradeBuySellScreen/Futures/**`, `**/TopPriceDetailCounter*`, `**/PMP*ViewModel*`, or `**/PMPEventListener*`, it SHALL prepend an "SR-3859 Invariants" section to its review output that lists the constraints from this spec.

#### Scenario: Reviewer output includes invariants

- **GIVEN** a diff matching one of the file patterns above
- **WHEN** the AI review runs
- **THEN** the review output SHALL contain a section titled "SR-3859 Invariants"
- **AND** SHALL list each `SHALL NOT` / `SHALL` requirement from this spec that is relevant to the changed files

#### Scenario: Diff re-introduces forbidden pattern

- **GIVEN** a diff adds `objectWillChange.send()` to `TradeFuturesViewModel.swift`
- **WHEN** the AI review runs
- **THEN** the review output SHALL flag the change as "REGRESSION: re-introduces SR-3859 anti-pattern"
- **AND** SHALL recommend the equivalent fix from this spec

### Requirement: jira-skill categorization

`jira-skill` `analysis.py` SHALL add `category: performance_live_data_loop` to `RootCauseCategory` and emit this sub-tag when an issue matches both the `performance` category and a symbol match on `MutableLiveData` / `objectWillChange` in the investigated code.

#### Scenario: New ticket classified into sub-category

- **GIVEN** a Jira ticket is analyzed whose investigation matches `MutableLiveData` and reports "laggy" / "hang" / "hot device"
- **WHEN** `analyze_snapshot` runs
- **THEN** the resulting bundle SHALL include `root_cause.sub_tag == "performance_live_data_loop"`

#### Scenario: Cross-reference to SR-3859

- **GIVEN** a future ticket matches `performance_live_data_loop`
- **WHEN** the bundle is rendered
- **THEN** it SHALL cite SR-3859 as a prior occurrence in the `related_issues` field
