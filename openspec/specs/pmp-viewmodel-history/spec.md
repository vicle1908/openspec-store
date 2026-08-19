## Purpose

Add `subscribeForHistory()` and the QUERY collector to `PMPViewModel`,
plus a new `pmpQueryToken: PMPQueryToken?` property. This enables
`WatchListTab` to migrate its `setOnQueryCallback` (chart data) consumer
to the `PMPViewModel.pmpDataFlow` pattern.

## Requirements

### Requirement: subscribe() SHALL preserve semantics for LIVE

`PMPViewModel.subscribe(counters, fields)` SHALL continue to open a LIVE
`PMPToken`, build `mHashmapIndexOfCounter`, and start a collector that
emits `PMPUpdate(kind = LIVE, ...)` to `pmpDataFlow`. This is unchanged
from the previous MR.

#### Scenario: subscribe() emits LIVE kind to pmpDataFlow

- **WHEN** `subscribe(counters, fields)` is called
- **AND** a price tick arrives for one of the subscribed topics
- **THEN** `pmpDataFlow` emits a `PMPUpdate` with `kind = LIVE`
- **AND** the `data` field is non-null and `chartData` is null

### Requirement: detach() preserves both tokens

`PMPViewModel.detach()` SHALL cancel BOTH the LIVE collector
(`collectorJob`) and the QUERY collector (`queryCollectorJob`), but
SHALL NOT close either token. Both `_pmpToken` and `_queryToken`
survive.

This is the lifecycle hook called from `Fragment.onPause()`.

#### Scenario: detach() cancels both collectors and preserves both tokens

- **WHEN** `subscribe(counters, fields)` is called (opens `_pmpToken`)
- **AND** `subscribeForHistory(counters, fields)` is called (opens `_queryToken`)
- **AND** `detach()` is called
- **THEN** `collectorJob` is cancelled
- **AND** `queryCollectorJob` is cancelled
- **AND** `_pmpToken` is still non-null (LIVE token preserved)
- **AND** `_queryToken` is still non-null (QUERY token preserved)

### Requirement: unsubscribe() closes both tokens

`PMPViewModel.unsubscribe()` SHALL cancel BOTH collectors AND close
BOTH tokens. This is the lifecycle hook called from
`Fragment.onDestroyView()`.

#### Scenario: unsubscribe() closes both tokens

- **WHEN** `subscribe(counters, fields)` is called (opens `_pmpToken`)
- **AND** `subscribeForHistory(counters, fields)` is called (opens `_queryToken`)
- **AND** `unsubscribe()` is called
- **THEN** `collectorJob` is cancelled
- **AND** `queryCollectorJob` is cancelled
- **AND** `_pmpToken` is nulled
- **AND** `_queryToken` is nulled
- **AND** `pmpToken` and `pmpQueryToken` properties return null

### Requirement: onCleared() is the safety net

`PMPViewModel.onCleared()` SHALL call `unsubscribe()`. This ensures both
tokens are closed even if the Fragment is destroyed without calling
`unsubscribe()` directly (e.g., due to an exception in the fragment
lifecycle).

#### Scenario: onCleared closes both tokens

- **WHEN** `subscribeForHistory(counters, fields)` is called, opening `_queryToken`
- **AND** `onCleared()` is called (e.g., ViewModel destroyed by the system)
- **THEN** `_queryToken` is nulled
- **AND** the QUERY token's `close()` is invoked, decrementing the
  historical node's ref-counts

### Requirement: subscribeForHistory opens a QUERY token

`PMPViewModel.subscribeForHistory(counters, fields)` SHALL:

1. Cancel any existing `queryCollectorJob` (idempotent).
2. If `_queryToken` is already open, restart the collector with the
   new counter list (reuses the existing token — same idempotent
   pattern as `subscribe()`).
3. Otherwise, call `PMPConnectionCenter.subscribeForHistory(counters,
   fields)` on `Dispatchers.IO` to get a new `PMPQueryToken`.
4. Build `mChartTopicIndexMap: Hashtable<String, ArrayList<Int>>` by
   iterating `counters` and calling `getHistoryChartTopicFormat()` for
   each.
5. Start a `viewModelScope.launch(Dispatchers.IO)` collector on
   `_queryToken.priceUpdates` that emits
   `PMPUpdate(kind = QUERY, topic, indices, data = null, chartData,
   isAllDataReturned = true)` to `_pmpDataFlow`.

```kotlin
fun subscribeForHistory(
    counters: List<CounterDetail>,
    fields: List<WatchListColumnsSettingModel>,
)
```

#### Scenario: subscribeForHistory is idempotent

- **WHEN** `subscribeForHistory(counters, fields)` is called twice with
  the same counter list
- **THEN** the second call reuses the existing `_queryToken`
- **AND** restarts the collector with the new counter list
- **AND** does NOT call `PMPConnectionCenter.subscribeForHistory()` again

#### Scenario: subscribeForHistory emits QUERY kind

- **WHEN** `subscribeForHistory(counters, fields)` is called
- **AND** the QUERY token's `priceUpdates` flow emits `("ABC",
  listOf("1.0", "2.0", "3.0"))` from the PMP server
- **THEN** `PMPViewModel` emits `PMPUpdate(kind = QUERY, topic = "ABC",
  indices = [...], data = null, chartData = listOf("1.0", "2.0", "3.0"),
  isAllDataReturned = true)` to `pmpDataFlow`

### Requirement: pmpQueryToken property exposed

`PMPViewModel` SHALL expose a public read-only property
`pmpQueryToken: PMPQueryToken?` that returns the QUERY token (or `null`
if not subscribed). This is used by `WatchListTab` to check whether the
chart query is already in flight (idempotency guard).

```kotlin
val pmpQueryToken: PMPQueryToken?
    get() = _queryToken
```

#### Scenario: pmpQueryToken is null before subscribeForHistory

- **WHEN** `PMPViewModel` is constructed (no subscriptions yet)
- **THEN** `pmpQueryToken` is null

#### Scenario: pmpQueryToken is non-null after subscribeForHistory

- **WHEN** `subscribeForHistory(counters, fields)` is called
- **THEN** `pmpQueryToken` is non-null
- **AND** points to the QUERY token

### Requirement: chartTopicIndexMap rebuilt on each subscribeForHistory

`mChartTopicIndexMap: Hashtable<String, ArrayList<Int>>` SHALL be
cleared and rebuilt on every `subscribeForHistory()` call. The map
maps chart topic string → list of counter indices that share that topic.

#### Scenario: chartTopicIndexMap is cleared and rebuilt

- **WHEN** `subscribeForHistory(counters1, fields)` is called with
  counters 1-3
- **THEN** `mChartTopicIndexMap` has 3 entries (one per counter's history topic)
- **WHEN** `subscribeForHistory(counters2, fields)` is called with
  different counters 4-6
- **THEN** `mChartTopicIndexMap` is cleared and rebuilt with 3 new entries (not 6)
