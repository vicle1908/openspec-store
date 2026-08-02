# SR-3859: Futures/FX Trade Ticket — Performance & Thermal Hot-Path Remediation

## Why

POEMS Mobile 3 v3.3.54 (`Mainflow_3.3.54_3` round test) exhibits app-wide lag, ANR-grade hangs and device thermal heating on the **Futures/FX → Order tab → tap any order** flow. The symptom is reproducible on both Android (Realme 9 / Android 13) and iOS (iPhone 11 Pro Max / iOS 26.0.1) when the system font is set to the largest available size and the locale is Traditional Chinese (`zh-Hant`). The reporter (`lytruong`) opened [SR-3859](https://psplit.atlassian.net/browse/SR-3859) as High priority, labeled `BUC_CORE` / `BUC_NON_FUNC`. We must land a remediation in the v3.3.54 release branch (or v3.3.55 patch) because the regression blocks the QA round test from passing.

Code investigation on the release worktrees (`release/v3.3.54_27_06_2026` for iOS, `release/v3.3.54_develop_27_06_2026` for Android) identified **two compounding hot-path patterns** unique to the Futures/FX order flow that are not present on the equity order flow:

1. **Android**: `TopPriceDetailCounterFutureFX.updateTopDetailWithPMP()` writes back to `mCounterInForDetailFutures.value` on every PMP tick, which re-fires its own observer chain (observer at line 205 of the same file runs `updateUICounterInfo` + `initPmpConnections`, and `mTopPricesPMPUtilViewModel` re-broadcasts the new state to every listener). This is a self-reinforcing LiveData loop amplified by the PMP Gson parsing hot path in `PMPUtilViewModel.getFinalHashMapPmpResponse()` (linear scan + per-tick `String.split(",")` allocations).
2. **iOS**: `TradeFuturesViewModel.sortByKey()` calls `objectWillChange.send()` (forces a full SwiftUI rebuild) *and* `TBSFuturesViewModel.currentOrderTypeIndex`/`currentActionIndex` `didSet` observers call `mapTradeInfo()` (heavy `makeStringMoney(...)` re-formatting) on every PMP tick via the `@Published counterPricePMPModel` chain. The `orderTradeInfo` model is mutated but not `@Published`, so updates flow through the upstream channel and trigger a duplicate re-render every tick.

Both platforms share the architectural smell: **a single PMP subscription fan-outs to many downstream `@Published` / `MutableLiveData` observers, with no `distinctUntilChanged`, no debouncing, and — critically — duplicate PMP subscriptions** because the position list, order list, order detail, and price header all independently subscribe to the same counter on the same screen stack.

The `jira-skill` bundle analyzer classifies SR-3859 as `Performance / Slow Loading` (root_cause category `performance`, fix_status `in_progress`) and recommends *"Implement pagination/lazy loading for large data sets"* and *"Add caching layer for repeated operations"* — both align with our findings (deduplicated PMP subscriptions + a price-stream-level cache are the two highest-leverage remediations). The previously completed `android-pmp-connection-center` change (MR !23433, target `release/v3.3.54_develop_27_06_2026`) introduces `PMPConnectionCenter` and `PMPViewModel` and migrates `NewOrderBottomSheet`, but **does not yet migrate Trade screens** — this change is the natural follow-on that extends the PMP singleton pattern into the Futures/FX order ticket and detail screens.

## What Changes

- **Deduplicate PMP subscriptions per counter** (both platforms). The Order list, Order detail, Position list, and Price header share one PMP stream per (counter, screen-stack) instead of N independent subscriptions. Implemented as a screen-scoped `PmpSubscriptionCoordinator` (iOS, Swift) and `PMPTicketSubscription` wrapper (Android, Kotlin) that owns the listener list and dispatches a deduplicated `Flow<PriceTick>`.
- **Add `distinctUntilChanged` + coalesce-by-frame** on the PMP price stream feeding `@Published` / `MutableLiveData`. iOS uses a `.removeDuplicates().throttle(for: .milliseconds(16), latest: true)` operator chain. Android uses a `Channel(Channel.CONFLATED)` consumed by a single coroutine, plus `Flow.distinctUntilChanged()` on `mCounterInForDetailFutures`.
- **Move heavy price-formatting off the main thread.** `TBSFuturesViewModel.mapTradeInfo()` and `makeStringMoney(...)` are debounced to the next run-loop tick and only the final `@Published` mutation happens on main. Android side: `pbPercentSVolkBVolk.progress` calculation moves to a `Dispatchers.Default` mapper that produces a pre-formatted `CharSequence` and posts to `binding?.root` via `view.post {}`.
- **Remove the redundant `objectWillChange.send()` in `TradeFuturesViewModel.sortByKey()`.** The `@Published` assignment already triggers UI update.
- **Replace per-tick `MutableLiveData.value = X` self-mutation** with a `MediatorLiveData<UiState>` that ignores no-op transitions and a `distinctUntilChangedBy { it.bid }` upstream operator in `PMPUtilViewModel.livePricesCallback`.
- **Pre-compute PMP field lookup table** in `PMPUtilViewModel` so `getFinalHashMapPmpResponse()` is O(1) per key (eliminates per-tick `mListColumnPmpEnum.firstOrNull { ... it.split(",") }` linear scan + allocation).
- **Add exponential backoff (50 → 100 → 200 → 500 ms, max depth 5) to `PMPUtilViewModel.handleConnectPMP()`** to prevent recursive spin when URL list is flaky.
- **New regression test fixtures**: snapshot-based unit tests that replay a recorded PMP burst (≥50 ticks/sec for 5 sec) and assert (a) `mapTradeInfo()` invocations ≤ N+1 per second, (b) `mCounterInForDetailFutures` fires ≤ N+1 per second, (c) no `objectWillChange.send()` calls during replay.

## Capabilities

### New Capabilities

- `pmp-price-stream-coalescing`: Cross-cutting specification for the screen-scoped PMP subscription coordinator and the coalesce/distinct pipeline applied to the Futures/FX order flow. Defines the dispatch contract, lifecycle hooks, and observability hooks that the two mobile platforms must implement against.
- `trade-ticket-pmp-anti-regression`: Regression test contract for the Futures/FX order hot-path. Defines the recorded burst-fixture format, the invariants that must hold (max main-thread work per second, no `objectWillChange.send()` per tick, LiveData observer fires ≤ 1 per actual price change), and the CI gate that runs against the v3.3.54 release worktrees.

### Modified Capabilities

- `ticket-intelligence-core`: Extend the `jira-skill` `RootCauseBundle` with a new `category: performance_live_data_loop` sub-tag so future LiveData re-fire bugs land in the same category as SR-3859.
- `ai-review-validation-consistency`: When the diff touches files under `TradeFutures*`, `TopPriceDetailCounter*`, or `PMP*`, surface a checklist in the AI review that points reviewers at the relevant invariants from `trade-ticket-pmp-anti-regression`.

## Impact

- **Affected repos**:
  - `poems-mobile3-ios` — `Pmobile3/Modules/Trade/TradeFutures/**`, `Pmobile3/Modules/Trade/TradeBuySellScreen/Futures/**`, `Pmobile3/Modules/Trade/Base/ViewModels/TradeBaseViewModel.swift`. New files: `Pmobile3/Modules/Trade/Common/PMP/PmpSubscriptionCoordinator.swift`, `Pmobile3/Modules/Trade/Common/PMP/PriceTickDeduplicator.swift`.
  - `poems-mobile3-android` — `app/src/main/java/com/tdt/pmobile3/ui/screens/trade/tradeticket/tradeticketfutures/**`, `app/src/main/java/com/tdt/pmobile3/ui/screens/trade/tradeticket/tradeticketFX/**`, `app/src/main/java/com/tdt/pmobile3/ui/screens/watchlists/counterdetail/common/TopPriceDetailCounterFutureFX.kt`, `app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUtilViewModel.kt`. New files: `app/src/main/java/com/tdt/pmobile3/pmpmodule/PMPTicketSubscription.kt`, `app/src/main/java/com/tdt/pmobile3/ui/screens/trade/common/PriceTickCoalescer.kt`.
- **Affected Jira**: SR-3859 (this), SR-3738 (related `android-pmp-connection-center` follow-on), SR-3323/SR-3223/SR-3319 (prior related perf bugs), SR-3729 (iOS trade ticket multiple-tap bug — sibling MR !17755).
- **Affected GitLab MRs**: SR-3738 MR !23433 (target: `release/v3.3.54_develop_27_06_2026`), SR-3729 MR !17755 (target: `release/v3.3.54_27_06_2026`). This change cherry-picks onto both release branches via dedicated worktrees `bugfix/SR-3859-futures-fx-perf` (Android + iOS).
- **Affected tests**: New `poems-mobile3-ios` XCTest bundle `PmpCoalescingTests`; new `poems-mobile3-android` Robolectric/Compose UI test `TradeTicketFutureFXPerformanceTest`.
- **Affected downstream tooling**: `jira-skill` `analysis.py` adds `performance_live_data_loop` to `RootCauseCategory`. `ai-review` prompt template gains a section "Trade/PMP hot-path invariants" injected when the diff matches the file patterns above.
- **Non-goals** (explicit):
  - We are NOT replacing the existing `PMPConnectionCenter` / `PMPViewModel` infrastructure introduced in `android-pmp-connection-center`. We are extending its pattern into the Trade screens via a screen-scoped coordinator; full migration to the global `PMPConnectionCenter` for all Trade screens is a separate change.
  - We are NOT rewriting the trade ticket UI (`feature_TJ_1656` / MR !17803 already in flight as a Draft).
  - We are NOT changing the PMP protocol, the server contract, or the network layer.
  - We are NOT touching the equity order ticket — the performance bug is specific to the Futures/FX code path.
  - We are NOT attempting to fix the "biggest font + Traditional Chinese" rendering cost itself; we are ensuring the hot-path code does not *amplify* the rendering cost via redundant re-renders.
