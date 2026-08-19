## Purpose

Add `subscribeForHistory()` to `PMPConnectionCenter` for one-shot historical
chart data subscriptions. This complements the existing `subscribe()` method
(live prices) and routes all chart topics to the `liveChart.historicalURL`
PMP node, which is a separate `PMPNode` instance from the per-product URL
nodes.

## Requirements

### Requirement: subscribeForHistory public method

`PMPConnectionCenter` SHALL provide a new `suspend fun subscribeForHistory(counters, subscribeFields): PMPQueryToken?` method that:

1. Loads `PMPSettingModel` from Room on `Dispatchers.IO`. If null, returns
   `null` immediately (mirror `subscribe()` at line 119).
2. Resolves each counter to a history topic via
   `getHistoryChartTopicFormat(intervalTime = "D")` (daily interval, the
   default for `WatchListTab` sparkline charts). If a counter returns
   `null` (e.g., missing exchange/market/code), skips that counter.
3. Resolves the historical URL from
   `PMPSettingModel.liveChart.historicalURL` with fallbacks:
   - Primary: `liveChart.historicalURL`
   - Fallback 1: `liveChart.alternativeHistoricalURLs.firstOrNull()`
   - If all are null/empty, logs a warning and returns `null`.
4. Gets or creates a `PMPNode` for the historical URL via
   `getOrCreateNode(url, alternatives)` (existing helper, line 323).
5. Subscribes each resolved topic to the historical node via
   `PMPNode.subscribeForHistory(subscriberId, topics, fields, onChart)`.
6. Returns a `PMPQueryToken` with `priceUpdates:
   SharedFlow<Pair<String, List<String>>>`.

The method SHALL be `suspend` because it loads `PMPSettingModel` from
Room on `Dispatchers.IO`.

```kotlin
suspend fun subscribeForHistory(
    counters: List<CounterDetail>,
    subscribeFields: List<WatchListColumnsSettingModel>,
): PMPQueryToken?
```

#### Scenario: subscribeForHistory returns null when PMPSettingModel is unavailable

- **WHEN** Room returns null for `pmpSettingsDao.getJsonPMPSettings()`
- **THEN** `subscribeForHistory` returns `null` immediately
- **AND** no node is created, no token is returned

#### Scenario: subscribeForHistory returns null when historicalURL is null

- **WHEN** `PMPSettingModel.liveChart` is null
- **OR** `liveChart.historicalURL` and all `alternativeHistoricalURLs` are null/empty
- **THEN** `subscribeForHistory` returns `null` immediately
- **AND** logs a warning indicating no historical URL is configured

#### Scenario: subscribeForHistory subscribes to the historical URL node

- **WHEN** `subscribeForHistory(counters, fields)` is called with 3 valid counters
- **AND** `PMPSettingModel.liveChart.historicalURL = "https://hist.example.com"`
- **THEN** all 3 counters' history topics are routed to the node at
  URL "https://hist.example.com"
- **AND** a `PMPQueryToken` is returned with `priceUpdates` flow

#### Scenario: subscribeForHistory skips counters with no history topic

- **WHEN** `subscribeForHistory(counters, fields)` is called with 5 counters
- **AND** 2 counters return `null` from `getHistoryChartTopicFormat()`
  (e.g., missing exchange)
- **THEN** only 3 history topics are subscribed
- **AND** the 2 skipped counters are logged as warnings

### Requirement: subscribeForHistory creates a separate node from live subscriptions

The historical URL node SHALL be a separate `PMPNode` instance from
per-product URL nodes. The center's `nodes` map SHALL contain both:

- A node for the per-product URL (e.g., "https://pmp100.poems.com.sg")
- A node for the historical URL (e.g., "https://pmp-historical.example.com")

The two nodes SHALL have independent `topicRefCounts` and lifecycle.

#### Scenario: subscribe() and subscribeForHistory() create different nodes

- **WHEN** `subscribe(counters, fields)` is called with counters that
  resolve to "https://pmp100.poems.com.sg"
- **AND** `subscribeForHistory(counters, fields)` is called with the
  same counters but resolving history topics to
  "https://hist.example.com"
- **THEN** `PMPConnectionCenter.nodes` contains 2 entries:
  - "https://pmp100.poems.com.sg" → live node
  - "https://hist.example.com" → historical node

### Requirement: subscribeForHistory SHALL be idempotent across calls

`subscribeForHistory()` SHALL be idempotent across multiple calls with
the same counter list. Each call SHALL return a new `PMPQueryToken`
instance (distinct `tokenId`), but the historical node's
`topicRefCounts` SHALL be the post-dedup count (not summed across calls).
This idempotency SHALL hold across the entire lifetime of the
`PMPConnectionCenter` — the historical node's `topicRefCounts` SHALL
be the union of all subscribed topics, not the sum of all subscription
calls.

#### Scenario: Two subscribeForHistory calls with same counters

- **WHEN** `subscribeForHistory(counters, fields)` is called twice with
  the same 3 counters
- **THEN** 2 distinct `PMPQueryToken` instances are returned (different `tokenId`)
- **AND** the historical node's `topicRefCounts` has 3 entries (one per unique topic), not 6

### Requirement: unsubscribeQuery for PMPQueryToken

`PMPConnectionCenter` SHALL provide a new `unsubscribeQuery(token: PMPQueryToken)` method that decrements the historical node's ref-counts (parallel to `unsubscribe(token: PMPToken)` for live subscriptions).

#### Scenario: unsubscribeQuery decrements historical node ref-counts

- **WHEN** `subscribeForHistory(counters, fields)` is called, incrementing
  the historical node's `topicRefCounts` to 3
- **AND** `unsubscribeQuery(token)` is called with the returned token
- **THEN** the historical node's `topicRefCounts` is decremented to 0
- **AND** the 60s teardown timer starts (if no other tokens hold the
  historical node)

### Requirement: PMPQueryToken class

A new class `PMPQueryToken` SHALL be created as a sibling of `PMPToken`.
It SHALL be `Closeable` and SHALL have a typed `priceUpdates: SharedFlow<Pair<String, List<String>>>` flow.

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

#### Scenario: PMPQueryToken.emitData emits to subscribers

- **WHEN** `emitData("ABC", listOf("1.0", "2.0", "3.0"))` is called
- **THEN** all active collectors of `priceUpdates` receive `("ABC", listOf("1.0", "2.0", "3.0"))`
- **AND** a new collector receives the last emission (replay = 1)

#### Scenario: PMPQueryToken.close decrements ref-counts

- **WHEN** `close()` is called on a `PMPQueryToken`
- **THEN** `PMPConnectionCenter.unsubscribeQuery(this)` is called
- **AND** the historical node's `topicRefCounts` is decremented
