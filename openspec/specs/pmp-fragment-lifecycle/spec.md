## Purpose

Define the canonical fragment lifecycle for migrated screens, replacing
the legacy `PMPUtilViewModel` callback-wiring pattern with the new
`PMPViewModel.pmpDataFlow` collection pattern. This applies to all 13
fragments being migrated in this MR.

## ADDED Requirements

### Requirement: onResume subscribes, onPause detaches, onDestroyView unsubscribes

Every migrated fragment SHALL implement this lifecycle:

```
onResume()         →  initPmpConnections()        (LIVE + QUERY)
onPause()          →  pmpViewModel.detach()        (cancel collectors, preserve tokens)
onDestroyView()    →  pmpViewModel.unsubscribe()   (cancel collectors, close tokens)
```

#### Scenario: Migrated fragment opens, shows data, pauses, detaches, resumes, reuses token

- **WHEN** the fragment is shown
- **AND** `onResume` calls `initPmpConnections()` which calls `pmpViewModel.subscribe(counters, fields)`
- **THEN** the LIVE token opens and the collector starts
- **WHEN** the fragment is paused
- **AND** `onPause` calls `pmpViewModel.detach()`
- **THEN** the collector is cancelled but the LIVE token survives
- **WHEN** the fragment resumes
- **AND** `onResume` calls `initPmpConnections()` again
- **THEN** the idempotent guard `pmpViewModel.pmpToken != null` short-circuits
- **AND** the existing token is reused
- **AND** the collector restarts

#### Scenario: Migrated fragment is destroyed, tokens closed

- **WHEN** `onDestroyView` calls `pmpViewModel.unsubscribe()`
- **THEN** both `_pmpToken` and `_queryToken` are closed
- **AND** `pmpViewModel.pmpToken` is null
- **AND** `pmpViewModel.pmpQueryToken` is null

### Requirement: pmpDataFlow collected via repeatOnLifecycle(STARTED)

The fragment SHALL collect `pmpDataFlow` inside
`viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED)` and SHALL
dispatch on `update.kind` before accessing `update.data` or
`update.chartData`.

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

This collection SHALL be set up in `onViewCreated` (after
`super.onViewCreated`) and SHALL be cancelled automatically by
`repeatOnLifecycle(STARTED)` when the fragment is no longer `STARTED`.

#### Scenario: pmpDataFlow collection cancels when fragment is stopped

- **WHEN** the fragment is in `STARTED` state
- **THEN** `pmpDataFlow.collect` is active
- **WHEN** the fragment transitions to `STOPPED`
- **THEN** the `collect` is cancelled automatically by `repeatOnLifecycle`
- **AND** the next `STARTED` re-attaches the collector

### Requirement: Live fan-out iterates update.indices

The fragment's `handleLive(update)` SHALL iterate `update.indices` to fan
out the update to every counter sharing the topic:

```kotlin
private fun handleLive(update: PMPUpdate) {
    if (update.kind != PMPUpdateKind.LIVE) return
    val data = update.data ?: return
    update.indices.forEach { idx ->
        // screen-specific dispatch using idx and data
    }
}
```

The fan-out is critical: the legacy `setOnResponseListenerWithTopicIndex`
called the callback once per (topic, index) pair; the new `pmpDataFlow`
emits one `PMPUpdate` per topic, and the fragment MUST iterate
`update.indices` to replicate the legacy behavior.

#### Scenario: Multiple counters share one topic, all receive the update

- **WHEN** topic "ABC" is shared by 3 counters (indices 0, 1, 2)
- **AND** a price tick arrives for topic "ABC"
- **THEN** `pmpDataFlow` emits one `PMPUpdate(kind = LIVE, topic = "ABC", indices = [0, 1, 2], ...)`
- **AND** `handleLive` iterates `indices` and calls the per-index
  handler 3 times (once for 0, once for 1, once for 2)

### Requirement: initPmpConnections is idempotent

The fragment's `initPmpConnections()` helper SHALL have an idempotent
guard:

```kotlin
private fun initPmpConnections() {
    if (pmpViewModel.pmpToken != null) return
    val counters = buildCounterList()
    val fields = getFinalColumnsPmp()
    if (counters.isNotEmpty() && fields.isNotEmpty()) {
        pmpViewModel.subscribe(counters, fields)
    }
}
```

The early return on `pmpViewModel.pmpToken != null` prevents duplicate
subscriptions on every `onResume` cycle.

#### Scenario: initPmpConnections is a no-op on second onResume

- **WHEN** `onResume` calls `initPmpConnections()` (opens the LIVE token)
- **AND** the fragment is paused and resumed
- **AND** `onResume` calls `initPmpConnections()` again
- **THEN** the early return short-circuits
- **AND** the existing LIVE token is reused

### Requirement: Prohibited legacy methods not called

A migrated fragment SHALL NOT call any of the following on the legacy
`PMPUtilViewModel`:

- `disconnectToPMP()`
- `resetAllData()`
- `unSubscribeQueryRequest()`
- `reSubscribe()`
- `setOnResponseListener`
- `setOnResponseListenerUSSO`
- `setOnResponseListenerWithTopicIndex`
- `setOnQueryCallback`

If a fragment has a feature flag that toggles between the legacy
`PMPUtilViewModel` path and the new `PMPViewModel` path, only ONE
path SHALL run at a time.

#### Scenario: Feature flag OFF runs legacy path only

- **WHEN** `BuildConfig.FEATURE_PMP_CENTER_HOME == false`
- **THEN** the fragment's PMP logic uses `mWatchListPMPUtilViewModel`
- **AND** `pmpViewModel` is not consulted

#### Scenario: Feature flag ON runs new path only

- **WHEN** `BuildConfig.FEATURE_PMP_CENTER_HOME == true`
- **THEN** the fragment's PMP logic uses `pmpViewModel`
- **AND** `mWatchListPMPUtilViewModel` is not consulted
