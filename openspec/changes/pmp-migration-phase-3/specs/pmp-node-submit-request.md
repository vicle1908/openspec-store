# Spec: PMPNode.submitRequest (SPEC-PMP-NODE-001)

**Status:** Draft
**Related change:** `pmp-migration-phase-3`
**Related files:** `app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPNode.kt`

## Purpose

Generalize `PMPNode.submitSubscribe` to `PMPNode.submitRequest` so it can
handle `STREAMING_SUBSCRIBE`, `STREAMING_UNSUBSCRIBE`, and `STREAMING_QUERY`
request types. The internal `buildSubscribeRequest()` (line 790) already
accepts a `requestType` parameter; only the call sites at lines 370 and 623
need lifting.

The public `PMPNode.subscribe()` API also gets a new `requestType` parameter
with default `STREAMING_SUBSCRIBE`, so existing callers are unchanged.
`PMPConnectionCenter.subscribeForHistory()` calls `subscribe()` with
`requestType = STREAMING_QUERY`.

## SPEC-PMP-NODE-001 — submitRequest contract

### 1.1 Private method signature (MUST)

```kotlin
// Before
private fun submitSubscribe(topics: List<String>, fieldMap: Map<String, MutableSet<String>>)

// After
private fun submitRequest(
    topics: List<String>,
    fieldMap: Map<String, MutableSet<String>>,
    requestType: PMPRequestType,
)
```

The `requestType` parameter MUST be one of:
- `PMPRequestType.STREAMING_SUBSCRIBE` (value = 1)
- `PMPRequestType.STREAMING_UNSUBSCRIBE` (value = 2)
- `PMPRequestType.STREAMING_QUERY` (value = 3)

### 1.2 Public `subscribe()` signature (MUST)

```kotlin
// Before
fun subscribe(
    subscriberId: UUID,
    topics: List<String>,
    fields: List<WatchListColumnsSettingModel>,
    onSnapshot: (String, LinkedHashMap<String, String>) -> Unit,
    onReady: (() -> Unit)? = null,
)

// After
fun subscribe(
    subscriberId: UUID,
    topics: List<String>,
    fields: List<WatchListColumnsSettingModel>,
    onSnapshot: (String, LinkedHashMap<String, String>) -> Unit,
    onReady: (() -> Unit)? = null,
    requestType: PMPRequestType = PMPRequestType.STREAMING_SUBSCRIBE,
)
```

The `requestType` parameter has a default value, so existing callers
(`PMPConnectionCenter.subscribe()`) are unchanged. The new
`PMPConnectionCenter.subscribeForHistory()` passes
`requestType = PMPRequestType.STREAMING_QUERY`.

**Note on `onSnapshot` signature for QUERY:** The callback signature is
`(String, LinkedHashMap<String, String>) -> Unit` for SUBSCRIBE. For
QUERY, the second parameter is a `List<String>` (chart points), not a
`LinkedHashMap`. This is handled by having a separate
`PMPConnectionCenter.subscribeForHistory()` that wraps the `PMPNode`
internally with a type-correct callback. The `PMPNode` public API stays
generic; the `LinkedHashMap` in `onSnapshot` is interpreted as a
type-erased container for both cases.

**Wait — this is a type-safety problem.** The `onSnapshot` callback
expects `LinkedHashMap`, but QUERY data is `List<String>`. We need a
cleaner abstraction.

**Resolution (Option C — REVISED):** Add a separate public method on
`PMPNode` for QUERY subscriptions with a type-correct callback:

```kotlin
// LIVE / SUBSCRIBE — existing, unchanged
fun subscribe(
    subscriberId: UUID,
    topics: List<String>,
    fields: List<WatchListColumnsSettingModel>,
    onSnapshot: (String, LinkedHashMap<String, String>) -> Unit,
    onReady: (() -> Unit)? = null,
)

// QUERY — NEW, this MR
fun subscribeForHistory(
    subscriberId: UUID,
    topics: List<String>,
    fields: List<WatchListColumnsSettingModel>,
    onChart: (String, List<String>) -> Unit,  // type-safe
    onReady: (() -> Unit)? = null,
)
```

`subscribeForHistory` shares the same internals (topic registration,
ref-count, login state) as `subscribe`, but uses `submitRequest(..., QUERY)`
internally and routes the response to `onChart` instead of `onSnapshot`.

This is a cleaner design — type safety is preserved, no boxing or
type erasure.

### 1.3 Behavior by request type (MUST)

**`STREAMING_SUBSCRIBE`:** Send a subscribe request to the PMP server. The
node increments `topicRefCounts` for each topic (existing behavior). Live
price ticks follow via the `PMPEventListener.livePricesCallback` and are
emitted through the `onSnapshot` callback.

**`STREAMING_UNSUBSCRIBE`:** Send an unsubscribe request. The node
decrements `topicRefCounts` for each topic. No more live ticks for these
topics.

**`STREAMING_QUERY`:** Send a one-shot query for historical chart data.
The node does NOT affect `topicRefCounts` for live subscriptions (the
ref-count is on the historical URL node, which is a separate node). The
server responds with a one-shot `QueryReturnBean` which is parsed into a
`List<String>` of `dayClose` values and emitted through the `onChart`
callback.

### 1.4 Connection state checks (MUST, existing behavior preserved)

The existing connection state checks at lines 730-751 of `PMPNode.kt`
MUST be applied to `submitRequest` for ALL three request types:

```kotlin
private fun submitRequest(
    topics: List<String>,
    fieldMap: Map<String, MutableSet<String>>,
    requestType: PMPRequestType,
) {
    val conn = connectionRef.get() ?: run {
        Timber.w("[PMPNode] submitRequest skipped: no connectionRef [$primaryUrl] type=$requestType")
        return
    }
    if (_state.value != State.Connected) {
        Timber.w(
            "[PMPNode] submitRequest skipped: state=${_state.value} " +
                "(not Connected) [$primaryUrl] type=$requestType"
        )
        return
    }
    // Snapshot guard against connectionRef swap (existing comment at line 737)
    if (conn !== connectionRef.get()) {
        Timber.w(
            "[PMPNode] submitRequest skipped: connectionRef swapped " +
                "after state check [$primaryUrl] type=$requestType"
        )
        return
    }
    val request = buildSubscribeRequest(topics, fieldMap, requestType)
    try {
        conn.submitSubscribeQueryRequest(request)
        Timber.d(
            "[PMPNode] submitRequest: sent topics=${topics.size} " +
                "type=$requestType [$primaryUrl]"
        )
    } catch (e: Throwable) {
        Timber.e(e, "[PMPNode] submitRequest failed [$primaryUrl]")
    }
}
```

### 1.5 `submitUnsubscribe` (MUST, unchanged)

`submitUnsubscribe(topics)` MUST remain a separate method. It is called
by `PMPConnectionCenter.unsubscribe()` to stop ticks for a topic. It is
NOT a variant of `submitRequest`; it has different semantics (decrement
ref-counts, not send an unsubscribe message to the server).

```kotlin
private fun submitUnsubscribe(topics: List<String>) {
    // Existing implementation at line 768 — UNCHANGED
}
```

### 1.6 Ref-count semantics (MUST be preserved)

- `submitRequest(STREAMING_SUBSCRIBE)` MUST increment `topicRefCounts` per topic.
- `submitRequest(STREAMING_UNSUBSCRIBE)` MUST NOT decrement `topicRefCounts`
  (unsubscribe is a wire-level operation, not a ref-count operation).
- `submitRequest(STREAMING_QUERY)` MUST NOT affect `topicRefCounts` for
  the live URL pool. The ref-count is on the historical URL node, which
  is a different `PMPNode` instance.

### 1.7 Thread safety (MUST, existing behavior preserved)

`submitRequest` is called from `PMPNode.subscribe()` and
`PMPNode.subscribeForHistory()` (both `scope.launch` blocks on
`Dispatchers.IO`). The existing `connectionRef.get()` and `_state.value`
checks are atomic. No new synchronization is required.

## Acceptance criteria

### Unit tests (MUST pass)

1. `PMPNodeTest.submitRequest SUBSCRIBE`:
   - Sends a request with `requestType = 1` to the PMP connection mock.
   - Increments `topicRefCounts` for each topic.

2. `PMPNodeTest.submitRequest UNSUBSCRIBE`:
   - Sends a request with `requestType = 2` to the PMP connection mock.

3. `PMPNodeTest.submitRequest QUERY`:
   - Sends a request with `requestType = 3` to the PMP connection mock.
   - Does NOT modify `topicRefCounts` for the live URL pool.

4. `PMPNodeTest.submitRequest state guard`:
   - When `_state != Connected`, `submitRequest` is a no-op (logged warning).
   - When `connectionRef` is null, `submitRequest` is a no-op.
   - When `connectionRef` has been swapped, `submitRequest` is a no-op.

5. `PMPNodeTest.subscribe existing call sites unchanged`:
   - Existing call sites of `PMPNode.subscribe()` (1 site: `PMPConnectionCenter.subscribe`)
     compile and pass tests with the new default `requestType = SUBSCRIBE`.
   - `PMPNodeTest.subscribeForHistory`:
     - Calls `submitRequest(..., STREAMING_QUERY)`.
     - Routes server response to `onChart` callback, not `onSnapshot`.

### Manual QA (MUST pass)

1. The 4 already-migrated screens (`MarketTopBaseFragment`,
   `MarketTopDetailBaseScreen`, `TabMarketStockScreen`, `NewOrderBottomSheet`)
   still work after the rename (they go through `PMPConnectionCenter` →
   `subscribe()` → `PMPNode.subscribe()`).
2. No regressions in the live price stream for any migrated screen.
3. A new unit test exercises `PMPNode.subscribeForHistory` with a mock
   PMP connection; the mock verifies `submitSubscribeQueryRequest` is
   called with `requestType = 3`.

## Migration impact on existing code

### Internal call sites (MUST update)

- `PMPNode.kt:370` — calls `submitSubscribe(...)` from `subscribe()`.
  Change to `submitRequest(..., STREAMING_SUBSCRIBE)`.
- `PMPNode.kt:623` — calls `submitSubscribe(...)` from `handleLoginResult`
  (re-subscribe on reconnect). Change to
  `submitRequest(..., STREAMING_SUBSCRIBE)`.
- `PMPNode.kt:725` — rename method signature.
- `PMPNode.kt:755` — update `buildSubscribeRequest` call to pass
  `requestType` parameter (already accepts it).

### Test code (MUST update)

- `app/src/test/java/com/tdt/pmobile3/viewmodels/common/PMPNodeTest.kt`
  — update 2 test names that mention `submitSubscribe` to `submitRequest`.
  The test bodies don't call `submitSubscribe` directly (they test via
  `subscribe()`), so no body changes needed; just the names.

### External API (MUST NOT change)

- `PMPNode.subscribe()` — keeps the same parameter list; `requestType` has
  a default value, so existing callers are unchanged.
- `PMPNode.unsubscribe()` — unchanged.
- `PMPNode.suspendForBackground()` — unchanged.
- `PMPNode.resumeAfterForeground()` — unchanged.
