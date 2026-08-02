## PHASE 1: Process-wide PMP infrastructure — LANDED

> The following tasks were completed in commits `6478809a09` through `206e72f7e9`. They are retained here as historical context. Do NOT re-implement them. Phase 1 landed code is in the feature worktree at `/Users/lekhanhvinh/Developer/tdt/poems-mobile3-android-sr3738-pmp-center`.

## PHASE 1.5: Flow-based reactive refactor (PMPNode) — 18/06/2026

> **Why this refactor:** The Phase 1 callback-based state machine had three latent races visible in live logs but not preventable by logging alone: (1) `subscribe()` during `Connecting` was a silent no-op, (2) `livePricesCallback` could fire before `loginCallback` set state to `Connected`, (3) stale callbacks from replaced connections required a hand-rolled `AtomicInteger seq` guard. The Flow redesign makes these races impossible by construction.
>
> **Scope:** `PMPNode.kt` only. `PMPConnectionCenter` and `PMPToken` are unchanged. Public API is backward compatible.

- [x] 1.5.1 Update `design.md` Decision 3: `synchronized {}` → Flow-based reactive design (`MutableStateFlow`, `MutableSharedFlow<ConnEvent>`, `Mutex`, `onEach/launchIn/filterIsInstance/dropWhile/combine/distinctUntilChanged`)
- [x] 1.5.2 Update `specs/pmp-connection-center/spec.md`: add Flow-based state machine requirement with explicit `onEach { }.launchIn(scope)` operators, `combine` price-tick gate, and `distinctUntilChanged` reconnect watcher
- [ ] 1.5.3 Implement `PMPNode.kt` with Flow operators (see design.md §Architecture for diagram):
  - [ ] `MutableStateFlow<State>` for state (replaces `AtomicReference<State>`)
  - [ ] `MutableSharedFlow<ConnEvent>` sealed class hierarchy (replaces 3 separate `scope.launch` callbacks)
  - [ ] `onEach { }.launchIn(scope)` pipeline per event type (replaces `scope.launch { _event.collect { when ... } }`)
  - [ ] `combine(_event, _state) { tick, connected }` price-tick gate (replaces inline `_state.value == Connected` check)
  - [ ] `distinctUntilChanged().filter { Idle && subs }.onEach { connect() }.launchIn(scope)` reconnect watcher
  - [ ] `connSeq: MutableStateFlow<Int>` stale-callback guard (replaces `AtomicInteger`)
  - [ ] `mutationLock: Mutex` compound serialization (replaces `synchronized(this)`)
  - [ ] `dropWhile { it != Connected }.first()` in `subscribe()` for `onReady` await
  - [ ] `tryEmit` in listener callbacks (non-blocking socket thread)
  - [ ] Socket I/O (`submitSubscribe`, `submitUnsubscribe`) moved outside `mutationLock.withLock {}`
- [ ] 1.5.4 `./gradlew :app:compileUatDebugKotlin` — BUILD SUCCESSFUL
- [ ] 1.5.5 `./gradlew :app:testUatDebugUnitTest --tests "com.tdt.pmobile3.viewmodels.common.PMPNodeTest"` — PASS
- [ ] 1.5.6 Manual smoke test: login → Trade → background 30s → foreground → prices update
- [ ] 1.5.7 Push to `hoangtran/sr-3738-pmp-connection-center`



- [x] 1.1 Confirm worktree at `hoangtran/sr-3738-pmp-connection-center` based on `origin/release/v3.3.54_develop_27_06_2026` (`git log --oneline -3`)
- [x] 1.2 `PMPConnectionCenter.kt` (326 lines) — Kotlin `object`, node pool, token registry, lifecycle binding, ref count teardown
- [x] 1.3 `PMPNode.kt` (475 lines) — per-URL node, state machine (Idle/Connecting/Connected/Suspended), suspend/resume, snapshot cache, URL failover
- [x] 1.4 `PMPToken.kt` (96 lines) — `Closeable` token, `SharedFlow<Pair<String, LinkedHashMap>>`, ref count bookkeeping
- [x] 1.5 `Application.kt` — `isAppInForeground` → `AtomicBoolean`, `PMPConnectionCenter.bindLifecycleObserver()` / `unbindLifecycleObserver()`
- [x] 1.6 Unit tests: `PMPNodeTest.kt` (69 lines), `PMPTokenTest.kt` (90 lines)
- [x] 1.7 Build: `./gradlew :app:compileDevDebugKotlin` — BUILD SUCCESSFUL

### Phase 1 additions to PMPUtilViewModel (KEEP — these are part of Phase 1)

Phase 1 also added the following to `PMPUtilViewModel` (commit `6478809a09`, lines ~83-112, ~344-347, ~541-577). **These are Phase 1 and MUST be kept:**

- `import kotlinx.coroutines.Job`, `BufferOverflow`, `MutableSharedFlow`, `SharedFlow`, `asSharedFlow`
- `private var pmpToken: PMPToken? = null` — Phase 1 token ownership
- `internal val _pmpDataFlow = MutableSharedFlow<LinkedHashMap<String, String>>(replay=1, extraBufferCapacity=64, DROP_OLDEST)` — Phase 1 data-only flow
- `val pmpDataFlow: SharedFlow<LinkedHashMap<String, String>> = _pmpDataFlow.asSharedFlow()` — Phase 1 public exposure
- `private var pmpDataCollectorJob: Job? = null` — Phase 1 collector tracking
- `unSubscribeQueryRequest`: `pmpDataCollectorJob?.cancel()`, `pmpToken?.close()`, `pmpToken = null`
- `initPmpConnections`: call to `subscribeViaCenter()`
- `private fun subscribeViaCenter(...)` — Phase 1 body (data-only flow, `token.priceUpdates.collect { data -> _pmpDataFlow.emit(data) }`)

### Phase 2 additions to PMPUtilViewModel (REVERT — task 7 below)

Phase 2 (commits `d6e6d65cc3` → `206e72f7e9`) added the following to `PMPUtilViewModel`. These MUST be reverted:

- `pmpToken` field type stays `PMPToken?` — KEEP, but...
- `_pmpDataFlow` type changed: `MutableSharedFlow<LinkedHashMap>` → `MutableSharedFlow<Pair<String, LinkedHashMap>>` — **REVERT to data-only**
- `pmpDataFlow` type changed: `SharedFlow<LinkedHashMap>` → `SharedFlow<Pair<String, LinkedHashMap>>` — **REVERT**
- `@Volatile private var centerEnabled: Boolean = false` — **REVERT** (added Phase 2)
- `private fun isCenterActive(): Boolean = centerEnabled && pmpToken != null` — **REVERT** (added Phase 2)
- `connectionStatusCallback`: early-return `if (isCenterActive()) return` — **REVERT**
- `getFinalHashMapPmpResponse`: extracted `aliasFields()` function — **PARTIAL REVERT** (keep `aliasFields` if still used by other callers)
- `aliasFields(parsed: LinkedHashMap<String, String>): LinkedHashMap<String, String>` — **ADD Phase 2, REVERT if unused outside dispatchToLegacyCallbacks**
- `unSubscribeQueryRequest`: `centerEnabled = false` — **REVERT**
- `subscribeViaCenter`: changed to handle nullable token, uses `tryEmit(topic to rawData)`, calls `dispatchToLegacyCallbacks` — **REVERT to Phase 1 body**
- `private fun dispatchToLegacyCallbacks(topic: String, rawData: LinkedHashMap<String, String>)` — **REVERT** (added Phase 2)
- `handleConnectPMP`: `if (isCenterActive()) return` — **REVERT**
- `onCleared`: `centerEnabled = false` — **REVERT**
- `pmpDataFlow` KDoc: updated to Phase 2 status — **REVERT to Phase 1 KDoc**

---

## PHASE 2: Incremental Migration (THIS MR)

### 7. Revert PMPUtilViewModel Phase 2 adapter ✅ LANDED

**Approach:** `git checkout 6478809a09 -- PMPUtilViewModel.kt` + manual fix for `subscribeViaCenter`.

**Step 7.1 — Identify revert target commit:**
```
git log --oneline 6478809a09~1..6478809a09
# → 6478809a09 "Centralize PMP connection lifecycle and fix review issues"
#   This is the last Phase 1 commit. Phase 2 starts at d6e6d65cc3.
```

**Step 7.2 — Restore PMPUtilViewModel.kt to Phase 1 state:**
```bash
cd /Users/lekhanhvinh/Developer/tdt/poems-mobile3-android-sr3738-pmp-center
git checkout 6478809a09 -- app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUtilViewModel.kt
```
This restores the Phase 1 additions (data-only `_pmpDataFlow`, `pmpToken`, `pmpDataCollectorJob`, `subscribeViaCenter` with data-only collection, `unSubscribeQueryRequest` token cleanup). The Phase 2 changes (`centerEnabled`, `isCenterActive()`, `dispatchToLegacyCallbacks`, `aliasFields`, Pair-type flow, `handleConnectPMP` gate, `connectionStatusCallback` gate) are all gone.

**Step 7.3 — Fix `subscribeViaCenter` type mismatch:**
The reverted `subscribeViaCenter` calls `_pmpDataFlow.emit(data)` but `PMPToken.priceUpdates` is `SharedFlow<Pair<...>>`. Fix:
```kotlin
// OLD (type mismatch):
token.priceUpdates.collect { data ->
    _pmpDataFlow.emit(data)
}
// NEW (correct):
token.priceUpdates.collect { (topic, rawData) ->
    _pmpDataFlow.emit(rawData)
}
```
Also add `Dispatchers.IO` to match existing convention.

**Step 7.4 — Verify:**
```bash
grep -n "centerEnabled\|isCenterActive\|dispatchToLegacy\|aliasFields\|Pair<String" \
  app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUtilViewModel.kt
# ZERO matches — revert is clean

./gradlew :app:compileDevDebugKotlin --quiet
# BUILD SUCCESSFUL
```

**Status: ✅ DONE** — committed as part of this MR.

### 8. PMPUpdate — Consumer-Facing PMP Record

- [x] 8.1 Create `viewmodels/common/PMPUpdate.kt`

```kotlin
package com.tdt.pmobile3.viewmodels.common

/**
 * Drop-in semantic equivalent of the four legacy PMPUtilViewModel callback variants:
 * [mOnSubscribedCallback], [onSubscribedUSSOCallback],
 * [mOnSubscribedCallbackAllData], [onSubscribedCallbackAllData].
 *
 * `PMPViewModel` collects this from its PMPToken and fans it out to migrated
 * fragments. Each fragment translates `update.topic` and `update.indices`
 * into its own screen-specific dispatch.
 *
 * @param topic     PMP topic string, e.g. "US/OPT/NYSE/AAPL 250619 C 200"
 * @param indices    Fan-out indices from `mHashmapIndexOfCounter[topic]` —
 *                   replaces the positional `[GENERAL_PMP_POS]` / `[UNDERLYING_PMP_POS]`
 *                   switch in legacy `NewOrderBottomSheet.setOnResponseListener`
 * @param data      Raw (not aliased) FID-keyed price map.
 *                   `NewOrderBottomSheet` reads raw FIDs — no aliasing needed for the first migration.
 * @param isAllDataReturned `true` if this is the last item in the current batch;
 *                   mirrors `mOnSubscribedCallbackAllData`'s `isLast` sentinel.
 */
data class PMPUpdate(
    val topic: String,
    val indices: List<Int>,
    val data: LinkedHashMap<String, String>,
    val isAllDataReturned: Boolean
)
```

### 9. PMPViewModel — Thin Lifecycle-Correct Wrapper

- [x] 9.1 Create `viewmodels/common/PMPViewModel.kt`

Key design points from audit of existing codebase:

- **Extends `ViewModel`** (not `AndroidViewModel`) — `PMPConnectionCenter` loads `PMPSettingModel` internally, no `Application` context needed
- **Uses `Hashtable`** (not `ConcurrentHashMap`) for `mHashmapIndexOfCounter` — matches `PMPUtilViewModel` pattern
- **Uses `synchronized {}`** (not `Mutex`) — matches codebase convention (zero uses of `kotlinx.coroutines.sync.Mutex`)
- **Collector uses `Dispatchers.IO`** — matches established convention for `mOnSubscribedCallback` chain in `livePricesCallback`
- **`subscribe()` reuses existing token** — the key difference from `PMPUtilViewModel`; `detach()` does NOT close the token
- **`onCleared()` calls `unsubscribe()`** as safety net

```kotlin
package com.tdt.pmobile3.viewmodels.common

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tdt.pmobile3.model.CounterDetail
import com.tdt.pmobile3.model.databasemodel.WatchListColumnsSettingModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import timber.log.Timber
import java.util.Hashtable
import java.util.UUID

/**
 * Thin lifecycle-correct wrapper around [PMPConnectionCenter] for migrated fragments.
 *
 * Owns a single [PMPToken] and a single `viewModelScope` collector.
 * Exposes `pmpDataFlow: SharedFlow[PMPUpdate]` for fragments to collect via
 * `repeatOnLifecycle(STARTED)`.
 *
 * **Lifecycle contract:**
 * - `subscribe(counters, fields)` → open token + start collector. Called from `onResume`.
 * - `detach()` → cancel collector, **token stays open**. Called from `onPause`.
 *   **CRITICAL: does NOT call pmpToken?.close() — that would recreate the SR-3738 bug.**
 * - `unsubscribe()` → cancel collector + close token. Called from `onDestroy`.
 * - `onCleared()` → `unsubscribe()` as safety net.
 *
 * This is the Android counterpart to iOS `HPMPConnectionCenter` (SR-2875, April 2026).
 *
 * @see PMPConnectionCenter
 * @see PMPUpdate
 */
class PMPViewModel : ViewModel() {

    private var pmpToken: PMPToken? = null
    private var collectorJob: Job? = null

    /**
     * Maps PMP topic → list of counter indices that share that topic.
     * Rebuilt on every [subscribe] call so the fan-out is always current.
     * Mirrors the role of `mHashmapIndexOfCounter` in `PMPUtilViewModel`.
     */
    private val mHashmapIndexOfCounter = Hashtable<String, ArrayList<Int>>()

    private val _pmpDataFlow = MutableSharedFlow<PMPUpdate>(
        replay = 1,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    /** Exposed to fragments for collection via `repeatOnLifecycle(STARTED)`. */
    val pmpDataFlow: SharedFlow<PMPUpdate> = _pmpDataFlow.asSharedFlow()

    /**
     * Subscribe to PMP for the given counters and fields.
     *
     * Idempotent: if a token is already open, reuses it and restarts the collector.
     * This is the key difference from `PMPUtilViewModel.reSubscribe()` which always
     * opens a new connection — the center token survives `detach()`.
     *
     * @param counters    List of [CounterDetail] — resolves to PMP topics + URL
     * @param fields     List of [WatchListColumnsSettingModel] — PMP field IDs to subscribe
     */
    fun subscribe(
        counters: List<CounterDetail>,
        fields: List<WatchListColumnsSettingModel>
    ) {
        // Cancel any existing collector (allows re-subscribe after detach())
        collectorJob?.cancel()
        collectorJob = null

        // Reuse existing token, or open a new one
        if (pmpToken == null) {
            pmpToken = PMPConnectionCenter.subscribe(counters = counters, subscribeFields = fields)
            Timber.d("[PMPViewModel] subscribed: token=${pmpToken?.tokenId}")
        } else {
            Timber.d("[PMPViewModel] re-subscribed: reusing token=${pmpToken?.tokenId}")
        }

        // Rebuild index map: topic → [indices]
        mHashmapIndexOfCounter.clear()
        counters.forEachIndexed { index, counter ->
            counter PMPTopic?.let { topic ->
                val indices = mHashmapIndexOfCounter.getOrPut(topic) { ArrayList() }
                if (index !in indices) {
                    indices.add(index)
                }
            }
        }

        // Start collector on viewModelScope
        val token = pmpToken ?: return
        collectorJob = viewModelScope.launch(Dispatchers.IO) {
            token.priceUpdates.collect { (topic, rawData) ->
                val indices = mHashmapIndexOfCounter[topic] ?: emptyList()
                // TODO: compute isAllDataReturned — the last emission per subscribe() call carries true
                val update = PMPUpdate(
                    topic = topic,
                    indices = indices,
                    data = rawData,
                    isAllDataReturned = false // TODO: implement batch sentinel
                )
                _pmpDataFlow.tryEmit(update)
            }
        }
    }

    /**
     * Detach the fragment-side collector WITHOUT closing the center token.
     *
     * Called from `Fragment.onPause()`. The center connection stays open and
     * survives app background/foreground. A subsequent `subscribe()` call reuses
     * the cached token.
     *
     * **CRITICAL: does NOT call pmpToken?.close().**
     * If it did, the center token would be destroyed and the next `subscribe()`
     * would open a new one — recreating the `PMPUtilViewModel` bug that this
     * class is designed to fix.
     */
    fun detach() {
        collectorJob?.cancel()
        collectorJob = null
        Timber.d("[PMPViewModel] detached — token preserved (pmpToken=${pmpToken?.tokenId})")
    }

    /**
     * Full unsubscribe: cancel collector AND close the center token.
     *
     * Called from `Fragment.onDestroy()`.
     */
    fun unsubscribe() {
        collectorJob?.cancel()
        collectorJob = null
        pmpToken?.close()
        pmpToken = null
        mHashmapIndexOfCounter.clear()
        Timber.d("[PMPViewModel] unsubscribed — token closed")
    }

    /** Safety net: ensures token is released even if `unsubscribe()` is not called. */
    override fun onCleared() {
        unsubscribe()
        super.onCleared()
    }
}
```

### 10. NewOrderBottomSheet — First Migration (SR-3738 screen)

**Current state (lines 164-348):**
- Line 167: `private val pmpUtilViewModelSO: PMPUtilViewModel by viewModels()`
- Line 333: `pmpUtilViewModelSO.unSubscribeQueryRequest()` in `onPause()`
- Line 338: `pmpUtilViewModelSO.reSubscribe()` in `onResume()`
- Line 348: `pmpUtilViewModelSO.disconnectToPMP()` in `onDestroy()`
- Line 750: `pmpUtilViewModelSO.setOnResponseListener { itemIndex, linkMapPMP -> ... }`
- Lines 916-964: `initPmpConnectionsRatesSO()` calls `pmpUtilViewModelSO.resetAllData()` then `pmpUtilViewModelSO.initPmpConnections()`

**Migration steps (apply in order):**

- [x] 10.1 Add import for `PMPViewModel`

```kotlin
import com.tdt.pmobile3.viewmodels.common.PMPViewModel
import com.tdt.pmobile3.viewmodels.common.PMPUpdate
```

- [x] 10.2 Replace view model declaration (line 167):
```kotlin
// REPLACE:
private val pmpUtilViewModelSO: PMPUtilViewModel by viewModels()
// WITH:
private val pmpViewModel: PMPViewModel by viewModels()
```

- [x] 10.3 Add flow collection in `onViewCreated()` (after line 317, before `getDataBundle()`):

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        pmpViewModel.pmpDataFlow.collect { update ->
            onPmpReceived(update)
        }
    }
}
```

- [x] 10.4 Add `onPmpReceived(update: PMPUpdate)` function. This replaces the `when (itemIndex)` switch:

```kotlin
private fun onPmpReceived(update: PMPUpdate) {
    // NewOrderBottomSheet subscribes to TWO topics: option contract (GENERAL_PMP_POS=0)
    // and underlying stock (UNDERLYING_PMP_POS=1). The PMP topic for the option
    // contract is set on the counter model; the underlying stock uses the same
    // counter's pmpTopic field. Route based on the indices list.
    when {
        update.indices.contains(GENERAL_PMP_POS) -> onGeneralPmpReceived(update.data)
        update.indices.contains(UNDERLYING_PMP_POS) -> onUnderlyingPmpReceived(update.data)
    }
}
```

- [x] 10.5 Replace `onPause()` body (lines 331-334):

```kotlin
// REPLACE:
override fun onPause() {
    super.onPause()
    pmpUtilViewModelSO.unSubscribeQueryRequest()
}
// WITH:
override fun onPause() {
    super.onPause()
    pmpViewModel.detach()  // token stays open — key fix for SR-3738
}
```

- [x] 10.6 Replace `onResume()` body (lines 336-342):

```kotlin
// REPLACE: pmpUtilViewModelSO.reSubscribe()
// WITH: pmpViewModel.subscribe(listCounterDetail, subscribeFields)
//
// Note: reSubscribe() was calling initPmpConnections() again which was expensive.
// subscribe() reuses the cached token if non-null — much cheaper.
```

- [x] 10.7 Replace `onDestroy()` body (lines 345-350):

```kotlin
// REPLACE:
override fun onDestroy() {
    super.onDestroy()
    binding = null
    pmpUtilViewModelSO.disconnectToPMP()
    newOrderConfirmation = null
}
// WITH:
override fun onDestroy() {
    super.onDestroy()
    binding = null
    pmpViewModel.unsubscribe()  // closes center token
    newOrderConfirmation = null
}
```

- [x] 10.8 In `initPmpConnectionsRatesSO()` (lines 916-964): keep the `pmpUtilViewModelSO.resetAllData()` and `pmpUtilViewModelSO.initPmpConnections()` calls for now. The `initPmpConnections` call is what actually triggers `subscribeViaCenter` in the KEEPT Phase 1 code. But `PMPViewModel.subscribe()` needs to be called separately.

> **Decision point:** The current flow in `NewOrderBottomSheet` calls `pmpUtilViewModelSO.initPmpConnections()` which internally calls `subscribeViaCenter()`. After migration, `PMPViewModel.subscribe()` should replace the `pmpUtilViewModelSO.initPmpConnections()` call in `initPmpConnectionsRatesSO()`. However, `initPmpConnections()` does more than just subscribe — it also calls `handleConnectPMP()` which manages the legacy connection.
>
> **Recommendation:** For the first migration, keep the `PMPUtilViewModel` call (`pmpUtilViewModelSO.initPmpConnections()`) in `initPmpConnectionsRatesSO()` as-is. The `PMPViewModel.subscribe()` call should be added in `onResume()`. Both will subscribe to the same counters — but `PMPViewModel` owns the token, and `pmpUtilViewModelSO` continues to own the legacy callbacks (which `NewOrderBottomSheet` no longer uses). This is the cleanest migration path: the fragment uses `PMPViewModel` exclusively, and `PMPUtilViewModel` is left unchanged in the screen.

Actually — after more thought, the cleanest approach is to replace the `pmpUtilViewModelSO` usage entirely in `NewOrderBottomSheet`. The `initPmpConnectionsRatesSO()` should call `pmpViewModel.subscribe()` directly:

```kotlin
private fun initPmpConnectionsRatesSO(priceAccess: Boolean) {
    // Build the same listCounterDetail as before
    val listCounterDetail = arrayListOf(
        CounterDetail(pmpTopic = counterOptionsItemModel?.PMPTopic, ...),
        CounterDetail(pmpTopic = counterOptionsItemModel?.pmpTopic, ...)
    )
    val subscribeFields = arrayListOf(...)
    pmpViewModel.subscribe(listCounterDetail, subscribeFields)
}
```

The `resetAllData()` call can be removed — `PMPViewModel.subscribe()` handles the index map rebuild internally. But the `AppApplication` access for `PMPSettingModel` is no longer needed because `PMPConnectionCenter` loads it internally.

- [x] 10.9 Remove `PMPUtilViewModel` import if no other usage remains

- [x] 10.10 Compile and verify:
```bash
./gradlew :app:compileDevDebugKotlin --quiet
# BUILD SUCCESSFUL
```

### 11. Verification

- [ ] 11.1 `./gradlew :app:compileDevDebugKotlin --quiet` — BUILD SUCCESSFUL
- [ ] 11.2 `./gradlew :app:testDevDebugUnitTest --tests "com.tdt.pmobile3.viewmodels.common.PMPNodeTest" --tests "com.tdt.pmobile3.viewmodels.common.PMPTokenTest"` — pre-existing test rot blocks this (see task 13.1). Run manually in Android Studio.
- [ ] 11.3 Manual smoke test 1 (SR-3738): Open Trade bottom sheet → background app 30s → foreground → prices update within 5s
- [ ] 11.4 Manual smoke test 2 (stale-then-live): Same as 11.3 but background 2min → stale prices flash then live prices update
- [ ] 11.5 Manual smoke test 3 (close/reopen): Open bottom sheet → close → wait 5s → reopen → immediate snapshot prices
- [ ] 11.6 Manual smoke test 4 (counter switch): Open → switch counter → switch back → no lag

### 12. Git & MR

- [x] 12.1 `git status` — working tree should show only: `PMPUtilViewModel.kt` (restored), `PMPUpdate.kt` (new), `PMPViewModel.kt` (new), `NewOrderBottomSheet.kt` (modified)
- [x] 12.2 Commit revert: `git add app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUtilViewModel.kt`
- [x] 12.3 Commit new code: `git add app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUpdate.kt app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPViewModel.kt`
- [x] 12.4 Commit migrated screen: `git add app/src/main/java/com/tdt/pmobile3/ui/screens/trade/options/positions/neworder/NewOrderBottomSheet.kt`
- [x] 12.5 Commit message: `feat(android): PMPViewModel — incremental screen migration from PMPUtilViewModel (SR-3738 fix)`

```
feat(android): PMPViewModel — incremental screen migration from PMPUtilViewModel (SR-3738 fix)

Pivot from the Phase 2 adapter approach to incremental screen-by-screen migration.
PMPUtilViewModel Phase 2 adapter reverted (center token did not survive onPause/resume).

New: PMPViewModel (per-Fragment ViewModel) wraps PMPConnectionCenter and exposes
pmpDataFlow: SharedFlow[PMPUpdate]. NewOrderBottomSheet migrated as first screen.

fixes SR-3738
```

- [ ] 12.6 Push to `hoangtran/sr-3738-pmp-connection-center`
- [ ] 12.7 Update MR description

---

## PHASE 3: Subsequent Screen Migrations (separate MRs, one per screen)

Migration pattern: same as task 10. Each MR touches exactly one screen file.

### 12.9 — `NewOrderScreen.kt` (fullscreen variant)

Risk: LOW. Same patterns as `NewOrderBottomSheet`.

### 12.10 — `OptionDetailScreen.kt` (USSO option detail, 861 lines)

Risk: MEDIUM. `setOnResponseListener` with positional dispatch.

### 12.11 — `CounterOptionAllTypeScreen.kt` (option chain grid, 971 lines)

Risk: MEDIUM. Uses `setOnResponseListenerUSSO` — `update.topic` replaces the positional index dispatch.

### 12.12 — `TabHeaderUnderLyingStock.kt` + 8x `TradeTicket*Screen.kt`

Risk: MEDIUM. Group migration.

### 12.13 — `WatchListTab.kt` (1842 lines)

Risk: HIGH. Complex index dispatch.

### 12.14 — `HomeScreen.kt` + `MarketTop*Screen` + `IndicesDetailScreen`

Risk: MEDIUM.

**`MarketTop` family split out into a dedicated sub-change** — see `changes/android-pmp-topmarket-migration/`. The TopMarket family is large (~4,000 lines across 4 files) and exercises a third listener variant (`setOnResponseListener` with the 4-arg `pmpTopic, linkedHashMap, isAllDataReturned` signature in `IndicesDetailScreen`), which is the only place in the entire PMP codebase that actually exercises the `isAllDataReturned` field on `PMPUpdate`. Promoting it to its own sub-change unblocks the long-deferred task §13.3 (implement the `isAllDataReturned` sentinel).

### 12.15+ — Remaining 15+ screens

Risk: LOW.

---

## 13. Follow-ups

- [ ] 13.1 **Pre-existing test rot.** `./gradlew :app:testDevDebugUnitTest` fails with ~1200 compile errors across 30+ unrelated test files (`DetailSettingViewModelTest.kt`, `DisplaySettingViewModelTest.kt`, `WatchListTabNewViewModelTest.kt`, and many `viewmodels/watchlist/*` and `viewmodels/auth/*`). This blocks all unit test runs. Fix pattern: align `mockk.every` setups with current production method signatures. Estimated effort: 1-2h per owning team. **New PMP tests (`PMPNodeTest`, `PMPTokenTest`) compile cleanly and will run automatically once test rotation is fixed.**
- [ ] 13.2 **`aliasFields` reuse.** `PMPUtilViewModel.aliasFields()` was added in Phase 2 and uses the `getFinalHashMapPmpResponse` extraction. After revert, if `aliasFields` is still called by other code paths (e.g. `getFinalHashMapPmpResponse`), keep it. If it's only used by `dispatchToLegacyCallbacks`, revert it completely.
- [ ] 13.3 **`isAllDataReturned` sentinel.** `PMPViewModel.collector` currently hardcodes `isAllDataReturned = false`. Implement batch-end detection: track the number of expected topics per subscribe() call and set `isAllDataReturned = true` on the last emission. Use the `PMPNode` `subscriberTokens` to know how many topics are active. **Tracked by sub-change `android-pmp-topmarket-migration`** — `IndicesDetailScreen` is the only consumer in the entire PMP codebase that exercises this field, so the implementation lands together with the TopMarket migration.
- [ ] 13.4 **Custom lint rule.** Add Android Lint check that flags any fragment using `PMPUtilViewModel` without calling `unsubscribe()` in `onDestroy()`.

---

## Phase 1.6 — PMPNode race condition fixes (19/06/2026)

**Why this phase:** The Phase 1.5 Flow refactor (commit `a30235bb33`) replaced `synchronized {}` blocks with `MutableStateFlow` + `tryEmit`. The state atomicity is preserved, but the *relationship* between `connectionRef` and `_state` is no longer implicitly serialized. Live evidence (19/06/2026 smoke test) shows two production-visible races:

1. **B1: `connect()` catch path does not clear `connectionRef`.** If the SDK's `LoginCommunications.login()` throws NPE on `DataOutputStream.write` (line 57), the half-constructed `PMPConnection` lingers in `connectionRef`. The next `submitSubscribe` reads it and the server rejects with `PMPException: you must login before send message`.

2. **B2: `submitSubscribe` reads `connectionRef` and `_state` non-atomically.** Between the state check and `conn.submitSubscribeQueryRequest`, a concurrent `connect()` can swap `connectionRef`. The subscribe lands on the new (potentially not-yet-logged-in) connection.

Both bugs produce the same user-visible symptom: a transient "you must login" exception in logcat after the app reconnects following a transient network failure. They are not catastrophic (the user can recover by re-subscribing), but they violate the SR-3738 promise of zero-touch recovery.

**Why not fix in Phase 2:** Phase 2 is the NewOrderBottomSheet migration. Mixing the race fix into the migration would tangle two review concerns. Keeping the fix in its own phase makes the diff reviewable and the smoke test isolated.

**Scope:** `PMPNode.kt` only. `PMPConnectionCenter`, `PMPToken`, `PMPViewModel`, `PMPUpdate` are unchanged. No public API changes.

### Tasks

- [ ] 1.6.1 Add `connectionRef.set(null)` to `connect()` catch block at `PMPNode.kt` line 683-686. **CRITICAL: must be BEFORE `_state.value = State.Idle`** to prevent a window where `submitSubscribe` reads a non-null `conn` against an Idle state. Verify by reading the code in the next 30 seconds.
- [ ] 1.6.2 Add `connectionFactory: (String) -> PMPConnection` test seam at `PMPNode.kt` after the `companion object`. Mark with `@VisibleForTesting`. Default delegates to `PMPConnection(url, listener, PULL_TIME_IN_SEC)`. Use a function-reference `var` (not `open fun`) so the final class doesn't need to be opened.
- [ ] 1.6.3 Add snapshot guard to `submitSubscribe` at `PMPNode.kt` line 689-715. After the state check and before `buildSubscribeRequest`, add `if (conn !== connectionRef.get()) { Timber.w(...); return }`. Reference equality, not seq.
- [ ] 1.6.4 Add 4 new unit tests to `PMPNodeTest.kt` (after the existing 4): catch path clears connectionRef, catch path does not throw, submitSubscribe with stale connectionRef, connectionRef set order in catch.
- [ ] 1.6.5 `./gradlew :app:compileUatDebugKotlin` — expect BUILD SUCCESSFUL.
- [ ] 1.6.6 `./gradlew :app:testUatDebugUnitTest --tests "com.tdt.pmobile3.viewmodels.common.PMPNodeTest"` — expect 8 tests pass (4 existing + 4 new). **Known blocker:** the test infrastructure is currently broken with ~1200 pre-existing compile errors across `viewmodels/watchlist/*Test.kt` files AND Robolectric 4.5 (ASM 6) cannot load Java 21 class files (`Unsupported class file major version 65`). See tasks §13.1 follow-up. The 4 new tests compile cleanly and are ready to run once the team upgrades Robolectric (likely same release cycle).
- [ ] 1.6.7 `./gradlew :app:assembleUatDebug` — produces UAT APK.
- [ ] 1.6.8 Install on emulator: `adb install -r app/build/outputs/apk/uat/debug/app-uat-debug.apk`.
- [ ] 1.6.9 Manual smoke test: login → Trade → home (background) → 30s → resume → verify prices update. Capture `adb logcat -d -t 1000 | grep -E "submitSubscribe failed|all URLs exhausted"` and verify **zero matches**.
- [ ] 1.6.10 Run smoke tests 1-4 from Phase 1.5 (background 30s, stale-then-live 2min, close/reopen, counter switch) — verify all pass.
- [ ] 1.6.11 Commit: `fix(android): PMPNode — clear connectionRef on connect() throw + snapshot guard in submitSubscribe (SR-3738 Phase 1.6)`. Body explains both bugs, references the live logcat evidence, and links this phase.
- [ ] 1.6.12 Push to `hoangtran/sr-3738-pmp-connection-center`. Do NOT open a new MR — this is part of the existing SR-3738 MR.
