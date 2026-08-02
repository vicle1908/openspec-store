## ADDED Requirements

### Requirement: Snapshot cache survives app background

Each `PMPNode` SHALL maintain a `topicSnapshots: MutableMap<String, LinkedHashMap<String, String>>` that stores the most recent price update for each subscribed topic. This map SHALL NOT be cleared by `suspendForBackground()`. It SHALL be the source of immediate emissions on `resumeAfterForeground()`. Snapshot entries SHALL be keyed by PMP topic string (e.g., `"US/OPT/NYSE/AAPL 250619 C 200"` for options, `"SG/HKSE/SPH"` for stocks).

#### Scenario: Snapshots persist across suspend/resume cycle
- **WHEN** the app moves to background (`ProcessLifecycleOwner.ON_STOP`) and the node calls `suspendForBackground()`
- **THEN** the `topicSnapshots` map SHALL retain all entries that were present before suspension
- **AND** when the app returns to foreground (`ON_START`) and the node calls `resumeAfterForeground()`, the cached snapshots SHALL be re-emitted to active subscribers before any live PMP push

### Requirement: Snapshot updated on every live price push MUST happen before fan-out

Whenever the `PMPEventListener.livePricesCallback()` receives a `SubscribeReturnBean`, the `topicSnapshots` map SHALL be updated for each topic in the response before the data is forwarded to token subscribers. Updates happen inside `viewModelScope.launch(Dispatchers.IO)` following the existing codebase pattern.

#### Scenario: Live push updates snapshot map before subscribers see the value
- **WHEN** `PMPEventListener.livePricesCallback()` receives a `SubscribeReturnBean` containing 3 topics with fresh prices
- **THEN** the `topicSnapshots` map SHALL be updated with the new price for each of the 3 topics
- **AND** only after the map update completes SHALL the data be forwarded to `PMPToken.priceUpdates` subscribers

### Requirement: Snapshot emitted as first value on resume

When `resumeAfterForeground()` successfully reconnects and resubscribes, it SHALL first iterate over `topicSnapshots` and emit each cached value to active subscribers' `SharedFlow` instances before waiting for the first live PMP push from the server. The emission order is implementation-defined but MUST emit all snapshots before any live data.

#### Scenario: Snapshots replay before live data on resume
- **WHEN** `resumeAfterForeground()` completes a successful reconnection and `topicSnapshots` contains entries for 2 subscribed topics
- **THEN** the node SHALL emit both cached snapshot values to active subscribers' `SharedFlow` instances
- **AND** no live PMP push data SHALL be emitted until all cached snapshots have been emitted

### Requirement: Snapshot replayed to new subscribers

When a new `PMPToken` is created and a `PMPNode` already has `topicSnapshots`, the new token's `priceUpdates` `SharedFlow` (configured with `replay = 1`) SHALL immediately replay the last snapshot value so the subscriber immediately sees the last known price without waiting for the next live push.

#### Scenario: New subscriber receives last snapshot immediately
- **WHEN** a new `PMPToken` is created for a topic that already has an entry in `topicSnapshots`
- **THEN** the new token's `priceUpdates` `SharedFlow` SHALL immediately replay the cached snapshot value to the first collector
- **AND** the collector SHALL see the last known price without waiting for the next live push from the PMP server

### Requirement: Snapshot cleared on explicit disconnect

The system SHALL clear `topicSnapshots` on all nodes when `PMPConnectionCenter.disconnectAll()` is called, along with stopping all connections and emptying the node map.

When `PMPConnectionCenter.disconnectAll()` is called, `topicSnapshots` SHALL be cleared on all nodes, all connections SHALL be stopped, and the node map SHALL be emptied.

> **Call site:** `PMPConnectionCenter.disconnectAll()` is dispatched from `AppApplication.isLogined`'s custom setter — when `isLogined` transitions from `true` to `false` (set by `LoginScreen.onCreate` after the user logs out), the setter triggers full PMP teardown. This is the only call site in Phase 1; additional call sites (e.g., explicit `MainActivity.onLogout()` invocation) are not required and may be added in later phases.

#### Scenario: disconnectAll wipes snapshots, connections, and node map
- **WHEN** `PMPConnectionCenter.disconnectAll()` is called from `AppApplication.isLogined`'s setter
- **THEN** `topicSnapshots` SHALL be cleared on every node
- **AND** every active `PMPConnection` SHALL be stopped
- **AND** the node map SHALL be emptied

### Requirement: Snapshot keyed by PMP topic string

The system SHALL key snapshots by PMP topic string (not by URL); topics are unique across URLs, and multiple tokens subscribing to the same topic on the same URL SHALL share the same snapshot entry.

Snapshots are keyed by PMP topic string (not by URL). Topics are unique across URLs. When multiple tokens subscribe to the same topic on the same URL, they share the same snapshot entry. The PMP topic string is the canonical key for all snapshot operations.

---

#### Scenario: App backgrounded for 2 minutes, foregrounds
- **WHEN** the app is in the background for 2 minutes
- **AND** `PMPNode.topicSnapshots` holds prices for 5 subscribed topics (e.g., option bid/ask, underlying price)
- **THEN** `suspendForBackground()` is called: `connection?.logout()` drops the TCP socket; `topicSnapshots` remains intact
- **WHEN** the app foregrounds
- **THEN** `resumeAfterForeground()` reconnects, logs in, resubscribes
- **AND** the 5 snapshot values are emitted immediately to all active subscribers' `SharedFlow` instances
- **AND** the screen UI flashes stale prices (from snapshot), then updates to live prices as they arrive from the server

#### Scenario: New screen subscribes after app foregrounds
- **WHEN** a new `PMPToken` is created after `resumeAfterForeground()` has already completed
- **AND** `PMPNode.topicSnapshots` has values for all subscribed topics
- **THEN** the new token's `priceUpdates` `SharedFlow` immediately replays the last snapshot (replay=1)
- **AND** the subscriber sees the last known price immediately
- **AND** subsequent live pushes flow through the normal callback path

#### Scenario: User logs out while app is backgrounded
- **WHEN** `AppApplication.isLogined` transitions from `true` to `false` (set by `LoginScreen.onCreate` post-logout)
- **THEN** the `isLogined` setter invokes `PMPConnectionCenter.disconnectAll()`
- **AND** all nodes call `connection?.logout()` and `connection = null`
- **AND** `topicSnapshots` is cleared on all nodes
- **AND** all nodes are removed from the node map
- **AND** `activeTokens` is cleared
- **AND** any subsequent `subscribe()` call starts fresh with no cached prices

#### Scenario: Option contract and underlying stock both in snapshot
- **WHEN** `NewOrderBottomSheet` subscribes to 2 topics: option contract (`GENERAL_PMP_POS`) and underlying stock (`UNDERLYING_PMP_POS`)
- **THEN** `topicSnapshots` contains 2 entries: one keyed by option PMP topic, one by underlying stock PMP topic
- **AND** each token's `SharedFlow` receives both snapshot emissions
- **AND** the UI dispatches each to the correct handler (`onGeneralPmpReceived` or `onUnderlyingPmpReceived`) based on the positional index

#### Scenario: Snapshot updates on every live price push
- **WHEN** `PMPEventListener.livePricesCallback()` fires with a `SubscribeReturnBean` containing bid/ask updates
- **THEN** `PMPNode.updateSnapshot()` writes each topic's data to `topicSnapshots` before forwarding to tokens
- **AND** subsequent snapshot emissions (e.g., after resume) emit the latest cached values
