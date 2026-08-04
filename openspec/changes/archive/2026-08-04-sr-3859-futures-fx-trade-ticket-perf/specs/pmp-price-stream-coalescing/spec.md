# Spec: PMP Price-Stream Coalescing

## Purpose

Define the cross-platform contract for a screen-scoped PMP (Price Message Protocol) subscription coordinator that eliminates duplicate PMP subscriptions per counter per screen stack and applies frame-level coalescing plus `distinctUntilChanged` semantics to the price stream consumed by the Futures/FX Trade screens on iOS and Android POEMS Mobile 3.

This capability extends (but does not replace) the existing `PMPConnectionCenter` / `PMPViewModel` pattern introduced for `NewOrderBottomSheet` in the `android-pmp-connection-center` change. The Trade screens require a screen-scoped variant because (a) the v3.3.54 release timeline does not allow migrating every PMP caller in the Trade module to the global singleton, and (b) the screen-scoped pattern gives 80% of the benefit (no duplicate listeners per screen stack) with 20% of the blast radius.

---

## ADDED Requirements

### Requirement: Screen-scoped PMP coordinator

The system SHALL provide a screen-scoped PMP subscription coordinator that deduplicates PMP price updates per `(counter, screen-stack)` tuple before forwarding them to N listeners.

#### Scenario: iOS — multiple consumers on the same screen stack subscribe to the same counter

- **GIVEN** a Futures/FX Order detail screen stack has two consumers (`PriceHeaderViewModel` and `OrderDetailViewModel`)
- **WHEN** both consumers subscribe to the same counter's PMP topic via `PmpSubscriptionCoordinator.subscribe(counter:listener:)`
- **THEN** the coordinator SHALL establish exactly one upstream PMP subscription for that counter
- **AND** SHALL dispatch each `PriceTick` to both listeners exactly once
- **AND** SHALL NOT call `PMPClient.subscribe(...)` a second time for the same counter on the same screen stack

#### Scenario: Android — multiple observers on the same Fragment subscribe to the same counter

- **GIVEN** a `TradeTicketFuturesScreen` and its parent `BaseTradeTicket` Fragment both observe PMP for the same counter
- **WHEN** both Fragments attach a `PMPTicketSubscription.collect { ... }` collector
- **THEN** the `PMPTicketSubscription` SHALL register exactly one `PMPEventListener` upstream
- **AND** SHALL fan-out each `PriceTick` to both collectors
- **AND** SHALL NOT call `PMPClient.subscribe(topic)` a second time for the same counter while at least one collector is attached

#### Scenario: Last listener detaches

- **GIVEN** a coordinator has one upstream subscription and two listeners attached
- **WHEN** the last listener calls `unsubscribe(...)` or its lifecycle owner enters `DESTROYED`
- **THEN** the coordinator SHALL dispose the upstream PMP subscription within 100 ms
- **AND** SHALL release any cached `PriceTick` state for that counter

### Requirement: Frame-coalesced price tick dispatch (16 ms)

The system SHALL coalesce consecutive PMP price ticks received within a single display frame (16 ms) into a single dispatch event per listener.

#### Scenario: iOS — burst of 4 ticks within 16 ms

- **GIVEN** a PMP burst produces 4 ticks for the same counter within 8 ms (typical Futures/FX rate)
- **WHEN** the burst is dispatched through `PmpSubscriptionCoordinator`
- **THEN** each listener SHALL receive exactly 1 `PriceTick` representing the latest tick of the burst
- **AND** the dispatch SHALL be scheduled on the next main RunLoop turn (no per-tick main-thread work)

#### Scenario: Android — burst of 4 ticks within 16 ms via CONFLATED channel

- **GIVEN** `PMPTicketSubscription` is backed by a `Channel(Channel.CONFLATED)` consumed by a single coroutine on `Dispatchers.Main.immediate`
- **WHEN** 4 ticks arrive on the producer side within 8 ms
- **THEN** the consumer coroutine SHALL emit only the latest `PriceTick` to its collectors
- **AND** no collector SHALL observe more than 1 emission per display frame

### Requirement: `distinctUntilChanged` on price stream

The system SHALL suppress `PriceTick` dispatches where the new tick's `bid`, `ask`, and `lastDone` are all equal to the previously dispatched tick for that counter.

#### Scenario: iOS — server re-sends identical bid/ask/lastDone

- **GIVEN** the upstream PMP sends two consecutive ticks with identical `(bid, ask, lastDone)` for a counter
- **WHEN** both ticks arrive at `PmpSubscriptionCoordinator`
- **THEN** the first tick SHALL be dispatched to listeners
- **AND** the second tick SHALL be suppressed (no dispatch)

#### Scenario: Android — same price re-broadcast

- **GIVEN** `PMPUtilViewModel.livePricesCallback` emits two identical `PriceTick` events
- **WHEN** they flow through `PriceTickCoalescer`
- **THEN** the second event SHALL be dropped before reaching any collector

### Requirement: Main-thread work budget per second

The system SHALL ensure that, under a sustained 50-tick/sec PMP burst on a single counter, the cumulative main-thread work attributable to PMP-driven UI updates on the Futures/FX Trade screens SHALL NOT exceed 6 distinct `@Published` mutations per second (iOS) and 6 `MediatorLiveData` emissions per second (Android).

#### Scenario: iOS — sustained 50 tick/sec burst on Order detail

- **GIVEN** `PmpSubscriptionCoordinator` is active for the Order detail counter with both header and detail listeners attached
- **WHEN** a recorded 50-tick/sec burst is replayed for 5 seconds
- **THEN** the total count of `objectWillChange.send()` / `@Published.willSet` invocations across all PMP-driven view models SHALL be ≤ 30 in 5 seconds (≤ 6/sec)

#### Scenario: Android — sustained 50 tick/sec burst on Trade ticket

- **GIVEN** `PMPTicketSubscription` is active for the Trade ticket counter with two Fragments observing
- **WHEN** a recorded 50-tick/sec burst is replayed for 5 seconds
- **THEN** the total count of `MediatorLiveData.setValue` / `postValue` calls on PMP-driven `UiState` SHALL be ≤ 30 in 5 seconds (≤ 6/sec)

### Requirement: Off-main heavy formatting

The system SHALL perform heavy price-formatting work (e.g., `makeStringMoney(...)` on iOS, `pbPercentSVolkBVolk.progress` divide on Android) off the main thread.

#### Scenario: iOS — `makeStringMoney` runs on global queue

- **GIVEN** a PMP tick triggers `mapTradeInfo()` in `TBSFuturesViewModel`
- **WHEN** `mapTradeInfo()` runs the `makeStringMoney(...)` computation
- **THEN** the computation SHALL execute on `DispatchQueue.global(qos: .userInitiated)`
- **AND** the final `@Published var submittedPrice` mutation SHALL happen on `DispatchQueue.main` after the computation completes

#### Scenario: Android — ProgressBar value formatting off main

- **GIVEN** a PMP tick triggers `updateTopDetailWithPMP()`
- **WHEN** the percentage value (`pbPercentSVolkBVolk.progress`) is calculated
- **THEN** the calculation SHALL run on `Dispatchers.Default`
- **AND** the resulting pre-formatted `CharSequence` SHALL be posted to `binding?.root` via `view.post {}`

### Requirement: Bounded PMP reconnect retry

The system SHALL apply exponential backoff with a bounded max depth when retrying PMP URL connections.

#### Scenario: Android — `handleConnectPMP()` with backoff

- **GIVEN** the URL list contains stale endpoints
- **WHEN** `handleConnectPMP()` enters its retry loop
- **THEN** it SHALL wait 50 ms before retry 1, 100 ms before retry 2, 200 ms before retry 3, 500 ms before retry 4, 500 ms before retry 5
- **AND** SHALL terminate the loop after depth 5 and log `Timber.tag("PMP-Failover").e(...)` with the failure context
- **AND** SHALL NOT recurse deeper than 5 levels

### Requirement: Pre-computed PMP field lookup

The system SHALL pre-compute a `Map<String, String>` from PMP field ID to canonical name at `PMPUtilViewModel` construction time so that `getFinalHashMapPmpResponse()` is O(1) per key.

#### Scenario: Android — `getFinalHashMapPmpResponse()` uses lookup map

- **GIVEN** `PMPUtilViewModel` has constructed `mPmpFieldLookup` from `PMPFieldsForSetting.values() + PMPFields.values()`
- **WHEN** `getFinalHashMapPmpResponse()` processes a tick payload
- **THEN** for each key in the payload, it SHALL perform `mPmpFieldLookup[key]?.let { finalHashMap[it] = value }`
- **AND** SHALL NOT call `String.split(...)` on any element of `mListColumnPmpEnum` per tick
- **AND** SHALL NOT iterate `mListColumnPmpEnum` linearly per key

### Requirement: Observability hook

The system SHALL emit a structured log entry per 1000 PMP ticks processed on the hot path with the fields: `counter`, `listener_count`, `dropped_count`, `dispatched_count`, `coalesce_ratio`.

#### Scenario: iOS — `os_log` debug entry

- **WHEN** 1000 ticks have been processed for a given counter
- **THEN** the coordinator SHALL emit `Logger(subsystem: "poems.trade", category: "pmp.coalescer").debug("\(counter): ticks=1000 dropped=\(X) dispatched=\(Y) ratio=\(Z)")`

#### Scenario: Android — `Timber.tag("PMP-Coalescer")` entry

- **WHEN** 1000 ticks have been processed for a given counter
- **THEN** `PMPTicketSubscription` SHALL emit `Timber.tag("PMP-Coalescer").d("$counter: ticks=1000 dropped=$X dispatched=$Y ratio=$Z")`
