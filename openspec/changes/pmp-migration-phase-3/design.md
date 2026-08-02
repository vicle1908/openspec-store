# Design: PMP Migration Phase 3

## Context

This change builds on `android-pmp-connection-center` (SR-3738). That MR
shipped `PMPConnectionCenter` (process singleton), `PMPNode` (per-URL
connection with ref-counting), `PMPToken` (Closeable subscription token),
`PMPViewModel` (per-Fragment ViewModel wrapper), and migrated 4 of 17
PMP-using screens to the new pattern.

`PMPUtilViewModel` is a 985-line god class with 30+ consumers, 5 listener
variants, and a per-Fragment lifecycle contract that triggers
`logout → login → re-subscribe` on every `onPause`/`onResume` cycle. The new
center was designed to fix this, but the migration is incomplete.

**This change migrates the remaining 13 fragments.** It requires two center
extensions (`PMPNode` QUERY support, `PMPConnectionCenter.subscribeForHistory`)
and one data class extension (`PMPUpdate.kind`).

## Goals / Non-Goals

**Goals:**

- Migrate 13 fragments from `PMPUtilViewModel` to `PMPViewModel`.
- Add `STREAMING_QUERY` (history chart) support to the center so
  `WatchListTab` can migrate.
- Unify the 4 legacy callback variants into a single `PMPUpdate` with a
  `kind` discriminator.
- Provide feature flags for side-by-side QA validation of the 2 P0 screens
  before defaulting to the new path.
- Provide a verification plan (unit tests + manual QA checklist) for every
  tier.

**Non-Goals:**

- Deleting `PMPUtilViewModel` (defer to T5).
- Migrating the remaining 4+ screens (defer to a follow-up).
- Moving `aliasFields` to a shared helper (defer to a follow-up).
- iOS changes.
- Custom lint rules (defer to a follow-up).

## Decisions

### Decision 1: `PMPUpdateKind` enum, not a sealed class

**Chosen:** Add a `kind: PMPUpdateKind` enum field to the existing
`PMPUpdate` data class. Use `init { require(...) }` to enforce invariants
on construction.

**Rationale:** A sealed class hierarchy would force every consumer to handle
all subtypes with exhaustive `when`, which is more rigorous but a larger
refactor. The enum + invariant pattern is conservative and matches the
team's existing style (e.g., `PMPRequestType` enum at `EnumClass.kt:218`).

**Invariants (enforced by `init {}`):**

- `kind == LIVE  → data != null && chartData == null`
- `kind == QUERY → data == null && chartData != null`
- `kind == USSO  → data != null && chartData == null`
- `kind == LIVE  → indices.isNotEmpty()`
- `kind == USSO  → indices.isNotEmpty()`
- `kind == QUERY → indices MAY be empty` (orphan chart topics are
  silently dropped by PMPViewModel's QUERY collector — the `init {}`
  invariant does not require `indices.isNotEmpty()` for QUERY)

**Alternative considered:** Sealed class `PMPUpdate.Live` / `PMPUpdate.Query` /
`PMPUpdate.Usso`. Rejected because it requires every `pmpDataFlow.collect`
site to handle all subtypes, even when the screen only ever emits one kind.
The enum + nullability check is the same safety with less boilerplate at the
consumption site.

### Decision 2: Separate `PMPQueryToken` class, not a `requestType` field on `PMPToken`

**Chosen:** Introduce a new `PMPQueryToken` class (sibling of `PMPToken`) with a
type-safe `priceUpdates: SharedFlow<Pair<String, List<String>>>` flow.
`PMPConnectionCenter.subscribeForHistory()` returns `PMPQueryToken`; the
existing `PMPConnectionCenter.subscribe()` continues returning `PMPToken`.

**Rationale:** `PMPToken` already exposes
`priceUpdates: SharedFlow<Pair<String, LinkedHashMap<String, String>>>`
(confirmed at `PMPToken.kt:65`). Type erasure would force callers to cast
when mixing `LinkedHashMap` and `List<String>` on the same flow. A separate
`PMPQueryToken` class gives the compiler enforceability:

- `PMPToken.priceUpdates`         → `(topic, data: LinkedHashMap<String, String>)` ✅
- `PMPQueryToken.priceUpdates`     → `(topic, chartPoints: List<String>)`      ✅

The `PMPNode` internally routes both through `ConnEvent.PriceTick` /
`ConnEvent.ChartData` (different sealed variants, different pipelines) but
the two token classes present the correct public types to their callers.

**Code confirmations:**

- `PMPToken.priceUpdates` returns `Pair<String, LinkedHashMap<String, String>>` (`PMPToken.kt:65`)
- `PMPUtilViewModel.historyChartCallback` emits `List<String>` (parsed `dayClose` values from `HistoryChartPMPModel.kt`)
- `WatchListTab.kt:587` calls `setOnQueryCallback { index, list -> ... }` where `list: List<String>`

**Alternative rejected:** Add `requestType: PMPRequestType` field to `PMPToken`
with default `STREAMING_SUBSCRIBE`. This loses compile-time type safety: the
same `priceUpdates` flow would carry both `LinkedHashMap` and `List<String>`,
requiring runtime casts at every consumption site. Runtime casts are a
maintainability liability in 13+ fragment migration targets.

### Decision 3: Historical URL is a separate URL pool

**Chosen:** The historical URL (`PMPSettingModel.liveChart.historicalURL`) is
treated as a separate URL pool. The center creates a `PMPNode` for it (just
like a normal product URL), and the QUERY flow routes topics to that node.
There are two `PMPNode` instances involved in a single `WatchListTab`:

- `PMPNode_LIVE`  — keyed on per-product URL (e.g. `https://pmp100.poems.com.sg`)
- `PMPNode_HIST`   — keyed on `PMPSettingModel.liveChart.historicalURL`

Both nodes share the same `PMPNode` class (same state machine, same Flow
pipelines, same ref-counting machinery) but own independent state.

**Code confirmation:** `PMPUtilViewModel.initHistoricalPmpConnection` (line 589)
builds a `CounterForPMPModel` with `isHistoricalModel = true` and a separate
URL list (`listHistoricalPmpUrls`), stored under `mHashMapCounterPmpModel[HISTORICAL_KEY]`.
This confirms the legacy code also uses a separate URL/pool for QUERY.

**Rationale:** `PMPNode` is keyed by URL. Ref-counts are per-node. The
historical URL is a different URL from the live URL, so it naturally has its
own node. No new `PMPNode` subclass needed.

### Decision 4: `PMPViewModel` holds two token references, not two ViewModels

**Chosen:** `PMPViewModel` exposes `pmpToken: PMPToken?` (live) and
`pmpQueryToken: PMPQueryToken?` (history). Both tokens live in the same
ViewModel instance. `detach()` cancels both collectors; `unsubscribe()` closes
both tokens.

**Rationale:** A migrated fragment may have both live and chart data
(e.g., `WatchListTab`). Two ViewModels would force the fragment to
coordinate two `viewModels<PMPViewModel>()` calls and two collectors. One
ViewModel with two tokens is simpler and matches the iOS pattern.

**Alternative considered:** Separate `PMPViewModel` and `PMPHistoryViewModel`.
Rejected because it fragments the API and forces the fragment to remember
which ViewModel owns which subscription.

### Decision 5: Feature flags default off; QA validates side-by-side

**Chosen:** Add 4 feature flags (`FEATURE_PMP_CENTER_HOME`,
`FEATURE_PMP_CENTER_WATCHLIST`, `FEATURE_PMP_CENTER_P1`,
`FEATURE_PMP_CENTER_P2`). All default `false`. The legacy `PMPUtilViewModel`
path runs when the flag is off; the new `PMPViewModel` path runs when on.

**Rationale:** The P0 screens (Home, WatchList) are the most-visited in the
app. Migrating them without side-by-side validation would require reverting
the entire MR if a regression slipped through. Feature flags enable
parallel-run QA: the same build can run either path, and the QA team
compares behavior.

**Lifecycle:** Flags are added in T2 (P0), T3 (P1), T4 (P2). They are
toggled to `true` after QA sign-off for each tier. Flags are removed in
T5 alongside the legacy code deletion.

### Decision 6: `WatchListTab` uses one collector, not two

**Chosen:** `WatchListTab` collects from a single `pmpDataFlow` and
dispatches on `update.kind` to handle LIVE (fan-out to every index sharing
the topic) and QUERY (chart data) in the same collector.

**Rationale:** Two collectors would race on `pmpDataFlow`'s
`MutableSharedFlow` (replay = 1). A single collector is the canonical
pattern (used in `MarketTopBaseFragment`).

**`update.indices` fan-out (MUST be done by the fragment):**

```kotlin
// Live: every index sharing this topic gets the update
update.indices.forEach { idx -> handleLive(idx, update.data) }

// Query: every index sharing this chart topic gets the chart update
// (same fan-out semantic as LIVE — one topic → many counters)
if (update.kind == QUERY) {
    update.indices.forEach { idx ->
        handleQuery(idx, update.topic, update.chartData ?: emptyList())
    }
}
```

The legacy `setOnResponseListenerWithTopicIndex` called the callback once
per (topic, index) pair. The new `pmpDataFlow` emits one `PMPUpdate` per
topic (with the list of sharing indices), and the fragment iterates
`update.indices`. This is **functionally equivalent** but the call site
shape is different.

### Decision 7: Orphan chart topics are silently dropped

**Chosen:** When `PMPViewModel`'s QUERY collector receives a chart update for
a topic not present in `mChartTopicIndexMap`, it SHALL NOT emit a
`PMPUpdate`. The update is silently dropped.

**Rationale:** This matches the legacy `PMPUtilViewModel.historyChartCallback`
which calls `mOnQueryCallback(index, list)` only when
`listIndexOfCounter?.isNotEmpty() == true`. Topics not in the index map
have no registered fragment handler, so emitting them would be wasted work.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│           PMPConnectionCenter  (Kotlin object, process singleton)   │
│                                                                  │
│  nodes: ConcurrentHashMap<URL, PMPNode>                           │
│    "https://pmp100.poems.com.sg"  → PMPNode_LIVE (existing)    │
│    "https://hist.example.com"    → PMPNode_HIST (NEW)           │
│                                                                  │
│  activeTokens: ConcurrentHashMap<UUID, WeakReference<PMPToken>> │
│  activeQueryTokens: ConcurrentHashMap<UUID, WeakReference<PMPQueryToken>>│
│                                                                  │
│  ProcessLifecycleOwner observer (onStart / onStop)               │
│                                                                  │
│  subscribe(counters, fields)                       ← unchanged     │
│    → returns PMPToken                                           │
│    → resolves per-product URL via PMPSettingModel                 │
│    → getOrCreateNode(perProductUrl) → PMPNode_LIVE            │
│                                                                  │
│  subscribeForHistory(counters, fields)            ← NEW          │
│    → resolves historical URL from PMPSettingModel.liveChart      │
│    → getOrCreateNode(historicalUrl) → PMPNode_HIST            │
│    → node.subscribeForHistory(subscriberId, topics, fields,     │
│        onChart = { t, pts -> token.emitData(t, pts) })         │
│    → returns PMPQueryToken                                     │
│                                                                  │
│  unsubscribe(token: PMPToken)                   ← unchanged       │
│  unsubscribeQuery(token: PMPQueryToken)          ← NEW          │
│  onAppForeground()                              ← unchanged     │
│  onAppBackground()                             ← unchanged     │
│  disconnectAll()                              ← unchanged     │
└──────────────────────────┬──────────────────────────────────────┘
                            │
         ┌─────────────────┴─────────────────┐
         │            ↓                        │
         ▼                                    ▼
┌──────────────────────────────┐  ┌────────────────────────────────────────┐
│ PMPNode_LIVE                  │  │ PMPNode_HIST                           │
│ URL: per-product URLs        │  │ URL: liveChart.historicalURL           │
│                              │  │                                        │
│ State: Idle│Connecting│     │  │ State: Idle│Connecting│              │
│          Connected│Suspended │  │          Connected│Suspended            │
│                              │  │                                        │
│ topicRefCounts (LIVE topics)│  │ topicRefCounts (QUERY topics)        │
│ tokenSubscriptions (LIVE)     │  │ queryTokenSubscriptions (QUERY)        │
│ topicSnapshots              │  │                                        │
│                              │  │                                        │
│ submitRequest(reqtype=SUBSCRIBE│ │ submitRequest(reqtype=QUERY)        │
│                              │  │                                        │
│ ┌──────────────────────────┐ │  │ ┌──────────────────────────────────┐ │
│ │ PMPEventListener.kt      │ │  │ │ PMPEventListener.kt             │ │
│ │                          │ │  │ │                                  │ │
│ │ override livePrices     │ │  │ │ override livePrices             │ │
│ │   Callback(...)  ✅    │ │  │ │   Callback(...)  ✅            │ │
│ │                          │ │  │ │                                  │ │
│ │ override historyChart   │ │  │ │ override historyChart             │ │
│ │   Callback(...)        │ │  │ │   Callback(...)  ✅ NEW         │ │
│ │   ← NOT overridden     │ │  │ │   → ConnEvent.ChartData(...)     │ │
│ │   (silently dropped)    │ │  │ │   (sub-samples dayClose, keeps   │ │
│ │                          │ │  │ │    index % 10 == 0 + last item) │ │
│ └──────────────────────────┘ │  │ └──────────────────────────────────┘ │
│                              │  │                                        │
│ Flow pipelines (4 existing):│  │ Flow pipelines (5 total):            │
│  P1: Login handler         │  │  P1: Login handler                  │
│  P2: Status handler        │  │  P2: Status handler                 │
│  P3: PriceTick gate       │  │  P3: PriceTick gate                 │
│  P4: Reconnect watcher     │  │  P4: Reconnect watcher              │
│                              │  │  P5: ChartData gate  ← NEW         │
│                              │  │     (gated on Connected,           │
│                              │  │      fans out to QUERY tokens)      │
│                              │  │                                        │
│ emitToAllTokens(topic,data)│  │ emitChartToAllQueryTokens(topic, pts)│
└──────────────┬─────────────┘  └──────────────┬─────────────────────────┘
               │ token.emitData(topic, data)             │
               │  LinkedHashMap<String, String>           │
               │                                        │
               ▼                                        ▼
┌──────────────────────────┐  ┌────────────────────────────────────────┐
│ PMPToken  (Closeable)    │  │ PMPQueryToken  (Closeable)           │
│                          │  │                                        │
│ priceUpdates: SharedFlow │  │ priceUpdates: SharedFlow              │
│   Pair<String,           │  │   Pair<String,                        │
│     LinkedHashMap<       │  │     List<String>>        ✅           │
│       String,String>>    │  │   (type-safe: no cast needed)        │
│   (type-safe)           │  │                                        │
│                          │  │ emitData(topic, chartPoints)          │
│ emitData(topic, data)  │  │ close() → center.unsubscribeQuery()   │
│ close() → center.    │  │                                        │
│   unsubscribe(this)       │  │                                        │
└──────────┬───────────────┘  └──────────────┬─────────────────────────┘
           │                                   │
           │ collected by                      │ collected by
           ▼                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│           PMPViewModel  (per Fragment)                              │
│                                                                  │
│  _pmpToken: PMPToken?          ← LIVE token (existing field)     │
│  _queryToken: PMPQueryToken?   ← QUERY token (NEW field)         │
│                                                                  │
│  mHashmapIndexOfCounter         ← existing (LIVE topic → indices)│
│  mChartTopicIndexMap            ← NEW (QUERY topic → indices)    │
│                                                                  │
│  collectorJob: Job?            ← collects _pmpToken.priceUpdates   │
│  queryCollectorJob: Job?        ← collects _queryToken.priceUpdates│
│                                                                  │
│  pmpDataFlow: MutableSharedFlow<PMPUpdate>                       │
│    replay=1, extraBufferCapacity=64, DROP_OLDEST                 │
│                                                                  │
│  subscribe(counters, fields)           ← existing                │
│    → sets _pmpToken                                          │
│    → builds mHashmapIndexOfCounter (LIVE topic → indices)      │
│    → collectorJob emits PMPUpdate(kind=LIVE, indices, data)    │
│                                                                  │
│  subscribeForHistory(counters, fields) ← NEW                     │
│    → sets _queryToken                                          │
│    → builds mChartTopicIndexMap (QUERY topic → indices)        │
│    → queryCollectorJob emits PMPUpdate(kind=QUERY,              │
│        indices, data=null, chartData=chartPoints,              │
│        isAllDataReturned=true)                                 │
│    → orphan chart topics (no registered index) are SKIPPED      │
│                                                                  │
│  detach()    ← cancels both collectors (tokens survive)           │
│  unsubscribe() ← cancels both, closes both tokens                 │
│  onCleared() ← calls unsubscribe() (safety net)                │
└──────────────────────────┬──────────────────────────────────────┘
                            │
                            │ collected by
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  Fragment  (single collector, dispatch on update.kind)             │
│                                                                  │
│  lifecycleScope.launch {                                         │
│    repeatOnLifecycle(STARTED) {                                  │
│      pmpViewModel.pmpDataFlow.collect { update ->              │
│        when (update.kind) {                                     │
│          LIVE  -> update.indices.forEach { idx ->              │
│                      handleLive(idx, update.data!!) }           │
│          QUERY -> update.indices.forEach { idx ->              │
│                      handleQuery(idx, update.topic,             │
│                        update.chartData!!) }                   │
│          USSO -> handleUsso(update.topic, update.data!!)     │
│        }                                                        │
│      }                                                          │
│    }                                                            │
│  }                                                              │
│                                                                  │
│  Lifecycle hooks:                                               │
│    onResume()     → initPmpConnections() + initPmpHistoryConnections()│
│    onPause()      → pmpViewModel.detach()                       │
│    onDestroyView() → pmpViewModel.unsubscribe()                 │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow: WatchListTab subscribe + chart query

```
Fragment.onResume()
  → initPmpConnections()
    → pmpViewModel.subscribe(counters, fields)
      → PMPConnectionCenter.subscribe(counters, fields)
        → resolve per-product URL per counter (PMPSettingModel)
        → getOrCreateNode(perProductUrl) → PMPNode_LIVE
        → PMPNode_LIVE.subscribe(tokenId, topics, fields,
            onSnapshot = { t, d -> token.emitData(t, d) })
          → topicRefCounts incremented
          → if not Connected: connect() + wait for login
        → return PMPToken (LIVE)
      → onTokenReady(token, counters, fields)
        → build mHashmapIndexOfCounter (topicLIVE → [indices])
        → collectorJob = viewModelScope.launch {
            token.priceUpdates.collect { (topic, rawData) -> ... }
          }
        → emit PMPUpdate(kind=LIVE, ...) to pmpDataFlow
  → initPmpHistoryConnections()
    → pmpViewModel.subscribeForHistory(counters, fields)
      → PMPConnectionCenter.subscribeForHistory(counters, fields)
        → resolve historical URL from PMPSettingModel.liveChart
        → getOrCreateNode(historicalUrl) → PMPNode_HIST
        → PMPNode_HIST.subscribeForHistory(
            tokenId, historyTopics, fields,
            onChart = { t, pts -> token.emitData(t, pts) })
          → topicRefCounts incremented (QUERY topic)
          → if not Connected: connect() + wait for login
        → return PMPQueryToken
      → build mChartTopicIndexMap (topicQUERY → [indices])
        → each counter: counter.getHistoryChartTopicFormat() → key
        → skipped if getHistoryChartTopicFormat() == null
      → queryCollectorJob = viewModelScope.launch {
          token.priceUpdates.collect { (topic, chartPoints) ->
            val indices = mChartTopicIndexMap[topic] ?: emptyList()
            if (indices.isEmpty()) return@collect  // orphan, skip
            val update = PMPUpdate(
              kind = QUERY,
              topic = topic,
              indices = indices,
              data = null,
              chartData = chartPoints,
              isAllDataReturned = true,
            )
            _pmpDataFlow.tryEmit(update)
          }
        }
```

## Legacy vs. New: Pro/Con Comparison

This table compares the existing `PMPUtilViewModel` approach (left in
each row) against the new `PMPConnectionCenter` + `PMPViewModel` approach
(right in each row).

| Dimension | `PMPUtilViewModel` (legacy) | `PMPCenter` + `PMPViewModel` (new) |
|-----------|------------------------------|-------------------------------------|
| **Connection pooling** | Per-Fragment `PmpConnectionPool` — each fragment holds its own connection. App-wide, many fragments pointing to the same PMP URL each hold a separate TCP socket. | Process-wide singleton `PMPConnectionCenter` — one TCP socket per unique URL across the entire app. |
| **Reconnect behavior** | `logout → login → re-subscribe` on every `onPause`/`onResume`. Causes visible flash on screen resume (~200ms latency). | Connection survives `onPause`; only the TCP socket is dropped on background. On `onResume`, no re-login/re-subscribe needed — cached snapshots are emitted immediately, then live ticks resume. |
| **Lifecycle correctness** | Fragments call `disconnectToPMP()` in `onPause`, `reSubscribe()` in `onResume`. Easy to get wrong: missing calls cause stale state or memory leaks. | `PMPToken` is `Closeable`; `PMPViewModel.detach()` cancels the collector but keeps the token open. `unsubscribe()` closes in `onDestroyView`. The center handles background/foreground via `ProcessLifecycleOwner`. |
| **Multiple subscriptions** | Each fragment has its own `PmpConnectionPool` entry. If two fragments show the same stock, two separate PMP sockets are open to the same server. | Multiple fragments share one `PMPNode` via token ref-counts. One TCP socket serves all fragments subscribed to that URL. |
| **Type safety (chart data)** | `setOnQueryCallback { index, list: List<String> -> ... }` — type-safe at the call site. But the underlying `historyChartCallback` path (QueryReturnBean → sub-sampled List<String>) is mixed into the same god-class listener. | `PMPQueryToken.priceUpdates: SharedFlow<Pair<String, List<String>>>` — type-safe at the compiler level. `PMPQueryToken` is a dedicated class for chart data; it cannot accidentally carry `LinkedHashMap` price data. |
| **Testability** | `PMPUtilViewModel` is a 985-line `AndroidViewModel`. Testing requires Robolectric or Instrumented tests. | `PMPNode`, `PMPConnectionCenter`, `PMPToken`, `PMPQueryToken` are plain Kotlin classes. `PMPNode.connectionFactory` is an `internal var` for test injection. Unit tests can test the state machine, ref-counting, and QUERY flow in pure JUnit without Android. |
| **Scope of change for Phase 3** | `PMPUtilViewModel` unchanged during migration. Each fragment gets a dual-path via feature flag. Legacy path and new path co-exist. | 13 fragment files change. Core infrastructure (`PMPNode`, `PMPConnectionCenter`, `PMPToken`, `PMPViewModel`, `PMPUpdate`) changes. One MR touches 25+ files. |
| **Feature flag complexity** | Legacy path is the default. New path runs only when flag is `true`. Easy to reason about: one flag controls one path. | 4 feature flags (P0/P1/P2/P3). During the migration window, each screen has 2 paths. When all tiers are enabled, flags can be removed. |
| **QUERY (chart) support** | `historyChartCallback` → `mOnQueryCallback` — fully implemented in legacy code. Sub-sampling logic (`SEGMENT_HISTORICAL_CHART = 10`, `HISTORICAL_WORKING_DAY_POINT = 250`) is embedded in `PMPUtilViewModel`. | NEW: `PMPNode` needs `historyChartCallback` override (currently missing — silent drop bug). Chart sub-sampling must be implemented at the `PMPNode` listener layer so fragments receive a clean `List<String>`. |
| **Code size delta** | `PMPUtilViewModel`: 985 lines, 30+ consumers | New code: ~500 lines across 5 core files. Fragment migrations: ~300 lines across 13 files. Total delta: ~800 lines. |
| **Rollback risk** | If the MR is reverted, all 13 screens revert to `PMPUtilViewModel`. No partial rollback needed. | Feature flags allow partial rollout per screen tier. If `PMPCenter` is broken, flagging off a screen reverts only that screen to legacy. Full rollback reverts all 13 screens. |
| **Future: USSO support** | `onSubscribedUSSOCallback` is a separate listener path in `PMPUtilViewModel`. | `PMPUpdate.kind = USSO` unifies this into the same `pmpDataFlow`. `NewOrderBottomSheet` can migrate to the single collector pattern. |
| **Future: other request types** | Adding new request types requires adding new callbacks to `PMPUtilViewModel`. | `PMPNode` already has `requestType` in `buildSubscribeRequest`. Adding a new type requires only a new `ConnEvent` variant + pipeline + token type — no change to existing pipelines. |

## Per-tier migration specifics

### T2: P0 (HomeScreen, WatchListTab)

**`HomeScreen.kt`:**

- Add `FEATURE_PMP_CENTER_HOME` check in `initPmpUtilObserve()`.
- When off: existing `mWatchListPMPUtilViewModel` path runs.
- When on: new `pmpViewModel` path runs.
- Both paths share the same `WatchListTabViewModel` state.

**`WatchListTab.kt`:**

- Add `FEATURE_PMP_CENTER_WATCHLIST` check.
- When on, both `subscribe()` (LIVE) and `subscribeForHistory()` (QUERY)
  are called in `onResume`.
- `setOnResponseListenerWithTopicIndex` callback becomes:
  `pmpDataFlow.collect { if (it.kind == LIVE) it.indices.forEach { idx -> handleLive(idx, it.data) } }`.
- `setOnQueryCallback` becomes:
  `if (it.kind == QUERY) it.indices.forEach { idx -> handleQuery(idx, it.topic, it.chartData ?: emptyList()) }`.

### T3: P1 batch

| File | Key change |
|------|-----------|
| `CounterDetailScreen.kt` | Remove `resetAllData()` from `loadData()`. `detach()` in `onPause`, `unsubscribe()` in `onDestroyView`. |
| `OptionDetailScreen.kt` | Remove `resetAllData()` in `initPmpConnectionsRatesSO()`. Add `unsubscribe()` in `onDestroyView`. |
| `MarketDepthTab.kt` | Remove `repeatOnLifecycle(RESUMED)` wrapper around `initPmpConnections()`. Use `onResume` lifecycle. |
| `TradeSummaryTab.kt` | Same as `MarketDepthTab`. |

### T4: P2 batch

All 6 P2 files follow the standard template. `CounterPriceDetailHeader.kt`
is the outlier — it is missing `onPause` entirely. The fix is to add
`pmpViewModel.detach()` in `onPause`.

### T5: P3 batch + legacy deletion

- `TabIdeas.kt` and `TopPriceDetailCounter.kt` follow the standard template.
- `TopPriceDetailCounter` is a base class; fix propagates to
  `TopPriceDetailCounterST.kt`.
- `gitnexus_impact PMPUtilViewModel` confirms zero callers.
- Delete `PMPUtilViewModel.kt`, `PmpConnectionPool`,
  `CounterForPMPModel.kt`, `PMPEventListener.kt`.
- Remove the 4 feature flags (no longer needed).

## File Map

| File | Action | Description |
|------|--------|-------------|
| `viewmodels/common/PMPNode.kt` | **Modify** | Add `historyChartCallback` override to listener; extend `ConnEvent` with `ChartData` variant; add 5th Flow pipeline for chart data; add `subscribeForHistory()` and `unsubscribeForHistory()` public methods; add `queryTokenSubscriptions` map; rename `submitSubscribe` → `submitRequest` |
| `viewmodels/common/PMPConnectionCenter.kt` | **Modify** | Add `subscribeForHistory()` method; add `unsubscribeQuery()` method; add `activeQueryTokens` registry |
| `viewmodels/common/PMPToken.kt` | — | No changes (unchanged — type-safe for LIVE data only) |
| `viewmodels/common/PMPQueryToken.kt` | **Add** | New class: type-safe `(topic, chartPoints: List<String>)` flow, `close()` → `center.unsubscribeQuery()` |
| `viewmodels/common/PMPViewModel.kt` | **Modify** | Add `_queryToken`, `pmpQueryToken`, `subscribeForHistory()`, QUERY collector, `mChartTopicIndexMap` |
| `viewmodels/common/PMPUpdate.kt` | **Modify** | Add `PMPUpdateKind`, `chartData` field, `init {}` invariant assertion |
| `ui/screens/market/stocktab/common/MarketTopBaseFragment.kt` | **Modify** | Pass `kind = LIVE` to `PMPUpdate(...)` constructor |
| `ui/screens/market/stocktab/common/MarketTopDetailBaseScreen.kt` | **Modify** | Same |
| `ui/screens/market/stocktab/detailmarkettops/IndicesDetailScreen.kt` | **Modify** | Same (extends MarketTopDetailBaseScreen) |
| `ui/screens/trade/options/positions/neworder/NewOrderBottomSheet.kt` | **Modify** | Pass `kind = USSO` to `PMPUpdate(...)` constructor |
| `ui/screens/market/stocktab/TabMarketStockScreen.kt` | **Modify** | Pass `kind = LIVE` to `PMPUpdate(...)` constructor |
| `ui/screens/home/HomeScreen.kt` | **Modify** | Migrate to `PMPViewModel` (P0) |
| `ui/screens/watchlists/watchlisttab/WatchListTab.kt` | **Modify** | Migrate to `PMPViewModel` (P0) |
| `ui/screens/watchlists/counterdetail/CounterDetailScreen.kt` | **Modify** | Migrate (P1) |
| `ui/screens/trade/options/positions/optiondetail/OptionDetailScreen.kt` | **Modify** | Migrate (P1) |
| `ui/screens/watchlists/counterdetail/counterdetailtab/marketdepth/MarketDepthTab.kt` | **Modify** | Migrate (P1) |
| `ui/screens/watchlists/counterdetail/counterdetailtab/tradesummary/TradeSummaryTab.kt` | **Modify** | Migrate (P1) |
| `ui/screens/watchlists/counterdetail/counterdetailtab/marketdepth/MarketDepthTabFutures.kt` | **Modify** | Migrate (P2) |
| `ui/screens/watchlists/counterdetail/counterdetailtab/TopPriceDetailCounterFX.kt` | **Modify** | Migrate (P2) |
| `ui/screens/watchlists/counterdetail/common/CounterListSectionFragment.kt` | **Modify** | Migrate (P2) |
| `ui/screens/watchlists/counterdetail/common/CounterPriceDetailHeader.kt` | **Modify** | Migrate (P2) — add missing `onPause` |
| `ui/screens/watchlists/counterdetail/CounterDetailScreenST.kt` | **Modify** | Migrate (P2) |
| `ui/screens/trade/options/positions/optioncounter/OptionCounterScreen.kt` | **Modify** | Migrate (P2) |
| `ui/screens/discover/TabIdeas.kt` | **Modify** | Migrate (P3) |
| `ui/screens/watchlists/counterdetail/counterdetailtab/TopPriceDetailCounter.kt` | **Modify** | Migrate (P3, base class) |
| `viewmodels/common/PMPUtilViewModel.kt` | **Delete** (T5) | After all migrations sign-off |
| `viewmodels/common/PmpConnectionPool` (object) | **Delete** (T5) | Same file as PMPUtilViewModel.kt |
| `model/CounterForPMPModel.kt` | **Delete** (T5) | Same |
| `pmpmodule/PMPEventListener.kt` | **Delete** (T5) | Same |
| `app/build.gradle` | **Modify** | Add 4 feature flags (defaults off) |

## Risks / Trade-offs

- **`PMPUpdate` constructor change is binary-incompatible.** All 4 already-migrated
  screens must update call sites. The change is mechanical: add
  `kind = PMPUpdateKind.LIVE` (or `USSO`) to each `PMPUpdate(...)` call.
  → **Mitigation:** Update them in the same MR (T1) so the build doesn't break.

- **`PMPNode.historyChartCallback` is currently missing.** `PMPNode.listener`
  (line 256) does NOT override `historyChartCallback`. Without adding it,
  all QUERY responses from the PMP library are silently dropped at the node
  layer.
  → **Mitigation:** Add the override in T1.4. The override parses
  `QueryReturnBean` → `List<String>` using the same sub-sampling logic as
  `PMPUtilViewModel.historyChartCallback` (verified in that method at line 140).

- **`PMPNode.subscribeForHistory` must use a separate `queryTokenSubscriptions`
  registry.** Using the same `tokenSubscriptions` map would cause LIVE and
  QUERY tokens to collide on the same subscriber ID.
  → **Mitigation:** `PMPNode` keeps two separate maps:
  `tokenSubscriptions` (LIVE) and `queryTokenSubscriptions` (QUERY).

- **`WatchListTab` fan-out changes from per-(topic, index) callback to a
  single `pmpDataFlow` collection with iteration.** Legacy code calls
  `mOnQueryCallback(index, list)` once per sharing counter. New code emits
  one `PMPUpdate` per topic and the fragment iterates `update.indices`.
  → **Mitigation:** Feature flag enables side-by-side QA. The handler must
  be idempotent w.r.t. duplicate (topic, index) pairs.

- **Feature flags add maintenance overhead.** Each flag has 2 paths to
  maintain, double the test surface area.
  → **Mitigation:** Flags are temporary; removed in T5. The legacy path
  is preserved as-is during the flag period (no code changes to
  `PMPUtilViewModel`).

- **`pmpDataFlow` is shared between LIVE and QUERY collectors.** Both
  collectors call `_pmpDataFlow.tryEmit(...)` from `Dispatchers.IO`. The
  `MutableSharedFlow` is thread-safe for `tryEmit` (it uses atomic
  operations internally).
  → **Mitigation:** `MutableSharedFlow.tryEmit` is thread-safe. The
  `replay = 1` semantic means a new collector gets the last emission from
  either kind, but the fragment dispatches on `kind` so it handles either
  correctly.

- **`PMPUtilViewModel.unSubscribeQueryRequest` was the legacy way to
  detach.** Some P1/P2 screens call it in `onPause`. The new code calls
  `pmpViewModel.detach()` instead.
  → **Mitigation:** Feature flag controls which path runs. Only one path
  executes at a time.

- **`mChartTopicIndexMap` uses `getHistoryChartTopicFormat()` which returns
  `null` for counters with missing `exchange`/`market`/`code`.**
  These counters are skipped during `mChartTopicIndexMap` building.
  → **Mitigation:** `subscribeForHistory` only subscribes counters where
  `getHistoryChartTopicFormat()` is non-null. Orphan chart topics (received
  from server but not in `mChartTopicIndexMap`) are silently dropped by
  the QUERY collector — matching the legacy `PMPUtilViewModel` semantic.

## Decisions Made (previously Open Questions)

- **`PMPUpdateKind.USSO` is included.** iOS does not have it, but the
  current `NewOrderBottomSheet` uses it. Keeping `USSO` is the safe choice;
  it can be removed in a future cleanup if iOS parity is prioritized.

- **`chartData` is `List<String>` (one list per topic).** Matches the
  legacy `mOnQueryCallback(index, list)` shape where `list: List<String>`
  is `dayClose` values already sub-sampled.

- **`PMPNode.submitSubscribe` is renamed to `submitRequest`.** The old name
  is misleading once it accepts a `requestType` parameter. The call site at
  line 755 is the only internal consumer; `PMPConnectionCenter` calls
  `PMPNode.subscribe()` (public API, unchanged).
