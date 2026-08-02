## Why

The TopMarket screen family (`MarketTopDetailBaseScreen`, `MarketTopBaseFragment`, `TabMarketStockScreen`, `IndicesDetailScreen`) — ~4,000 lines across 4 files — still uses the legacy `PMPUtilViewModel` callback pattern (`setOnResponseListener`, `setOnResponseListenerUSSO`). The first incremental migration (`NewOrderBottomSheet`, landed in `android-pmp-connection-center` Phase 2) proved the `PMPViewModel` + `repeatOnLifecycle(STARTED) { collect }` pattern works and resolves the SR-3738 bottom-sheet lifecycle bug. The Market Top tab is the next-highest-priority migration because (a) it is the primary "discover counters" surface, (b) the base screen is the parent of multiple subclasses, so the migration pattern established here becomes the template for the remaining 27+ PMP consumer screens, and (c) `IndicesDetailScreen` is the only file in the entire PMP codebase that exercises the 4-arg `setOnResponseListener(pmpTopic, linkedHashMap, isAllDataReturned)` variant — migrating it forces the long-deferred `isAllDataReturned` sentinel implementation (parent change task §13.3) to land at the same time.

## What Changes

- **Migrate** `MarketTopDetailBaseScreen.kt` (1328 lines) — replace `mMarketPMPUtilVM.setOnResponseListener { topic, linkedHashMap, _ -> ... }` (line 894) with `pmpViewModel.pmpDataFlow.collect { onPmpReceived(it) }`. The screen uses topic-keyed dispatch via `getIndexByTopic(topic)`, which maps directly onto `PMPUpdate.indices` fan-out.
- **Migrate** `MarketTopBaseFragment.kt` (715 lines) — replace positional `setOnResponseListener { index, linkedHashMap -> ... }` (line 506) with topic-keyed dispatch via `pmpViewModel.pmpDataFlow`.
- **Migrate** `TabMarketStockScreen.kt` (1608 lines) — same pattern as `MarketTopBaseFragment`.
- **Migrate** `IndicesDetailScreen.kt` (366 lines) — replace 4-arg `setOnResponseListener { pmpTopic, linkedHashMap, isAllDataReturned -> ... }` (line 81). This screen is the **first consumer of `PMPUpdate.isAllDataReturned`**, which forces the sentinel to be implemented (see MODIFIED spec).
- **Modify** `PMPViewModel.subscribe()` — implement the `isAllDataReturned` sentinel that has been hardcoded `false` since Phase 2 (parent change task §13.3). The algorithm: on each emission, increment a per-subscribe `emissionCounter`; when the counter reaches the size of `mHashmapIndexOfCounter` (the number of distinct PMP topics in the current subscription), set `isAllDataReturned = true` for that emission and reset the counter. Edge case: when only one topic is subscribed, every emission carries `isAllDataReturned = true` (the batch is always complete after one tick).
- **Modify** `PMPViewModel.subscribe()` — restore `aliasFields()` on every emission so that the `data` field of `PMPUpdate` is keyed by the canonical `WatchListColumnsSettingModel.value` strings (e.g., `"9,F009,P23"` for `TRADE_PRICE`), NOT raw PMP FIDs. This restores the legacy semantic that all current consumers (`NewOrderBottomSheet.onUnderlyingPmpReceived`, `NewOrderBottomSheet.onGeneralPmpReceived`, `MarketStockViewModel.updateDataForTopMarket`) rely on when they do `linkMapPMP[PMPFieldsForSetting.X.columnsSettingModel.value]` lookups. Without aliasing, the migrated screens will silently show empty price fields (the lookups return null because the data is keyed by raw FIDs like `"9"`, not the canonical alias). The PMPNode returns raw data; the aliasing happens at the PMPViewModel layer to keep PMPNode screen-agnostic.
- **No new classes or files** beyond edits to existing files. The `PMPUpdate` data class is unchanged.

## Capabilities

### New Capabilities

_None — this sub-change reuses capabilities introduced by the parent change `android-pmp-connection-center` (`pmp-view-model`, `pmp-connection-center`, `pmp-subscription-token`, `pmp-node-snapshot-cache`). The TopMarket screens are consumers of `pmp-view-model`, not extensions of it._

### Modified Capabilities

- `pmp-view-model`: Two requirement changes are needed:
  1. The `PMPViewModel.subscribe()` algorithm MUST compute `isAllDataReturned` correctly per the requirements in `specs/pmp-view-model/spec.md` (Requirement: "PMPViewModel computes isAllDataReturned sentinel per topic batch"). This is the production implementation of the placeholder field that has been hardcoded `false` since Phase 2 of the parent change.
  2. The `PMPViewModel.subscribe()` collector MUST call `aliasFields(rawData, subscribeFields)` on every emission before calling `_pmpDataFlow.tryEmit(...)` so that the `PMPUpdate.data` field uses canonical field IDs (`WatchListColumnsSettingModel.value` strings like `"9,F009,P23"`) instead of raw PMP FIDs (`"9"`, `"F001"`, etc.). Without this, all migrated screens that look up fields via `linkMapPMP[PMPFieldsForSetting.X.columnsSettingModel.value]` will silently fail. This is the canonical fix for parent task §13.2 (`aliasFields` reuse) — restoring the aliasing that the legacy `PMPUtilViewModel.livePricesCallback` provided via `getFinalHashMapPmpResponse`.

  No other capability is modified.

## Impact

**Affected files (4 screens + 1 view model):**

| File | Action | LoC | Pattern |
|------|--------|-----|---------|
| `app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPViewModel.kt` | Modify | 157 (existing) | Add `emissionCounter` + per-subscribe topic count tracking |
| `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/common/MarketTopDetailBaseScreen.kt` | Modify | 1328 | Topic-keyed dispatch (3-arg listener) |
| `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/common/MarketTopBaseFragment.kt` | Modify | 715 | Positional dispatch via topic lookup |
| `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/TabMarketStockScreen.kt` | Modify | 1608 | Positional dispatch via topic lookup |
| `app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/detailmarkettops/IndicesDetailScreen.kt` | Modify | 366 | 4-arg listener with `isAllDataReturned` |

**Risk classification:**

- `MarketTopDetailBaseScreen` — **MEDIUM**. Base class. Subclasses inherit the migration; subclasses that override `initPmpConnections()` (line 1073) will need their overrides updated.
- `MarketTopBaseFragment`, `TabMarketStockScreen` — **LOW**. Standard positional pattern, same shape as the landed `NewOrderBottomSheet` migration.
- `IndicesDetailScreen` — **LOW-MEDIUM**. Only 366 lines, but it is the first consumer of `isAllDataReturned`, so the implementation of that sentinel must land first (or alongside).

**Coupling with parent change:**

- Resolves parent task §13.3 (`isAllDataReturned` sentinel).
- Closes parent task §12.14 (TopMarket family migration).
- Does not affect any other capability.

**No new dependencies.** Pure Kotlin code change; no Gradle, no manifest, no PMP library change.

**No test changes.** The pre-existing test rot (parent task §13.1 — 1200 compile errors across unrelated test files) blocks all unit test runs, and the new logic in `PMPViewModel` is small enough to verify via the manual smoke tests in tasks.md §Verification.

## Non-Goals

- Migrating `HomeScreen.kt` (1797 lines, multiple PMP consumers) — separate sub-change.
- Migrating `WatchListTab.kt` (1842 lines, complex index dispatch) — separate sub-change, higher risk.
- Migrating `OptionDetailScreen.kt`, `CounterOptionAllTypeScreen.kt`, `TradeTicket*Screen.kt` — separate sub-changes, scheduled in the parent change's §12.10–§12.12.
- Deleting `PMPUtilViewModel` — deferred until the last consumer migrates (probably v3.4 or later).
- Implementing `aliasFields` extraction (parent task §13.2) — separate follow-up, only needed by screens that consume human-readable column names.
- Custom lint rule (parent task §13.4) — separate follow-up.
- Resolving pre-existing test rot (parent task §13.1) — separate effort by owning teams.
- iOS-side changes (SR-2875 equivalent already shipped on iOS in April 2026).
