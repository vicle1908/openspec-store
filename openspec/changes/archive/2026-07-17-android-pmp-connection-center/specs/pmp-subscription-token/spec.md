## ADDED Requirements

### Requirement: PMPToken is Closeable and holds a SharedFlow

`PMPToken` SHALL be a class that implements `Closeable`. It SHALL expose a `SharedFlow<Pair<String, LinkedHashMap<String, String>>>` property named `priceUpdates` representing live PMP price data. The first element of the pair is the PMP topic string (e.g. `"US/OPT/NYSE/AAPL 250619 C 200"`); the second is the field-name-keyed price map. Each emission is a single topic's price map. `LinkedHashMap` SHALL be used to preserve field insertion order which existing UI adapters depend on. The topic tag is required because `PMPNode` fans out to multiple tokens — each emission must carry its topic so the consumer (via `PMPViewModel`) can resolve counter indices.

#### Scenario: PMPToken exposes Closeable contract with topic-tagged SharedFlow
- **WHEN** a caller constructs a `PMPToken` and obtains `priceUpdates`
- **THEN** the property SHALL be a `SharedFlow<Pair<String, LinkedHashMap<String, String>>>` and the token SHALL implement `java.io.Closeable`
- **AND** emissions SHALL carry the topic string as the first element of the pair

### Requirement: Token close triggers unsubscribe

Calling `token.close()` SHALL decrement `topicRefCounts` on every `PMPNode` involved in the subscription. It SHALL remove the token from `PMPConnectionCenter.activeTokens`. If the node's ref counts drop to zero, the node SHALL schedule `connectionTeardownDelay` (60 seconds) before disconnecting.

#### Scenario: Token close decrements ref counts and schedules teardown
- **WHEN** `token.close()` is called on a token subscribed to 3 topics across 2 PMP nodes
- **THEN** `topicRefCounts` SHALL be decremented on both nodes for those topics
- **AND** the token SHALL be removed from `PMPConnectionCenter.activeTokens`
- **AND** if a node's ref counts reach zero, the node SHALL schedule `connectionTeardownDelay` (60s) before disconnecting

### Requirement: Auto-cleanup contract

Callers in Kotlin SHALL use explicit `close()` in `Fragment.onDestroy()` or `ViewModel.onCleared()`. `PMPToken` does not use finalizers (Kotlin has no deterministic `deinit`). `PMPViewModel.onCleared()` SHALL call `pmpToken?.close()` as a safety net. The token SHALL be stored in a nullable field and nulled after close.

#### Scenario: ViewModel.onCleared closes token as safety net
- **WHEN** `PMPViewModel.onCleared()` is invoked and the Fragment did not explicitly call `unsubscribe()`
- **THEN** `pmpToken?.close()` SHALL be called and `pmpToken` SHALL be set to null
- **AND** ref counts SHALL be decremented, preventing orphaned subscriptions

### Requirement: Token holds subscription metadata

Each `PMPToken` SHALL hold the `tokenId` (UUID), the list of subscribed `topics`, the `fields` `Set<String>`, and a `topicsByResolvedURL: Map<String, List<String>>` mapping resolved URLs to their subscribed topics. This metadata is required for `unsubscribe()` to correctly decrement per-node ref counts.

#### Scenario: Token metadata covers all fields needed for unsubscribe
- **WHEN** a `PMPToken` is constructed with a list of topics and a `fields` set
- **THEN** the token SHALL expose `tokenId: UUID`, `topics: List<String>`, `fields: Set<String>`, and `topicsByResolvedURL: Map<String, List<String>>`
- **AND** `unsubscribe()` SHALL iterate `topicsByResolvedURL` to decrement the correct per-node ref counts

### Requirement: Subscribers receive data via SharedFlow

The `priceUpdates` `SharedFlow` SHALL be configured with `replay = 1` (last cached value replayed to new collectors), `extraBufferCapacity = 64`, and `onBufferOverflow = BufferOverflow.DROP_OLDEST`. New collectors after a `Suspended → Connected` resume SHALL first receive the snapshot value, then live updates.

#### Scenario: New collector receives snapshot then live updates
- **WHEN** a new collector subscribes to `priceUpdates` after a `Suspended → Connected` resume
- **THEN** the collector SHALL first receive the cached snapshot value (replay=1)
- **AND** subsequent live PMP pushes SHALL emit additional values
- **AND** if the buffer overflows, the oldest emission SHALL be dropped (BufferOverflow.DROP_OLDEST)

### Requirement: Unique token ID per subscribe call

Each call to `PMPConnectionCenter.subscribe()` SHALL generate a new `UUID` as the `tokenId`. This ID is passed as the `subscriberID` when constructing `SubscribeQueryRequest`, allowing the PMP server to distinguish multiple concurrent subscribers on the same socket.

#### Scenario: Concurrent subscribers receive distinct tokenIds
- **WHEN** two fragments call `PMPConnectionCenter.subscribe()` concurrently with overlapping topics
- **THEN** each returned `PMPToken` SHALL have a distinct `tokenId` (UUID)
- **AND** each `SubscribeQueryRequest` SHALL be sent with its own `subscriberID` so the PMP server can route responses correctly

---

#### Scenario: Token closed explicitly in Fragment.onDestroy
- **WHEN** `NewOrderBottomSheet.onDestroy()` calls `pmpViewModel.unsubscribe()` which calls `pmpToken.close()`
- **THEN** the token's topics are unregistered from each node's `topicRefCounts`
- **AND** the token is removed from `PMPConnectionCenter.activeTokens`
- **AND** if no other tokens hold subscriptions, the node schedules connection teardown

#### Scenario: Token collected via repeatOnLifecycle
- **WHEN** a Fragment collects `pmpToken.priceUpdates` using `repeatOnLifecycle(Lifecycle.State.STARTED)`
- **THEN** collection starts when the lifecycle is `STARTED`
- **AND** collection is cancelled when lifecycle drops below `STARTED`
- **AND** the SharedFlow buffer (replay=1) holds the last emission so no data is lost between stop and resume

#### Scenario: Fragment recreated after configuration change
- **WHEN** a configuration change (rotation) destroys and recreates a Fragment
- **THEN** the old `PMPToken` is closed in `onDestroy()` of the destroyed Fragment
- **AND** a new `PMPToken` is created when the recreated Fragment calls `initPmpConnections()`
- **AND** `PMPConnectionCenter` handles both independently

#### Scenario: SharedFlow replay on new collector
- **WHEN** a new collector subscribes to `pmpToken.priceUpdates` and a snapshot exists
- **THEN** the collector immediately receives the last `topicSnapshots` value (replay=1)
- **AND** subsequent live PMP pushes emit additional values

#### Scenario: Token not explicitly closed, ViewModel cleared
- **WHEN** a Fragment's `PMPToken` is not explicitly closed (programming error)
- **AND** `PMPViewModel.onCleared()` is called
- **THEN** `pmpToken?.close()` is called as safety net
- **AND** ref counts are decremented, preventing orphaned subscriptions
