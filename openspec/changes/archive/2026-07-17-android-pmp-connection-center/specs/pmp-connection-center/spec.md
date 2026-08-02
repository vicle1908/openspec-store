## ADDED Requirements

### Requirement: PMPConnectionCenter is a process-wide singleton

`PMPConnectionCenter` SHALL be a Kotlin `object` (process singleton) that manages the global pool of `PMPNode` instances keyed by PMP server URL. It SHALL expose a `subscribe()` method that accepts counters, fields, and a callback, and returns a `PMPToken`. It SHALL own the app lifecycle binding via `ProcessLifecycleOwner`.

#### Scenario: PMPConnectionCenter is a singleton accessed via object declaration
- **WHEN** any code in the app process calls `PMPConnectionCenter.subscribe(...)`
- **THEN** the call SHALL resolve to the same singleton instance regardless of which class invoked it
- **AND** the same `PMPConnectionCenter` SHALL hold the shared `PMPNode` map across the process

### Requirement: PMPToken priceUpdates is a topic-tagged flow

`PMPToken.priceUpdates` SHALL be a `SharedFlow<Pair<String, LinkedHashMap<String, String>>>` where the first element of the pair is the PMP topic string and the second is the field-name-keyed price data. The topic tag is required for `PMPViewModel` consumers to look up the counter index via `mHashmapIndexOfCounter[topic]`. New collectors SHALL receive the most recent pair immediately (replay=1). The pair is emitted via `tryEmit` from `PMPNode.emitToAllTokens` → `PMPToken.emitData`.

#### Scenario: New collector receives the latest topic-tagged pair via replay
- **WHEN** a `PMPToken` has emitted at least one `(topic, data)` pair and a new collector starts collecting `priceUpdates`
- **THEN** the new collector SHALL receive the most recent pair immediately (replay=1)
- **AND** subsequent emissions SHALL carry the topic string as the first element of the pair

### Requirement: Phase 2 — center re-broadcasts into legacy callback chain — ROLLED BACK

The system MUST NOT implement the Phase 2 re-broadcast into the legacy callback chain; that approach was rolled back (see "Why" below) and the active contract is incremental migration via `PMPViewModel`.

> **THIS REQUIREMENT IS ARCHITECTURAL CONTEXT ONLY — ROLLED BACK IN THIS MR.**
> The approach described here was implemented in Phase 2 of the original MR (commits `bca640577e` through `8.11`) but was reverted because it introduced four real risks (see `design.md` "Pivot to Incremental Migration"):
> 1. The center does not survive a normal `onPause`/`onResume` cycle — the fix only worked for the first cycle.
> 2. Two `PMPConnection` instances per URL ran in parallel — double TCP traffic and race conditions.
> 3. `resetAllData()` caused center token churn on every counter switch.
> 4. `dispatchToLegacyCallbacks` duplicated `livePricesCallback` line-for-line — a source of future drift.
>
> After revert, `PMPUtilViewModel` is in its pre-MR state. `PMPConnectionCenter` is consumed exclusively via `PMPViewModel`. This requirement is retained as architectural context for the decision to pivot.

When `PMPUtilViewModel.initPmpConnections()` was called and `PMPConnectionCenter.subscribe()` returned a non-null token, the adapter implementation:
1. Suppressed the legacy `mPMPEventListener`-driven `PMPConnection` (no second socket per URL).
2. Suppressed `connectionStatusCallback` handling in the legacy listener (the center owned reconnection).
3. Subscribed a collector to `PMPToken.priceUpdates` that re-broadcasts each `(topic, data)` pair to the existing `mOnSubscribedCallback` / `onSubscribedUSSOCallback` / `mOnSubscribedCallbackAllData` / `onSubscribedCallbackAllData` consumers via `dispatchToLegacyCallbacks`.

#### Scenario: Phase 2 re-broadcast path is intentionally absent after rollback
- **WHEN** the active code is inspected for a `dispatchToLegacyCallbacks` adapter from `PMPToken.priceUpdates` to the legacy `mOnSubscribedCallback*` consumers
- **THEN** that adapter SHALL NOT be present
- **AND** `PMPConnectionCenter` SHALL be consumed exclusively via `PMPViewModel`

### Requirement: Node pooling by PMP URL

When `subscribe()` is called with counters that resolve to the same PMP URL, `PMPConnectionCenter` SHALL reuse the existing `PMPNode` for that URL rather than creating a new one. Each unique PMP URL SHALL map to at most one `PMPNode`. Multiple tokens subscribing to the same URL SHALL share the node's underlying `PMPConnection`. URL resolution uses `PMPSettingModel` loaded from the Room database (via `PmpSettingsDao`), which is fetched from `GET global/settings/pmp` on app login.

#### Scenario: Two subscriptions to the same URL share one PMPNode
- **WHEN** `subscribe()` is called twice with counters that resolve to the same PMP URL
- **THEN** `PMPConnectionCenter` SHALL return two distinct `PMPToken`s backed by the same single `PMPNode`
- **AND** no second `PMPNode` SHALL be created for that URL

### Requirement: App lifecycle suspend/resume

`PMPConnectionCenter` SHALL register a `DefaultLifecycleObserver` with `ProcessLifecycleOwner`. On `ON_STOP` it SHALL call `suspendForBackground()` on every active `PMPNode`. On `ON_START` it SHALL call `resumeAfterForeground()` on every active `PMPNode`. This behavior SHALL be active whenever `observesApplicationLifecycle` config is true (default).

#### Scenario: App background triggers suspend on every active PMPNode
- **WHEN** `ProcessLifecycleOwner` emits `ON_STOP` and the app has at least one active `PMPNode`
- **THEN** `PMPConnectionCenter` SHALL call `suspendForBackground()` on every active `PMPNode`

### Requirement: Thread-safe state access

All state mutations in `PMPConnectionCenter` (node map, token registry, ref counts) SHALL be protected by `ConcurrentHashMap` for maps and `synchronized {}` blocks for compound operations. This matches the existing codebase pattern in `PMPUtilViewModel` which uses `synchronized {}` on `mHashMapCounterPmpModel`.

#### Scenario: Concurrent mutations do not corrupt the node map
- **WHEN** two threads concurrently call `subscribe()` for the same URL while another thread calls `unsubscribe()`
- **THEN** the internal node map SHALL remain consistent (no lost updates, no duplicate keys, no torn reads)

### Requirement: Token registry with weak references

`PMPConnectionCenter` SHALL hold tokens in a `ConcurrentHashMap<UUID, WeakReference<PMPToken>>`. When a `PMPNode` emits on its `nodeIdleSubject` (signaled when its ref counts drop to zero), dead weak references SHALL be purged. Nodes with zero active subscriptions SHALL schedule a `connectionTeardownDelay` (60 seconds by default) before calling `connection.logout()`.

#### Scenario: Tokens held weakly are purged when GC'd
- **WHEN** a `PMPToken` is no longer referenced outside `PMPConnectionCenter` and the JVM garbage-collects it
- **THEN** the corresponding `WeakReference` SHALL be removed from the token registry on the next `nodeIdleSubject` emission

### Requirement: Lifecycle integration uses ProcessLifecycleOwner

`PMPConnectionCenter` SHALL observe `ProcessLifecycleOwner` (the recommended Android API for app-wide foreground/background tracking) via a `DefaultLifecycleObserver`. The observer SHALL be registered exactly once (guarded by `AtomicBoolean.compareAndSet`) from `Application.onCreate()` via `PMPConnectionCenter.bindLifecycleObserver()`. This matches the Android Developers guidance that `ProcessLifecycleOwner` is the correct source for "is the app in the foreground" semantics (not `ActivityLifecycleCallbacks`, which gives per-activity granularity).

#### Scenario: bindLifecycleObserver is idempotent across Application restarts
- **WHEN** `Application.onCreate()` calls `PMPConnectionCenter.bindLifecycleObserver()` more than once (e.g. process restart)
- **THEN** only one observer SHALL be registered with `ProcessLifecycleOwner` (guarded by `AtomicBoolean.compareAndSet`)

### Requirement: Re-emission uses tryEmit, not emit

`PMPToken.emitData` and `PMPViewModel.subscribeViaCenter` SHALL use `tryEmit` (not suspending `emit`) when pushing into the `MutableSharedFlow`. The flow is configured with `replay = 1`, `extraBufferCapacity = 64`, and `BufferOverflow.DROP_OLDEST`, so `tryEmit` is always non-blocking and matches the "never block the PMP dispatch loop on a slow or absent collector" contract. Callers do not need to be in a coroutine to re-emit.

#### Scenario: Re-emission never blocks the PMP dispatch loop
- **WHEN** `PMPToken.emitData` is called from the PMP dispatch thread with no active collector
- **THEN** the call SHALL return immediately via `tryEmit` (never suspending) and SHALL NOT block the dispatch loop

### Requirement: ViewModel collector stays on the viewModelScope

`PMPViewModel` SHALL collect `PMPToken.priceUpdates` inside `viewModelScope.launch`. The collector MUST NOT be launched on a separate `CoroutineScope` because it must be cancelled automatically when the ViewModel is cleared (see `onCleared()`), preventing leaks of collectors observing the center's `SharedFlow`. The dispatcher inside the launch is intentionally `Dispatchers.IO` to match the existing convention for `mOnSubscribedCallback*` consumers in `livePricesCallback`, which expect to be invoked off the main thread.

#### Scenario: ViewModel collector is cancelled on onCleared
- **WHEN** `PMPViewModel.onCleared()` is invoked
- **THEN** the `viewModelScope.launch` collector SHALL be cancelled along with the rest of `viewModelScope`
- **AND** no orphan collector SHALL remain subscribed to `PMPToken.priceUpdates`

---

### Requirement: PMPNode state machine — Flow-based reactive implementation

Each `PMPNode` SHALL implement a state machine with at least four states: `Idle`, `Connecting`, `Connected`, and `Suspended`. State transitions SHALL be driven by connection events, lifecycle events, and subscription activity. Transitions SHALL be logged with Timber.

The state machine SHALL be implemented using Kotlin Coroutines `Flow` operators as follows:

- `MutableStateFlow<State>` for atomic state storage. State transitions (`_state.value = ...`) are atomic by construction; no external locking is needed for single-field writes.
- `MutableSharedFlow<ConnEvent>` as the single event channel. All three PMP library callbacks (`loginCallback`, `connectionStatusCallback`, `livePricesCallback`) SHALL convert their arguments into sealed `ConnEvent` subclasses (`LoginResult`, `StatusChanged`, `PriceTick`) and emit via `_event.tryEmit()`. Using a single channel guarantees that events from the three callbacks are strictly ordered.
- Each event type SHALL be routed to its handler using `filterIsInstance<ConnEvent.X>()` + `onEach { handleX(it) }.launchIn(scope)` — not `when(event)` inside a single `scope.launch { _event.collect { } }` block.
- The price-tick actor SHALL gate emissions on `state == Connected` using a `combine(_event, _state) { tick, state -> tick to (state == Connected) }.filter { (_, isConnected) -> isConnected }` pipeline — so that ticks arriving before login completes are buffered (in `topicSnapshots`) but NOT fanned out to tokens until the node is confirmed Connected. This is the explicit "connect successfully THEN subscribe" enforcement point.
- Compound mutations (e.g., decrement ref count + remove topic + maybe send unsubscribe + maybe schedule teardown) SHALL be serialized via `kotlinx.coroutines.sync.Mutex.withLock { }`. `synchronized {}` MUST NOT be used inside suspend functions that may cross suspend points.
- The stale-callback guard (SR-3738) SHALL use a `MutableStateFlow<Int>` (`connSeq`) that increments on each `connect()` call. Events carry `event.seq`; the handler SHALL check `event.seq == connSeq.value` before acting. The `connSeq` `StateFlow` also serves as the "which connection is current" marker so that a late callback from an old connection is always discarded.
- The reconnect watcher SHALL use `_state.distinctUntilChanged().filter { it == State.Idle && hasActiveSubscriptions }.onEach { connect() }.launchIn(scope)` — so that a node that reached `Idle` (e.g. login exhausted all URLs) automatically restarts when a new subscription arrives.

**Why not `synchronized {}`:** `synchronized {}` is a Java intrinsic lock that blocks the calling thread. It does not compose with coroutines: holding a `synchronized {}` lock across a suspend point (e.g. `delay()`, an `await()` on I/O) blocks the coroutine dispatcher thread. `Mutex.withLock {}` is a suspend function — it releases the thread while waiting, making it safe for use inside coroutines that may suspend.

#### Scenario: PMPNode transitions Idle → Connecting → Connected on login success
- **WHEN** a new subscription arrives and the node starts `connect()`
- **THEN** the state SHALL transition `Idle → Connecting` and SHALL transition `Connecting → Connected` once `loginCallback` fires with `rc == 0`
- **AND** each transition SHALL be logged via Timber

### Requirement: Suspend drops socket and preserves subscription state

When `suspendForBackground()` is called on a `PMPNode`, it SHALL call `connection?.logout()` to close the underlying TCP socket. It SHALL then set `connection = null` and transition state to `Suspended` (when previously `Connected`) or to `Idle` (when previously `Connecting` — see the Connecting→Idle carve-out below). It SHALL NOT clear `topicRefCounts`, `topicFieldUnion`, or `topicSnapshots`. Pending subscriptions SHALL be retained.

#### Scenario: Suspend closes socket and preserves subscription metadata
- **WHEN** `suspendForBackground()` is called on a `Connected` node
- **THEN** `connection?.logout()` SHALL be invoked
- **AND** `connection` SHALL be set to `null`
- **AND** state SHALL transition to `Suspended`
- **AND** `topicRefCounts`, `topicFieldUnion`, and `topicSnapshots` SHALL remain unchanged

### Requirement: Connecting state reverts to Idle (not Suspended) on background

When `suspendForBackground()` is called while a `PMPNode` is in `Connecting` state (the TCP handshake is in progress but `loginCallback` has not yet fired), the node SHALL transition to `Idle` rather than `Suspended`. The in-flight `connectionRef` SHALL be discarded. Rationale: `handleLoginCallback` is invoked by the `phillip.pmp` library from its own thread; if we allowed `Connecting → Suspended`, a late login callback could transition the node to `Connected` while the app is backgrounded, leaving it in a "connected but actually dead" state. Reverting to `Idle` is the only safe option — `resumeAfterForeground` on the next foreground will see `Idle` and start a fresh connection.

#### Scenario: Suspend during Connecting reverts to Idle and discards in-flight login
- **WHEN** `suspendForBackground()` is called on a `Connecting` node
- **THEN** the state SHALL transition to `Idle` (not `Suspended`)
- **AND** any subsequent `loginCallback` from the discarded `connectionRef` SHALL NOT transition the node to `Connected`

### Requirement: Resume reconnects and resubscribes

When `resumeAfterForeground()` is called on a `PMPNode` that has active subscriptions and is in `Suspended` state, it SHALL reconnect from URL index 0, re-authenticate with `PMP_USER_NAME = "test"` / `PMP_PASS_WORD = "1111"` (hardcoded constants in `Config.kt`), and re-send all active subscriptions. It SHALL then emit all `topicSnapshots` values as new emissions to any active subscribers before the first live PMP push arrives.

#### Scenario: Resume re-authenticates and replays cached snapshots
- **WHEN** `resumeAfterForeground()` is called on a `Suspended` node with active subscriptions
- **THEN** the node SHALL reconnect from URL index 0
- **AND** SHALL call `login("test", "1111")`
- **AND** SHALL re-send every active subscription
- **AND** SHALL emit every `topicSnapshots` entry to active subscribers before the first live PMP push

### Requirement: URL failover on connect failure

`PMPNode` SHALL maintain a `currentUrlIndex` and a list of alternative URLs from `PMPSettingModel.Market`. The list is ordered: `primaryURL` (index 0), then `alternativeURLs`, then `primaryDelayedURL`, then `alternativeDelayedURLs`. If connection to the primary URL fails (signaled via `connectionStatusCallback` with status != `"1"`), it SHALL increment `currentUrlIndex` and retry with the next URL. After exhausting all URLs, it SHALL transition to `Idle`. On `resumeAfterForeground()`, it SHALL reset `currentUrlIndex` to 0.

#### Scenario: Primary URL failure advances to the next URL in the list
- **WHEN** `connectionStatusCallback` reports a non-success status for the current URL
- **THEN** the node SHALL increment `currentUrlIndex` and SHALL retry with the URL at the new index
- **AND** if all URLs are exhausted, the node SHALL transition to `Idle`

### Requirement: Connection teardown delay

When a `PMPNode` has zero active subscriptions and zero active tokens, it SHALL NOT immediately drop the connection. It SHALL schedule a `connectionTeardownDelay` timer (default 60,000 ms). If a new subscription arrives before the timer fires, the timer SHALL be cancelled and the node SHALL be reused.

#### Scenario: Teardown delay is cancelled by a new subscription arriving in time
- **WHEN** a `PMPNode` has zero subscriptions and has scheduled `connectionTeardownDelay`
- **AND** a new subscription arrives before the timer fires
- **THEN** the timer SHALL be cancelled
- **AND** the node SHALL be reused for the new subscription

### Requirement: Login uses hardcoded credentials

Every new `PMPConnection` SHALL call `login("test", "1111")` after connecting. These are hardcoded constants (`PMP_USER_NAME`, `PMP_PASS_WORD` in `Config.kt`) — the same for all users, server-level authentication. Login success is signaled via `loginCallback` with `rc == 0`.

#### Scenario: Each new PMPConnection authenticates with hardcoded test credentials
- **WHEN** `PMPConnection` is created and the TCP handshake completes
- **THEN** the node SHALL call `login("test", "1111")` exactly once per connection
- **AND** SHALL treat `loginCallback` with `rc == 0` as success and any other `rc` as failure

---

#### Scenario: App backgrounds with active subscriptions
- **WHEN** the app enters the background while at least one `PMPToken` holds an active subscription
- **THEN** `PMPConnectionCenter.onAppBackground()` is called via `ProcessLifecycleOwner`
- **AND** every `PMPNode` calls `suspendForBackground()`:
  - if state is `Connected`: `connection?.logout()` drops the TCP socket, `connection` is set to `null`, state becomes `Suspended`
  - if state is `Connecting`: `connection` is set to `null`, state becomes `Idle` (the in-flight login callback, when it arrives, will be discarded)
  - if state is `Idle` or already `Suspended`: no-op
  - `topicRefCounts`, `topicFieldUnion`, and `topicSnapshots` are preserved in memory
  - `PmpConnectionPool` URL entries remain registered

#### Scenario: App foregrounds after background
- **WHEN** the app enters the foreground while at least one `PMPNode` has active subscriptions
- **THEN** `PMPConnectionCenter.onAppForeground()` is called via `ProcessLifecycleOwner`
- **AND** each `PMPNode` calls `resumeAfterForeground()`:
  - if state != Suspended: skip
  - `currentUrlIndex` is reset to 0
  - `PMPConnection(primaryUrl, listener, 0)` is created
  - `connection.setConnectionTimeout(5000)` is called
  - `connection.login("test", "1111")` is called
  - all active subscriptions are re-sent via `submitSubscribeQueryRequest()`
  - all `topicSnapshots` values are emitted immediately to all subscriber tokens
  - state becomes `Connected`

#### Scenario: Multiple screens subscribe to the same PMP URL
- **WHEN** two different fragments both call `PMPConnectionCenter.subscribe()` with counters that resolve to the same PMP URL
- **THEN** both tokens share the same underlying `PMPNode`
- **AND** each token independently increments and decrements `topicRefCounts`
- **AND** closing one token does not disconnect the other token's subscription
- **AND** both tokens receive the same price updates via their respective `SharedFlow` emissions

#### Scenario: Token closed, other tokens still subscribed
- **WHEN** one `PMPToken` calls `close()` while other tokens still hold subscriptions to the same node
- **THEN** the node's ref counts decrement for that token's topics
- **AND** the `PMPConnection` remains open because ref counts are non-zero
- **AND** other tokens continue to receive price updates uninterrupted

#### Scenario: Last token closed, connection teardown scheduled
- **WHEN** the last `PMPToken` for a node calls `close()`
- **THEN** the node's ref counts drop to zero
- **AND** `connectionTeardownDelay` timer (60s) is scheduled
- **AND** `connection?.logout()` is called when the timer fires (NOT `stop()` — the `phillip.pmp` library exposes `logout()` only)
- **AND** if a new token subscribes before the delay fires, the timer is cancelled and the node is reused with the existing connection

#### Scenario: URL failover on primary failure
- **WHEN** `PMPNode.connect()` fails on the primary URL (status != `"1"`)
- **THEN** `currentUrlIndex` is incremented
- **AND** `connectionStatusCallback` triggers a retry with the next URL in the list
- **AND** if all URLs are exhausted, state becomes `Idle` and the center is notified
- **AND** on `resumeAfterForeground()`, `currentUrlIndex` resets to 0

#### Scenario: New subscription arrives during Suspended state
- **WHEN** a new `subscribe()` call arrives on a node that is in `Suspended` state
- **THEN** the node immediately calls `resumeAfterForeground()` as part of the subscribe operation
- **AND** it reconnects and resubscribes, acting as if the app just foregrounded
- **AND** snapshot values are emitted before the first live push

#### Scenario: Login fails and retries the next URL
- **WHEN** `PMPNode.handleLoginCallback()` receives a `LoginReturnBean` with `rc != 0`
- **THEN** the node advances `currentUrlIndex` and calls `connect()` to try the next URL in the failover list
- **AND** if all URLs are exhausted, `urlIndex` resets to 0 and state becomes `Idle`
- **AND** the next call to `resumeAfterForeground()` retries the primary URL from index 0

#### Scenario: App backgrounds mid-handshake (Connecting state)
- **WHEN** `suspendForBackground()` is called while the node is in `Connecting` state
- **THEN** the node transitions to `Idle` (NOT `Suspended`)
- **AND** the in-flight `connection` reference is discarded
- **AND** when the late `loginCallback` arrives, the node is in `Idle` and discards the late callback
- **AND** `resumeAfterForeground()` on the next foreground will start a fresh connection

#### Scenario: Trade bottom sheet (USSO options) recovers after app background (SR-3738)

This scenario addresses SR-3738: opening the Trade bottom sheet, backgrounding the app for several minutes, and observing that USSO options prices (Last Done, Change, Change%, Bid, Ask) stop updating — the bottom sheet only recovers when the user closes and reopens it.

The fix works through `PMPViewModel` — the migrated fragment uses `PMPConnectionCenter` directly rather than through `PMPUtilViewModel`.

- **WHEN** `NewOrderBottomSheet` is shown, it calls `pmpViewModel.subscribe(counters, fields)` which opens a `PMPToken` in `PMPConnectionCenter`
- **AND** `viewLifecycleOwner.repeatOnLifecycle(STARTED) { pmpViewModel.pmpDataFlow.collect { ... } }` is active — the fragment is collecting `PMPUpdate` emissions
- **AND** `NewOrderBottomSheet.onPause()` calls `pmpViewModel.detach()` — the fragment-side collector is cancelled but the center token **stays open** (the key difference from `PMPUtilViewModel`)
- **AND** the app enters the background, `ProcessLifecycleOwner.ON_STOP` → `PMPConnectionCenter.onAppBackground()` drops the TCP socket on every `PMPNode`; subscriptions, `topicRefCounts`, and `topicSnapshots` are preserved
- **WHEN** the app returns to the foreground, `ProcessLifecycleOwner.ON_START` → `PMPConnectionCenter.onAppForeground()` reconnects each node, re-logs in, re-subscribes, and emits cached `topicSnapshots` to all tokens
- **THEN** `PMPToken.priceUpdates` emits the snapshot for each topic
- **AND** when `NewOrderBottomSheet.onResume()` is called (either after the app foregrounds or when the user taps back into the sheet), `pmpViewModel.subscribe()` reuses the cached token and reattaches the `viewModelScope` collector
- **AND** the first emission the collector receives is the latest snapshot (replay=1 on the token's flow)
- **AND** the bottom sheet's USSO options prices update within ~5 seconds of foregrounding, without requiring the user to close and reopen the sheet

#### Scenario: ViewModel is cleared while collector is active
- **WHEN** `PMPViewModel.onCleared()` is called (the host Fragment is being permanently destroyed, not just a config change)
- **THEN** `collectorJob?.cancel()` cancels the `viewModelScope` collector
- **AND** `pmpToken?.close()` decrements node ref counts
- **AND** no `PMPConnectionCenter` background work is cancelled (the center is a process singleton and outlives the ViewModel)

#### Scenario: App is logged out while PMP subscriptions are active
- **WHEN** the user logs out (the `LoginScreen.onCreate` flow sets `AppApplication.isLogined = false`)
- **THEN** the `isLogined` setter transitions from `true` to `false` and calls `PMPConnectionCenter.disconnectAll()` synchronously
- **AND** every active `PMPNode` transitions to `Idle` with its `connection` reference cleared
- **AND** all `PMPToken` weak references are purged
- **AND** the next login (which re-fetches `PMPSettingModel` and may resolve to a different PMP URL set) starts with a clean slate — no stale `currentUrlIndex`, no leaked ref counts, no orphan sockets

#### Scenario: Lifecycle observer is registered exactly once
- **WHEN** `PMPConnectionCenter.bindLifecycleObserver()` is called from `Application.onCreate()` (the only call site in the codebase)
- **THEN** the `AtomicBoolean lifecycleObserverRegistered` CAS guard ensures that subsequent calls (e.g. from instrumented tests that re-trigger `onCreate`) are no-ops
- **AND** `ProcessLifecycleOwner.get().lifecycle.addObserver(lifecycleObserver)` is invoked at most once per process lifetime
- **AND** `unbindLifecycleObserver()` is provided as a test hook (not used in production) so tests can detach and re-attach the observer without leaking listeners

---

## Phase 1.6 — PMPNode race condition fixes (19/06/2026)

The Phase 1.5 Flow refactor (commit `a30235bb33`) simplified the state machine but exposed two production-visible races that the previous callback-based design happened to mask via `synchronized(this)` blocks. With `MutableStateFlow` + `tryEmit`, the state is atomic but the relationship between `connectionRef` and `_state` is not.

### Requirement: connect() catch block clears connectionRef

When `PMPNode.connect()` throws (e.g., the documented `NullPointerException` in `com.phillip.pmp.core.LoginCommunications.login()` on `DataOutputStream.write`), the catch block SHALL clear `connectionRef` and transition `_state` to `Idle`. The order MUST be `connectionRef.set(null)` BEFORE `_state.value = State.Idle` to prevent a window where `submitSubscribe` could read a stale `conn` while the state has already been reset.

This matches the existing cleanup pattern in `emitIdleAndStop` (which sets `connectionRef.set(null)` then `_state.value = State.Idle`) and `stopConnection` (same order). The absence of the clear in the `connect()` catch block was an oversight in the Phase 1.5 refactor.

### Requirement: submitSubscribe snapshots and re-verifies connectionRef

`PMPNode.submitSubscribe` SHALL snapshot `connectionRef.get()` once at the start, then re-verify identity AFTER the state check but BEFORE calling `conn.submitSubscribeQueryRequest(request)`. If the snapshot no longer matches the current `connectionRef`, the call SHALL abort with a Timber warning and not send the request. This prevents a duplicate-send race where a concurrent `connect()` (triggered by `reconnect-watcher` or another subscriber) swaps `connectionRef` between the state check and the I/O call. The new connection may not have completed its login handshake, so the server would reject the subscribe with `PMPException: you must login before send message to PMPException server!`.

The verification is `conn !== connectionRef.get()` (reference equality), not sequence-number equality — by the time `submitSubscribe` is reached, the sequence is already correct via the upstream stale-callback guard in `handleLoginResult`.

### Requirement: PMPNode.createConnection is overridable for tests

`PMPNode` SHALL expose an internal `@VisibleForTesting var connectionFactory: (String) -> PMPConnection` that wraps the `PMPConnection(url, listener, PULL_TIME_IN_SEC)` constructor. Production code calls this from `connect()`; tests SHALL reassign it to inject a factory that throws (to exercise the catch path) or returns a mock that records `submitSubscribeQueryRequest` calls. The default value delegates to the real constructor. The property is a function-reference `var` rather than an `open fun` so that the `final` `PMPNode` class does not need to be opened. The property SHALL be marked `@VisibleForTesting` (AndroidX annotation) and placed after the `companion object`.

### Scenario: PMPNode.connect() SDK NPE is recovered

- **WHEN** `PMPConnection` constructor or `conn.login()` throws (e.g., the documented `NPE` in `LoginCommunications.login` line 57)
- **THEN** the catch block at `PMPNode.connect()` line 683-686 calls `connectionRef.set(null)` BEFORE `_state.value = State.Idle`
- **AND** a subsequent `submitSubscribe` call (e.g., from `reconnect-watcher` after the next successful `connect()`) reads a null `connectionRef` and returns early with a "no connectionRef" Timber warning
- **AND** the user does NOT see a "you must login before send message" exception in logcat

### Scenario: submitSubscribe detects connectionRef swap

- **WHEN** `PMPNode.submitSubscribe` reads `connectionRef.get()` and captures it as `conn`
- **AND** between the state check (`_state.value == Connected`) and the call site of `conn.submitSubscribeQueryRequest(request)`, another coroutine calls `PMPNode.connect()` which calls `connectionRef.set(newConn)`
- **THEN** the re-verification `conn !== connectionRef.get()` is true
- **AND** `submitSubscribe` returns early with a "connectionRef swapped after state check" Timber warning
- **AND** the new `conn` (the one whose login just completed) becomes the sole target of the next `submitSubscribe` triggered by `handleLoginResult` at line 593

### Scenario: Tests cover catch path and snapshot guard

- **WHEN** the unit test class `PMPNodeTest` runs under `RobolectricTestRunner` with `Config(sdk = [29])`
- **THEN** 4 new tests pass:
  1. `connect() catch path clears connectionRef` — exercises the `createConnection` seam to throw, verifies `connectionRef.get() == null` and `_state.value == Idle` after.
  2. `connect() catch path does not throw` — same seam, verifies no exception escapes.
  3. `submitSubscribe with stale connectionRef` — sets `connectionRef = connA`, then swaps to `connB`, calls `submitSubscribe` via the test seam, verifies `connA.submitSubscribeQueryRequest` is NOT called.
  4. `connectionRef set order in connect() catch` — verifies `connectionRef.set(null)` executes before `_state.value = State.Idle` by observing the state transition in a side effect.
- **AND** existing 4 tests (constructor rejection, initial state, suspendForBackground no-op) continue to pass.
