## ADDED Requirements

### Requirement: PMPViewModel computes isAllDataReturned sentinel per topic batch

`PMPViewModel.subscribe(counters: List<CounterDetail>, fields: List<WatchListColumnsSettingModel>)` SHALL compute the `isAllDataReturned` field on each emitted `PMPUpdate` based on a per-subscribe emission counter:

1. After the `mHashmapIndexOfCounter` rebuild and before starting the collector, `subscribe()` MUST reset the batch tracker: set `emissionCounter.set(0)` and `expectedTopicCount.set(mHashmapIndexOfCounter.size)`. The `expectedTopicCount` value MUST be the count of **distinct** PMP topics, not the count of counters — multiple counters may share a topic via `mHashmapIndexOfCounter`, and `PMPConnectionCenter.expandOvernightCfd` may add 2 topics per overnight CFD counter (regular + Asian session). The `mHashmapIndexOfCounter.size` value correctly captures the post-dedup distinct topic count.
2. The collector MUST increment `emissionCounter` on every emission (atomic read-modify-write via `AtomicInteger.incrementAndGet()`) and compute `isLast = (emissionCounter.get() >= expectedTopicCount.get())`. The current `PMPUpdate` carries `isAllDataReturned = isLast`. After emitting an `isLast = true` update, the collector MUST reset `emissionCounter.set(0)` so the next batch starts at zero.
3. When `subscribe()` is called with a single distinct topic (`expectedTopicCount == 1`), every emission carries `isAllDataReturned = true` (the batch is complete after one tick).
4. When `subscribe()` is called with K distinct topics, the Nth emission in each group of K carries `isAllDataReturned = true` (where N is the emission that brings `emissionCounter` to `expectedTopicCount`).
5. When the PMP server delivers fewer topics than `expectedTopicCount` in a batch (e.g., 2 of 4 expected topics), `isAllDataReturned` does NOT fire for that batch. The counter is preserved and the next batch's emissions continue to increment. `isAllDataReturned = true` will fire on whichever emission brings the counter to `expectedTopicCount` — possibly across multiple server batches. This semantic matches the legacy `mOnSubscribedCallbackAllData`'s `indexPmp == this.lastIndex` behavior, which also only fires when the server delivers a complete batch.

`PMPViewModel` SHALL expose two private fields used by the `isAllDataReturned` algorithm:

```kotlin
private val emissionCounter = AtomicInteger(0)
private val expectedTopicCount = AtomicInteger(0)
```

Both fields MUST be `java.util.concurrent.atomic.AtomicInteger` to allow safe read-modify-write from the `Dispatchers.IO` collector thread and the main-thread `subscribe()` function without explicit synchronization. Both fields MUST be reset to their initial values on every `subscribe()` call (step 1 of this requirement).

> **Rationale:** The per-subscribe emission counter reproduces the legacy `PMPUtilViewModel.mOnSubscribedCallbackAllData` semantics, which fired `isAllDataReturned = true` when `indexPmp == this.lastIndex` (the per-batch boundary). The new ViewModel uses `AtomicInteger` to match the existing `connectionRef: AtomicReference<PMPConnection>` pattern in `PMPNode` and avoid the deadlock risk of `synchronized {}` blocks across suspend points (see `pmp-connection-center` spec §Flow-based reactive implementation).

#### Scenario: Single-topic subscription — every emission is the last

- **WHEN** `PMPViewModel.subscribe(counters, fields)` is called with all counters sharing one PMP topic (e.g., four counters all subscribed via topic `"US/STK/NYSE/AAPL"`)
- **AND** `expectedTopicCount` is set to 1
- **AND** the PMP server pushes 10 price updates over 5 seconds
- **THEN** all 10 emissions carry `isAllDataReturned = true` (each is the Kth emission where K = 1)
- **AND** the fragment-side collector receives 10 `PMPUpdate(topic, indices, data, isAllDataReturned = true)` values

#### Scenario: Multi-topic subscription — isAllDataReturned fires on the Nth emission

- **WHEN** `PMPViewModel.subscribe(counters, fields)` is called with counters that resolve to 4 distinct PMP topics (e.g., `"US/STK/NYSE/AAPL"`, `"US/STK/NYSE/MSFT"`, `"US/STK/NASDAQ/GOOG"`, `"US/STK/NASDAQ/AMZN"`)
- **AND** `expectedTopicCount` is set to 4
- **AND** the PMP server pushes 4 price updates in quick succession (one per topic)
- **THEN** the first 3 emissions carry `isAllDataReturned = false`
- **AND** the 4th emission carries `isAllDataReturned = true`
- **AND** the 5th emission (next batch) carries `isAllDataReturned = false` again, with the 8th carrying `true`, etc.

#### Scenario: Counter switch resets the batch tracker

- **WHEN** `PMPViewModel.subscribe(countersA, fields)` is called with 3 distinct topics and 2 emissions have been received
- **AND THEN** `pmpViewModel.detach()` is called
- **AND THEN** `PMPViewModel.subscribe(countersB, fields)` is called with 5 distinct topics (a different counter set)
- **THEN** `expectedTopicCount` is reset to 5
- **AND** `emissionCounter` is reset to 0
- **AND** the first 4 emissions of the new batch carry `isAllDataReturned = false`
- **AND** the 5th emission carries `isAllDataReturned = true`

#### Scenario: detach() preserves the counter (does NOT reset)

- **WHEN** `PMPViewModel.subscribe(counters, fields)` is called with 3 distinct topics and 2 emissions have been received (counter = 2)
- **AND THEN** `pmpViewModel.detach()` is called
- **THEN** `emissionCounter` retains its value of 2 (NOT reset — the counter is internal to the ViewModel, detached from the fragment collector)
- **AND** the next call to `subscribe()` (e.g., on `onResume` after a pause) resets the counter to 0 along with `expectedTopicCount`

> **Rationale for NOT resetting on `detach()`:** The counter is per-ViewModel, not per-subscribe. A fragment that detaches mid-batch will call `subscribe()` again on the next `onResume`, and that `subscribe()` call resets the counter. The intermediate state is irrelevant because no emissions are forwarded to the fragment between `detach()` and the next `subscribe()`.

#### Scenario: IndicesDetailScreen renders exactly once per batch

- **WHEN** `IndicesDetailScreen.onPmpReceived(update)` is called for an `update` with `update.isAllDataReturned = false`
- **THEN** the screen updates only the row for `update.topic` (incremental update)
- **WHEN** `IndicesDetailScreen.onPmpReceived(update)` is called for an `update` with `update.isAllDataReturned = true`
- **THEN** the screen re-renders the entire indices grid with the latest snapshot (batch commit) — `MarketStockViewModel.updateDataForTopMarket` calls `sortListCounterByField(isKeepCurrentSort = true)` in this branch

#### Scenario: Server delivers partial batch — isAllDataReturned does not fire

- **WHEN** `PMPViewModel.subscribe(counters, fields)` is called with 4 distinct topics (`expectedTopicCount = 4`)
- **AND** the PMP server delivers only 2 of the 4 topics in the first batch (e.g., `"US/STK/NYSE/AAPL"` and `"US/STK/NYSE/MSFT"`)
- **THEN** both emissions carry `isAllDataReturned = false`
- **AND** `emissionCounter` is now 2 (NOT reset)
- **AND** the next server batch delivers the remaining 2 topics
- **AND** the 3rd and 4th emissions (across the two batches) carry `isAllDataReturned = false` and `true` respectively

> **Trade-off documented:** This scenario represents a data-availability gap (some topics never produced updates in this batch). The fragment will only see `isAllDataReturned = true` once the missing topics eventually produce an update. In practice, the PMP server reliably delivers all subscribed topics within ~5 seconds of the initial subscribe, so this edge case is rare. If it becomes a problem in production, the algorithm can be augmented with a 5-second timer that fires `isAllDataReturned = true` on the last seen emission regardless of count.

### Requirement: PMPViewModel exposes isAllDataReturned batch tracker

`PMPViewModel` SHALL expose two private fields used by the `isAllDataReturned` algorithm:

```kotlin
private val emissionCounter = AtomicInteger(0)
private val expectedTopicCount = AtomicInteger(0)
```

Both fields MUST be `java.util.concurrent.atomic.AtomicInteger` to allow safe read-modify-write from the `Dispatchers.IO` collector thread and the main-thread `subscribe()` function without explicit synchronization. Both fields MUST be reset to their initial values on every `subscribe()` call (step 1 of the `isAllDataReturned` requirement).

> **Rationale:** The `AtomicInteger` choice matches the existing `connectionRef: AtomicReference<PMPConnection>` pattern in `PMPNode` and avoids the deadlock risk of `synchronized {}` blocks across suspend points (see `pmp-connection-center` spec §Flow-based reactive implementation).

#### Scenario: Fresh PMPViewModel instance has both counters at zero

- **WHEN** a new `PMPViewModel` is constructed (e.g., during a Fragment's first `by viewModels()` call)
- **THEN** `emissionCounter.get() == 0`
- **AND** `expectedTopicCount.get() == 0`
- **AND** the counters remain at zero until the first `subscribe(counters, fields)` call is made

### Requirement: PMPViewModel aliases PMP field IDs to canonical WatchListColumnsSettingModel values

The `data` field on every emitted `PMPUpdate` SHALL be keyed by the canonical `WatchListColumnsSettingModel.value` string (e.g., `"9,F009,P23"` for `PMPFieldsForSetting.TRADE_PRICE`), NOT by raw PMP FID keys (e.g., `"9"`, `"F001"`, `"P2"`).

`PMPViewModel` SHALL call a private `aliasFields(rawData: LinkedHashMap<String, String>, subscribeFields: List<WatchListColumnsSettingModel>): LinkedHashMap<String, String>` function on every `PMPToken.priceUpdates` emission before constructing the `PMPUpdate`. The algorithm:

1. Build a list of canonical values: `canonicalValues = subscribeFields.map { it.value }` (e.g., `["9,F009,P23", "11,F011,P8", "1,F001,P2", ...]`)
2. For each `(rawKey, value)` entry in `rawData`:
   - Find the canonical value whose comma-separated list contains `rawKey`: `canonical = canonicalValues.firstOrNull { it.split(",").contains(rawKey) }`
   - If `canonical != null`, write `aliased[canonical] = value`
   - Else, write `aliased[rawKey] = value` (pass through unknown fields unchanged)
3. Return the aliased map

> **Rationale:** The legacy `PMPUtilViewModel.livePricesCallback` called `getFinalHashMapPmpResponse(rawJson)` which performed the same aliasing when `mIsUseDefaultFidID = true` (the default). Every existing consumer reads data via `linkMapPMP[PMPFieldsForSetting.X.columnsSettingModel.value]` (e.g., `linkMapPMP["9,F009,P23"]` for trade price), which assumes the aliased form. The new `PMPNode.handlePriceTick → parsePmpJsonResponse` returns raw FIDs (e.g., the hash map would be keyed by `"9"`, not `"9,F009,P23"`). Without aliasing in `PMPViewModel`, all migrated consumers that perform the `linkMapPMP[PMPFieldsForSetting.X.columnsSettingModel.value]` lookup pattern will silently fail — the lookup returns `null` and the screen shows empty price fields.

> **Why at the ViewModel layer, not PMPNode or PMPToken:** `PMPNode` is screen-agnostic and must not know about `WatchListColumnsSettingModel`. `PMPToken` is a generic wrapper. The aliasing is specific to the screen-facing API (the `PMPUpdate.data` field), so it belongs at the `PMPViewModel` collector — the screen-facing translation layer.

#### Scenario: Aliased field lookup matches the legacy semantic

- **WHEN** `PMPViewModel.subscribe(counters, fields)` is called with `fields` containing `PMPFieldsForSetting.TRADE_PRICE.columnsSettingModel` (whose `value = "9,F009,P23"`)
- **AND** the PMP server delivers a price update with raw key `"9"` and value `"123.45"`
- **THEN** the `PMPUpdate.data` map SHALL contain the entry `"9,F009,P23" -> "123.45"` (NOT `"9" -> "123.45"`)
- **AND** a consumer doing `linkMapPMP[PMPFieldsForSetting.TRADE_PRICE.columnsSettingModel.value]` (i.e., `linkMapPMP["9,F009,P23"]`) SHALL receive `"123.45"` — matching the legacy `mOnSubscribedCallbackAllData` semantic

#### Scenario: Multiple aliases for the same raw key

- **WHEN** `subscribeFields` contains two fields with overlapping aliases, e.g., field A's `value = "9,F009"` and field B's `value = "9,F009,P23"`
- **AND** the PMP server delivers a price update with raw key `"9"`
- **THEN** the `PMPUpdate.data` map SHALL contain the entry for field A's canonical value (`"9,F009"`) — the first match in `subscribeFields.map { it.value }` wins, matching the legacy `mListColumnPmpEnum.firstOrNull` semantic

#### Scenario: Unknown raw key passes through

- **WHEN** the PMP server delivers a price update with raw key `"999"` that does not appear in any `subscribeFields.value` (e.g., a future field added by the server that has no client enum yet)
- **THEN** the `PMPUpdate.data` map SHALL contain the entry `"999" -> <value>` (passed through unchanged)
- **AND** the consumer can still read the value via `linkMapPMP["999"]` if it knows about the field

#### Scenario: Raw key matches multiple aliases — first wins

- **WHEN** `subscribeFields` is `listOf(TRADE_PRICE.columnsSettingModel, CHANGE.columnsSettingModel)` and both have `value` containing `"9"`
- **THEN** only the first canonical value (`"9,F009,P23"`) appears in the aliased map for the raw key `"9"`
- **AND** the second canonical value's mapping is dropped for this raw key (this matches the legacy `mListColumnPmpEnum.firstOrNull` behavior)

### Requirement: TopMarket screen family migrated to PMPViewModel

The four TopMarket screen files MUST consume PMP data via the new `PMPViewModel` + `repeatOnLifecycle(STARTED) { collect }` pattern instead of the legacy `PMPUtilViewModel.setOnResponseListener(...)` callback. The four files are:

1. `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/common/MarketTopDetailBaseScreen.kt` (1328 LoC) — base class extended by `IndicesDetailScreen`, `HKPreIPODetailScreen`, `FractionalShareTopDetailBaseScreen` (which is further extended)
2. `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/common/MarketTopBaseFragment.kt` (715 LoC) — base class extended by `TopVolumeFragment`, `TopLoserFragment`, `TopGainerFragment`, `HKPreIPOFragment`
3. `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/TabMarketStockScreen.kt` (1608 LoC) — standalone fragment with no subclasses
4. `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/detailmarkettops/IndicesDetailScreen.kt` (366 LoC) — concrete subclass of `MarketTopDetailBaseScreen`, the **only** file in the entire PMP codebase that consumes the `isAllDataReturned` field

For each migrated screen:

- The screen SHALL declare `private val pmpViewModel: PMPViewModel by viewModels()` (or `protected` for base classes that subclasses need to access).
- The screen SHALL collect `pmpViewModel.pmpDataFlow` via `viewLifecycleOwner.lifecycleScope.launch { viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) { pmpViewModel.pmpDataFlow.collect { update -> onPmpReceived(update) } } }` in `onViewCreated`.
- The screen SHALL cache the most recent `(counters, fields)` pair in fragment-level fields (`pmpCounters: List<CounterDetail>?`, `pmpFields: List<WatchListColumnsSettingModel>?`) so that `onResume()` can re-arm the collector by calling `pmpViewModel.subscribe(counters, fields)` without re-hitting `mMarketStockViewModel.topMarketModelLD.value` (or equivalent). The cache pattern is borrowed from the `NewOrderBottomSheet` migration (which has the same shape).
- The screen SHALL call `pmpViewModel.subscribe(counters, fields)` in `onResume()` (or equivalent lifecycle hook like `onMarketTopPmpResume()` in `MarketTopBaseFragment`) if the cached fields are non-null. The `subscribe()` call MUST be guarded by the cache check so it is a no-op on the first entry (where the cache is still null).
- The screen SHALL call `pmpViewModel.detach()` in `onPause()` — the center token STAYS OPEN (this is the SR-3738 fix; the legacy `unSubscribeQueryRequest()` and `disconnectToPMP()` are both no-ops in the new architecture).
- The screen SHALL call `pmpViewModel.unsubscribe()` in `onDestroy()` to close the center token. The screen SHALL also null out the cache fields in `onDestroy()` to drop strong refs to `PMPSettingModel`-derived data.
- The screen SHALL implement `protected open fun onPmpReceived(update: PMPUpdate)` (or `private` for standalone fragments like `TabMarketStockScreen`) that dispatches based on `update.indices` (positional dispatch for `MarketTopBaseFragment` and `TabMarketStockScreen`) or `update.topic` (topic-keyed dispatch for `MarketTopDetailBaseScreen`) and `update.isAllDataReturned` (batch commit for `IndicesDetailScreen`).
- The legacy `mMarketPMPUtilVM.setOnResponseListener { ... }` callback SHALL be removed.
- The legacy `mMarketPMPUtilVM` field MAY be kept as `@Suppress("unused")` until the last subclass migrates (separate sub-changes, parent change task §12.14+).
- The legacy `mMarketPMPUtilVM.resetAllData()` calls in `TabMarketStockScreen` (lines 170, 579) SHALL be removed — `pmpViewModel.subscribe()` handles index map rebuild and counter reset internally.
- The legacy `getIndexByTopic(topic: String?): Int?` function in `MarketTopDetailBaseScreen` (line 804) MAY be removed after migration (its purpose is replaced by `update.indices.firstOrNull()`).

#### Scenario: MarketTopDetailBaseScreen migrated — subclasses inherit the new pattern

- **WHEN** `MarketTopDetailBaseScreen` is migrated to use `pmpViewModel.pmpDataFlow.collect { onPmpReceived(it) }`
- **AND** the legacy `mMarketPMPUtilVM.setOnResponseListener { topic, linkedHashMap, _ -> ... }` callback (line 894) is removed
- **THEN** the subclasses `IndicesDetailScreen`, `HKPreIPODetailScreen`, and `FractionalShareTopDetailBaseScreen` inherit the new pattern
- **AND** none of the subclasses override `initPmpConnections()` (verified by grep), so the base class migration propagates cleanly

#### Scenario: MarketTopBaseFragment migrated — subclasses inherit the new pattern

- **WHEN** `MarketTopBaseFragment` is migrated to use `pmpViewModel.pmpDataFlow.collect { onPmpReceived(it) }`
- **THEN** the subclasses `TopVolumeFragment`, `TopLoserFragment`, `TopGainerFragment`, and `HKPreIPOFragment` inherit the new pattern
- **AND** `onMarketTopPmpResume()` (line 649) calls `pmpViewModel.subscribe(counters, fields)` using the cached values (replacing the legacy `mMarketPMPUtilViewModel.reSubscribe()`)

#### Scenario: TabMarketStockScreen migrated — standalone fragment

- **WHEN** `TabMarketStockScreen` is migrated to use `pmpViewModel.pmpDataFlow.collect { onPmpReceived(it) }`
- **THEN** the screen behaves identically to before (positional dispatch via `update.indices`)
- **AND** the legacy `mMarketPMPUtilViewModel.setOnResponseListener { index, linkedHashMap -> ... }` callback (line 607) is removed
- **AND** the two `mMarketPMPUtilViewModel.resetAllData()` calls (lines 170, 579) are removed — they no longer have a target

#### Scenario: IndicesDetailScreen migrated — uses isAllDataReturned to commit batches

- **WHEN** `IndicesDetailScreen` is migrated to override `onPmpReceived(update: PMPUpdate)`
- **THEN** the screen branches on `update.isAllDataReturned`:
  - `update.isAllDataReturned = false` → incremental update of the row for `update.topic` via `mMarketStockVM.updateDataForTopMarket(update.topic, update.data, false)`
  - `update.isAllDataReturned = true` → batch commit: `mMarketStockVM.updateDataForTopMarket(update.topic, update.data, true)` which triggers `sortListCounterByField(isKeepCurrentSort = true)` to re-sort the indices grid
- **AND** the screen uses the `PMPViewModel` `isAllDataReturned` algorithm specified above
- **AND** the legacy `mMarketPMPUtilVM.setOnResponseListener { pmpTopic, linkedHashMap, isAllDataReturned -> ... }` callback (line 81) is removed
- **AND** the existing `mMarketStockVM.updateDataForTopMarket(pmpTopic, linkMapPMP, isAllDataReturned)` call site is preserved unchanged (the view model is a separate concern from PMP migration)

#### Scenario: Cache pattern enables re-subscribe on onResume without re-hitting the source

- **WHEN** `MarketTopDetailBaseScreen.onResume()` is called after the screen was paused and detached
- **AND** the cached `pmpCounters` and `pmpFields` are non-null
- **THEN** `pmpViewModel.subscribe(pmpCounters!!, pmpFields!!)` is called
- **AND** `subscribe()` reuses the existing token (because `pmpToken` is non-null) and just restarts the collector
- **AND** no DAO call to `getJsonPMPSettings()` is made (the cache prevents re-loading)
- **AND** the center connection is preserved across the pause cycle — this is the SR-3738 fix

#### Scenario: First entry populates the cache (cold-start)

- **WHEN** `MarketTopDetailBaseScreen` is shown for the first time
- **AND** the REST API response is loaded into `mMarketStockVM.topMarketModelLD.value`
- **AND** `initPmpConnections()` (line 1073) is called
- **THEN** `initPmpConnections()` builds `counters` and `pmpList`, stores them in `pmpCounters` and `pmpFields` (cache), and calls `pmpViewModel.subscribe(counters, pmpList)`
- **AND** on subsequent `onResume()` calls, the cache is non-null and `subscribe()` reuses the existing token
