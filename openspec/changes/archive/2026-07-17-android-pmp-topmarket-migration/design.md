# Design — `android-pmp-topmarket-migration`

## Context

`PMPViewModel` is the lifecycle-correct thin wrapper around `PMPConnectionCenter` introduced in `android-pmp-connection-center` Phase 2. It exposes a `SharedFlow<PMPUpdate>` that fragments collect via `repeatOnLifecycle(STARTED)` instead of the legacy `setOnResponseListener` callback wiring. The first migration, `NewOrderBottomSheet` (SR-3738 screen), landed and proved the pattern works.

The TopMarket screen family is the second migration wave. It is the **Market** tab in the app — the primary surface where users discover top-volume and top-movement counters. The family consists of four files in `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/`:

| File | LoC | Listener pattern | Inheritance |
|------|-----|------------------|-------------|
| `common/MarketTopDetailBaseScreen.kt` | 1328 | `setOnResponseListener { topic, linkedHashMap, _ -> ... }` (3-arg, topic-keyed) | `open class MarketTopDetailBaseScreen : BaseFragment()` — extended by `IndicesDetailScreen`, `HKPreIPODetailScreen`, `FractionalShareTopDetailBaseScreen` (which is further extended) |
| `common/MarketTopBaseFragment.kt` | 715 | `setOnResponseListener { index, linkedHashMap -> ... }` (positional) | `open class MarketTopBaseFragment : BaseFragment()` — extended by `TopVolumeFragment`, `TopLoserFragment`, `TopGainerFragment`, `HKPreIPOFragment` |
| `TabMarketStockScreen.kt` | 1608 | `setOnResponseListener { index, linkedHashMap -> ... }` (positional) | `open class TabMarketStockScreen : BaseFragment()` — standalone, no subclasses in this repo |
| `detailmarkettops/IndicesDetailScreen.kt` | 366 | `setOnResponseListener { pmpTopic, linkedHashMap, isAllDataReturned -> ... }` (4-arg, with sentinel) | `class IndicesDetailScreen : MarketTopDetailBaseScreen()` — concrete subclass |

The four target files share a common pattern: each is the **base** of a class hierarchy, and migrating the base automatically migrates the subclasses. None of the subclasses override `initPmpConnections()` (verified by grep), so the base class migration propagates cleanly.

`IndicesDetailScreen` is the **only file in the entire PMP codebase** that exercises the `isAllDataReturned` field on the legacy `mOnSubscribedCallbackAllData`. Migrating it requires the sentinel to actually work, which has been hardcoded `false` in `PMPViewModel` since Phase 2 landed. This sub-change therefore couples the TopMarket migration with the implementation of task §13.3 from the parent change.

## Goals / Non-Goals

**Goals:**
- Migrate the four TopMarket screens to the `PMPViewModel` + `repeatOnLifecycle(STARTED) { collect }` pattern
- Implement the `isAllDataReturned` sentinel in `PMPViewModel` correctly so `IndicesDetailScreen` semantics are preserved
- Establish a reusable migration pattern for the remaining 27+ PMP consumer screens (each as its own follow-up sub-change)
- Maintain URL pooling across the migrated screens — multiple screens sharing the same PMP URL should reuse one `PMPNode`
- Preserve the SR-3738 fix — app background/foreground does not affect the center connection

**Non-Goals:**
- Migrating `HomeScreen`, `WatchListTab`, `OptionDetailScreen`, `CounterOptionAllTypeScreen`, `TradeTicket*Screen` (each is its own sub-change per parent task §12.10–§12.15+)
- Deleting `PMPUtilViewModel` (deferred until the last consumer migrates, probably v3.4 or later)
- Resolving pre-existing test rot (parent task §13.1 — separate effort by owning teams)
- Custom lint rule for `unsubscribe()` in `onDestroy()` (parent task §13.4 — separate follow-up)
- iOS-side changes (SR-2875 equivalent already shipped on iOS in April 2026)
- **Extracting `aliasFields` to a standalone helper module** — aliasing is restored to `PMPViewModel` in this sub-change (Decision 7), but lives as a `private` function, not a shared utility. If a second screen family needs aliasing, it can be extracted to `PMPConnectionCenter` or a new `PMPAlias` helper in a follow-up.

## Decisions

### Decision 1: Implement `isAllDataReturned` via per-subscribe emission counting

**Chosen:** Add an `emissionCounter: AtomicInteger` field to `PMPViewModel` and a `expectedTopicCount: AtomicInteger` field. On every `subscribe()` call, set `expectedTopicCount = mHashmapIndexOfCounter.size` (the number of distinct PMP topics in this subscription, post-`expandOvernightCfd` dedup in `PMPConnectionCenter`). The collector increments `emissionCounter` on every emission; when the counter reaches `expectedTopicCount`, the next `tryEmit` carries `isAllDataReturned = true` and the counter is reset to zero (ready for the next batch).

**Why `mHashmapIndexOfCounter.size` (not the counter list size):** `expandOvernightCfd` in `PMPConnectionCenter` produces 2 topics per overnight CFD counter (regular + Asian session). After dedup in `PMPViewModel.mHashmapIndexOfCounter` (keyed by `counter.getPmpTopicByPriceAgreement()`), multiple counters may share one topic. The legacy `livePricesCallback` iterates `subscribeReturnValues` with `indexPmp == this.lastIndex`, where `this.lastIndex` is the position in the server's batch — which is also per-distinct-topic (one emission per topic per batch). So `mHashmapIndexOfCounter.size` correctly reproduces the legacy semantics.

**Algorithm:**
```kotlin
// In PMPViewModel.subscribe(counters, fields), after building mHashmapIndexOfCounter:
expectedTopicCount.set(mHashmapIndexOfCounter.size)
emissionCounter.set(0)

// In the collector:
token.priceUpdates.collect { (topic, rawData) ->
    val indices = mHashmapIndexOfCounter[topic] ?: emptyList()
    val aliasedData = aliasFields(rawData, subscribeFields)  // see Decision 7
    val counter = emissionCounter.incrementAndGet()
    val isLast = counter >= expectedTopicCount.get()
    if (isLast) emissionCounter.set(0)
    val update = PMPUpdate(topic, indices, aliasedData, isAllDataReturned = isLast)
    _pmpDataFlow.tryEmit(update)
}
```

**Edge cases:**
- **Single-topic subscription** (`expectedTopicCount == 1`): every emission carries `isAllDataReturned = true`. The `isLast = (1 >= 1)` branch is hit on the first emission. This is the correct behavior because a single-topic batch is "complete" after one tick.
- **Re-subscribe with different counters** (counter switch on `MarketTopDetailBaseScreen`): the `subscribe()` call resets both counters, so a new batch starts cleanly.
- **Collector cancelled mid-batch** (`detach()`): `emissionCounter` keeps its current value, but no emissions are forwarded. On the next `subscribe()` (e.g., onResume after onPause), the counters reset to zero + the new topic count, so a stale counter value cannot affect the next batch.
- **Empty topic list** (`mHashmapIndexOfCounter.size == 0`): impossible in practice — `PMPConnectionCenter.subscribe` returns null if no topics resolve (line 153-156), and `PMPViewModel.subscribe` returns early in that case (line 81-84).
- **Server delivers fewer topics than subscribed in a batch** (e.g., 2 of 4 expected topics): `isAllDataReturned` does NOT fire for this batch. The counter is not reset, and the next batch's emissions continue to increment. The `isAllDataReturned = true` will fire on whichever emission causes the counter to reach `expectedTopicCount` — possibly across multiple server batches. This is semantically equivalent to the legacy `indexPmp == this.lastIndex` (which also only fires when the server delivers the full batch).

**Alternatives considered:**
1. **Set `isAllDataReturned = true` on every emission.** Rejected — `IndicesDetailScreen` uses the sentinel to detect "all 4 indices in this batch are loaded" (the user wants to show a single render after all 4 are in, not after each). Every-true breaks that contract.
2. **Use `PMPNode.subscriberTokens.size` as the topic count.** Rejected — `subscriberTokens` is keyed by `UUID` (one per token, not one per topic), and it is `PMPNode`-internal state that the ViewModel should not depend on. The view-model-local counter is simpler and self-contained.
3. **Time-window debounce in the collector (e.g., 100ms timeout).** Rejected — this would delay all emissions by 100ms, which is unacceptable for live price updates (which fire multiple times per second during market hours). The emission counter approach is event-driven and has zero latency overhead.
4. **Compute `isAllDataReturned` lazily on the consumer side.** Rejected — pushes algorithm complexity to every consumer, defeating the purpose of `PMPUpdate` carrying the sentinel.

### Decision 2: Topic-keyed dispatch as the primary migration pattern

**Chosen:** For all four migrated screens, use `pmpViewModel.pmpDataFlow.collect { update -> onPmpReceived(update) }` and dispatch based on `update.topic` and/or `update.indices`, not `update.topic` alone.

**Rationale:** The legacy `MarketTopDetailBaseScreen` uses topic-keyed dispatch (`getIndexByTopic(topic) -> adapter index`), and the legacy `MarketTopBaseFragment` + `TabMarketStockScreen` use positional dispatch. Both styles map onto `PMPUpdate`: the `indices` field carries the fan-out indices, and `topic` carries the PMP topic. The new code can use either or both depending on the screen's existing logic.

**Example mapping for `MarketTopDetailBaseScreen`:**
```kotlin
// Legacy (line 894):
mMarketPMPUtilVM.setOnResponseListener { topic, linkedHashMap, _ ->
    val index = getIndexByTopic(topic) ?: return@setOnResponseListener
    // ...update adapter at `index` with `linkedHashMap`...
}

// Migrated:
private fun onPmpReceived(update: PMPUpdate) {
    val index = update.indices.firstOrNull() ?: return
    // ...update adapter at `index` with `update.data`...
}
```

The `indices` list is the fan-out that `mHashmapIndexOfCounter[topic]?.forEach { ... }` was computing in `PMPViewModel.subscribe()`. For TopMarket, the index map is `topic → [adapter position]`, so each `PMPUpdate` carries one index (the adapter position of the counter that emitted the update).

**Example mapping for `IndicesDetailScreen`:**
```kotlin
// Legacy (line 81):
mMarketPMPUtilVM.setOnResponseListener { pmpTopic, linkedHashMap, isAllDataReturned ->
    if (isAllDataReturned) {
        // ...re-render the entire indices grid with the latest snapshot...
    } else {
        // ...update just the row for pmpTopic...
    }
}

// Migrated:
private fun onPmpReceived(update: PMPUpdate) {
    if (update.isAllDataReturned) {
        // ...re-render the entire indices grid with the latest snapshot...
    } else {
        // ...update just the row for update.topic...
    }
}
```

### Decision 3: Per-screen ViewModel, not a shared `PMPViewModel` for the whole Market tab

**Chosen:** Each screen declares its own `private val pmpViewModel: PMPViewModel by viewModels()`. The Fragment's `ViewModel` is scoped to the Fragment, not the Activity, matching the established pattern in `NewOrderBottomSheet`.

**Rationale:** A shared `PMPViewModel` scoped to the Activity would be the wrong granularity: when `TabMarketStockScreen` is destroyed (user swipes to a different tab), its subscriptions should release. The center connection itself is process-scoped (via `PMPConnectionCenter`) — the ViewModel just owns a `PMPToken` for its lifetime, and the center ref-counts the token's topics.

URL pooling still works correctly: if two TopMarket screens subscribe to the same PMP URL, the center's `ConcurrentHashMap<String, PMPNode>` shares one `PMPNode` between them, and each ViewModel owns its own `PMPToken` for the same node.

### Decision 4: Migrate in dependency order — base screen first, then fragments, then IndicesDetailScreen

**Chosen:** Migration order: `MarketTopDetailBaseScreen` → `MarketTopBaseFragment` → `TabMarketStockScreen` → `IndicesDetailScreen`.

**Rationale:**
- `MarketTopDetailBaseScreen` is the base class. If a subclass overrides `initPmpConnections()` (line 1073), the override must be updated to call `pmpViewModel.subscribe()` instead of `mMarketPMPUtilVM.initPmpConnections()`. Doing the base first reveals all the override sites that need touching.
- `MarketTopBaseFragment` and `TabMarketStockScreen` are independent consumers — can be done in either order after the base.
- `IndicesDetailScreen` is the only consumer of `isAllDataReturned` — it MUST be migrated last, because the `PMPViewModel.subscribe()` change lands together with it. If `IndicesDetailScreen` were migrated before `PMPViewModel` computes the sentinel correctly, the screen would receive `isAllDataReturned = false` always, and its `isAllDataReturned` branch would never fire.

**Risk reduction:** Each migration is its own commit / its own MR-ready changeset. If `IndicesDetailScreen` proves problematic, the other three are already merged and the `isAllDataReturned` change can be reverted independently.

### Decision 5: Keep `mMarketPMPUtilVM` field in `MarketTopDetailBaseScreen` until the last subclass migrates

**Chosen:** During the migration, the base class keeps its `mMarketPMPUtilVM: PMPUtilViewModel by viewModels()` field but stops using it. Subclasses that override `onResume` / `onPause` / `onDestroy` continue to work — the `mMarketPMPUtilVM` field is just unused.

**Rationale:** `MarketTopDetailBaseScreen` is the base of a class hierarchy (`IndicesDetailScreen`, `HKPreIPODetailScreen`, `FractionalShareTopDetailBaseScreen` extend it). Subclasses that inherit may call `mMarketPMPUtilVM.{initPmpConnections, reSubscribe, disconnectToPMP, unSubscribeQueryRequest}()` from their own lifecycle methods. Removing the field would break those subclasses until they are also migrated, which is out of scope for this sub-change. Keeping the field as `@Suppress("unused")` is a stopgap until all subclasses migrate (separate sub-changes, parent task §12.14+).

**Same applies to `MarketTopBaseFragment`:** the four fragments (`TopVolumeFragment`, `TopLoserFragment`, `TopGainerFragment`, `HKPreIPOFragment`) that extend it inherit the migration. The `mMarketPMPUtilVM` field stays in the base as `@Suppress("unused")`.

**Removal trigger:** When the last subclass migrates, `mMarketPMPUtilVM` is removed from the base class in a follow-up commit. This is part of Phase 4 (parent change) — "Delete `PMPUtilViewModel` and `PmpConnectionPool` (future, after all migrations)."

### Decision 6: `subscribe()` resets the emission counter on every call

**Chosen:** `PMPViewModel.subscribe()` resets `emissionCounter` to 0 and `expectedTopicCount` to the new topic count at the start of the function, before starting the collector.

**Rationale:** The collector may have been cancelled by a previous `detach()` call. The new collector must start with fresh counter state so a stale `emissionCounter` from a previous `subscribe()` cannot fire `isAllDataReturned = true` prematurely.

**Implementation note:** `AtomicInteger.set(0)` and `AtomicInteger.set(distinctTopicCount)` are non-blocking and safe to call from any thread. They are called from `subscribe()` which runs on the main thread, so no thread-safety issues.

### Decision 7: Restore `aliasFields()` on every emission to preserve legacy semantic

**Chosen:** Add a private `aliasFields()` function to `PMPViewModel` that takes the raw `LinkedHashMap<String, String>` from `PMPNode` and the `subscribeFields: List<WatchListColumnsSettingModel>` passed to `subscribe()`, and returns a new `LinkedHashMap` where each raw FID key (e.g., `"9"`) is replaced by the canonical `WatchListColumnsSettingModel.value` string (e.g., `"9,F009,P23"`). The collector calls `aliasFields(rawData, subscribeFields)` before constructing `PMPUpdate`.

**Rationale:** The legacy `PMPUtilViewModel.livePricesCallback` calls `getFinalHashMapPmpResponse(rawJson)` (lines 99-122), which aliases raw FIDs to canonical `value` strings when `mIsUseDefaultFidID = true` (the default). Every existing consumer reads data via `linkMapPMP[PMPFieldsForSetting.X.columnsSettingModel.value]` (e.g., `linkMapPMP["9,F009,P23"]`), which assumes the aliased form. The new `PMPNode.handlePriceTick → parsePmpJsonResponse` returns raw FIDs (e.g., `linkMapPMP["9"]` would match, but `linkMapPMP["9,F009,P23"]` would not). Restoring aliasing in `PMPViewModel` keeps the existing consumer code unchanged and matches the established `mListColumnPmpEnum` / `mIsUseDefaultFidID` semantic from `PMPUtilViewModel`.

**Algorithm (preserved from `PMPUtilViewModel.getFinalHashMapPmpResponse`):**
```kotlin
private fun aliasFields(
    rawData: LinkedHashMap<String, String>,
    subscribeFields: List<WatchListColumnsSettingModel>
): LinkedHashMap<String, String> {
    val aliased = linkedMapOf<String, String>()
    val canonicalValues = subscribeFields.map { it.value }  // e.g., ["9,F009,P23", "11,F011,P8", ...]
    rawData.forEach { (rawKey, value) ->
        val canonical = canonicalValues.firstOrNull { canonicalValue ->
            canonicalValue.split(",").contains(rawKey)
        }
        if (canonical != null) {
            aliased[canonical] = value
        } else {
            aliased[rawKey] = value  // pass through unknown fields as-is
        }
    }
    return aliased
}
```

**Where to put `aliasFields`:** private function in `PMPViewModel`. The data shape is screen-agnostic (aliased key), so it belongs at the ViewModel layer. `PMPNode` stays screen-agnostic (raw FIDs); `PMPToken.priceUpdates` stays as `Pair<String, LinkedHashMap<String, String>>` with raw data; only the ViewModel's collector aliases.

**Edge cases:**
- **Raw key not in any `subscribeFields.value`**: the raw key is passed through unchanged. This handles server fields the consumer did not subscribe to (e.g., a future field added by the server that has no client enum yet).
- **Multiple `subscribeFields` with overlapping aliases** (e.g., two fields whose `value` strings both contain `"9"`): the `firstOrNull` returns the first match, preserving `mListColumnPmpEnum.firstOrNull` semantic. In practice this doesn't happen — each canonical value is unique.
- **`rawData` is empty**: `aliasFields` returns an empty map. The collector emits an empty `PMPUpdate.data` with `isAllDataReturned = false`.

**Note on the existing `NewOrderBottomSheet` migration:** the landed code does NOT call `aliasFields` in the collector (line 109 of `PMPViewModel.kt` does `data = rawData`). This means the migrated `NewOrderBottomSheet` may currently be silently broken for price fields that don't match the raw FID lookup. This is a critical question that must be resolved before/alongside the TopMarket migration. **Recommendation:** add `aliasFields` to `PMPViewModel` in this MR — it fixes both the TopMarket migration AND the pre-existing `NewOrderBottomSheet` issue at the same time.

## Architecture (post-migration)

```
┌────────────────────────────────────────────────────────────┐
│ PMPViewModel (per Fragment)                                 │
│                                                              │
│  pmpToken: PMPToken?                                         │
│  collectorJob: Job?                                          │
│  pmpDataFlow: SharedFlow<PMPUpdate>                          │
│                                                              │
│  emissionCounter: AtomicInteger      ← NEW                  │
│  expectedTopicCount: AtomicInteger   ← NEW                  │
│                                                              │
│  subscribe(counters, fields):                                │
│    1. open/reuse token                                       │
│    2. rebuild mHashmapIndexOfCounter                        │
│    3. expectedTopicCount.set(mHashmapIndexOfCounter.size)    │
│    4. emissionCounter.set(0)                                 │
│    5. launch collector:                                      │
│         for each (topic, rawData):                           │
│           indices = mHashmapIndexOfCounter[topic]            │
│           aliasedData = aliasFields(rawData, fields)         │
│           counter = emissionCounter.incrementAndGet()        │
│           isLast = counter >= expectedTopicCount.get()       │
│           if (isLast) emissionCounter.set(0)                 │
│           tryEmit(PMPUpdate(topic, indices, aliasedData,     │
│                              isAllDataReturned = isLast))    │
│                                                              │
│  detach() / unsubscribe() unchanged                         │
│  aliasFields(rawData, fields): LinkedHashMap  ← NEW (private)│
│                                                              │
│  ┌─ aliasFields ──────────────────────────────────────────┐  │
│  │ for each (rawKey, value) in rawData:                   │  │
│  │   canonical = subscribeFields.firstOrNull {            │  │
│  │     it.value.split(",").contains(rawKey)               │  │
│  │   }                                                    │  │
│  │   aliased[canonical ?: rawKey] = value                 │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬─────────────────────────┘
                                   │ collected by
                                   ▼
┌────────────────────────────────────────────────────────────┐
│ Fragment (e.g. MarketTopDetailBaseScreen)                   │
│  repeatOnLifecycle(STARTED) {                                │
│    pmpViewModel.pmpDataFlow.collect { update ->              │
│      onPmpReceived(update)                                   │
│    }                                                         │
│  }                                                           │
│                                                              │
│  // Cache for re-subscribe on onResume:                       │
│  pmpCounters: List<CounterDetail>?                            │
│  pmpFields: List<WatchListColumnsSettingModel>?               │
│                                                              │
│  override fun onResume() {                                   │
│    super.onResume()                                          │
│    val (counters, fields) = pmpCounters to pmpFields         │
│    if (counters != null && fields != null) {                 │
│      pmpViewModel.subscribe(counters, fields)                │
│    }                                                         │
│  }                                                           │
│  override fun onPause() {                                    │
│    super.onPause()                                           │
│    pmpViewModel.detach()                                     │
│  }                                                           │
│  override fun onDestroy() {                                  │
│    super.onDestroy()                                         │
│    pmpViewModel.unsubscribe()                                │
│    pmpCounters = null; pmpFields = null                      │
│  }                                                           │
└────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

- **[Risk] `mMarketPMPUtilVM` kept as `@Suppress("unused")` in the base class until last subclass migrates.** This is a code smell that needs follow-up. → **Mitigation:** Add a comment in the base class pointing to the next migration sub-change. Add a TODO with the count of remaining subclasses. Plan removal in Phase 4.

- **[Risk] `emissionCounter` is per-ViewModel, not per-subscribe.** If a fragment calls `subscribe()` with the same topic count twice, the counter resets correctly. But if it calls `subscribe()` with a different topic count after some emissions, the counter value from the previous batch is discarded. → **Mitigation:** This is by design — `subscribe()` is the batch boundary. The counter MUST reset on every `subscribe()` call. Documented in code KDoc.

- **[Risk] `emissionCounter` can race with the `tryEmit` in the collector.** The collector runs on `Dispatchers.IO` (per the existing convention). The `subscribe()` function runs on the main thread. The `AtomicInteger.incrementAndGet()` is atomic, so no two emissions can get the same counter value. → **Mitigation:** Use `AtomicInteger` (already in stdlib) — not `synchronized {}` — so the read-modify-write is single-instruction.

- **[Risk] `MarketTopDetailBaseScreen` is a base class — subclasses may override `initPmpConnections()` (line 1073).** If a subclass overrides and calls `mMarketPMPUtilVM.initPmpConnections()` directly, the base migration doesn't help. → **Mitigation:** Grep the codebase for `initPmpConnections(` overrides of this base class before merging. If any exist, decide whether to migrate the subclass in this sub-change or in a follow-up.

- **[Risk] `IndicesDetailScreen` is small (366 lines) but its semantics depend on `isAllDataReturned` firing exactly once per batch.** If the algorithm over- or under-fires, the screen renders incorrectly. → **Mitigation:** The smoke test in tasks.md §C.4 explicitly checks that the indices grid re-renders exactly once per batch (not 0 times, not 4 times).

- **[Risk] `expectedTopicCount` is computed from `counters.mapNotNull { it.PMPTopic }.distinct().size` — but `PMPConnectionCenter` may filter out duplicates server-side.** If the center dedupes by topic before reaching the ViewModel, the actual number of distinct topics the ViewModel sees may be less than `expectedTopicCount`. → **Mitigation:** Read `PMPConnectionCenter.subscribe()` to confirm it does not dedupe (it does not — the center passes the topic list through to `PMPNode.subscribe()` unchanged). Documented in `pmp-connection-center` spec §Node pooling by PMP URL.

- **[Risk] `getIndexByTopic(topic)` in `MarketTopDetailBaseScreen` is called inside the legacy listener body. If we naively move the body to `onPmpReceived(update)`, the function is still called from the same place — but the listener registration `mMarketPMPUtilVM.setOnResponseListener { ... }` is removed.** → **Mitigation:** No code logic change required — the function is the same, the call site moves. The `indices` field on `PMPUpdate` is the new return value of `getIndexByTopic()`.

- **[Risk] URL failover: the Market Top tab shows counters from multiple markets (HK, US, SG, JP, etc.). Each market may have its own PMP URL. If the center fails over to a delayed URL, the screen should keep showing the data.** → **Mitigation:** No change required — the failover is handled at `PMPNode` level (see `pmp-connection-center` spec §URL failover on connect failure). The ViewModel sees the same data, just from a different underlying socket.

## Migration Plan

### Phase A: PMPViewModel `isAllDataReturned` algorithm

1. Add `emissionCounter: AtomicInteger` and `expectedTopicCount: AtomicInteger` fields to `PMPViewModel`.
2. In `subscribe()`, set both counters before starting the collector.
3. In the collector, increment `emissionCounter` and compute `isLast` per the algorithm in Decision 1.
4. Verify by reading the diff and confirming that the existing `NewOrderBottomSheet` semantics (which never reads `isAllDataReturned`) are unaffected.

### Phase B: Migrate `MarketTopDetailBaseScreen`

1. Add `private val pmpViewModel: PMPViewModel by viewModels()`.
2. Remove `mMarketPMPUtilVM.setOnResponseListener { topic, linkedHashMap, _ -> ... }` (line 894).
3. Add `viewLifecycleOwner.repeatOnLifecycle(STARTED) { pmpViewModel.pmpDataFlow.collect { onPmpReceived(it) } }` in `onViewCreated`.
4. Implement `private fun onPmpReceived(update: PMPUpdate)`.
5. In `onResume` / `onPause` / `onDestroy`, replace `mMarketPMPUtilVM.{reSubscribe, unSubscribeQueryRequest, disconnectToPMP}()` with `pmpViewModel.{subscribe, detach, unsubscribe}()`.
6. Keep `mMarketPMPUtilVM: PMPUtilViewModel by viewModels()` field as `@Suppress("unused")` (Decision 5).
7. In `initPmpConnections()` (line 1073), replace `mMarketPMPUtilVM.initPmpConnections(...)` with `pmpViewModel.subscribe(counters, pmpList)`.

### Phase C: Migrate `MarketTopBaseFragment` and `TabMarketStockScreen`

1. Same pattern as Phase B. The dispatch uses `update.indices` directly (no `getIndexByTopic` lookup needed because the fragment has a 1:1 topic↔index mapping).

### Phase D: Migrate `IndicesDetailScreen` + verify `isAllDataReturned`

1. Same pattern as Phase B. The dispatch branches on `update.isAllDataReturned`.
2. Smoke test: open the Indices detail screen, confirm the indices grid re-renders exactly once per batch.
3. If the smoke test fails, debug the `emissionCounter` algorithm by adding temporary Timber logs.

### Phase E: Commit, MR, merge

1. Commit 1: `feat(android): PMPViewModel — implement isAllDataReturned sentinel` (PMPViewModel + tests)
2. Commit 2: `refactor(android): MarketTop screens — migrate from PMPUtilViewModel to PMPViewModel` (4 screens)
3. Push to `hoangtran/sr-3738-pmp-connection-center` (or new branch `hoangtran/sr-3859-topmarket-pmp-migration` if separate MR preferred)

### Rollback strategy

- If `PMPViewModel.subscribe()` change breaks a screen that previously worked: revert the `subscribe()` change. The legacy `mMarketPMPUtilVM.setOnResponseListener { ... }` paths in the migrated screens become stale (they would be removed as part of Phase B/C/D) — to rollback safely, the migrated screens must keep the `setOnResponseListener` calls commented out rather than deleted, so a single revert restores the previous behavior.

- If a specific screen migration breaks: revert that screen's commit only. The other three screens stay on the new pattern.

## Open Questions

> **All four open questions are RESOLVED.** This section is preserved as historical context and verification evidence. See **Decisions 1–7** for the answers.

1. **RESOLVED: `mMarketPMPUtilVM` field handling in base classes.** Keep the field as `@Suppress("unused")` until the last subclass migrates (Decision 5). Reasoning: removing it now would break `IndicesDetailScreen` / `HKPreIPODetailScreen` / `FractionalShareTopDetailBaseScreen` (subclasses of `MarketTopDetailBaseScreen`) and `TopVolumeFragment` / `TopLoserFragment` / `TopGainerFragment` / `HKPreIPOFragment` (subclasses of `MarketTopBaseFragment`) until they are also migrated — out of scope for this sub-change. Removal is Phase 4 (parent change). **Verified by**: `grep -n "mMarketPMPUtilVM" app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/` shows subclasses that don't override PMP callbacks but inherit the field; `@Suppress("unused")` is the correct stopgap.

2. **RESOLVED: Inheritance relationship between MarketTop base classes.** `MarketTopBaseFragment` and `MarketTopDetailBaseScreen` are **siblings**, both extending `BaseFragment()` directly. They are NOT parent/child. The base class migration is independent. **Verified by**: `grep -n "class .* : .*MarketTop" app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/` returns 6 subclasses — 3 for `MarketTopDetailBaseScreen` (`IndicesDetailScreen`, `HKPreIPODetailScreen`, `FractionalShareTopDetailBaseScreen`) and 4 for `MarketTopBaseFragment` (`TopVolumeFragment`, `TopLoserFragment`, `TopGainerFragment`, `HKPreIPOFragment`). `TabMarketStockScreen` is a standalone `open class` with no subclasses in this repo. Migrating each base class automatically migrates its subclasses because none of them override `initPmpConnections()` (verified by `grep -rn "override fun initPmpConnections" app/src/main/java/com/tdt/pmobile3/ui/screens/market/` → 0 matches).

3. **RESOLVED: Parameter signature compatibility.** `PMPViewModel.subscribe(counters: List<CounterDetail>, fields: List<WatchListColumnsSettingModel>)` and `mMarketPMPUtilVM.initPmpConnections(listCounterDetail: List<CounterDetail>, listPmpFields: List<WatchListColumnsSettingModel>)` have the same parameter shape. Call sites can be updated 1:1 — the only required adjustment is replacing `mMarketPMPUtilVM.initPmpConnections(listCounterDetail, listPmpFields)` with `pmpViewModel.subscribe(listCounterDetail, listPmpFields)`. **Verified by**: reading both signatures and confirming the type and order match.

4. **RESOLVED: `isInitializedPmpConn()` early-return guard semantics.** The guard is preserved in migrated screens as `if (pmpViewModel.pmpToken != null) return` at the top of `initPmpConnections()`. This matches the legacy "do nothing if already subscribed" behavior. The guard is not strictly required because `PMPViewModel.subscribe()` itself handles the "reuse existing token" case (it returns early when `pmpToken != null` AND the counter sets match), but preserving the guard is cheaper than re-deriving the equivalence and matches the existing pattern in the four target screens. **Verified by**: reading `PMPViewModel.subscribe()` (lines 65-100 in the landed code) which checks `pmpToken != null` early-return; the guard at the screen layer is redundant but harmless.
