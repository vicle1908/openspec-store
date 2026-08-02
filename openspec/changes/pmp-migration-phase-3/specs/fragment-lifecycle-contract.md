# Spec: Fragment lifecycle contract (SPEC-PMP-FRAGMENT-001)

**Status:** Draft
**Related change:** `pmp-migration-phase-3`

## Purpose

Define the canonical fragment lifecycle for migrated screens, replacing
the legacy `PMPUtilViewModel` callback-wiring pattern with the new
`PMPViewModel.pmpDataFlow` collection pattern.

## SPEC-PMP-FRAGMENT-001 — Migrated fragment lifecycle

### 1.1 Lifecycle contract (MUST)

Every migrated fragment MUST implement this lifecycle:

```
onResume()         →  initPmpConnections()        (LIVE + QUERY)
onPause()          →  pmpViewModel.detach()        (cancel collectors, preserve tokens)
onDestroyView()    →  pmpViewModel.unsubscribe()   (cancel collectors, close tokens)
```

### 1.2 Prohibited patterns (MUST NOT)

A migrated fragment MUST NOT call any of the following methods on the
`PMPViewModel` (they don't exist or are wrong):

- `disconnectToPMP()` — does not exist on `PMPViewModel`.
- `resetAllData()` — does not exist on `PMPViewModel`.
- `unSubscribeQueryRequest()` — does not exist on `PMPViewModel`.
- `reSubscribe()` — does not exist on `PMPViewModel`.

A migrated fragment MUST NOT call any of the following on the legacy
`PMPUtilViewModel` (it would conflict with the new path):

- `disconnectToPMP()`, `resetAllData()`, `unSubscribeQueryRequest()`,
  `reSubscribe()`, `setOnResponseListener`, `setOnResponseListenerUSSO`,
  `setOnResponseListenerWithTopicIndex`, `setOnQueryCallback`.

If a fragment has a feature flag that toggles between the legacy
`PMPUtilViewModel` path and the new `PMPViewModel` path, only ONE
path runs at a time. Both paths MUST NOT be active simultaneously.

### 1.3 `onResume` lifecycle (MUST)

```kotlin
override fun onResume() {
    super.onResume()
    // ... other onResume logic ...
    initPmpConnections()        // subscribes LIVE if not already
    initPmpHistoryConnections() // subscribes QUERY if not already (for chart screens)
}
```

The `onResume` MUST call both `initPmpConnections()` and
`initPmpHistoryConnections()` (the latter only for screens that need
chart data, e.g., `WatchListTab`).

The fragment MUST NOT do any PMP setup that bypasses
`PMPViewModel.subscribe()` / `subscribeForHistory()`. The center is the
only owner of PMP state; the fragment only initiates subscriptions
through the ViewModel.

### 1.4 `onPause` lifecycle (MUST)

```kotlin
override fun onPause() {
    pmpViewModel.detach()   // cancel both collectors, preserve both tokens
    // ... other onPause logic ...
    super.onPause()
}
```

The `pmpViewModel.detach()` call MUST be the first thing in `onPause`
(before any other PMP-related cleanup). This ensures the center stops
emitting to the fragment immediately when the fragment is no longer
visible.

The fragment MUST NOT call `disconnectToPMP()`, `resetAllData()`,
`logout()`, or any method that destroys the token.

**Exception (only for fragments with feature flag and dual-path support):**
When the feature flag is OFF, the fragment may call the legacy
`PMPUtilViewModel.disconnectToPMP()` and `resetAllData()`. When the
flag is ON, the fragment calls only `pmpViewModel.detach()`.

### 1.5 `onDestroyView` lifecycle (MUST)

```kotlin
override fun onDestroyView() {
    pmpViewModel.unsubscribe()  // cancel both collectors, close both tokens
    // ... other onDestroyView logic ...
    super.onDestroyView()
}
```

The `pmpViewModel.unsubscribe()` call MUST be the first thing in
`onDestroyView`. This ensures the tokens are closed and the center's
ref-counts decrement. If ref-count reaches zero on a node, the 60s
teardown timer starts.

### 1.6 `pmpDataFlow` collection (MUST)

The fragment MUST collect `pmpDataFlow` inside `repeatOnLifecycle(STARTED)`:

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        pmpViewModel.pmpDataFlow.collect { update ->
            when (update.kind) {
                PMPUpdateKind.LIVE -> handleLive(update)
                PMPUpdateKind.QUERY -> handleQuery(update)
                PMPUpdateKind.USSO -> handleUsso(update)
            }
        }
    }
}
```

This MUST be set up in `onViewCreated` (after `super.onViewCreated`) and
MUST be cancelled automatically by `repeatOnLifecycle(STARTED)` when
the fragment is no longer `STARTED`. The collection does not need to be
manually cancelled in `onPause` or `onDestroyView` — `repeatOnLifecycle`
handles it.

### 1.7 `kind` dispatch (MUST)

The fragment MUST dispatch on `update.kind` before accessing
`update.data` or `update.chartData`. The compiler enforces
nullability via the `init {}` invariants in `PMPUpdate` (see
`pmp-update-contract.md`):

- `kind == LIVE  → data != null && chartData == null`
- `kind == QUERY → data == null && chartData != null`
- `kind == USSO  → data != null && chartData == null`

### 1.8 `initPmpConnections()` pattern (MUST)

```kotlin
private fun initPmpConnections() {
    if (pmpViewModel.pmpToken != null) return  // idempotent
    val counters = buildCounterList()
    val fields = getFinalColumnsPmp()
    if (counters.isNotEmpty() && fields.isNotEmpty()) {
        pmpViewModel.subscribe(counters, fields)
    }
}
```

The early return on `pmpViewModel.pmpToken != null` is the idempotency
guard. If a previous `onResume` already subscribed, the token survives
the `onPause → detach` cycle, and this `onResume` is a no-op.

### 1.9 `initPmpHistoryConnections()` pattern (MUST, for chart screens)

```kotlin
private fun initPmpHistoryConnections() {
    if (pmpViewModel.pmpQueryToken != null) return  // idempotent
    val counters = buildCounterList()
    val fields = getFinalColumnsPmp()  // or a different field set for chart
    if (counters.isNotEmpty() && fields.isNotEmpty()) {
        pmpViewModel.subscribeForHistory(counters, fields)
    }
}
```

The early return on `pmpViewModel.pmpQueryToken != null` is the
idempotency guard for the QUERY token.

### 1.10 `handleLive(update: PMPUpdate)` (MUST)

The fragment MUST iterate `update.indices` to fan out the update to
every counter sharing the topic:

```kotlin
private fun handleLive(update: PMPUpdate) {
    if (update.kind != PMPUpdateKind.LIVE) return  // safety check
    val data = update.data ?: return  // compiler should prevent this, but safety
    update.indices.forEach { idx ->
        // screen-specific dispatch using idx and data
        // (e.g., updateListWithPMP(idx, data))
    }
}
```

**The fan-out is critical.** The legacy
`setOnResponseListenerWithTopicIndex` called the callback once per
(topic, index) pair. The new `pmpDataFlow` emits one `PMPUpdate` per
topic, and the fragment MUST iterate `update.indices` to replicate the
legacy behavior.

### 1.11 `handleQuery(update: PMPUpdate)` (MUST, for chart screens)

```kotlin
private fun handleQuery(update: PMPUpdate) {
    if (update.kind != PMPUpdateKind.QUERY) return  // safety check
    val chart = update.chartData ?: return
    // screen-specific dispatch using update.topic and chart
    // (e.g., drawSparkline(counterIndex, chart))
}
```

The chart data is a `List<String>` of `dayClose` values. The fragment
MUST look up the counter index from `update.topic` (using
`mChartTopicIndexMap` in `WatchListTab`, or a similar screen-specific
mapping).

### 1.12 `handleUsso(update: PMPUpdate)` (MUST, for USSO screens)

`USSO` is the kind used by `NewOrderBottomSheet`. The legacy code calls
`mOnSubscribedCallback(index, hashMapPMP)` with positional indices
(GENERAL_PMP_POS = 0, UNDERLYING_PMP_POS = 1). The new code uses
`update.indices.firstOrNull()` (or iterates) to get the index, and
`update.data` is the raw FID-keyed map.

```kotlin
private fun handleUsso(update: PMPUpdate) {
    if (update.kind != PMPUpdateKind.USSO) return  // safety check
    val data = update.data ?: return
    val index = update.indices.firstOrNull() ?: return
    when (index) {
        GENERAL_PMP_POS -> updateGreeks(data)
        UNDERLYING_PMP_POS -> updateUnderlying(data)
    }
}
```

## Acceptance criteria

### Per-fragment manual QA (MUST pass for each migrated screen)

For every migrated fragment, the following MUST be verified:

1. **Open screen → data appears within 3s.**
   - LIVE: prices tick within 3s.
   - QUERY (chart screens): sparkline renders within 3s.

2. **Switch away (background) → wait 10s → return → data resumes within 1s.**
   - The center survives the fragment pause; on resume, the token is
     reused and the collector reattaches.
   - No re-login, no re-subscribe (token survives).

3. **Pull-to-refresh → connection survives.**
   - The new `subscribe()` call on resume re-emits the index map without
     destroying the token.
   - The center has 1 node alive (per URL), not 1 per refresh.

4. **Navigate through 3 sub-screens → connection count stays bounded.**
   - The center's `nodes` map has at most N entries, where N is the
     number of unique URL pools (live + historical), not 1 per screen.

5. **Fragment destroy → tokens closed.**
   - `pmpViewModel.pmpToken` is `null` after `onDestroyView()`.
   - `pmpViewModel.pmpQueryToken` is `null` if it was open.
   - The center's `activeTokens` map does not contain the destroyed
     token's `tokenId` (verified via `gitnexus_impact` or runtime log).

6. **Chart data matches legacy semantic (chart screens).**
   - The sparkline's `dayClose` values are identical to the legacy
     `setOnQueryCallback` data (same order, same values).
   - Verified by visual comparison during side-by-side QA.

7. **Live fan-out matches legacy semantic.**
   - For each topic shared by N counters, every counter's UI is updated
     N times (once per emission × one emission per topic).
   - The legacy `setOnResponseListenerWithTopicIndex` did the same.

### Automated tests (MUST pass)

1. **`PMPViewModel.detach()` preserves both tokens.**
2. **`PMPViewModel.unsubscribe()` closes both tokens.**
3. **`PMPUpdate` invariant assertions** (covered in `pmp-update-contract.md`).
4. **`PMPQueryToken.close()` decrements the historical node's ref-count.**

## Migration impact on existing code

### P0 — `HomeScreen.kt`

- Replace `mWatchListPMPUtilViewModel.disconnectToPMP()` and
  `resetAllData()` calls with `pmpViewModel.detach()` in `onPause`.
- Remove all other disconnect/reset calls (lines 357, 469, 1123, 1556).
- Add `FEATURE_PMP_CENTER_HOME` build flag check in `initPmpUtilObserve()`.
- When flag is OFF, the legacy `mWatchListPMPUtilViewModel` path runs.
- When flag is ON, the new `pmpViewModel` path runs.

### P0 — `WatchListTab.kt`

- Add `FEATURE_PMP_CENTER_WATCHLIST` build flag check.
- Replace `setOnResponseListenerWithTopicIndex { ... }` (line 572) with
  `handleLive(update)` in the `pmpDataFlow` collector.
- Replace `setOnQueryCallback { ... }` (line 587) with
  `handleQuery(update)` in the collector.
- Replace `mWatchListPMPUtilViewModel.reSubscribe(getFinalColumnsPMP())`
  (lines 727, 759) with `pmpViewModel.subscribe(counters, fields)`.
- Replace `mWatchListPMPUtilViewModel.updatePMPTopics(...)` and
  `updatePMPTopicsByPage(...)` with `pmpViewModel.subscribe(counters, fields)`.
- Remove `mIsFirstInitPmpConnection` state; replace `isInitializedPmpConn()`
  with `pmpViewModel.pmpToken != null`.
- Remove `resetPMPPositionCheck()` in `onPause`.

### P1 — 4 files

- `CounterDetailScreen.kt` — remove `resetAllData()` from `loadData()`;
  add `pmpViewModel.detach()` in `onPause`, `unsubscribe()` in
  `onDestroyView()`.
- `OptionDetailScreen.kt` — same pattern, plus remove `resetAllData()`
  in `initPmpConnectionsRatesSO()`.
- `MarketDepthTab.kt` — remove `repeatOnLifecycle(RESUMED)` wrapper
  around init; use `onResume` lifecycle.
- `TradeSummaryTab.kt` — same as `MarketDepthTab`.

### P2 — 6 files

- Standard template, all 6 files.
- `CounterPriceDetailHeader.kt` is missing `onPause` entirely; add
  `pmpViewModel.detach()` in `onPause`.

### P3 — 2 files

- Standard template.
- `TopPriceDetailCounter.kt` is a base class; changes propagate to
  `TopPriceDetailCounterST.kt`.
