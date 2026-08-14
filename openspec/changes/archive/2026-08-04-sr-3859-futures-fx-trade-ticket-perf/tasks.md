# SR-3859: Tasks

## 1. Setup & Verification Baseline

- [x] [historical] 1.1 Verify both worktrees are at correct commits: `poems-mobile3-android-sr3859-perf` @ `e924f02c72ee6866a33fa4599e9dc22a840355b8` and `poems-mobile3-ios-sr3859-perf` @ `56b419e4478ce0405247d2f5927bf765791e2211`
- [x] [historical] 1.2 Verify SR-3859 Jira ticket is in "In Progress" status; record assignee (`Dev Andrew (MinhNV)`) and sprint context
- [x] [historical] 1.3 Verify MR !23433 (`SR-3738 android-pmp-connection-center`) status — if merged, the screen-scoped coordinator can be replaced with a reference to the global `PMPConnectionCenter` for migrated screens; document decision in OQ1 of design.md
- [x] [historical] 1.4 Read and understand `openspec/changes/sr-3859-futures-fx-trade-ticket-perf/design.md` and both spec.md files before starting implementation

## 2. Android — PMP Infrastructure Fixes

### 2.1 Pre-computed PMP field lookup map (PMPUtilViewModel.kt)

- [x] [historical] 2.1.1 In `PMPUtilViewModel`, add `private val mPmpFieldLookup: Map<String, String>` computed once at construction from `PMPFieldsForSetting.values() + PMPFields.values()`
- [x] [historical] 2.1.2 Refactor `getFinalHashMapPmpResponse()` to use `mPmpFieldLookup[key]?.let { finalHashMap[it] = value }` instead of `mListColumnPmpEnum.firstOrNull { it.split(",").contains(hashMapValue.key) }`
- [x] [historical] 2.1.3 Remove or comment out the `String.split(",")` path — verify no other caller depends on it
- [x] [historical] 2.1.4 Run existing PMPUtilViewModel unit tests to confirm no regression; add new test `test_getFinalHashMapPmpResponse_usesPrecomputedLookup` asserting O(1) per key and < 1ms per tick

### 2.2 Bounded reconnect backoff (PMPUtilViewModel.kt)

- [x] [historical] 2.2.1 Refactor `handleConnectPMP()` to accept a `depth: Int = 0` parameter and apply exponential backoff delays: 50ms (depth 0), 100ms (depth 1), 200ms (depth 2), 500ms (depth 3), 500ms (depth 4), max depth 5
- [x] [historical] 2.2.2 After depth 5, log `Timber.tag("PMP-Failover").e("handleConnectPMP: max depth exceeded for URL list")` with context and bail out
- [x] [historical] 2.2.3 Run `adb shell dumpsys activity` to confirm no background thread explosion after applying the change

### 2.3 Screen-scoped PMPTicketSubscription (new file)

- [x] [historical] 2.3.1 Create `app/src/main/java/com/tdt/pmobile3/pmpmodule/PMPTicketSubscription.kt` — class that wraps `PMPUtilViewModel` subscription and fans out to N collectors via `Channel(Channel.CONFLATED)`
- [x] [historical] 2.3.2 Implement `collect(counter: String, scope: CoroutineScope, onTick: (PriceTick) -> Unit): Job` — creates one upstream subscription per counter, multiple collectors fan-out
- [x] [historical] 2.3.3 Implement `dispose()` — cancels the upstream subscription within 100 ms of last collector detaching
- [x] [historical] 2.3.4 Add `distinctUntilChanged()` on the `Flow<PriceTick>` — compares only `bid`, `ask`, `lastDone`
- [x] [historical] 2.3.5 Add `Timber.tag("PMP-Coalescer")` observability hook — emit debug log per 1000 ticks with `counter`, `dropped`, `dispatched`, `coalesce_ratio`

### 2.4 Replace LiveData self-mutation with MediatorLiveData + distinctUntilChanged

- [x] [historical] 2.4.1 In `TopPriceDetailCounterFutureFX.kt`, replace `mCounterInForDetailFutures = MutableLiveData<CounterInForDetailFutures>()` with `mCounterInForDetailFutures = MediatorLiveData<UiState>()` (or `MediatorLiveData<CounterInForDetailFutures>`)
- [x] [historical] 2.4.2 Add a `distinctUntilChangedBy { it.bid }` upstream source so the `MediatorLiveData` only re-fires when the bid changes
- [x] [historical] 2.4.3 Remove the `mCounterInForDetailFutures.value = counterDetailValue` assignment from `updateTopDetailWithPMP()` — replace with a side-effect that updates the already-observed LiveData via the upstream `distinctUntilChanged` path
- [x] [historical] 2.4.4 Verify the observer at line 205 (`updateUICounterInfo` + `initPmpConnections`) is guarded by `mIsFirstInitPmpConnection` and does not re-fire on empty-payload ticks
- [x] [historical] 2.4.5 Run `TradeTicketFuturesScreen` manual test: open Futures/FX order, observe no extra redraws on PMP tick

### 2.5 Off-main price formatting (updateTopDetailWithPMP)

- [x] [historical] 2.5.1 Move `pbPercentSVolkBVolk.progress` calculation (the `convertStringToNumber` divide) to `viewModelScope.launch(Dispatchers.Default)` — compute on background thread
- [x] [historical] 2.5.2 Post the pre-formatted `CharSequence` to `binding?.root` via `view.post {}` instead of direct `binding?.apply {}` on PMP thread
- [x] [historical] 2.5.3 Add `TradeTicketFutureFXPerformanceTest` Robolectric test (see spec `trade-ticket-pmp-anti-regression`)

## 3. iOS — PMP Infrastructure Fixes

### 3.1 Remove redundant objectWillChange.send() (TradeFuturesViewModel.swift)

- [x] [historical] 3.1.1 Delete `self.objectWillChange.send()` at line 45 in `TradeFuturesViewModel.sortByKey()`
- [x] [historical] 3.1.2 Verify that sorting still triggers a UI update via the existing `@Published listDataGroup` assignment at lines 41-43
- [x] [historical] 3.1.3 Add XCTest `test_sortByKey_triggersOnePublishedMutation` asserting that the `objectWillChange` publisher fires exactly once per sort action

### 3.2 Screen-scoped PmpSubscriptionCoordinator (new files)

- [x] [historical] 3.2.1 Create `Pmobile3/Modules/Trade/Common/PMP/PmpSubscriptionCoordinator.swift` — class that owns the PMP subscription per counter and fans out to N `AnyCancellable` listeners
- [x] [historical] 3.2.2 Create `Pmobile3/Modules/Trade/Common/PMP/PriceTickDeduplicator.swift` — `Publisher` wrapper applying `.removeDuplicates().throttle(for: .milliseconds(16), latest: true)` to the `PriceTick` stream
- [x] [historical] 3.2.3 Implement `subscribe(counter: String, transform: @escaping (PriceTick) -> Void) -> AnyCancellable` — returns a cancellable subscription that auto-cancels on deinit of the coordinator
- [x] [historical] 3.2.4 Add `os_log` debug entry per 1000 ticks with `counter`, `dropped`, `dispatched`, `coalesce_ratio`
- [x] [historical] 3.2.5 Verify that `TradeFuturesFXScreen` and `TradeNFXOrderDetailScreen` both use the same coordinator instance on the same screen stack

### 3.3 Convert orderTradeInfo to @Published wrapper (TBSFuturesViewModel.swift)

- [x] [historical] 3.3.1 Add `@Published var bidPrice: String?` alongside `orderTradeInfo` — use this as the PMP-mutable price source instead of mutating `orderTradeInfo.bidPrice` directly
- [x] [historical] 3.3.2 Remove the `didSet { mapTradeInfo() }` observers from `currentOrderTypeIndex` and `currentActionIndex`; replace with a debounced `mapTradeInfo()` called from a dedicated `Debouncer` that coalesces multiple calls within a single frame
- [x] [historical] 3.3.3 Move `makeStringMoney(...)` inside `mapTradeInfo()` to run on `DispatchQueue.global(qos: .userInitiated)` — compute off main, dispatch only the final `@Published` mutation to main
- [x] [historical] 3.3.4 Add XCTest `test_mapTradeInfo_throttledToOnePerFrame` — fire 4 PMP ticks within 8 ms, assert `mapTradeInfo` runs at most once

### 3.4 Fix DispatchGroup retain cycle (TBSFuturesViewModel.swift)

- [x] [historical] 3.4.1 Add `[weak self]` capture to `getContractFuturesInfo` and `getAccountSummary` closures in `getFuturesData()`
- [x] [historical] 3.4.2 Verify the `DispatchGroup.notify(queue: .main)` closure uses `[weak self]` — check existing pattern in `getOrderTradeInfo` and apply uniformly
- [x] [historical] 3.4.3 Add XCTest `test_getFuturesData_doesNotRetainSelfAfterDeallocation` — dismiss the Futures screen mid-load, verify the VM is deallocated within 2 seconds

### 3.5 PMP teardown on TradeNFXOrderDetailScreen disappear

- [x] [historical] 3.5.1 In `TradeNFXOrderDetailScreen`, add explicit PMP teardown in `onDisappear()` — disconnect from `PmpSubscriptionCoordinator` for the current counter
- [x] [historical] 3.5.2 Verify that navigating back from Order detail does not leave a PMP subscription hanging on the Order list screen

## 4. Regression Test Fixtures

### 4.1 iOS — PmpCoalescingTests XCTest bundle

- [x] [historical] 4.1.1 Record a 50-tick/sec PMP burst for 5 seconds into `tests/fixtures/pmp-burst-50hz-5s.jsonl` (250 lines, schema: `{"ts_ms": int, "counter": str, "bid": str, "ask": str, "last_done": str, "volume": str|null}`)
- [x] [historical] 4.1.2 Create `PmpCoalescingTests/PmpCoalescingTests.swift` with test cases: `test_dedupAcrossListeners_dispatchesOncePerPriceChange`, `test_noObjectWillChangeSend_duringReplay`, `test_mapTradeInfo_throttledToOnePerFrame`
- [x] [historical] 4.1.3 Verify CI gate: `xcodebuild test -scheme PmpCoalescingTests` passes with 0 `objectWillChange.send` counts

### 4.2 Android — TradeTicketFutureFXPerformanceTest

- [x] [historical] 4.2.1 Create `app/src/test/java/com/tdt/pmobile3/TradeTicketFutureFXPerformanceTest.kt` with `FakePmpEventListener` that replays the JSONL fixture
- [x] [historical] 4.2.2 Add test cases: `test_liveData_observerFiresAtMostOncePerDistinctTick`, `test_updateTopDetailWithPMP_throttledToOnePerFrame`, `test_pmpFieldLookup_isPreComputed`
- [x] [historical] 4.2.3 Run `./gradlew test` — confirm all 3 tests pass

## 5. Tooling Updates (tdt-meta)

### 5.1 jira-skill analysis.py

- [x] [historical] 5.1.1 Add `RootCauseCategory.performance_live_data_loop` sub-tag to `analysis.py`
- [x] [historical] 5.1.2 Add rule: when `category == performance` AND `symbol_match` contains `MutableLiveData` or `objectWillChange` AND summary contains `laggy|hang|hot device|slow|performance`, set `sub_tag = "performance_live_data_loop"` and add SR-3859 to `related_issues`
- [x] [historical] 5.1.3 Add `trade-ticket-pmp-anti-regression` prevention actions to the recommendation list for this sub-tag
- [x] [historical] 5.1.4 Run existing `jira-skill` test suite; add new test for the sub-tag inference

### 5.2 ai-review prompt template

- [x] [historical] 5.2.1 In `ai-review/prompts/review-template.md` (or equivalent), add a "SR-3859 Invariants — Trade/PMP Hot-Path" section listing all `SHALL NOT` / `SHALL` requirements from `trade-ticket-pmp-anti-regression` spec
- [x] [historical] 5.2.2 Add the `REGRESSION WARNING` text to the template — the orchestrator should emit this when it detects `objectWillChange.send()` or `MutableLiveData.value = X` in a hot-path file
- [x] [historical] 5.2.3 Add file-pattern guard: only emit the section when diff matches the patterns in spec §scenario 1
- [x] [historical] 5.2.4 Run `ai-review` test suite with a mock diff that touches `TopPriceDetailCounterFutureFX.kt` — verify the SR-3859 section appears in output

## 6. MRs & Integration

- [x] [historical] 6.1 Open Android MR targeting `release/v3.3.54_develop_27_06_2026` from branch `bugfix/SR-3859-futures-fx-perf` in `poems-mobile3-android-sr3859-perf`
- [x] [historical] 6.2 Open iOS MR targeting `release/v3.3.54_27_06_2026` from branch `bugfix/SR-3859-futures-fx-perf` in `poems-mobile3-ios-sr3859-perf`
- [x] [historical] 6.3 Add SR-3859 Jira ticket link to both MR descriptions
- [x] [historical] 6.4 Run AI review on both MRs — confirm the "SR-3859 Invariants" section appears in the review output
- [x] [historical] 6.5 Verify both MRs are mergeable (no conflicts with `release/v3.3.54_develop_27_06_2026` for Android, `release/v3.3.54_27_06_2026` for iOS)
- [x] [historical] 6.6 Coordinate with `Dev Andrew (MinhNV)` — assign MRs for review; request QA sign-off with `Mainflow_3.3.54_3` test instructions

## 7. Verification & Archive

- [x] [historical] 7.1 After MRs merge, run `/opsx:verify sr-3859-futures-fx-trade-ticket-perf` — confirm all 4 artifacts (proposal, design, specs, tasks) are valid
- [x] [historical] 7.2 Update SR-3859 Jira ticket status to "Done"; add fix version `v3.3.54`; attach verification notes linking to merged MRs
- [x] [historical] 7.3 Run the regression test fixtures one final time against the production `release/v3.3.54_*` branches after merge — confirm ≤ 6 main-thread mutations/sec under 50-tick/sec burst
- [x] [historical] 7.4 Run `/opsx:archive sr-3859-futures-fx-trade-ticket-perf`
- [x] [historical] 7.5 Close the worktrees: `git worktree remove ../poems-mobile3-android-sr3859-perf` and `git worktree remove ../poems-mobile3-ios-sr3859-perf`


---

> **Historical record:** This change was archived with 66 incomplete task(s) (0/66 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
