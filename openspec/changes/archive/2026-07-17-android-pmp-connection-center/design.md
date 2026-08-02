## Context

Android's `PMPUtilViewModel` (985 lines, `viewmodels/common/`) is the current abstraction for PMP real-time price streaming. It is scoped per-Fragment as an `AndroidViewModel`, and each of the 30+ screens that use PMP follows an identical pattern: `onPause()` → `unSubscribeQueryRequest()`, `onResume()` → `reSubscribe()`, `onDestroy()` → `disconnectToPMP()`. This pattern is fragile for two reasons:

1. **Server-side unsubscribe on background**: `unSubscribeQueryRequest()` sends `STREAMING_UNSUBSCRIBE` to the PMP server, which forgets the subscription entirely. On `onResume()`, `reSubscribe()` must re-send `STREAMING_SUBSCRIBE` — but if `mHashMapCounterPmpModel` is empty (e.g., because `resetAllData()` cleared it), nothing happens and prices stay frozen.

2. **`BottomSheetDialogFragment` lifecycle is unreliable**: `onResume()` may not be called when expected — particularly when navigating back to an already-visible sheet (SR-3738).

iOS solved this in April 2026 by shipping `HPMPConnectionCenter` (SR-2875) — a global singleton with URL-pooled nodes, app lifecycle binding, and separated "socket teardown" from "subscription forget." This design mirrors that architecture for Android.

## Goals / Non-Goals

**Goals:**
- Fix SR-3738 by ensuring PMP subscriptions survive app background/foreground regardless of Fragment lifecycle
- Eliminate per-screen PMP lifecycle boilerplate via a centralized, lifecycle-aware singleton
- Provide a reactive `SharedFlow`-based API that replaces the callback-wiring pattern (`setOnResponseListener()`)
- Cache last-known prices in memory and emit them immediately on app foreground (stale-then-live pattern)
- Enable URL connection pooling: multiple screens sharing the same PMP URL reuse one TCP socket
- **Migrate screens incrementally** — leave `PMPUtilViewModel` untouched after Phase 1, create a new thin `PMPViewModel`, migrate one screen at a time, each migration is its own MR

**Non-Goals:**
- Modifying `PMPUtilViewModel` as part of this change (Phase 2 of the original MR was rolled back — see "Pivot to Incremental Migration" below)
- Deleting `PMPUtilViewModel` in this MR (touches 30+ screens; defer to a follow-up after the last consumer migrates)
- Migrating all 30+ Fragment screens in this MR (one screen at a time, ordered by SR-3738 priority)
- Persistent caching across process death (app restart still requires full re-subscription)
- Changes to the `phillip.pmp` third-party library
- iOS-side changes (SR-2875 already shipped)
- Calling `PMPConnection.stop()` in existing code — this method **does not exist** on the `phillip.pmp` library's public API. The library exposes only `login()` and `logout()`. The new design calls `logout()` in `suspendForBackground()`.

## Pivot to Incremental Migration

A second-pass audit of the Phase 1+2 approach (modify `PMPUtilViewModel` to delegate to center internally, with a `dispatchToLegacyCallbacks` adapter for the 30+ existing screens) surfaced four real risks:

### Risk 1 — The center does not survive a normal `onPause`/`onResume` cycle

Every Fragment calls `pmpUtilViewModelSO.unSubscribeQueryRequest()` in `onPause`, which the Phase 2 adapter hooks to also close the center token (`pmpToken?.close()` at `PMPUtilViewModel.kt:389`). When the Fragment resumes, `reSubscribe()` re-subscribes the **legacy** connection but does NOT call `subscribeViaCenter()`. The center token is dead until the next `initPmpConnections()` call.

```
BottomSheet shown    → initPmpConnections()  → CENTER OPENS
BottomSheet onResume → reSubscribe()         → (no center call)        ❌
BottomSheet onPause  → unSubscribeQueryRequest() → pmpToken?.close()   ❌ CENTER CLOSES
BottomSheet onResume → reSubscribe()         → legacy subscribes only, center is dead
```

The bug fix only works for the very first cycle. After the first pause, the user sees the original SR-3738 bug return.

### Risk 2 — Two `PMPConnection` instances per URL run in parallel

The Phase 2 gate (`if (isCenterActive()) return` in `handleConnectPMP` and `connectionStatusCallback`) only suppresses new legacy connection *creation*. The legacy `cachePmpConnection` is still constructed in the first `initPmpConnections()` call (before the gate is set), the legacy `mPMPEventListener` is still attached, and `mHashMapCounterPmpModel` is still populated. `reSubscribe()` calls `handleSubscribePmp` which sends `STREAMING_SUBSCRIBE` to the legacy `activatedPmpConnection` directly (line 467 of the original Phase 2 patch). Result: **two TCP sockets per URL, two subscriptions per topic, double wire traffic**, and the race condition between the two connections for the same PMP URL slot that the comment at lines 84-87 acknowledges.

### Risk 3 — `resetAllData()` causes center token churn

`initPmpConnections()` calls `resetAllData()` at line 551, which calls `unSubscribeQueryRequest()` at line 483, which closes the center token. Then at line 595 `subscribeViaCenter()` opens a new one. Every counter switch on `NewOrderBottomSheet.initPmpConnectionsRatesSO()` (which calls `resetAllData()` then `initPmpConnections()`) does this churn. If the user switches counters rapidly, the center may tear down a node (60-second grace period) only to immediately recreate it.

### Risk 4 — `dispatchToLegacyCallbacks` duplicates `livePricesCallback` line-for-line

The Phase 2 adapter at `PMPUtilViewModel.kt:657-680` is structurally identical to the legacy `livePricesCallback` at lines 142-173. Same `isAutoHandleEmptyResponse` branch, same `mHashmapIndexOfCounter` fan-out, same `onSubscribedUSSOCallback` invocation, same `mOnSubscribedCallbackAllData` call. Any future fix to the dispatch logic must be applied to both — a known source of drift.

### Decision: revert Phase 2 of `PMPUtilViewModel`, ship a new `PMPViewModel` instead

`PMPUtilViewModel` is a 980-line god class with 30+ consumers, 5 listener variants, and a per-Fragment lifecycle contract. Modifying it for a global lifecycle-correct behavior is the wrong granularity. The right move is:

1. **Revert** `PMPUtilViewModel` to its Phase 1 state. Restore from git commit `6478809a09` ("Centralize PMP connection lifecycle and fix review issues") — the last commit before Phase 2 started (`d6e6d65cc3`). This removes `centerEnabled`, `isCenterActive()`, `dispatchToLegacyCallbacks`, `aliasFields`, the `Pair`-type flow change, the `handleConnectPMP` gate, and the `connectionStatusCallback` gate. The Phase 1 additions (`pmpToken`, `_pmpDataFlow`, `pmpDataCollectorJob`, `subscribeViaCenter` with data-only collection) are kept — they are correct for Phase 2.
2. **Create** a new `PMPViewModel` (~150 lines) that wraps `PMPConnectionCenter` directly. Exposes `pmpDataFlow: SharedFlow<PMPUpdate>` for fragments to collect via `repeatOnLifecycle(STARTED) { collect }`. Owns a single `PMPToken` and a single `viewModelScope` collector. Cancels everything in `onCleared()`.
3. **Migrate** `NewOrderBottomSheet` (the SR-3738 screen) first. The bottom sheet is the test case that proves the new pattern works end-to-end. Other 29+ screens keep using `PMPUtilViewModel` unchanged.
4. **Migrate** additional screens in follow-up MRs, one at a time. Each migration is independent, fully reviewable, and reversible.

## Decisions

### Decision 1: Kotlin `object` singleton over `Application`-scoped bean

**Chosen:** Kotlin `object` (process singleton via top-level `object`).

**Rationale:** The existing `PmpConnectionPool` in `PMPUtilViewModel.kt` is already a top-level `object`. A new `PMPConnectionCenter` follows the same pattern — simpler than introducing a custom `Application.onCreate()` registration. `ProcessLifecycleOwner.get().lifecycle.addObserver()` is called directly in the `object`'s init block. The singleton initializes lazily on first access.

**Alternative considered:** Register as a bean in `Application` via Hilt/Dagger. Rejected — `PMPConnectionCenter` is a pure in-process component with no Android framework dependencies; an `object` is idiomatic Kotlin and requires zero DI wiring.

### Decision 2: `SharedFlow<Pair<String, LinkedHashMap<String, String>>>` over `StateFlow<Map<String, String>>`

**Chosen:** `SharedFlow` with `replay = 1` for price updates.

**Rationale:** PMP price data is a stream of discrete events, not a persistent state. `SharedFlow` is the correct abstraction for "fire-and-forget" event streams. `replay = 1` ensures new collectors (e.g., after Fragment recreation) immediately receive the last cached snapshot. The `LinkedHashMap` preserves field ordering which existing UI adapters depend on. `extraBufferCapacity = 64` handles bursty updates without dropping.

The pair shape `(topic, data)` is required so the consumer can route each emission to the correct counter index. This is consumed by `PMPViewModel` (new) which fans it out into a `PMPUpdate` record (see Decision 5).

**Existing pattern confirmation:** `WatchListTabViewModel.kt` uses `MutableSharedFlow<Pair<String, Boolean>>` with `asSharedFlow()` — exactly the same pattern established in the codebase. `CounterOptionAllTypeScreen` uses `ConcurrentHashMap<String, LinkedHashMap<String, String>>` for buffering PMP data, confirming the per-topic map pattern.

### Decision 3: Flow-based reactive state machine with `Mutex`

**Chosen:** `MutableStateFlow<State>` for atomic state, `MutableSharedFlow<ConnEvent>` for the event channel, `kotlinx.coroutines.sync.Mutex` for compound mutation serialization, and Flow operators (`onEach`, `launchIn`, `filterIsInstance`, `dropWhile`, `combine`, `distinctUntilChanged`) for the state machine.

**Rationale:** The original decision used `synchronized {}` blocks — a Java intrinsic that works for simple reads/writes but requires careful lock-ordering for compound sequences. PMPNode's mutations are compound: "decrement ref count, remove entry, maybe send unsubscribe, maybe schedule teardown." The original design required `synchronized(this)` around the entire block.

The Flow-based redesign eliminates compound mutation complexity by:

1. **Single `MutableSharedFlow<ConnEvent>`** as the event channel: three independent PMP callbacks (status, login, price) are converted to sealed `ConnEvent` subclasses and funneled into one flow. This guarantees event ordering — the price-tick actor and the login handler always process events in the order they were emitted.

2. **`MutableStateFlow<State>`** replaces the `AtomicReference<State>`: state transitions are atomic by construction. No `synchronized {}` needed around `_state.value = Connected`.

3. **`kotlinx.coroutines.sync.Mutex`** replaces `synchronized {}` for compound sequences. `Mutex.withLock {}` is a suspend function, so it can be called from coroutines holding the lock across a `delay()` (e.g., the teardown timer awaiting the lock). `synchronized {}` cannot be held across suspend points — using it inside a `suspend fun` that might suspend creates a deadlock risk. The teardown coroutine in the original design was carefully placed outside `synchronized {}` blocks to avoid this; `Mutex.withLock {}` makes this impossible to get wrong.

4. **`onEach { }.launchIn(scope)`** replaces `scope.launch { collect { } }` — a declarative style where the Flow pipeline is composed, not imperative. The state machine's three actors (login handler, price-tick gate, reconnect watcher) are declared as independent pipelines with no shared mutable state between them.

5. **`filterIsInstance<ConnEvent.LoginResult>()`** replaces `when (event)` dispatch — the type system routes each event to the correct handler at the Flow level.

6. **The price-tick gate uses a Flow `combine`** between `_state` and `_event` — the tick actor only fires when `state == Connected`, enforced by the Flow operator itself rather than a runtime check:

```kotlin
_event
    .filterIsInstance<ConnEvent.PriceTick>()
    .combine(_state) { tick, state -> tick to (state == State.Connected) }
    .filter { (_, isConnected) -> isConnected }
    .onEach { (tick, _) -> handlePriceTick(tick) }
    .launchIn(scope)
```

**Important note on `synchronized {}` in `PMPConnectionCenter`:** This decision applies only to `PMPNode`. `PMPConnectionCenter` uses `ConcurrentHashMap` for its node pool and token registry — dictionary operations are atomic, and compound sequences (subscribe → node.subscribe → token.open) use separate `synchronized {}` blocks. `PMPConnectionCenter` is not changed in this Flow refactor; it still uses the original `synchronized {}` design, which is correct for its simpler use case.

**Migration path:** The Flow refactor is backward compatible. `PMPConnectionCenter` is unchanged; `PMPNode` now uses Flow internally. The public API (`subscribe`, `unsubscribe`, `suspendForBackground`, `resumeAfterForeground`, `stopConnection`) has the same signatures. `PMPToken` is unchanged.

### Decision 4: `ConcurrentHashMap` for node pool and token registry

**Chosen:** `ConcurrentHashMap<String, PMPNode>` and `ConcurrentHashMap<UUID, WeakReference<PMPToken>>`.

**Rationale:** `ConcurrentHashMap` is already used in this codebase (`SessionManager.kt`, `CounterOptionAllTypeScreen.kt` for pending PMP data). It is the natural choice for concurrent read/write maps. The alternative `synchronized {}` + `HashMap` would work but `ConcurrentHashMap` is more idiomatic for concurrent access patterns.

### Decision 5: New `PMPViewModel` exposes `SharedFlow<PMPUpdate>` for incremental migration

**Chosen:** A new `PMPViewModel` wraps `PMPConnectionCenter` and exposes `pmpDataFlow: SharedFlow<PMPUpdate>` to fragments. Fragments collect via `repeatOnLifecycle(STARTED) { collect }`.

**`PMPUpdate` shape:**

```kotlin
data class PMPUpdate(
    val topic: String,
    val indices: List<Int>,     // list of counter indices that share this topic
    val data: LinkedHashMap<String, String>,  // raw (not aliased) field map
    val isAllDataReturned: Boolean  // mirrors mOnSubscribedCallbackAllData's isLast flag
)
```

**Rationale for the `indices` and `isAllDataReturned` fields:**

The legacy `livePricesCallback` dispatches to `mHashmapIndexOfCounter[topic]?.forEach { index -> mOnSubscribedCallback?.invoke(index, it) }` — it fans one topic out to multiple consumer indices. `mOnSubscribedCallbackAllData` also takes an `isAllDataReturned: Boolean` flag (`indexPmp == this.lastIndex` in the legacy code). To preserve the legacy callback contract without forcing each migrated screen to rebuild the index map itself, the `PMPViewModel` collector enriches each pair from the center into a `PMPUpdate` with both the indices and the is-last flag. The migrated fragment then translates `pmpDataFlow.collect { u -> ... }` into the same per-index dispatch the legacy `mOnSubscribedCallback?.invoke(index, it)` was doing.

**Why not just expose the raw pair:**

A new consumer of `PMPConnectionCenter.priceUpdates` would have to:
1. Look up `mHashmapIndexOfCounter[topic]` itself (the data isn't in the pair)
2. Track batch-end conditions itself (the data isn't in the pair)
3. Re-implement `aliasFields` if the consumer needs human-readable field names

The `PMPViewModel` collapses all three into the `PMPUpdate` shape, so each migrated fragment only handles the screen-specific dispatch logic.

**`aliasFields` belongs in `PMPViewModel` (or the consumer), not in the center:**

Field aliasing depends on per-screen state (`mListColumnPmpEnum`, `mIsUseDefaultFidID`) that varies across consumers. The center stays screen-agnostic. The `PMPViewModel` exposes raw data; migrated fragments either (a) use the raw FID-keyed map directly, or (b) call a shared `PMPFieldAlias` helper. For the first migration (`NewOrderBottomSheet`), the screen reads raw FIDs already — no aliasing is needed.

### Decision 6: Per-Fragment `ViewModel` scoped, not `Activity` scoped

**Chosen:** Each migrated fragment uses `by viewModels<PMPViewModel>()` — the same scoping as `PMPUtilViewModel` today.

**Rationale:** A `PMPViewModel` instance lives as long as the host Fragment. The `PMPToken` it owns lives as long as the `ViewModel` does (cancelled in `onCleared()`). This matches the user expectation: when the bottom sheet is dismissed and the Fragment is destroyed, the PMP subscription for that sheet's counters is released.

**Important:** The underlying `PMPConnection` is **process-scoped** via `PMPConnectionCenter` — when the Fragment's `PMPViewModel` is destroyed, the token closes, ref counts decrement, and the node may teardown after 60s. But the node's `topicSnapshots` survive, so a re-subscribe (e.g., user reopens the bottom sheet) sees the last known price immediately. The center is the long-lived owner; `PMPViewModel` is the short-lived owner; this is the correct layering.

### Decision 7: `PMPViewModel` is a `ViewModel`, not an `AndroidViewModel`

**Chosen:** `PMPViewModel` extends `androidx.lifecycle.ViewModel` (not `AndroidViewModel`).

**Rationale:** `PMPUtilViewModel` extends `AndroidViewModel` because it needs `Application` context to access `BuildDaoDatabase.getPmpSettingsDao(getApplication())`. `PMPViewModel` does NOT need `Application` context — `PMPConnectionCenter` already loads `PMPSettingModel` internally. A plain `ViewModel` is simpler, easier to test (no Robolectric needed for the VM under test), and matches the pattern in `WatchListTabViewModel`, `CashDividendViewModel`, `UpcomingViewModel`, and 30+ other VMs in the codebase.

**Where the counters/fields come from in the migrated fragment:**

```kotlin
// NewOrderBottomSheet — migrated to PMPViewModel
class NewOrderBottomSheet : BottomSheetDialogFragment() {
    private val pmpViewModel: PMPViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Collect PMP updates — collection is automatic on STARTED, cancelled on STOPPED
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                pmpViewModel.pmpDataFlow.collect { update -> onPmpUpdate(update) }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        // Subscribe with the current counter + fields (same call site as before, just the receiver is different)
        pmpViewModel.subscribe(counters, subscribeFields)
    }

    override fun onPause() {
        super.onPause()
        // Detach: PMPViewModel no longer re-broadcasts. Center token STAYS OPEN
        // (this is the key difference from PMPUtilViewModel — see Risk 1).
        pmpViewModel.detach()
    }

    override fun onDestroy() {
        super.onDestroy()
        // Full unsubscribe + close the PMPToken. Triggers ref count decrement.
        pmpViewModel.unsubscribe()
    }
}
```

**Lifecycle semantics for `PMPViewModel.subscribe / detach / unsubscribe`:**

| Method | Called from | Effect on token | Effect on center connection |
|--------|-------------|------------------|------------------------------|
| `subscribe(counters, fields)` | `onResume` | Opens token (or reuses cached one) | Opens / reuses `PMPNode` |
| `detach()` | `onPause` | Detaches the `viewModelScope` collector; **token stays open** | Connection stays open |
| `unsubscribe()` | `onDestroy` | Closes the token | Ref counts decrement; node may teardown after 60s |
| (none — automatic) | `onCleared` (VM destroy) | Closes the token (safety net) | Ref counts decrement |

**Why `detach()` is the key fix for Risk 1:**

`detach()` detaches the fragment-side `viewModelScope` collector (so the fragment doesn't update when invisible) but does NOT close the center token. When `onResume` calls `subscribe()` again, the cached token is reused and a fresh `viewModelScope` collector attaches. The center connection survives all `onPause`/`onResume` cycles within the Fragment's lifetime — which is exactly what SR-3738 needs.

### Decision 8: URL pooling with per-URL `PMPNode` instances

**Chosen:** One `PMPNode` per unique PMP URL, keyed in `ConcurrentHashMap<String, PMPNode>`.

**Rationale:** Matches iOS architecture exactly (`nodes: [String: HPMPConnectionNode]`). The PMP library allows multiple subscriptions on a single `PMPConnection`; multiplexing by URL maximizes socket reuse. URLs are loaded from `PMPSettingModel` (fetched from `GET global/settings/pmp` API, cached in Room DB), with up to 4 URLs per product-market combination (primary, primaryDelayed, alternative, alternativeDelayed).

**Relationship to existing `PmpConnectionPool`:** The new `PMPConnectionCenter.nodes` map supersedes `PmpConnectionPool.mListActivePmpConnection` (which only tracks URLs as strings). `PmpConnectionPool` is left in place for backward compatibility until all consumers migrate.

### Decision 9: 60-second `connectionTeardownDelay`

**Chosen:** After the last token closes, a node schedules a 60-second timer before calling `connection.logout()`.

**Rationale:** Based on iOS SR-2875 implementation. Realistic user behavior includes quick tab switches. A 60-second window covers the common case. The timer is cancellable — if a new subscription arrives, the timer is cleared and the node is reused.

### Decision 10: `PMPConnection.logout()` is the only teardown method

**Chosen:** `suspendForBackground()` calls `connection?.logout()` (NOT `connection?.stop()`).

**Rationale:** The `phillip.pmp` library exposes only `login()` and `logout()`; there is no `stop()` on the library's public API. The original design proposed `stop()` with `logout()` fallback, but `stop()` does not exist. `logout()` sends a logout message to the server and may wait for acknowledgment — this is acceptable for backgrounding (we are dropping the socket anyway). The `Connecting → Idle` carve-out handles the case where the in-flight `loginCallback` is still pending.

### Decision 11: `AtomicBoolean` for `isAppInForeground`

**Chosen:** The existing `isAppInForeground: Boolean` in `Application.kt` is not thread-safe. Use `AtomicBoolean` instead.

**Rationale:** `isAppInForeground` is read from PMP callback threads (unknown thread from library) and written from the main thread (ProcessLifecycleOwner). Without synchronization, this is a race condition. `AtomicBoolean.compareAndSet()` provides safe read/write without `synchronized {}` overhead.

**Scope:** This is a fix to the existing `Application.kt` code, not part of `PMPConnectionCenter` per se, but is done in the same MR.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 PMPConnectionCenter  (Kotlin object)              │
│  nodes: ConcurrentHashMap<String, PMPNode>                       │
│  activeTokens: ConcurrentHashMap<UUID, WeakReference<PMPToken>>  │
│  nodeTeardownJobs: ConcurrentHashMap<String, Job>                │
│  nodeIdleCancellables: MutableMap<String, Cancellable>           │
│  config: Config                                                  │
│                                                                  │
│  + ProcessLifecycleOwner observer (ON_START / ON_STOP)           │
│                                                                  │
│  subscribe(counters, fields, callback): PMPToken                  │
│  unsubscribe(token)                                              │
│  disconnectAll()  ← called on logout                            │
│  onAppForeground()  ← from ProcessLifecycleOwner                │
│  onAppBackground()  ← from ProcessLifecycleOwner                │
└──────────────────────────────┬──────────────────────────────────┘
                               │ owns
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  PMPNode  (one per unique PMP URL, pooled)                      │
│                                                                  │
│  ## Flow-based state machine (refactored 18/06/2026)            │
│                                                                  │
│  MutableStateFlow<State> — atomic state: Idle/Connecting/      │
│    Connected/Suspended. Transitions driven by Flow operators.    │
│                                                                  │
│  MutableSharedFlow<ConnEvent> — single event channel from       │
│    three PMP callbacks (status/login/price) funneled into one  │
│    ordered stream of sealed ConnEvent subclasses.               │
│                                                                  │
│  ┌──────────────────── Event pipeline ──────────────────────┐   │
│  │                                                      │   │
│  │  PMPConnection listener callbacks                     │   │
│  │    loginCallback ──→ ConnEvent.LoginResult           │   │
│  │    connectionStatusCallback ──→ ConnEvent.StatusChanged │   │
│  │    livePricesCallback ──→ ConnEvent.PriceTick         │   │
│  │         │                                          │   │
│  │         ▼ _event.tryEmit()                         │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │         MutableSharedFlow<ConnEvent>         │   │   │
│  │  │   (replay=0, buffer=128, DROP_OLDEST)       │   │   │
│  │  └──────┬────────────────┬────────────────┬─────┘   │   │
│  │         │                │                │          │   │
│  │    filterIsInstance  filterIsInstance  filterIsInstance │
│  │         │                │                │          │   │
│  │         ▼                ▼                ▼          │   │
│  │  ┌──────────┐   ┌──────────────────┐  ┌───────────┐ │   │
│  │  │ LoginResult│  │  StatusChanged   │  │ PriceTick │ │   │
│  │  │  actor    │  │    actor        │  │  actor    │ │   │
│  │  │ onEach{ } │  │   onEach{ }     │  │  onEach{ }│ │   │
│  │  │.launchIn │  │  .launchIn      │  │ .launchIn │ │   │
│  │  │  (scope) │  │    (scope)      │  │  (scope)  │ │   │
│  │  └──────┬───┘  └───────┬────────┘  └─────┬─────┘ │   │
│  │         │               │                  │        │   │
│  │         ▼               ▼                  ▼        │   │
│  │  _state.value  _state.value          _state.value  │   │
│  │  = Connected   (info only)         (gate check)   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────── State pipeline ───────────────────────────┐   │
│  │                                                           │   │
│  │  _state: MutableStateFlow<State>                        │   │
│  │     │                                                    │   │
│  │     ├──→ .distinctUntilChanged()                        │   │
│  │     │    ├──→ filter { Idle && hasActiveSubs }          │   │
│  │     │    │    └──→ onEach { connect() } .launchIn(scope) │   │
│  │     │    └──→ (state exposed to public API)             │   │
│  │     │                                                    │   │
│  │     └──→ .filter { Connected }                          │   │
│  │          └──→ onEach { <wake pending onReady callbacks> }│   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
│  connSeq: MutableStateFlow<Int> — stale callback guard         │
│    (increment on connect, event.seq == connSeq.value check)     │
│                                                                  │
│  mutationLock: Mutex — serializes compound mutations             │
│    (subscribe/unsubscribe teardown) via withLock { }            │
│                                                                  │
│  topicRefCounts: ConcurrentHashMap<String, AtomicInteger>      │
│  topicFieldUnion: ConcurrentHashMap<String, MutableSet<String>> │
│  topicSnapshots: ConcurrentHashMap<String, LinkedHashMap>      │
│  currentUrlIndex: AtomicInteger                                  │
│  subscriberTokens: ConcurrentHashMap<UUID, TokenSubscription>    │
│                                                                  │
│  subscribe(subscriberId, topics, fields)                         │
│  unsubscribe(subscriberId, topics, fields)                       │
│  suspendForBackground()  ← connection.logout(), state = Suspended │
│  resumeAfterForeground()  ← reconnect, login, resubscribe       │
└──────────────────────────────┬──────────────────────────────────┘
                               │ emits via PMPEventListener callbacks
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  PMPToken  (Closeable, per screen subscription)                  │
│  tokenId: UUID                                                  │
│  topics: List<String>                                           │
│  fields: Set<String>                                            │
│  topicsByResolvedURL: Map<String, List<String>>                  │
│  priceUpdates: SharedFlow<Pair<String, LinkedHashMap>>           │
│    (replay=1, extraBufferCapacity=64, onBufferOverflow=DROP_OLDEST)│
│  center: PMPConnectionCenter                                     │
│                                                                  │
│  close() ← decrement ref counts, remove from activeTokens         │
└──────────────────────────────┬──────────────────────────────────┘
                               │ collected by
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  PMPViewModel  (NEW — per Fragment)                              │
│  pmpToken: PMPToken?  ← owned, not borrowed                    │
│  collectorJob: Job?  ← viewModelScope.launch { token.collect }  │
│  pmpDataFlow: SharedFlow<PMPUpdate>                             │
│    (replay=1, extraBufferCapacity=64, DROP_OLDEST)              │
│                                                                  │
│  subscribe(counters, fields)  ← opens token, starts collector    │
│  detach()  ← cancels collector, token STAYS OPEN                │
│  unsubscribe()  ← cancels collector, closes token               │
│  onCleared()  ← unsubscribe() safety net                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │ collected by
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Fragment / BottomSheet (e.g. NewOrderBottomSheet)               │
│  viewLifecycleOwner.lifecycleScope.launch {                     │
│    viewLifecycleOwner.repeatOnLifecycle(STARTED) {              │
│      pmpViewModel.pmpDataFlow.collect { update ->               │
│        when (update.topic) { ... }  ← screen-specific dispatch    │
│      }                                                           │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```
│  nodes: ConcurrentHashMap<String, PMPNode>                       │
│  activeTokens: ConcurrentHashMap<UUID, WeakReference<PMPToken>>  │
│  nodeTeardownJobs: ConcurrentHashMap<String, Job>                │
│  nodeIdleCancellables: MutableMap<String, Cancellable>          │
│  config: Config                                                  │
│                                                                 │
│  + ProcessLifecycleOwner observer (ON_START / ON_STOP)           │
│                                                                 │
│  subscribe(counters, fields, callback): PMPToken                  │
│  unsubscribe(token)                                              │
│  disconnectAll()  ← called on logout                            │
│  onAppForeground()  ← from ProcessLifecycleOwner                │
│  onAppBackground()  ← from ProcessLifecycleOwner                │
└──────────────────────────────┬──────────────────────────────────┘
                                │ owns
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  PMPNode  (one per unique PMP URL, pooled)                      │
│  state: NodeState (Idle | Connecting | Connected | Suspended)      │
│  connection: PMPConnection?  ← from phillip.pmp library          │
│  topicRefCounts: MutableMap<String, Int>  ← survives bg         │
│  topicFieldUnion: MutableMap<String, Set<String>>  ← survives bg │
│  topicSnapshots: MutableMap<String, LinkedHashMap>  ← survives   │
│  currentUrlIndex: Int = 0                                        │
│  alternativeUrls: List<String>                                   │
│  subscriberTokens: MutableMap<UUID, TokenSubscription>             │
│                                                                 │
│  subscribe(subscriberId, topics, fields)                         │
│  unsubscribe(subscriberId, topics, fields)                       │
│  suspendForBackground()  ← connection.logout(), state = Suspended │
│  resumeAfterForeground()  ← reconnect, login, resubscribe       │
└──────────────────────────────┬──────────────────────────────────┘
                               │ emits via PMPEventListener callbacks
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  PMPToken  (Closeable, per screen subscription)                  │
│  tokenId: UUID                                                  │
│  topics: List<String>                                           │
│  fields: Set<String>                                            │
│  topicsByResolvedURL: Map<String, List<String>>                  │
│  priceUpdates: SharedFlow<Pair<String, LinkedHashMap>>           │
│    (replay=1, extraBufferCapacity=64, onBufferOverflow=DROP_OLDEST)│
│  center: PMPConnectionCenter                                     │
│                                                                 │
│  close() ← decrement ref counts, remove from activeTokens         │
└──────────────────────────────┬──────────────────────────────────┘
                               │ collected by
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  PMPViewModel  (NEW — per Fragment)                              │
│  pmpToken: PMPToken?  ← owned, not borrowed                      │
│  collectorJob: Job?  ← viewModelScope.launch { token.collect }  │
│  pmpDataFlow: SharedFlow<PMPUpdate>                             │
│    (replay=1, extraBufferCapacity=64, DROP_OLDEST)              │
│                                                                 │
│  subscribe(counters, fields)  ← opens token, starts collector    │
│  detach()  ← cancels collector, token STAYS OPEN                │
│  unsubscribe()  ← cancels collector, closes token               │
│  onCleared()  ← unsubscribe() safety net                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │ collected by
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Fragment / BottomSheet (e.g. NewOrderBottomSheet)               │
│  viewLifecycleOwner.lifecycleScope.launch {                     │
│    viewLifecycleOwner.repeatOnLifecycle(STARTED) {              │
│      pmpViewModel.pmpDataFlow.collect { update ->               │
│        when (update.topic) { ... }  ← screen-specific dispatch    │
│      }                                                           │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

**`PMPUpdate` data class:**

```kotlin
data class PMPUpdate(
    val topic: String,                          // PMP topic string
    val indices: List<Int>,                     // fan-out indices from mHashmapIndexOfCounter[topic]
    val data: LinkedHashMap<String, String>,    // raw (not aliased) field map
    val isAllDataReturned: Boolean              // true if this is the last item in the batch
)
```

## Data Flow

### Subscribe (migrated fragment)

```
Fragment.onResume()
  → pmpViewModel.subscribe(counters, fields)
    → PMPConnectionCenter.subscribe(counters, fields)
      → resolve URL per counter via PMPSettingModel (from Room DB cache)
      → getOrCreateNode(url) → PMPNode
      → PMPNode.subscribe(tokenId, topics, fields)
        → increment topicRefCounts per topic
        → add TokenSubscription to subscriberTokens
        → if node.state == Idle: node.connect()
          → PMPConnection(url, listener, PULL_TIME_IN_SEC=0)
          → connection.setConnectionTimeout(5000)
          → connection.login("test", "1111")
      → PMPToken returned (stored in pmpViewModel.pmpToken)
      → PMPEventListener.livePricesCallback() fires (on library thread)
        → PMPNode.updateSnapshot(topic, data)
        → for each TokenSubscription: token.priceUpdates.tryEmit(topic to data)
          → PMPViewModel collector receives (topic, data)
            → resolve mHashmapIndexOfCounter[topic] → indices
            → _pmpDataFlow.tryEmit(PMPUpdate(topic, indices, data, isLast))
              → Fragment collects via repeatOnLifecycle(STARTED)
                → onPmpReceived(update) → screen-specific dispatch
```

### Fragment pause (migrated fragment — the key fix for Risk 1)

```
Fragment.onPause()
  → pmpViewModel.detach()
    → collectorJob.cancel()  ← fragment-side collector stops
    → pmpToken STAYS OPEN   ← center connection is NOT torn down
                              ref counts unchanged
```

The center connection survives the fragment pause. On app background, the center suspends the node; on app foreground, the center resumes and emits snapshots. The fragment's `onPause` does not affect either lifecycle.

### App Background

```
ProcessLifecycleOwner.ON_STOP
  → PMPConnectionCenter.onAppBackground()
    → for each PMPNode (synchronized(nodes)):
        → suspendForBackground()
          → cancelConnectionTeardown()
          → TokenSubscription entries preserved (subscriberTokens map unchanged)
          → connection?.logout()
          → connection = null
          → state = Suspended (or Idle if Connecting)
          → topicRefCounts KEPT
          → topicFieldUnion KEPT
          → topicSnapshots KEPT
    → remove nodes with no active subscriptions (sweep)
```

### App Foreground

```
ProcessLifecycleOwner.ON_START
  → PMPConnectionCenter.onAppForeground()
    → for each PMPNode with active subscriptions (synchronized(nodes)):
        → resumeAfterForeground()
          → if state != Suspended: skip
          → currentUrlIndex = 0
          → connection = PMPConnection(primaryUrl, listener, 0)
          → connection.setConnectionTimeout(5000)
          → connection.login("test", "1111")
          → for each (subscriberId, topics, fields): connection.submitSubscribeQueryRequest()
          → for each (topic, snapshot): emit to all subscriber tokens (stale prices first)
          → state = Connected
    → live prices follow via PMPEventListener callback
```

### SR-3738 — Trade bottom sheet lifecycle

```
User opens NewOrderBottomSheet
  → onViewCreated: viewLifecycleOwner.repeatOnLifecycle(STARTED) { pmpViewModel.pmpDataFlow.collect { ... } }
  → onResume: pmpViewModel.subscribe(counters, fields)  ← center token opens
  → onPause:  pmpViewModel.detach()                      ← fragment collector stops, token STAYS OPEN

User backgrounds app
  → ProcessLifecycleOwner.ON_STOP → PMPConnectionCenter.onAppBackground()
  → Node suspends (logout, state=Suspended, topicSnapshots preserved)
  → NewOrderBottomSheet.onPause runs → pmpViewModel.detach() (no-op for center)

User foregrounds app
  → ProcessLifecycleOwner.ON_START → PMPConnectionCenter.onAppForeground()
  → Node resumes (reconnect, login, resubscribe, emit topicSnapshots)
  → PMPToken.priceUpdates emits (topic, snapshot) for each cached topic
  → PMPViewModel collector receives (even if fragment is not yet STARTED — the
    collectorJob was cancelled by detach, so these emissions are lost.
    THIS IS BY DESIGN — fragment will START again, will resubscribe, will receive
    the latest snapshot via replay=1.)
  → NewOrderBottomSheet.onStart → onResume
  → pmpViewModel.subscribe(counters, fields)  ← reuses cached token (or opens new if center teardown was triggered)
  → Fragment collector reattaches
  → First emission is the latest snapshot (replay=1) → onPmpReceived → UI updates
  → Subsequent live pushes → UI updates

User navigates away from bottom sheet
  → onDestroy: pmpViewModel.unsubscribe()
    → collectorJob.cancel()
    → pmpToken.close()  ← center ref counts decrement
    → if last token: node schedules 60s teardown
```

### USSO-Specific Note

`NewOrderBottomSheet` subscribes to **two topics**: the option contract (index 0, `GENERAL_PMP_POS`) and the underlying stock (index 1, `UNDERLYING_PMP_POS`). Both use the **regular positional callback** (`setOnResponseListener { itemIndex, hashMap }`), NOT the USSO-specific TPC callback (`setOnResponseListenerUSSO`). The TPC callback is used only by `CounterOptionAllTypeScreen` (option chain grid).

In the migrated `NewOrderBottomSheet`, the `PMPUpdate.topic` is used to dispatch — the migrated screen keeps a `Map<String, (LinkedHashMap) -> Unit>` (one entry per topic) instead of a `when (itemIndex)` switch. This is actually cleaner than the original.

Greeks (delta, gamma, vega, theta, rho) are computed **100% client-side** via `USSOUtils.calDGVBS()` (Black-Scholes) — never via PMP. The PMP stream only delivers bid/ask/lastDone prices. When bid or ask price changes, `updateDeltaIVGamma()` recalculates Greeks.

### REST First, PMP Then

All screens using PMP follow a two-phase pattern:
1. **REST API** loads initial data (snapshot) with pre-computed Greeks (server-side when available)
2. **PMP stream** delivers live bid/ask updates; if bid/ask changes, Greeks are recalculated client-side

On app foreground, snapshot replay means the UI shows the last known bid/ask from the snapshot cache, then updates to live prices as they arrive.

## File Map

| File | Action | Description |
|------|--------|-------------|
| `viewmodels/common/PMPConnectionCenter.kt` | **Landed** | Singleton object: node pool, lifecycle binding, token registry |
| `viewmodels/common/PMPToken.kt` | **Landed** | Closeable token: SharedFlow<Pair>, ref count bookkeeping |
| `viewmodels/common/PMPNode.kt` | **Landed** | Per-URL node: state machine, suspend/resume, snapshot cache |
| `viewmodels/common/PMPUpdate.kt` | **New (this MR)** | `data class PMPUpdate(topic, indices, data, isAllDataReturned)` — the consumer-facing record |
| `viewmodels/common/PMPViewModel.kt` | **New (this MR)** | Per-Fragment ViewModel: owns PMPToken, exposes `pmpDataFlow: SharedFlow<PMPUpdate>` |
| `viewmodels/common/PMPUtilViewModel.kt` | **Revert (this MR)** | Restore pre-MR state (drop `subscribeViaCenter`, `dispatchToLegacyCallbacks`, `pmpDataFlow`, `pmpToken`, `pmpDataCollectorJob`, `centerEnabled` gate, `aliasFields` extraction) |
| `Application.kt` | **Landed** | Fix `isAppInForeground` to `AtomicBoolean`; register center with ProcessLifecycleOwner |
| `ui/screens/trade/options/positions/neworder/NewOrderBottomSheet.kt` | **Modify (this MR)** | Replace `PMPUtilViewModel.setOnResponseListener` with `PMPViewModel.pmpDataFlow` + `repeatOnLifecycle(STARTED)` |
| `ui/screens/trade/options/positions/neworder/NewOrderScreen.kt` | **No change** | Stays on `PMPUtilViewModel` — migration deferred to a follow-up MR |
| `pmpmodule/PMPEventListener.kt` | **No change** | Unchanged |
| `config/Config.kt` | **No change** | `PMP_USER_NAME`, `PMP_PASS_WORD`, `PMP_CONNECTION_TIMEOUT` constants already exist |

## Risks / Trade-offs

- **[Risk] `PMPConnection.stop()` does not exist on `phillip.pmp`**: The library has only `login()` and `logout()`. The original design proposed `stop()` with `logout()` fallback, but `stop()` is not on the public API. → **Mitigation**: Use `logout()` directly. The `Connecting → Idle` carve-out handles in-flight login callbacks.

- **[Risk] Token leak if `close()` not called**: Callers MUST call `pmpViewModel.unsubscribe()` in `onDestroy()`. If forgotten, the token leaks in `activeTokens` until the node's teardown timer fires. → **Mitigation**: `PMPViewModel.onCleared()` calls `unsubscribe()` as a safety net. Document the contract clearly in code. Add a custom lint rule in a follow-up.

- **[Risk] `isAppInForeground` race condition**: The existing `Boolean` in `Application.kt` is read/written from multiple threads. → **Mitigation**: Change to `AtomicBoolean` (landed with Phase 1).

- **[Risk] Duplicate subscription on same topic**: If two tokens both subscribe to the same topic on the same node, the PMP server sends data twice. → **Mitigation**: `topicRefCounts` handles deduplication at the application level. Server-side subscription is keyed by `subscriberID` (UUID per token), so multiple app-level subscriptions to the same topic on the same URL should not cause duplicate server messages.

- **[Risk] `detach()` semantics differ from `unSubscribeQueryRequest()`**: `PMPUtilViewModel.unSubscribeQueryRequest()` closes the center token (causing the Phase 2 Risk 1). `PMPViewModel.detach()` keeps the token open. → **Mitigation**: Document the difference clearly in the KDoc on both methods. The fragment lifecycle wiring (`onPause → detach`, `onDestroy → unsubscribe`) is the canonical pattern. Add a comment in `PMPViewModel` warning against calling `unsubscribe()` from `onPause`.

- **[Risk] Fragment collector receives emissions while token is suspended**: If the fragment collector is active while the app is backgrounded, the suspended node will not emit. → **Mitigation**: The fragment is also paused when the app is backgrounded (`onPause` is called as part of the background sequence), so the fragment collector is cancelled by `detach()` before the node suspends. The token itself does not need to track "is the app in foreground" — the center does that.

- **[Risk] `mHashmapIndexOfCounter` rebuild must be clean**: `PMPUtilViewModel`'s `mHashmapIndexOfCounter` (used in the Phase 2 adapter that is being reverted) accumulated duplicate indices on re-subscribe because it was never cleared before rebuilding — `initPmpConnections` called `resetAllData()` which cleared the model but not the index map, and `updateListIndices` kept appending. `PMPViewModel` avoids this by clearing `mHashmapIndexOfCounter` before each `subscribe()` call rebuilds it. → **Mitigation**: `PMPViewModel.subscribe()` calls `mHashmapIndexOfCounter.clear()` before rebuilding. The fragment scope guarantees only one active collector at a time, so concurrent rebuilds are not a concern.

## Migration Plan

### Phase 1: Process-wide PMP infrastructure (landed)

1. Create `PMPNode.kt`, `PMPToken.kt`, `PMPConnectionCenter.kt`
2. Fix `isAppInForeground` to `AtomicBoolean` in `Application.kt`
3. Register center with ProcessLifecycleOwner in `Application.kt`
4. Verify `PMPUtilViewModel` builds with the new center available (no behavior change to it yet)

> Phase 1 of the original MR also added the `PMPUtilViewModel` adapter (Phase 2 below). That adapter is being **reverted** in this MR (Phase 2 incremental). After revert, the only consumer of `PMPConnectionCenter` in production code is the new `PMPViewModel`.

### Phase 2: New `PMPViewModel` + first migration (this MR)

1. Revert `PMPUtilViewModel` Phase 2 adapter (drop `centerEnabled`, `isCenterActive()`, `dispatchToLegacyCallbacks`, `aliasFields`, the `Pair`-type flow change, `handleConnectPMP` gate, `connectionStatusCallback` gate). Restore from git commit `6478809a09` — the last Phase 1 commit. Phase 2 adapter was added in `d6e6d65cc3`.
2. Create `viewmodels/common/PMPUpdate.kt` — `data class PMPUpdate(topic, indices, data, isAllDataReturned)`
3. Create `viewmodels/common/PMPViewModel.kt` — `ViewModel` with `subscribe / detach / unsubscribe` and `pmpDataFlow: SharedFlow<PMPUpdate>`
4. Migrate `NewOrderBottomSheet` to use `PMPViewModel`:
   - Replace `private val pmpUtilViewModelSO: PMPUtilViewModel by viewModels()` with `private val pmpViewModel: PMPViewModel by viewModels()`
   - Replace `setPmpListener()` (callback registration) with `viewLifecycleOwner.lifecycleScope.launch { viewLifecycleOwner.repeatOnLifecycle(STARTED) { pmpViewModel.pmpDataFlow.collect { update -> onPmpReceived(update) } } }`
   - Replace `setOnResponseListener` callback body with `onPmpReceived(update: PMPUpdate)` — the function dispatches based on `update.topic` and iterates `update.indices`
   - Replace `pmpUtilViewModelSO.unSubscribeQueryRequest()` in `onPause` with `pmpViewModel.detach()`
   - Replace `pmpUtilViewModelSO.reSubscribe()` in `onResume` with `pmpViewModel.subscribe(counters, fields)`
   - Replace `pmpUtilViewModelSO.disconnectToPMP()` in `onDestroy` with `pmpViewModel.unsubscribe()`
5. Run unit tests and lint
6. Manual smoke test: open Trade bottom sheet → background 30s → foreground → prices update within 5s (proves the center survives the fragment pause — the key fix for SR-3738)
7. Manual smoke test: open Trade bottom sheet → switch counter → switch back → prices update without lag (proves the center handles counter switches via resetAllData + re-subscribe)
8. Target branch: `release/v3.3.54_develop_27_06_2026`

### Phase 3: Migrate high-priority screens (separate MRs, one screen per MR)

In rough priority order (each MR is small, self-contained, fully reviewable):

1. `NewOrderScreen` (fullscreen variant of the bottom sheet)
2. `OptionDetailScreen` (USSO option detail — `setOnResponseListener` consumer)
3. `CounterOptionAllTypeScreen` (option chain grid — `setOnResponseListenerUSSO` consumer)
4. `TabHeaderUnderLyingStock` (small View, `setOnResponseListener` consumer)
5. `BaseTradeTicket` + `TradeTicket{CFD,FX,SG,HK,Fund,Futures}Screen` (8 files, all `setOnResponseListener` consumers with similar lifecycle)
6. `WatchListTab` (high-volume consumer with `setOnResponseListenerWithTopicIndex` + `setOnQueryCallback`)
7. `HomeScreen` (large file, 1797 lines, multiple consumers)
8. `MarketTopDetailBaseScreen` + `MarketTopBaseFragment` + `IndicesDetailScreen`
9. `CounterDetailScreen` + `CounterDetailScreenST` + `CounterOptionAllTypeScreen`
10. The remaining 15+ watchlist sub-screens (MarketDepth, TimeAndSale, TradeSummary, KeyStats, etc.)

Each migration is its own MR with its own OpenSpec change or sub-task. The pattern is identical to Phase 2: replace `PMPUtilViewModel` with `PMPViewModel`, replace callback registration with `repeatOnLifecycle(STARTED)`, replace per-Fragment lifecycle methods with `subscribe / detach / unsubscribe`.

### Phase 4: Delete `PMPUtilViewModel` and `PmpConnectionPool` (future, after all migrations)

1. Verify no screens still use `PMPUtilViewModel`
2. Delete `PMPUtilViewModel.kt` and `PmpConnectionPool`
3. Verify no screens still use `PmpConnectionPool.mListActivePmpConnection`
4. Delete `PmpConnectionPool` (or rename to `PMPConnectionCenter.PmpConnectionPool` if it lives on the center)

## Open Questions

1. **Should `aliasFields` move to a shared helper or stay duplicated?** Currently the legacy `PMPUtilViewModel` has `aliasFields()` and migrated screens either (a) read raw FIDs directly, or (b) duplicate the aliasing. For the first migration (`NewOrderBottomSheet`), raw FIDs work — no aliasing needed. For `WatchListTab` and `HomeScreen`, the column names are human-readable and aliasing is needed. **Recommendation:** create `PMPFieldAlias` helper when the second migration needs it.

2. **Snapshot eviction policy**: If a user subscribes to 500 counters and backgrounds for a long time, `topicSnapshots` holds 500 entries (~100KB). Is this acceptable? Recommendation: yes for now.

3. **`connectionTeardownDelay` configuration**: Should this be a compile-time constant or runtime config? Recommendation: compile-time constant `CONNECTION_TEARDOWN_DELAY_MS = 60_000L` matching iOS.

4. **`distinctUntilChanged` on snapshot replay**: Should the SharedFlow suppress snapshot emissions that are identical to the next live value? Recommendation: defer to Phase 3 when we have more UX data.

5. **Custom lint rule for `PMPToken.close()`**: Should we add a custom Android Lint check that flags any `PMPViewModel` field in a Fragment without a matching `unsubscribe()` call in `onDestroy`? **Recommendation:** yes, but defer to a follow-up MR. The current `onCleared()` safety net is sufficient for the first migration.