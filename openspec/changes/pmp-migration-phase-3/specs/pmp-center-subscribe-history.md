# Spec: PMPConnectionCenter.subscribeForHistory (SPEC-PMP-CENTER-001)

**Status:** Draft
**Related change:** `pmp-migration-phase-3`
**Related files:** `app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPConnectionCenter.kt`

## Purpose

Add `subscribeForHistory()` to `PMPConnectionCenter` for one-shot historical
chart data subscriptions. This complements the existing `subscribe()` method
(live prices) and routes all chart topics to the `liveChart.historicalURL`
PMP node, which is a separate `PMPNode` instance from the per-product URL
nodes.

## SPEC-PMP-CENTER-001 — subscribeForHistory contract

### 1.1 Method signature (MUST)

```kotlin
suspend fun subscribeForHistory(
    counters: List<CounterDetail>,
    subscribeFields: List<WatchListColumnsSettingModel>,
): PMPToken?
```

The method MUST be `suspend` because it loads `PMPSettingModel` from Room
on `Dispatchers.IO` (mirroring the existing `subscribe()` at line 119).

### 1.2 Behavior (MUST)

1. **Load `PMPSettingModel`** from Room on `Dispatchers.IO`. If null,
   return `null` immediately (mirror `subscribe()` at line 119).

2. **Resolve each counter to a history topic** via
   `getHistoryChartTopicFormat(intervalTime = "D")` (daily interval, the
   default for `WatchListTab` sparkline charts). If a counter returns
   `null` (e.g., missing exchange/market/code), skip that counter.

3. **Resolve the historical URL** from
   `PMPSettingModel.liveChart.historicalURL` with fallbacks:
   - Primary: `liveChart.historicalURL`
   - Fallback 1: `liveChart.alternativeHistoricalURLs.firstOrNull()`
   - If all are null/empty, log a warning and return `null`.

4. **Get or create a `PMPNode` for the historical URL.** The
   `getOrCreateNode(url, alternatives)` helper (line 323) handles this.
   The historical URL is just another URL pool.

5. **Subscribe each resolved topic** to the historical node via
   `PMPNode.subscribeForHistory(subscriberId, topics, fields, onChart)`.
   The `onChart` callback emits `(topic, chartPoints)` through
   `PMPQueryToken.emitData()`.

6. **Return a `PMPQueryToken`** (sibling of `PMPToken`, defined in
   `pmp-viewmodel-contract.md` §1.3). The token's
   `priceUpdates: SharedFlow<Pair<String, List<String>>>` carries the
   chart data (one `Pair` per topic, one-shot).

> **Revision note:** This spec was originally drafted to return a `PMPToken`
> with a `requestType = STREAMING_QUERY` field. The design decision in
> `design.md` Decision 2 selected the cleaner alternative of a dedicated
> `PMPQueryToken` class with type-safe data. See `pmp-viewmodel-contract.md`
> §1.3 for the full class definition. `PMPToken` does NOT carry a
> `requestType` field.

### 1.3 Counter list resolution (MUST)

For each `CounterDetail` in `counters`:

```kotlin
val historyTopic = counter.getHistoryChartTopicFormat(intervalTime = "D")
if (historyTopic == null) {
    Timber.w("[PMPConnectionCenter] subscribeForHistory: counter has no history topic")
    return@forEach
}
```

The `getHistoryChartTopicFormat()` function is at
`CounterDetail.kt:95`. It returns `null` if `exchange`, `market`, or
`code` is null/empty. For SEHK exchange, it converts to HKSE.

### 1.4 URL resolution (MUST)

```kotlin
val historicalUrl = pmpModel.liveChart?.historicalURL
    ?: pmpModel.liveChart?.alternativeHistoricalURLs?.firstOrNull()
if (historicalUrl.isNullOrEmpty()) {
    Timber.w("[PMPConnectionCenter] subscribeForHistory: no historical URL in PMPSettingModel")
    return null
}
```

The `LiveChart` model is at `model/responseapimodel/LiveChart.kt:3-14`.
It has `historicalURL: String` and
`alternativeHistoricalURLs: List<String>`.

### 1.5 Node creation (MUST)

```kotlin
val node = getOrCreateNode(
    url = historicalUrl,
    alternativeUrls = pmpModel.liveChart?.alternativeHistoricalURLs ?: emptyList(),
)
```

The historical URL node is a normal `PMPNode` — same ref-counting,
same login state machine, same 60s teardown timer. The only difference
is which topics it's subscribed to and which `requestType` is used.

### 1.6 Token construction (MUST)

```kotlin
val tokenId = UUID.randomUUID()
val queryToken = PMPQueryToken(
    tokenId = tokenId,
    topics = allHistoryTopics,
    subscribeFields = subscribeFields,
    _topicsByResolvedUrl = mapOf(historicalUrl to allHistoryTopics),
    center = WeakReference(this),
)
```

`PMPQueryToken` is a sibling of `PMPToken` (defined in
`pmp-viewmodel-contract.md` §1.3). It is type-safe for chart data:
`priceUpdates: SharedFlow<Pair<String, List<String>>>`. The historical URL
node receives `STREAMING_QUERY` requests, but this is implicit at the
node level (decided when `subscribeForHistory()` is called on `PMPNode`)
— the token does not need to carry a `requestType` discriminator.

### 1.7 Ref-count semantics (MUST)

The historical node's `topicRefCounts` is incremented for each unique
history topic (mirroring the live node's behavior). The ref-count is
per-node (URL is the key), so the historical node's ref-count is
independent of the live node's ref-count.

When `PMPToken.close()` is called on the QUERY token, the historical
node's `topicRefCounts` is decremented. The 60s teardown timer may
fire if the ref-count reaches zero.

### 1.8 Thread safety (MUST, existing pattern)

`getOrCreateNode` is the existing thread-safe helper. The `WeakReference`
in `activeTokens` is the same pattern as the existing `subscribe()`.
No new synchronization is required.

## Acceptance criteria

### Unit tests (MUST pass)

1. `PMPConnectionCenterTest.subscribeForHistory happy path`:
   - Loads `PMPSettingModel` from Room mock.
   - Resolves 3 counters to 3 history topics.
   - Routes all 3 topics to the historical URL.
   - Returns a `PMPQueryToken` with `topics` containing the 3 history topics.

2. `PMPConnectionCenterTest.subscribeForHistory null PMPSettingModel`:
   - Room returns null.
   - `subscribeForHistory` returns null.

3. `PMPConnectionCenterTest.subscribeForHistory null historicalURL`:
   - `PMPSettingModel.liveChart` is null.
   - `subscribeForHistory` returns null.

4. `PMPConnectionCenterTest.subscribeForHistory mixed counters`:
   - 5 counters, 2 have no `getHistoryChartTopicFormat()`.
   - 3 history topics are subscribed.
   - The 2 skipped counters are logged as warnings.

5. `PMPConnectionCenterTest.subscribeForHistory separate node from live`:
   - 2 `subscribe()` calls (live) + 1 `subscribeForHistory()` call.
   - Total nodes in `center.nodes`: 2 (live URL + historical URL), not 1.

6. `PMPConnectionCenterTest.subscribeForHistory idempotent`:
   - 2 calls with the same counter list.
   - Returns 2 different `PMPToken` instances (each call gets a new
     `tokenId`).
   - The historical node's `topicRefCounts` is 3 (not 6) — duplicate
     topic subscriptions share the ref-count.

### Manual QA (MUST pass)

1. `WatchListTab` opens → sparkline charts render within 3s.
2. Switching to another tab → sparkline charts re-render on return.
3. The chart data matches the legacy `setOnQueryCallback` semantic
   (same closing prices, same order).

## Migration impact on existing code

### New public API (this MR)

`PMPConnectionCenter.subscribeForHistory(counters, fields): PMPToken?` is
added next to the existing `subscribe()` (line 115). No existing API
changes.

### Refactored helpers (MUST add)

Two new private helpers in `PMPConnectionCenter.kt`:

1. `resolveHistoricalUrl(pmpModel: PMPSettingModel): String?` — encapsulates
   the URL resolution logic.
2. `getOrCreateNode` is reused (no changes).

### PMPToken / PMPQueryToken

`PMPQueryToken` is a new sibling class defined in
`pmp-viewmodel-contract.md` §1.3. `PMPToken` is unchanged — no
`requestType` field is added. The center's two methods return distinct
types: `subscribe() → PMPToken` (for live data, existing) and
`subscribeForHistory() → PMPQueryToken` (for chart data, NEW). Both are
`Closeable` and have parallel APIs.
