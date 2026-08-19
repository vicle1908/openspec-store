# Spec: PMPViewModel contract (SPEC-PMP-VM-001)

**Status:** Draft
**Related change:** `pmp-migration-phase-3`
**Related files:**
- `app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPViewModel.kt`
- `app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPToken.kt`
- `app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUpdate.kt`

## Purpose

Add `subscribeForHistory()` and the QUERY collector to `PMPViewModel`,
plus a `requestType` field to `PMPToken`. This enables `WatchListTab` to
migrate its `setOnQueryCallback` (chart data) consumer to the
`PMPViewModel.pmpDataFlow` pattern.

## SPEC-PMP-VM-001 — PMPViewModel public API additions

### 1.1 Updated public API (MUST)

```kotlin
class PMPViewModel : ViewModel() {
    // Existing — unchanged
    fun subscribe(counters: List<CounterDetail>, fields: List<WatchListColumnsSettingModel>)

    // NEW — this MR
    fun subscribeForHistory(counters: List<CounterDetail>, fields: List<WatchListColumnsSettingModel>)

    // Existing — semantics updated to cover both tokens
    fun detach()      // cancel both collectors, preserve both tokens (onPause)
    fun unsubscribe() // cancel both collectors, close both tokens (onDestroyView)

    // Existing
    val pmpDataFlow: SharedFlow<PMPUpdate>

    // Existing — unchanged
    val pmpToken: PMPToken?  // the LIVE token (or null)

    // NEW — this MR
    val pmpQueryToken: PMPToken?  // the QUERY token (or null)
}
```

### 1.2 `subscribeForHistory()` semantics (MUST)

```kotlin
fun subscribeForHistory(
    counters: List<CounterDetail>,
    fields: List<WatchListColumnsSettingModel>,
) {
    // Idempotent: if _queryToken is already open, restart the collector
    // with the new counter list.
    if (_queryToken != null) {
        queryCollectorJob?.cancel()
        queryCollectorJob = null
        onQueryTokenReady(_queryToken!!, counters, fields)
        return
    }

    viewModelScope.launch(Dispatchers.IO) {
        val token = PMPConnectionCenter.subscribeForHistory(
            counters = counters,
            subscribeFields = fields,
        ) ?: return@launch
        if (_queryToken != null) { token.close(); return@launch }
        _queryToken = token
        onQueryTokenReady(token, counters, fields)
    }
}
```

The method MUST be idempotent. If `_queryToken` is already open, it
restarts the collector without closing the existing token (matching the
`subscribe()` behavior at line 112 of `PMPViewModel.kt`).

### 1.3 `onQueryTokenReady()` (MUST)

```kotlin
private fun onQueryTokenReady(
    token: PMPToken,
    counters: List<CounterDetail>,
    fields: List<WatchListColumnsSettingModel>,
) {
    // Build chartTopic → counterIndices map (mirrors mHashmapIndexOfCounter
    // for live subscriptions). WatchListTab looks up the index from the
    // chart topic when handling a QUERY update.
    mChartTopicIndexMap.clear()
    counters.forEachIndexed { index, counter ->
        val chartTopic = counter.getHistoryChartTopicFormat() ?: return@forEachIndexed
        mChartTopicIndexMap.getOrPut(chartTopic) { ArrayList() }.add(index)
    }

    queryCollectorJob = viewModelScope.launch(Dispatchers.IO) {
        token.priceUpdates.collect { (topic, rawChart) ->
            val indices = mChartTopicIndexMap[topic] ?: emptyList()
            _pmpDataFlow.tryEmit(
                PMPUpdate(
                    kind = PMPUpdateKind.QUERY,
                    topic = topic,
                    indices = indices,
                    data = null,
                    chartData = rawChart as? List<String>,
                    isAllDataReturned = true,  // QUERY is one-shot
                )
            )
        }
    }
}
```

**Note on `rawChart` type:** The `PMPToken.priceUpdates` is typed as
`SharedFlow<Pair<String, LinkedHashMap<String, String>>>`. For QUERY
subscriptions, the second element is actually a `List<String>`. This
requires a type-safety improvement in `PMPToken.priceUpdates`.

**See `pmp-token-shape.md` (this spec) for the resolution.** The
resolution is to make `PMPToken.priceUpdates` type-generic over the
data type, OR to add a separate `PMPToken.priceUpdates` variant for
QUERY subscriptions. Decision: keep `PMPToken.priceUpdates` simple
(`SharedFlow<Pair<String, LinkedHashMap<String, String>>>` for LIVE
only), and add a new `PMPQueryToken` class for QUERY subscriptions.

**REVISED DECISION:** Add a new `PMPQueryToken` class. This is cleaner
than type-erasing the existing token. The center returns a
`PMPQueryToken` from `subscribeForHistory()` and a `PMPToken` from
`subscribe()`. Both are `Closeable` and have a similar `priceUpdates`
API, but with type-correct data shapes.

```kotlin
class PMPQueryToken(
    val tokenId: UUID,
    val topics: List<String>,
    val subscribeFields: List<WatchListColumnsSettingModel>,
    private val _topicsByResolvedUrl: Map<String, List<String>>,
    private val center: WeakReference<PMPConnectionCenter>,
) : Closeable {

    private val _priceUpdates = MutableSharedFlow<Pair<String, List<String>>>(
        replay = 1,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST,
    )

    val priceUpdates: SharedFlow<Pair<String, List<String>>> = _priceUpdates.asSharedFlow()

    fun emitData(topic: String, data: List<String>) {
        _priceUpdates.tryEmit(topic to data)
    }

    override fun close() {
        val c = center.get()
        if (c != null) {
            c.unsubscribeQuery(this)
        }
    }
}
```

`PMPConnectionCenter.unsubscribeQuery(token: PMPQueryToken)` is a new
method that decrements the historical node's ref-counts (parallel to
`unsubscribe(token: PMPToken)` for live subscriptions).

### 1.4 `detach()` updated semantics (MUST)

`detach()` MUST cancel BOTH collectors (live + query) and preserve
BOTH tokens. This is the lifecycle hook called from `Fragment.onPause()`.

```kotlin
fun detach() {
    collectorJob?.cancel()
    collectorJob = null
    queryCollectorJob?.cancel()
    queryCollectorJob = null
    Timber.d(
        "[PMPViewModel] detached — both collectors cancelled; " +
            "_pmpToken=${_pmpToken?.tokenId} _queryToken=${_queryToken?.tokenId}"
    )
}
```

### 1.5 `unsubscribe()` updated semantics (MUST)

`unsubscribe()` MUST cancel BOTH collectors AND close BOTH tokens.
This is the lifecycle hook called from `Fragment.onDestroyView()`.

```kotlin
fun unsubscribe() {
    collectorJob?.cancel()
    collectorJob = null
    _pmpToken?.close()
    _pmpToken = null
    mHashmapIndexOfCounter.clear()

    queryCollectorJob?.cancel()
    queryCollectorJob = null
    _queryToken?.close()
    _queryToken = null
    mChartTopicIndexMap.clear()

    Timber.d("[PMPViewModel] unsubscribed — both tokens closed")
}
```

### 1.6 `onCleared()` (MUST, existing behavior preserved)

`onCleared()` MUST call `unsubscribe()` as a safety net. This is unchanged
from the existing implementation.

### 1.7 `pmpToken` property (MUST, unchanged)

The `pmpToken: PMPToken?` property MUST continue to expose the LIVE token
(or `null` if not subscribed). This preserves the API for the 4
already-migrated screens.

### 1.8 `pmpQueryToken` property (MUST, NEW)

The `pmpQueryToken: PMPQueryToken?` property MUST expose the QUERY token
(or `null` if not subscribed). This is used by `WatchListTab` to check
whether the chart query is already in flight (idempotency guard).

### 1.9 Internal state (MUST)

```kotlin
class PMPViewModel : ViewModel() {
    // Existing
    private var _pmpToken: PMPToken? = null
    private var collectorJob: Job? = null
    private val mHashmapIndexOfCounter = Hashtable<String, ArrayList<Int>>()

    // NEW
    private var _queryToken: PMPQueryToken? = null
    private var queryCollectorJob: Job? = null
    private val mChartTopicIndexMap = Hashtable<String, ArrayList<Int>>()

    // Existing
    private val emissionCounter = AtomicInteger(0)
    private val expectedTopicCount = AtomicInteger(0)
    private val _pmpDataFlow = MutableSharedFlow<PMPUpdate>(replay = 1, ...)
    val pmpDataFlow: SharedFlow<PMPUpdate> = _pmpDataFlow.asSharedFlow()
    val pmpToken: PMPToken? get() = _pmpToken

    // NEW
    val pmpQueryToken: PMPQueryToken? get() = _queryToken

    // ... existing methods ...
    fun subscribe(counters, fields) { ... }
    fun detach() { ... }
    fun unsubscribe() { ... }

    // NEW
    fun subscribeForHistory(counters, fields) { ... }
    private fun onQueryTokenReady(token, counters, fields) { ... }
}
```

## SPEC-PMP-VM-002 — `PMPToken.requestType` field (NEW, MAY be optional)

### 2.1 Decision: `PMPQueryToken` instead of `requestType` field (REVISED)

**After further consideration:** Rather than adding a `requestType` field
to `PMPToken` (which would type-erase the data shape), the cleaner design
is a separate `PMPQueryToken` class. See section 1.3 above.

**The `requestType` field is NOT added to `PMPToken`.** Instead, the
type system disambiguates: `PMPToken` is for LIVE data;
`PMPQueryToken` is for QUERY data. Both are `Closeable` and have similar
APIs, but with type-correct `priceUpdates` flows.

### 2.2 `PMPConnectionCenter` API changes (MUST)

The center gains a new method:

```kotlin
suspend fun unsubscribeQuery(token: PMPQueryToken)
```

This decrements the historical node's ref-counts (parallel to
`unsubscribe(token: PMPToken)` for live subscriptions).

## SPEC-PMP-VM-003 — `PMPUpdate` emission for QUERY (MUST)

### 3.1 QUERY emission shape (MUST)

For QUERY emissions, `PMPViewModel` MUST emit:

```kotlin
PMPUpdate(
    kind = PMPUpdateKind.QUERY,
    topic = chartTopic,                  // e.g. "\D\SG\HKSE\2800"
    indices = chartTopicIndexMap[topic] ?: emptyList(),
    data = null,
    chartData = rawChartPoints,          // List<String> of dayClose values
    isAllDataReturned = true,            // QUERY is one-shot
)
```

### 3.2 Fragment handling (MUST)

The fragment's collector dispatches on `kind`:

```kotlin
pmpViewModel.pmpDataFlow.collect { update ->
    when (update.kind) {
        PMPUpdateKind.LIVE -> update.indices.forEach { idx ->
            handleLive(idx, update.data)
        }
        PMPUpdateKind.QUERY -> update.chartData?.let { chart ->
            handleQuery(update.topic, chart)
        }
        PMPUpdateKind.USSO -> update.data?.let { data ->
            handleUsso(update.topic, data)
        }
    }
}
```

The `chartData` parameter is null for LIVE and USSO; the `?` safe-call
prevents a runtime null-pointer exception. The compiler enforces
`chartData != null` for QUERY (via the `init {}` invariant in
`PMPUpdate`).

## Acceptance criteria

### Unit tests (MUST pass)

1. `PMPViewModelTest.subscribeForHistory idempotent`:
   - Two `subscribeForHistory(counters, fields)` calls.
   - Second call reuses `_queryToken` and restarts the collector.

2. `PMPViewModelTest.subscribeForHistory emits QUERY kind`:
   - `PMPQueryToken.emitData(topic, listOf("1.0", "2.0"))` is called.
   - `pmpDataFlow` emits `PMPUpdate(QUERY, topic, indices, null, listOf("1.0", "2.0"), isAllDataReturned=true)`.

3. `PMPViewModelTest.detach cancels both collectors`:
   - `subscribe(counters, fields)` then `subscribeForHistory(counters, fields)`.
   - `detach()` cancels both `collectorJob` and `queryCollectorJob`.
   - Both tokens survive (not nulled).

4. `PMPViewModelTest.unsubscribe closes both tokens`:
   - `subscribe(counters, fields)` then `subscribeForHistory(counters, fields)`.
   - `unsubscribe()` nulls both `_pmpToken` and `_queryToken`.
   - `pmpToken` and `pmpQueryToken` both return null.

5. `PMPViewModelTest.onCleared safety net`:
   - `subscribeForHistory(counters, fields)`.
   - `_queryToken` is non-null.
   - `onCleared()` is called.
   - `_queryToken` is null after `onCleared()`.

6. `PMPViewModelTest.chartTopicIndexMap rebuilt on each subscribe`:
   - `subscribeForHistory(counters1, fields)` → `mChartTopicIndexMap` has N entries.
   - `subscribeForHistory(counters2, fields)` (different counters) →
     `mChartTopicIndexMap` has M entries (cleared and rebuilt, not
     appended).

### Manual QA (MUST pass)

1. `WatchListTab` opens → live prices tick, sparkline charts render.
2. Switching tabs and back → both live prices and charts re-render.
3. The chart data matches the legacy `setOnQueryCallback` semantic
   (same closing prices, same order).
4. Pull-to-refresh → connection survives (no `resetAllData`).

## Migration impact on existing code

### New files (this MR)

- `viewmodels/common/PMPQueryToken.kt` — sibling of `PMPToken`, typed
  for chart data.

### Modified files (this MR)

- `PMPViewModel.kt` — adds `subscribeForHistory`, `onQueryTokenReady`,
  `_queryToken`, `queryCollectorJob`, `mChartTopicIndexMap`,
  `pmpQueryToken`. Updates `detach()` and `unsubscribe()` to cover both
  tokens.
- `PMPConnectionCenter.kt` — adds `unsubscribeQuery(token: PMPQueryToken)`.

### Unchanged files

- `PMPToken.kt` — no `requestType` field added (revised decision).
- `PMPNode.kt` — public API unchanged (the `submitRequest` rename is
  internal; see `pmp-node-submit-request.md`).
