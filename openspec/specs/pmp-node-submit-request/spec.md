## Purpose

Generalize `PMPNode.submitSubscribe` to `PMPNode.submitRequest` so it can
handle `STREAMING_SUBSCRIBE`, `STREAMING_UNSUBSCRIBE`, and `STREAMING_QUERY`
request types. The internal `buildSubscribeRequest()` (line 790) already
accepts a `requestType` parameter; only the call sites at lines 370 and
623 need lifting. Add a new public `PMPNode.subscribeForHistory()` method
with a type-safe callback for chart data.

## MODIFIED Requirements

### Requirement: submitSubscribe renamed to submitRequest with requestType parameter

The private method `submitSubscribe(topics, fieldMap)` SHALL be renamed
to `submitRequest(topics, fieldMap, requestType)` and SHALL accept a
`requestType: PMPRequestType` parameter.

```kotlin
private fun submitRequest(
    topics: List<String>,
    fieldMap: Map<String, MutableSet<String>>,
    requestType: PMPRequestType,
)
```

The `requestType` SHALL be one of:
- `PMPRequestType.STREAMING_SUBSCRIBE` (value = 1)
- `PMPRequestType.STREAMING_UNSUBSCRIBE` (value = 2)
- `PMPRequestType.STREAMING_QUERY` (value = 3)

The two existing internal call sites (line 370 in `subscribe()` and line
623 in `handleLoginResult`) SHALL pass `STREAMING_SUBSCRIBE` to preserve
existing behavior.

#### Scenario: submitRequest SUBSCRIBE sends a subscribe request

- **WHEN** `submitRequest(topics, fieldMap, STREAMING_SUBSCRIBE)` is called
- **AND** the node is in `State.Connected`
- **THEN** `conn.submitSubscribeQueryRequest(request)` is called with a request body containing `requestType = 1`
- **AND** `topicRefCounts` is incremented for each topic

#### Scenario: submitRequest QUERY does not affect live topicRefCounts

- **WHEN** `submitRequest(topics, fieldMap, STREAMING_QUERY)` is called
- **THEN** `conn.submitSubscribeQueryRequest(request)` is called with `requestType = 3`
- **AND** `topicRefCounts` is NOT modified (the ref-count is on the historical URL node, a separate `PMPNode` instance)

### Requirement: Connection state guards SHALL be preserved

`submitRequest` SHALL enforce the same connection state guards as the
existing `submitSubscribe` for all three request types. The existing
connection state checks at lines 730-751 of `PMPNode.kt` SHALL be
applied as follows:
- If `connectionRef.get() == null`, skip the request (logged warning).
- If `_state.value != State.Connected`, skip the request (logged warning).
- If `connectionRef` has been swapped between the state check and the
  `submitSubscribeQueryRequest` call, skip the request (snapshot guard).

#### Scenario: submitRequest is a no-op when state is Connecting

- **WHEN** `submitRequest(topics, fieldMap, STREAMING_QUERY)` is called
- **AND** the node is in `State.Connecting` (login in progress)
- **THEN** the request is skipped with a logged warning
- **AND** no exception is thrown

#### Scenario: submitRequest is a no-op when connectionRef is null

- **WHEN** `submitRequest(topics, fieldMap, STREAMING_QUERY)` is called
- **AND** `connectionRef.get() == null` (e.g., the node was torn down)
- **THEN** the request is skipped with a logged warning

## ADDED Requirements

### Requirement: subscribeForHistory public method SHALL be added for chart data

A new public method SHALL be added to `PMPNode` with the signature
`subscribeForHistory(subscriberId, topics, fields, onChart, onReady)`.
It SHALL mirror the existing `subscribe()` method's internals (token
registration, ref-count, login state machine) but use
`submitRequest(..., STREAMING_QUERY)` internally and route the response
to the `onChart` callback instead of `onSnapshot`.

```kotlin
fun subscribeForHistory(
    subscriberId: UUID,
    topics: List<String>,
    fields: List<WatchListColumnsSettingModel>,
    onChart: (String, List<String>) -> Unit,
    onReady: (() -> Unit)? = null,
)
```

The `onChart` callback SHALL receive `(topic, chartPoints)` pairs where
`chartPoints` is a `List<String>` of `dayClose` values parsed from the
PMP server's `QueryReturnBean` response.

The existing `subscribe()` method SHALL be unchanged (its public API
keeps the same parameter list; no `requestType` parameter is added to it
because the type-safe callback is preferred over a type-erased one).

#### Scenario: subscribeForHistory sends a STREAMING_QUERY request

- **WHEN** `subscribeForHistory(subscriberId, topics, fields, onChart, onReady)` is called
- **AND** the node is in `State.Connected`
- **THEN** `submitRequest(topics, fieldMap, STREAMING_QUERY)` is called
- **AND** `topicRefCounts` is NOT modified (the ref-count is on the historical URL node)

#### Scenario: subscribeForHistory routes response to onChart

- **WHEN** a `QueryReturnBean` arrives for topic "X" with chart points ["1.0", "2.0", "3.0"]
- **THEN** `onChart("X", ["1.0", "2.0", "3.0"])` is invoked
- **AND** the `onSnapshot` callback (used for LIVE) is NOT invoked

### Requirement: Ref-count semantics SHALL be preserved

- `submitRequest(STREAMING_SUBSCRIBE)` SHALL increment `topicRefCounts` per topic.
- `submitRequest(STREAMING_UNSUBSCRIBE)` SHALL NOT decrement `topicRefCounts`
  (unsubscribe is a wire-level operation, not a ref-count operation).
- `submitRequest(STREAMING_QUERY)` SHALL NOT affect `topicRefCounts` for
  the live URL pool. The ref-count is on the historical URL node, which
  is a different `PMPNode` instance.

#### Scenario: Ref-counts are per-URL pool

- **WHEN** `submitRequest(topics1, fieldMap, STREAMING_SUBSCRIBE)` is
  called on the live URL node (e.g., "https://pmp100.poems.com.sg")
- **AND** `submitRequest(topics2, fieldMap, STREAMING_QUERY)` is called
  on the historical URL node (e.g., "https://hist.example.com")
- **THEN** the live node's `topicRefCounts` includes `topics1` but NOT `topics2`
- **AND** the historical node's `topicRefCounts` includes `topics2` but NOT `topics1`
