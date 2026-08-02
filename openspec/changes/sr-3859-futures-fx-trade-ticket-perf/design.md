# SR-3859: Design — Futures/FX Trade Ticket Performance Remediation

## Context

SR-3859 reports "App is laggy, hang and device is hot on Futures/FX order" on both iOS and Android POEMS Mobile 3 v3.3.54. The symptoms appear on the Futures/FX → Order tab → tap any order flow. The reporter (`lytruong`) attached a screen recording of the Android side (`20260617_162251.mp4`).

Investigation on the release worktrees (`release/v3.3.54_27_06_2026` for iOS, `release/v3.3.54_develop_27_06_2026` for Android) identified two compounding anti-patterns unique to the Futures/FX order hot path:

### iOS hot path
1. `TradeFuturesViewModel.sortByKey()` calls `self.objectWillChange.send()` at line 45, forcing a full SwiftUI body re-evaluation on every column tap. The preceding `@Published` assignment at lines 41-43 already triggers an update; the `send()` is a redundant sledgehammer.
2. `TBSFuturesViewModel.currentOrderTypeIndex` and `currentActionIndex` have `didSet { mapTradeInfo() }` observers (lines 29-40). `mapTradeInfo()` re-allocates `actions`/`orderTypes`/`validity` and recomputes `submittedPrice` via `makeStringMoney(...)`. Both observers fire on the same RunLoop turn when PMP pushes a new bid/ask mid-tap, causing two full reruns per PMP tick.
3. `orderTradeInfo` is mutated (e.g., `bidPrice = value` in `handleBidPriceFromPMP`) but is *not* `@Published`, so the price flow routes through the upstream `@Published counterPricePMPModel` and triggers `mapTradeInfo()` for *every* PMP message — typically 4×/sec, ×3 fields = 12 reruns/sec.
4. `getFuturesData()` retains `self` via `DispatchGroup.notify(queue: .main)` for the futures/order-info/account-summary chain. Only the `getOrderTradeInfo` closure uses `[weak self]`. The other two retain; if the screen is popped mid-load, the VM stays alive and keeps the PMP callback chain alive, defeating SwiftUI view teardown.

### Android hot path
1. `TopPriceDetailCounterFutureFX.updateTopDetailWithPMP()` writes `mCounterInForDetailFutures.value = counterDetailValue` at line 176 on every PMP tick. This re-fires the observer at line 205 (which runs `updateUICounterInfo(...)` + `initPmpConnections()`) and every other listener on the LiveData — including the upstream `mTopPricesPMPUtilViewModel` callback registered at line 89-96. The result is a self-reinforcing observer loop.
2. `PMPUtilViewModel.getFinalHashMapPmpResponse()` (lines 188-204) does `mListColumnPmpEnum.firstOrNull { it.split(",").contains(hashMapValue.key) }` for every key of every tick. That's ~30 string-split allocations per tick × 4 ticks/sec × 8 fields = ~960 allocations/sec.
3. `PMPUtilViewModel.handleConnectPMP()` is recursive without backoff (lines 715-763). If the URL list is stale, it spins on `Dispatchers.Default`.
4. `mIsFirstPMPUpdate` flag (line 88) flips on every empty `LinkedHashMap` payload but does not prevent the empty-payload re-fire cycle from triggering the LiveData observer.

### Cross-cutting
- The Position list, Order list, Order detail, and Price header all independently subscribe to PMP for the same counter on the same screen stack. There is no per-(counter, screen-stack) coordinator.
- The `jira-skill` bundle analyzer classifies the bug as `Performance / Slow Loading` and recommends pagination/lazy loading and caching — both align with deduplicating subscriptions + adding a price-stream-level cache.

### Prior art
- `android-pmp-connection-center` (MR !23433, target `release/v3.3.54_develop_27_06_2026`) introduces `PMPConnectionCenter` + `PMPViewModel` and migrates `NewOrderBottomSheet`. The Trade screens were *not* migrated in that MR — this change is the natural follow-on.
- The Trade ticket UI rewrite (`feature_TJ_1656` / MR !17803, Draft) is a separate, much larger effort and explicitly out of scope.

### Stakeholders
- `lytruong` (reporter, QA) — needs the round test `Mainflow_3.3.54_3` to pass.
- `Dev Andrew (MinhNV)` (assignee) — owns the implementation.
- iOS + Android Trade module owners — review the per-platform contracts.

## Goals / Non-Goals

### Goals
- Reduce main-thread work on the Futures/FX Order tab to ≤ 1 full view rebuild per second under a recorded 50-tick/sec PMP burst.
- Eliminate duplicate PMP subscriptions per counter per screen stack on both platforms.
- Add CI-gated regression tests that fail the build if a future change reintroduces the LiveData self-mutation pattern or the redundant `objectWillChange.send()`.
- Extend the `PMPConnectionCenter` pattern from `NewOrderBottomSheet` into the Trade screens without breaking the v3.3.54 release timeline.

### Non-Goals
- We are NOT replacing the existing `PMPConnectionCenter` / `PMPViewModel` infrastructure. We are reusing its pattern via a screen-scoped coordinator.
- We are NOT rewriting the trade ticket UI (covered by `feature_TJ_1656`).
- We are NOT changing the PMP protocol, server contract, or network layer.
- We are NOT touching the equity order ticket — the bug is specific to the Futures/FX code path.
- We are NOT attempting to fix the "biggest font + Traditional Chinese" rendering cost itself.

## Decisions

### D1. Screen-scoped PMP coordinator (not global singleton)
**Choice**: Per-screen-stack `PmpSubscriptionCoordinator` (iOS) / `PMPTicketSubscription` (Android) that owns the listener list and dispatches a deduplicated `Flow<PriceTick>` to N consumers.

**Alternatives considered**:
- *Global `PMPConnectionCenter` singleton across the app* (already introduced for `NewOrderBottomSheet`). Rejected for v3.3.54 because it requires migrating all PMP callers in the Trade module; that's a larger blast radius than the v3.3.54 hotfix warrants. The screen-scoped coordinator gives us 80% of the benefit (no duplicate listeners) with 20% of the risk.
- *Weak-reference table per counter*. Rejected because PMP topics are short-lived and the dedup logic is the same regardless of lifetime.

**Rationale**: Matches the prior `android-pmp-connection-center` pattern at smaller scope; the global migration can be done as a follow-up change.

### D2. Coalesce + distinct-by-frame on the price stream
**Choice**: iOS uses a `removeDuplicates().throttle(for: .milliseconds(16), latest: true)` chain on the `Publisher` that the coordinator emits. Android uses a `Channel(Channel.CONFLATED)` consumed by a single coroutine, plus `Flow.distinctUntilChanged()` on `mCounterInForDetailFutures`.

**Alternatives considered**:
- *Debounce (e.g., 100ms)*. Rejected because it would introduce visible lag on legitimate price changes.
- *Throttle to 1Hz*. Rejected because it would lose the 4Hz tick rate that the UI needs for animated price flashes.

**Rationale**: 16ms = one display frame. Coalescing-by-frame preserves the visual tick rate (4Hz) without re-rendering 4 times within the same frame. `distinctUntilChanged` filters out no-op updates where the server re-sends the same price.

### D3. Move heavy formatting off the main thread
**Choice**: iOS `mapTradeInfo()` is debounced via `DispatchQueue.main.async` coalesce, and the actual `makeStringMoney(...)` work runs on `DispatchQueue.global(qos: .userInitiated)`. Android `pbPercentSVolkBVolk.progress` calculation runs in a `Dispatchers.Default` mapper that produces a pre-formatted `CharSequence`.

**Alternatives considered**:
- *Actor isolation*. Rejected because the Swift migration to actors in the Trade module is not done; introducing one here would be a one-off.
- *Run on main with no debounce*. This is the current state; it's what we're fixing.

**Rationale**: Mirrors the prior `TBSFuturesViewModel.handleBidPriceFromPMP` pattern (which already uses `DispatchQueue.global` for the actual string conversion) and extends it to the price-formatting chain.

### D4. Remove the redundant `objectWillChange.send()` in iOS
**Choice**: Delete the call at line 45. The `@Published listDataGroup` assignment at lines 41-43 already triggers the UI update.

**Alternatives considered**:
- *Replace with `objectWillChange.send()` of a nested observable*. Rejected because there's no nested observable — `listDataGroup` is the single source of truth.

**Rationale**: This is a pure deletion with no behavior change beyond removing the redundant rebuild. Safe.

### D5. Replace per-tick `MutableLiveData.value = X` with `MediatorLiveData<UiState>` + distinct
**Choice**: `mCounterInForDetailFutures` becomes a `MediatorLiveData<UiState>` with a `distinctUntilChanged()` upstream operator in `PMPUtilViewModel`. UI updates only when the *new state* differs from the prior state (compared by `bid`/`ask`/`lastDone` only — not by reference).

**Alternatives considered**:
- *SingleLiveEvent*. Rejected because we need to broadcast the *current* state, not a one-shot event.
- *StateFlow with `distinctUntilChangedBy`*. Viable but requires migrating all collectors; the v3.3.54 timeline doesn't allow it.

**Rationale**: Minimal-change remediation that solves the self-fire loop without a full coroutine migration.

### D6. Pre-compute PMP field lookup map
**Choice**: At `PMPUtilViewModel` construction time, build `private val mPmpFieldLookup: Map<String, String> = build { ... }` once. `getFinalHashMapPmpResponse()` becomes a single `mPmpFieldLookup[key]?.let { finalHashMap[it] = value }` per key. No more linear scan, no more `String.split(",")` per tick.

**Alternatives considered**:
- *Build the map lazily on first use*. Rejected because the construction cost is one-time and predictable; the lazy path would re-introduce the linear scan on cold start.

**Rationale**: O(N) → O(1) per key with no allocation.

### D7. Exponential backoff on `handleConnectPMP()`
**Choice**: Backoff 50ms → 100ms → 200ms → 500ms → max depth 5. After max depth, log to `Timber.tag("PMP-Failover")` and bail out (the upstream health check will trigger a retry on the next user action).

**Alternatives considered**:
- *Linear backoff*. Rejected because the recursion is depth-bounded; exponential matches the existing webhook failover pattern in `webhook-receiver`.
- *Indefinite retry*. This is the current state and is part of the bug.

**Rationale**: Bounded retry prevents `Dispatchers.Default` starvation.

### D8. New regression test fixtures
**Choice**: 
- iOS: `PmpCoalescingTests` XCTest bundle with a recorded 50-tick/sec burst replay fixture (5 seconds). Asserts: `mapTradeInfo()` invocations ≤ 6 per second; no `objectWillChange.send()` calls during replay; `PmpSubscriptionCoordinator` dispatches exactly 1 `PriceTick` per actual price change.
- Android: `TradeTicketFutureFXPerformanceTest` (Robolectric + Compose UI test) with a `FakePmpEventListener` that emits 50 ticks/sec for 5 seconds. Asserts: `mCounterInForDetailFutures` observer fires ≤ 6 per second; `updateTopDetailWithPMP` invocations ≤ 6 per second; no `binding` null-dereference.

**Alternatives considered**:
- *Espresso macro benchmark*. Rejected because the bug manifests at the LiveData/SwiftUI level, not the rendered frame level. The unit-level test is more precise.
- *Live network replay*. Rejected because it would be flaky and require a test PMP server.

**Rationale**: Deterministic, fast, runs in CI.

### D9. Extension to `jira-skill` and `ai-review`
**Choice**: 
- `jira-skill` `analysis.py` adds `category: performance_live_data_loop` to `RootCauseCategory`. New rule: if any issue summary has `category == performance` and the bundle contains a `MutableLiveData` or `objectWillChange` symbol match, emit the sub-tag.
- `ai-review` prompt template gains a section "Trade/PMP hot-path invariants" injected when the diff matches `TradeFutures*`, `TopPriceDetailCounter*`, or `PMP*` file patterns.

**Alternatives considered**:
- *No tooling changes, rely on code review*. Rejected because the same bug class has now manifested in SR-3323, SR-3223, SR-3319, and SR-3859 — a code-review-only approach has demonstrably failed.

**Rationale**: Make the regression visible at PR time so it doesn't recur.

## Risks / Trade-offs

- **[Risk] Touching the hot PMP path could introduce subtle ordering bugs** → Mitigation: gate the change behind a `feature_flag_pmp_coalescing` (iOS) / `BuildConfig.PMP_COALESCING_ENABLED` (Android) default-on flag, plus the regression test fixtures. Roll back by toggling the flag.
- **[Risk] The `PmpSubscriptionCoordinator` is a new pattern that future Trade screen authors may not adopt** → Mitigation: include a `// SR-3859: ALL Trade screens MUST obtain PMP through PmpSubscriptionCoordinator` header comment in the new file and a lint check in the iOS module.
- **[Risk] Backport friction — v3.3.54 is a release branch and we may need to ship to `release/v3.3.54_develop_27_06_2026` while `android-pmp-connection-center` MR !23433 is still in review** → Mitigation: keep the worktree branch `bugfix/SR-3859-futures-fx-perf` independent of MR !23433. If MR !23433 merges first, rebase SR-3859 onto the updated tip and drop the screen-scoped coordinator in favor of the global one for the migrated screens.
- **[Risk] `MediatorLiveData<UiState>` migration may break observers that depend on the imperative `setValue` semantics** → Mitigation: keep `mCounterInForDetailFutures` as a public alias to the new MediatorLiveData; existing observers continue to work unchanged.
- **[Risk] Tests recorded at 50 tick/sec may not reflect production 4 Hz** → Mitigation: the test asserts ≤ 6 rebuilds/sec, which gives 50% headroom over the production 4Hz rate × 1 coalesced frame.

## Migration Plan

1. **Cut worktrees** (already done): `poems-mobile3-android-sr3859-perf` from `origin/release/v3.3.54_develop_27_06_2026` @ `e924f02c72`; `poems-mobile3-ios-sr3859-perf` from `origin/release/v3.3.54_27_06_2026` @ `56b419e447`. Both branched as `bugfix/SR-3859-futures-fx-perf`.
2. **Implement Android fixes** on the Android worktree:
   - Add `PMPTicketSubscription.kt` + `PriceTickCoalescer.kt`.
   - Migrate `TopPriceDetailCounterFutureFX.updateTopDetailWithPMP()` to consume from `PMPTicketSubscription` and write to `MediatorLiveData<UiState>` with `distinctUntilChangedBy { it.bid }`.
   - Migrate `PMPUtilViewModel.getFinalHashMapPmpResponse()` to use pre-computed `mPmpFieldLookup`.
   - Add `handleConnectPMP()` backoff.
   - Add `TradeTicketFutureFXPerformanceTest`.
3. **Implement iOS fixes** on the iOS worktree:
   - Add `PmpSubscriptionCoordinator.swift` + `PriceTickDeduplicator.swift`.
   - Migrate `TradeFuturesViewModel.sortByKey()` to drop `objectWillChange.send()`.
   - Migrate `TBSFuturesViewModel` to consume from `PmpSubscriptionCoordinator`, debounce `mapTradeInfo()`, convert `orderTradeInfo` to `@Published`.
   - Add `PmpCoalescingTests`.
4. **Run regression tests** in both worktrees; attach test output to the change folder as `verification.md`.
5. **Update tooling** (in `tdt-meta`):
   - `jira-skill` `analysis.py`: add `performance_live_data_loop` category.
   - `ai-review` prompt template: add Trade/PMP invariants section.
6. **Open MRs**:
   - Android: target `release/v3.3.54_develop_27_06_2026`.
   - iOS: target `release/v3.3.54_27_06_2026`.
7. **Validation gate**: AI review must check that the diff does not re-introduce `MutableLiveData.value = X` in `updateTopDetailWithPMP` and does not re-introduce `objectWillChange.send()` in `sortByKey`.
8. **Rollback**: All changes are gated behind a feature flag. Disable the flag, rebuild, redeploy via the existing `webhook-receiver` / `ai-review` deploy scripts (`bash scripts/deploy.sh` per repo).
9. **Archive**: After MRs merge, run `/opsx:verify` then `/opsx:archive sr-3859-futures-fx-trade-ticket-perf`.

## Open Questions

- OQ1. Should the screen-scoped coordinator be merged into the global `PMPConnectionCenter` introduced by MR !23433 once that MR lands, or kept as a separate pattern? **Owner**: `Dev Andrew (MinhNV)`. **Due**: before archive. **Default if unresolved**: keep separate (lower risk, smaller blast radius).
- OQ2. Does the BigSur-style "biggest font + zh-Hant" pre-condition affect the iOS `mapTradeInfo()` work the same way as Android `updateTopDetailWithPMP`, or is the iOS amplification dominated by `objectWillChange.send()`? **Owner**: iOS reviewer. **Default if unresolved**: profile both, ship the fix that has the higher measured win.
- OQ3. Should the regression test fixtures ship as part of the v3.3.54 hotfix, or as a follow-up? **Default if unresolved**: ship with the fix; the test is what prevents regression.
