## Why

Android's PMP (Price Market Platform) real-time price streaming has a structural bug: `PMPUtilViewModel` is scoped per-Fragment and sends **server-side unsubscribes** on `onPause()`. When `BottomSheetDialogFragment` lifecycle is unreliable (SR-3738), `onResume()` is missed, prices stop updating, and the user sees stale data until they navigate away and back. iOS solved this in April 2026 (SR-2875) by introducing `HPMPConnectionCenter` — a global singleton that separates "tear down socket" from "forget subscription." Android has no equivalent, and the pattern of 30+ screens each managing their own PMP lifecycle is the root cause.

Platform parity is also the #1 root cause category in v3.3.54 (113 of 246 bugs, 45.9%), making this a systemic improvement, not just a one-off fix.

## What Changes

**Phase 1 (this MR — already landed):** Process-wide PMP infrastructure.

- **New** `PMPConnectionCenter` — a process-wide Kotlin `object` singleton that owns all PMP connections and manages app-level lifecycle (background/foreground) via `ProcessLifecycleOwner`.
- **New** `PMPNode` — one per unique PMP URL, pooled and shared across screens. Holds `topicRefCounts` and `topicSnapshots` in memory across app background so subscriptions survive and stale prices flash immediately on foreground.
- **New** `PMPToken` — a `Closeable` token returned from `subscribe()`. Callers collect a `SharedFlow<Pair<String, LinkedHashMap<String, String>>>` from the token. On `close()`, ref counts decrement and nodes may teardown after a delay.
- **Modify** `PMPUtilViewModel` — **REVERTED**: the Phase 2 adapter (Phase 2 of the original MR) is rolled back. `PMPUtilViewModel` is restored to its pre-MR state. `PMPConnectionCenter` is consumed exclusively via the new `PMPViewModel`, not via `PMPUtilViewModel`. This eliminates four risks introduced by the adapter approach.
- **Modify** `Application.kt` — register `PMPConnectionCenter` with the existing `ProcessLifecycleOwner` observer so it drives foreground/background events.

**Phase 2 (next MR — INCREMENTAL MIGRATION, this change):** New thin `PMPViewModel` for incremental screen-by-screen migration.

> **Pivot rationale:** A second-pass audit of the Phase 1+2 `PMPUtilViewModel` adapter approach surfaced four real risks:
> 1. **The center does not survive a normal `onPause`/`onResume` cycle.** Every Fragment calls `unSubscribeQueryRequest()` in `onPause` which closes the center token. After the first pause, the center is gone, and `reSubscribe()` does not reopen it. The bug-fix works for only the first cycle.
> 2. **Two `PMPConnection` instances per URL run in parallel.** The Phase 2 gate (`isCenterActive()`) suppresses new legacy connection *creation* but does not tear down existing ones. Double TCP traffic, double subscriptions, race conditions on the same PMP URL.
> 3. **`resetAllData()` causes center token churn on every counter switch.** Every counter change closes the center token and immediately opens a new one.
> 4. **`dispatchToLegacyCallbacks` duplicates `livePricesCallback` line-for-line.** Future fixes to the dispatch logic must be applied to both — a known source of drift.
>
> Modifying a 980-line god class with 30+ consumers, 5 listener variants, and a per-Fragment lifecycle contract is the wrong granularity for this kind of change. The cleaner approach is to leave `PMPUtilViewModel` alone and create a new thin `PMPViewModel` that owns the center lifecycle. Screens migrate one at a time — each migration is independent, fully reviewable, and reversible.

- **New** `PMPViewModel` (~150 lines) — a lifecycle-correct thin wrapper around `PMPConnectionCenter`. Exposes `pmpDataFlow: SharedFlow<PMPUpdate>` carrying topic, indices, raw data, and the `isAllDataReturned` flag. Owns a single `PMPToken` and a single `viewModelScope` collector. Cancels everything in `onCleared()`.
- **Migrate** `NewOrderBottomSheet` (the SR-3738 screen) — replaces `PMPUtilViewModel` + `setOnResponseListener` with `PMPViewModel` + `repeatOnLifecycle(STARTED) { collect }`. This is the FIRST migration.
- **Revert** the `PMPUtilViewModel` adapter (Phase 2 of the original MR) — restore `PMPUtilViewModel` to its pre-MR state. The center is still used via `PMPViewModel`, not via `PMPUtilViewModel`. This eliminates risks #1-#4 above for `NewOrderBottomSheet`.

**Phase 3+ (future MRs, one screen at a time):**

- Migrate `OptionDetailScreen`, `CounterOptionAllTypeScreen`, `TradeTicket*`, `WatchListTab`, `HomeScreen`, `MarketTop*` — each migration is its own MR, its own risk.
- Delete the legacy `PMPUtilViewModel` once the last consumer migrates (probably v3.4 or later — touching 30+ screens in one MR is too much).
- Optional: drop `PmpConnectionPool` once all consumers migrate.

## Capabilities

### New Capabilities

- `pmp-connection-center`: Process-wide singleton managing PMP connection lifecycle with URL-pooled nodes, app foreground/background resumption, topic reference counting, and in-memory price snapshots. Replaces the per-Fragment onPause/onResume pattern with a reactive `SharedFlow`-based API.
- `pmp-subscription-token`: A `Closeable` token that wraps a `SharedFlow` of PMP price updates. Auto-decrements node ref counts on `close()`. Eliminates callback-based `setOnResponseListener()` wiring across all screens.
- `pmp-node-snapshot-cache`: In-memory `topicSnapshots` per `PMPNode` that survive app background. When the app foregrounds, new subscribers receive the last known price as the first emission before live data arrives — matching iOS behavior.
- **`pmp-view-model` (NEW — incremental migration enabler)**: A thin `ViewModel` that owns a single `PMPToken` and exposes `pmpDataFlow: SharedFlow<PMPUpdate>` for fragments to collect via `repeatOnLifecycle(STARTED)`. Decouples PMP lifecycle from the per-Fragment `initPmpConnections / unSubscribeQueryRequest / reSubscribe / disconnectToPMP` rhythm. Each migrated fragment is independent.

### Modified Capabilities

- _(none — `PMPUtilViewModel` adapter is an implementation detail to be reverted in this MR. After revert, `PMPUtilViewModel` is back to its pre-MR state and is no longer changed by this change.)_

## Non-Goals

- Deleting `PMPUtilViewModel` in the same MR (touches 30+ screens; defer to a follow-up after the last consumer migrates).
- Migrating all 30+ Fragment screens in one MR (one screen at a time, ordered by SR-3738 priority).
- iOS-side changes (SR-2875 equivalent already shipped on iOS in April 2026).
- Changes to the `phillip.pmp` library (third-party).
- Persistent price caching across process death (app restart still requires full re-subscription).

## Impact

- **Android only** — iOS already has `HPMPConnectionCenter` from SR-2875.
- **Phase 1 (already landed, commits `6478809a09` → `206e72f7e9`):** Process-wide PMP infrastructure. `PMPConnectionCenter.kt` (326 lines), `PMPNode.kt` (475 lines), `PMPToken.kt` (96 lines), `Application.kt` changes. Phase 1 also added Phase-1-class additions to `PMPUtilViewModel.kt` (data-only `pmpDataFlow`, `pmpToken` field, `pmpDataCollectorJob`, `subscribeViaCenter`) which are **kept**.
- **Phase 2 (this MR):**
  - **Revert** `PMPUtilViewModel.kt` Phase 2 adapter (restore pre-MR state, drop `subscribeViaCenter`, `dispatchToLegacyCallbacks`, `pmpDataFlow`, `pmpToken`, `pmpDataCollectorJob`, `centerEnabled` gate).
  - **New** `viewmodels/common/PMPViewModel.kt` (~150 lines) and `viewmodels/common/PMPUpdate.kt` (~30 lines).
  - **Modified** `ui/screens/trade/options/positions/neworder/NewOrderBottomSheet.kt` (replace `setOnResponseListener` callback with `repeatOnLifecycle(STARTED) { collect }`).
  - **Modified** `viewmodels/common/PMPUtilViewModel.kt` (back to its pre-MR state).
- **Risk:** Low for Phase 2. `NewOrderBottomSheet` is the only screen touched. If migration fails, the revert path is local to one file. Other 29+ screens keep using `PMPUtilViewModel` unchanged.