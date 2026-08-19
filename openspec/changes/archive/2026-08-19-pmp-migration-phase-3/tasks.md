# Tasks: pmp-migration-phase-3

## Spec Phase (S1)

- [x] Write `proposal.md` (DONE — see file)
- [x] Write `design.md` (DONE — see file)
- [x] Write `specs/pmp-update-contract.md` (DONE — see file)
- [x] Write `specs/pmp-node-submit-request.md` (DONE — see file)
- [x] Write `specs/pmp-center-subscribe-history.md` (DONE — see file)
- [x] Write `specs/pmp-viewmodel-contract.md` (DONE — see file)
- [x] Write `specs/fragment-lifecycle-contract.md` (DONE — see file)
- [x] Write `tasks.md` (this file)
  - All 8 spec files verified to exist. `openspec validate --strict pmp-migration-phase-3` → exit 0.

## Spec Gate (S2)

- [x] Self-review: every MUST/SHALL in the 5 spec files is testable
- [x] Self-review: acceptance criteria cover happy path + 3 failure modes each
- [x] Self-review: no spec item depends on unspecified implementation detail
- [x] Self-review: consistent with `MarketTopBaseFragment` and `NewOrderBottomSheet` patterns
- [x] Self-review: at least one unit test sketched for each MUST
  - **Issue found & resolved:** `pmp-center-subscribe-history.md` originally described a `PMPToken` with `requestType` field; the design.md Decision 2 (and `pmp-viewmodel-contract.md` §1.3, §2.1) had revised this to a dedicated `PMPQueryToken` class for type safety. Spec and proposal.md updated to reflect the design decision.

## T1: Center Extensions

- [ ] Add `PMPUpdateKind` enum and `chartData` field to `PMPUpdate`; `init {}` invariant assertion
- [ ] Update 4 already-migrated screens to pass `kind = ...` to `PMPUpdate(...)` constructor:
  - `MarketTopBaseFragment.kt` → `LIVE`
  - `MarketTopDetailBaseScreen.kt` → `LIVE`
  - `TabMarketStockScreen.kt` → `LIVE`
  - `NewOrderBottomSheet.kt` → `USSO`
- [ ] Create `PMPQueryToken.kt` (sibling of `PMPToken`, typed for chart data)
- [ ] Add `subscribeForHistory()` to `PMPConnectionCenter` (resolves historical URL, returns `PMPQueryToken?`)
- [ ] Add `unsubscribeQuery(token: PMPQueryToken)` to `PMPConnectionCenter` (decrement historical node ref-count)
- [ ] Rename `PMPNode.submitSubscribe` → `submitRequest(topics, fieldMap, requestType)` (internal)
- [ ] Add `PMPNode.subscribeForHistory(...)` (public, type-safe callback for chart data)
- [ ] Add `PMPViewModel.subscribeForHistory(counters, fields)` (public, opens `_queryToken`)
- [ ] Add `PMPViewModel._queryToken`, `queryCollectorJob`, `mChartTopicIndexMap`, `pmpQueryToken`
- [ ] Update `PMPViewModel.detach()` to cancel both collectors
- [ ] Update `PMPViewModel.unsubscribe()` to close both tokens
- [ ] Add `onQueryTokenReady()` private method
- [ ] Update QUERY collector to emit `PMPUpdate(QUERY, ...)`
- [ ] Write `PMPUpdateTest`: invariant assertions for LIVE/QUERY/USSO
- [ ] Write `PMPNodeTest`: `submitRequest` SUBSCRIBE/UNSUBSCRIBE/QUERY, state guard
- [ ] Write `PMPConnectionCenterTest`: `subscribeForHistory` happy path, null PMPSettingModel, mixed counters
- [ ] Write `PMPViewModelTest`: `subscribeForHistory` idempotent, both tokens coexist, detach/unsubscribe semantics
- [ ] Run `gitnexus detect_changes` for review

## T2: P0 Migration

- [ ] Add `BuildConfig.FEATURE_PMP_CENTER_HOME` (default `false`)
- [ ] Add `BuildConfig.FEATURE_PMP_CENTER_WATCHLIST` (default `false`)
- [ ] Add the flags to `app/build.gradle`
- [ ] Migrate `WatchListTab.kt` (handleLive fan-out, handleQuery for charts, feature flag)
- [ ] Migrate `HomeScreen.kt` (remove 4 disconnect+reset pairs, feature flag)
- [ ] Manual QA: tab switch preserves token, chart renders, no reconnect storm
- [ ] Verify in side-by-side: legacy `PMPUtilViewModel` path vs new `PMPViewModel` path produce same data
- [ ] Toggle `FEATURE_PMP_CENTER_WATCHLIST` and `FEATURE_PMP_CENTER_HOME` to `true` in UAT
- [ ] QA sign-off

## T3: P1 Batch

- [ ] Add `BuildConfig.FEATURE_PMP_CENTER_P1` (default `false`)
- [ ] Migrate `CounterDetailScreen.kt` (remove `resetAllData()` in `loadData()`; add `detach()` in `onPause`, `unsubscribe()` in `onDestroyView`)
- [ ] Migrate `OptionDetailScreen.kt` (remove `resetAllData()` in `initPmpConnectionsRatesSO()`; add `unsubscribe()` in `onDestroyView`)
- [ ] Migrate `MarketDepthTab.kt` (remove `repeatOnLifecycle(RESUMED)` wrapper)
- [ ] Migrate `TradeSummaryTab.kt` (remove `repeatOnLifecycle(RESUMED)` wrapper)
- [ ] Manual QA: counter detail flows, option flow, market depth, trade summary
- [ ] Toggle `FEATURE_PMP_CENTER_P1` to `true` in UAT; QA sign-off

## T4: P2 Batch

- [ ] Add `BuildConfig.FEATURE_PMP_CENTER_P2` (default `false`)
- [ ] Migrate `MarketDepthTabFutures.kt`
- [ ] Migrate `TopPriceDetailCounterFX.kt` (add `detach()` in `onPause`)
- [ ] Migrate `CounterListSectionFragment.kt`
- [ ] Migrate `CounterPriceDetailHeader.kt` (add missing `onPause`)
- [ ] Migrate `CounterDetailScreenST.kt`
- [ ] Migrate `OptionCounterScreen.kt`
- [ ] Manual QA: each counter detail sub-screen, FX, futures
- [ ] Toggle `FEATURE_PMP_CENTER_P2` to `true` in UAT; QA sign-off

## T5: P3 Batch + Legacy Deletion

- [ ] Migrate `TabIdeas.kt`
- [ ] Migrate `TopPriceDetailCounter.kt` (base class — propagates to `TopPriceDetailCounterST.kt`)
- [ ] Manual QA: discover screen, stock detail
- [ ] `gitnexus_impact PMPUtilViewModel` — confirm zero callers
- [ ] `gitnexus_impact PMPEventListener` — confirm zero callers
- [ ] `gitnexus_impact CounterForPMPModel` — confirm zero callers
- [ ] `gitnexus_impact PmpConnectionPool` (the `object` in `PMPUtilViewModel.kt`) — confirm zero callers
- [ ] Delete `PMPUtilViewModel.kt`
- [ ] Delete `PmpConnectionPool` (object inside the deleted file)
- [ ] Delete `CounterForPMPModel.kt`
- [ ] Delete `PMPEventListener.kt`
- [ ] Remove the 4 feature flags from `app/build.gradle`
- [ ] Remove the `if (BuildConfig.FEATURE_PMP_CENTER_*)` branches from each migrated fragment
- [ ] Run `gitnexus detect_changes` for review
- [ ] Run full test suite + ruff lint + mypy
- [ ] Run the manual QA checklist one more time end-to-end
- [ ] `/opsx:archive pmp-migration-phase-3`
