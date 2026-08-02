## ADDED Requirements

### Requirement: PMPUpdate is the consumer-facing PMP price record

`PMPUpdate` SHALL be a `data class` with four properties:

```kotlin
data class PMPUpdate(
    val topic: String,                          // PMP topic string (e.g. "US/OPT/NYSE/AAPL 250619 C 200")
    val indices: List<Int>,                    // fan-out indices from mHashmapIndexOfCounter[topic]
    val data: LinkedHashMap<String, String>,  // raw (not aliased) field map
    val isAllDataReturned: Boolean            // true if this is the last item in the current batch
)
```

The `topic` property lets consumers dispatch to the correct handler without positional index lookups. The `indices` property mirrors the fan-out that `mHashmapIndexOfCounter[topic]?.forEach { mOnSubscribedCallback?.invoke(it, data) }` was doing in `livePricesCallback`. The `isAllDataReturned` mirrors the `indexPmp == this.lastIndex` sentinel that `mOnSubscribedCallbackAllData` uses. This record is the drop-in semantic equivalent of the four legacy callback variants combined.

#### Scenario: PMPUpdate carries topic, indices, data, and isAllDataReturned
- **WHEN** the `PMPViewModel` collector emits a `PMPUpdate` for the last topic in a `SubscribeReturnBean` batch
- **THEN** the emitted value SHALL contain `topic` (PMP topic string), `indices` (resolved from `mHashmapIndexOfCounter[topic]`), `data` (raw field map), and `isAllDataReturned = true` because it is the last item in the batch

### Requirement: PMPViewModel owns a single PMPToken and collector

`PMPViewModel` SHALL be a `androidx.lifecycle.ViewModel` (not `AndroidViewModel`) with the following owned resources:

```kotlin
class PMPViewModel : ViewModel() {
    private var pmpToken: PMPToken? = null
    private var collectorJob: Job? = null
    private var _pmpDataFlow = MutableSharedFlow<PMPUpdate>(
        replay = 1,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val pmpDataFlow: SharedFlow<PMPUpdate> = _pmpDataFlow.asSharedFlow()

    // mHashmapIndexOfCounter: Hashtable<String, ArrayList<Int>> — rebuilt on each subscribe()
}
```

The ViewModel owns exactly one `PMPToken` and exactly one `viewModelScope.launch` collector at a time. The `pmpDataFlow` is a `SharedFlow<PMPUpdate>` with the same buffer configuration as `PMPToken.priceUpdates` (replay=1, extraBufferCapacity=64, DROP_OLDEST).

#### Scenario: PMPViewModel holds at most one token and one collector at a time
- **WHEN** `PMPViewModel.subscribe()` is called while a previous `collectorJob` is still active
- **THEN** the previous `collectorJob` SHALL be cancelled before the new one starts
- **AND** at most one `pmpToken` SHALL be held by the ViewModel at any time

### Requirement: subscribe() opens or reuses token, starts collector

`PMPViewModel.subscribe(counters: List<CounterDetail>, fields: List<WatchListColumnsSettingModel>)` SHALL:

1. Cancel any existing `collectorJob` (idempotent — allows re-subscribe after `detach()`)
2. Call `PMPConnectionCenter.subscribe(counters, fields)` which returns a `PMPToken` — **reuse the existing token if one is already open** (stored in `pmpToken`)
3. Rebuild `mHashmapIndexOfCounter` by iterating `counters` and calling `updateListIndices(topic, index)` for each (the same pattern `PMPUtilViewModel` uses)
4. Start a new `viewModelScope.launch(Dispatchers.IO)` collector on `pmpToken.priceUpdates`:
   - For each `(topic, data)` pair from the center: resolve `indices = mHashmapIndexOfCounter[topic] ?: emptyList()`
   - Compute `isAllDataReturned` — the last emission per subscribe() call carries `true`
   - `tryEmit(PMPUpdate(topic, indices, data, isAllDataReturned))` into `_pmpDataFlow`

> **IMPORTANT:** `subscribe()` MUST check if `pmpToken` is already non-null. If the center token is still open (e.g., after a `detach()` call that kept the token alive), `subscribe()` reuses the existing token and restarts the collector. This is the key design difference from `PMPUtilViewModel` — the center token survives `detach()`.

#### Scenario: subscribe() reuses an existing token after detach
- **WHEN** `pmpViewModel.subscribe(counters, fields)` is called and `pmpToken` is already non-null (from a prior `subscribe()` followed by `detach()`)
- **THEN** the existing `PMPToken` SHALL be reused and a new `collectorJob` SHALL be started against it
- **AND** a fresh `PMPConnectionCenter.subscribe()` SHALL NOT be invoked

### Requirement: detach() cancels collector without closing token

`PMPViewModel.detach()` SHALL cancel `collectorJob` without calling `pmpToken?.close()`. The token **stays open** in `PMPConnectionCenter`. This is the fix for SR-3738: the center connection is independent of the fragment lifecycle, so app background/foreground does not affect it. A subsequent `subscribe()` call reuses the cached token.

> **CRITICAL:** `detach()` MUST NOT call `pmpToken?.close()`. If it does, the center token is destroyed and the next `subscribe()` opens a new one — recreating the `PMPUtilViewModel` bug that `PMPViewModel` is designed to fix.

#### Scenario: detach() cancels collector only, token stays open
- **WHEN** `pmpViewModel.detach()` is called from `NewOrderBottomSheet.onPause()`
- **THEN** `collectorJob.cancel()` SHALL run
- **AND** `pmpToken?.close()` SHALL NOT be called
- **AND** a subsequent `pmpViewModel.subscribe(counters, fields)` SHALL reuse the still-open token

### Requirement: unsubscribe() cancels collector and closes token

`PMPViewModel.unsubscribe()` SHALL cancel `collectorJob` AND call `pmpToken?.close()`. This is called from the Fragment's `onDestroy()` (or equivalent). After `close()`, `pmpToken` is nulled.

#### Scenario: unsubscribe() cancels collector, closes token, nulls field
- **WHEN** `pmpViewModel.unsubscribe()` is called from `NewOrderBottomSheet.onDestroy()`
- **THEN** `collectorJob.cancel()` SHALL run and `pmpToken?.close()` SHALL be called
- **AND** `pmpToken` SHALL be set to null after `close()`

### Requirement: onCleared() is the safety net

`PMPViewModel.onCleared()` SHALL call `unsubscribe()`. This ensures the token is closed even if the Fragment is destroyed without calling `unsubscribe()` directly (e.g., due to an exception in the fragment lifecycle).

#### Scenario: onCleared() closes the token even if Fragment forgot to unsubscribe
- **WHEN** `PMPViewModel.onCleared()` is invoked and the Fragment did not call `unsubscribe()`
- **THEN** `unsubscribe()` SHALL be called as a safety net
- **AND** ref counts SHALL be decremented in `PMPConnectionCenter`, preventing orphaned subscriptions

### Requirement: Collector runs on Dispatchers.IO

The `viewModelScope.launch` collector in `subscribe()` SHALL use `Dispatchers.IO`. This matches the existing convention for `mOnSubscribedCallback*` consumers in `livePricesCallback`, which expect to be invoked off the main thread. The fragment's `repeatOnLifecycle(STARTED)` scope uses the main thread — it launches the coroutine on `Dispatchers.Main.immediate` by default — but the `viewModelScope.launch(Dispatchers.IO)` inside the ViewModel ensures the fan-out to `mOnSubscribedCallback` and `onSubscribedUSSOCallback` remains off-thread.

#### Scenario: Collector runs on Dispatchers.IO and never blocks main thread
- **WHEN** `PMPViewModel.subscribe()` starts its collector
- **THEN** the `viewModelScope.launch` SHALL use `Dispatchers.IO` as the dispatcher
- **AND** the fan-out into `_pmpDataFlow` SHALL NOT run on the main thread

---

#### Scenario: Fragment shows → subscribes → pauses → detaches → resumes → subscribes (SR-3738 path)
- **WHEN** `NewOrderBottomSheet` is shown: `pmpViewModel.subscribe(counters, fields)` opens the center token and starts the collector
- **AND** `NewOrderBottomSheet.onPause()`: `pmpViewModel.detach()` cancels the collector; token **stays open**
- **AND** app enters background: `PMPConnectionCenter.onAppBackground()` suspends the node; subscriptions preserved
- **AND** app foregrounds: `PMPConnectionCenter.onAppForeground()` resumes the node; snapshots emitted; collector is not reattached (fragment is still paused)
- **WHEN** `NewOrderBottomSheet.onResume()`: `pmpViewModel.subscribe(counters, fields)` reuses the cached token, restarts collector
- **THEN** the first emission is the latest snapshot (replay=1); the collector receives it and pushes to `_pmpDataFlow`
- **AND** `repeatOnLifecycle(STARTED)` on the fragment side receives the update and updates the UI

#### Scenario: Token not explicitly closed, ViewModel cleared
- **WHEN** a Fragment's `PMPViewModel` is not explicitly unsubscribed (programming error)
- **AND** `PMPViewModel.onCleared()` is called
- **THEN** `unsubscribe()` is called as safety net
- **AND** `collectorJob.cancel()` and `pmpToken?.close()` run
- **AND** ref counts are decremented in `PMPConnectionCenter`, preventing orphaned subscriptions

#### Scenario: Counter switch (resetAllData + re-subscribe)
- **WHEN** `NewOrderBottomSheet` switches counter: `pmpViewModel.detach()` + `pmpViewModel.subscribe(newCounters, fields)` is called
- **AND** the new counters may resolve to different PMP topics or different URLs than the previous subscription
- **THEN** `mHashmapIndexOfCounter` is rebuilt with the new topic→index mapping
- **AND** the existing `PMPToken` is reused if the URL pool overlaps; a new token is created if the URL pool is entirely new
- **AND** the old topic subscriptions are decremented; the new topics are incremented

#### Scenario: Fragment destroyed (sheet dismissed)
- **WHEN** `NewOrderBottomSheet.onDestroy()` calls `pmpViewModel.unsubscribe()`
- **THEN** `collectorJob.cancel()` cancels the active collector
- **AND** `pmpToken?.close()` calls `PMPConnectionCenter.unsubscribe(this)`, decrementing ref counts
- **AND** if no other tokens hold subscriptions to the same node, the node schedules 60s teardown
- **AND** `topicSnapshots` on the node survive the token close — a new subscription will see them

#### Scenario: Two fragments share the same PMP URL (URL pooling)
- **WHEN** `NewOrderBottomSheet` and `OptionDetailScreen` are both visible and both call `PMPViewModel.subscribe()` with counters that resolve to the same PMP URL
- **THEN** both fragments share the same underlying `PMPNode` in `PMPConnectionCenter`
- **AND** each fragment has its own `PMPToken` and its own `PMPViewModel` instance
- **AND** closing one token (fragment destroyed) does not close the node's connection
- **AND** the other fragment continues to receive price updates uninterrupted

#### Scenario: Snapshot replay on new subscriber after node resume
- **WHEN** `PMPConnectionCenter.onAppForeground()` emits cached `topicSnapshots` to all active `PMPToken` instances
- **AND** `NewOrderBottomSheet` is still paused (fragment is in STOPPED state)
- **THEN** the fragment's `repeatOnLifecycle(STARTED)` block is not collecting — the emission is received by `PMPViewModel`'s `viewModelScope` collector but not forwarded to the fragment UI
- **AND** when `NewOrderBottomSheet.onResume()` calls `pmpViewModel.subscribe()`, the fresh `viewModelScope` collector subscribes to `_pmpDataFlow`
- **AND** `_pmpDataFlow` replays the last emitted `PMPUpdate` (replay=1) immediately to the new collector
- **AND** the fragment UI receives the stale snapshot as the first update
- **AND** subsequent live PMP pushes arrive and the UI updates to live prices
