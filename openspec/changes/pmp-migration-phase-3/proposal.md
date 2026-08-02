# Migrate 13 remaining fragments to `PMPViewModel` (`pmp-migration-phase-3`)

## Why

`PMPConnectionCenter` (SR-3738, landed) is a process-wide singleton that owns
PMP TCP sockets and survives app background/foreground. The center was designed
to fix the per-Fragment destroy-on-pause anti-pattern in `PMPUtilViewModel` —
but only 4 of 17 PMP-using screens have migrated. The other 13 still:

- Call `disconnectToPMP()` + `resetAllData()` in `onPause` (destroys the socket)
- Call `reSubscribe()` in `onResume` (re-creates the socket + re-authenticates)
- Call `resetAllData()` in pull-to-refresh paths (destroys the socket)
- Have missing `onDestroy` cleanup in some files (leaks subscriptions)
- Use `repeatOnLifecycle(RESUMED)` to wrap init (defeats the lifecycle)

Every app switch on these 13 screens triggers a **logout + TCP teardown + login +
re-subscribe** cycle. The center was designed to make this unnecessary.

iOS shipped the equivalent (`HPMPConnectionCenter`, SR-2875) in April 2026.
Android has 4 of 17 screens migrated. This change migrates the remaining 13.

## What Changes

**Two center extensions** (required before any P0 fragment can migrate):

- **`PMPNode.submitSubscribe` → `PMPNode.submitRequest(topics, fieldMap, requestType)`**
  — adds `STREAMING_QUERY` (one-shot historical data) support. The internal
  `buildSubscribeRequest()` (line 790 of `PMPNode.kt`) already accepts
  `requestType`; only the call site at line 755 needs lifting. The historical
  URL pool (`PMPSettingModel.liveChart.historicalURL`) is a separate
  `PMPNode` keyed by URL — same ref-counting, no new node subclass.
- **`PMPConnectionCenter.subscribeForHistory(counters, fields): PMPQueryToken?`** —
  resolves each `CounterDetail` to its history topic via
  `getHistoryChartTopicFormat()`, routes all topics to the historical URL node,
  and returns a `PMPQueryToken` (sibling of `PMPToken`, type-safe for chart data).
  The design decision to introduce `PMPQueryToken` rather than adding a
  `requestType` field to `PMPToken` is documented in `design.md` Decision 2
  and `pmp-viewmodel-contract.md` §1.3.

**One data class extension:**

- **`PMPUpdate` adds `kind: PMPUpdateKind` and `chartData: List<String>?`**.
  The current shape is 4 fields; the new shape has 6. `init { require(...) }`
  enforces mutual exclusion: `LIVE → data!=null, chartData==null`;
  `QUERY → data==null, chartData!=null`; `USSO → data!=null, chartData==null`.
  The constructor change is binary-incompatible — the 4 already-migrated
  screens (`MarketTopBaseFragment`, `MarketTopDetailBaseScreen`,
  `TabMarketStockScreen`, `NewOrderBottomSheet`) are updated in the same MR
  to pass `kind = ...` explicitly.

**One ViewModel extension:**

- **`PMPViewModel.subscribeForHistory(counters, fields)`** — opens a separate
  `PMPToken` for historical data. The fragment can have both `_pmpToken` (live)
  and `_queryToken` (history) open simultaneously; both close in `unsubscribe()`.
  `detach()` cancels both collectors but preserves both tokens.

**Thirteen fragment migrations**, prioritized:

- **P0** (2 files): `HomeScreen.kt`, `WatchListTab.kt` — full anti-pattern.
  `WatchListTab` additionally uses `STREAMING_QUERY` for chart data and
  `setOnResponseListenerWithTopicIndex` for multi-counter fan-out.
- **P1** (4 files): `CounterDetailScreen.kt`, `OptionDetailScreen.kt`,
  `MarketDepthTab.kt`, `TradeSummaryTab.kt` — missing destroy or wrong
  `repeatOnLifecycle` wrapper.
- **P2** (6 files): `MarketDepthTabFutures.kt`, `TopPriceDetailCounterFX.kt`,
  `CounterListSectionFragment.kt`, `CounterPriceDetailHeader.kt` (missing
  `onPause`), `CounterDetailScreenST.kt`, `OptionCounterScreen.kt`.
- **P3** (2 files): `TabIdeas.kt`, `TopPriceDetailCounter.kt` (base class
  fix propagates to `TopPriceDetailCounterST.kt`).

**Four feature flags** for side-by-side parallel QA:

- `BuildConfig.FEATURE_PMP_CENTER_HOME` (default `false`) — gates `HomeScreen`
- `BuildConfig.FEATURE_PMP_CENTER_WATCHLIST` (default `false`) — gates
  `WatchListTab`
- `BuildConfig.FEATURE_PMP_CENTER_P1` (default `false`) — gates the 4 P1 files
- `BuildConfig.FEATURE_PMP_CENTER_P2` (default `false`) — gates the 6 P2 files

When the flag is off, the legacy `PMPUtilViewModel` path runs. When on, the
new `PMPViewModel` path runs. The two paths run side-by-side in the same
build so QA can compare behavior. After sign-off, flags default to `true` and
the legacy path is removed in T5.

## Capabilities

### New Capabilities

- `pmp-update-kind` — `PMPUpdate` carries a `PMPUpdateKind` enum discriminator
  and a `chartData: List<String>?` field. Enables unified `when (kind)` dispatch
  in fragments.
- `pmp-node-submit-request` — `PMPNode.submitRequest(topics, fieldMap, requestType)`
  supports `STREAMING_SUBSCRIBE`, `STREAMING_UNSUBSCRIBE`, and
  `STREAMING_QUERY` request types. Backward-compatible rename of the existing
  `submitSubscribe` method.
- `pmp-center-subscribe-history` — `PMPConnectionCenter.subscribeForHistory()`
  creates a token against the historical URL pool, separate from the live URL
  pool.
- `pmp-viewmodel-history` — `PMPViewModel.subscribeForHistory()` exposes
  historical data through the same `pmpDataFlow: SharedFlow<PMPUpdate>` with
  `PMPUpdateKind.QUERY`.
- `pmp-fragment-migration-p3` — 13 fragments migrated to the
  `subscribe/detach/unsubscribe` lifecycle. Each migration is independent and
  reversible via the per-tier feature flag.

### Modified Capabilities

- `pmp-subscription-token` (existing) — `PMPToken` is unchanged; the new
  `PMPQueryToken` class is a sibling. Backward-compatible.
- `pmp-view-model` (existing) — adds `subscribeForHistory()`,
  `_queryToken: PMPQueryToken?`, `pmpQueryToken: PMPQueryToken?`, and a second
  collector for QUERY emissions.

## Non-Goals

- **Deleting `PMPUtilViewModel` in this MR.** Defer to T5 after all 13 migrations
  are sign-offed. `gitnexus_impact PMPUtilViewModel` confirms zero callers before
  deletion.
- **Migrating the remaining 4+ screens** (e.g., trade ticket variants,
  `CounterOptionAllTypeScreen`). Out of scope; defer to a follow-up.
- **iOS-side changes.** iOS already has the equivalent (`HPMPConnectionCenter`,
  SR-2875, April 2026). No iOS work needed.
- **Changes to the `phillip.pmp` third-party library.** Out of scope.
- **Moving `aliasFields` to a shared helper.** It is duplicated in
  `PMPViewModel` and `PMPUtilViewModel` today; extraction is a separate
  follow-up MR. The new spec preserves the duplication.
- **Persistent price caching across process death.** App restart still
  requires full re-subscription.
- **Custom lint rules** for the `subscribe/detach/unsubscribe` lifecycle.
  Deferred to a follow-up MR.

## Impact

- **Android only.** iOS unaffected.
- **5 center files modified:** `PMPNode.kt` (rename + QUERY branch),
  `PMPConnectionCenter.kt` (add `subscribeForHistory`),
  `PMPQueryToken.kt` (new file — type-safe chart token),
  `PMPViewModel.kt` (add `subscribeForHistory` + QUERY collector),
  `PMPUpdate.kt` (add `PMPUpdateKind` + `chartData` + invariant assertion).
- **4 already-migrated screens updated** for the `PMPUpdate` constructor change:
  `MarketTopBaseFragment.kt`, `MarketTopDetailBaseScreen.kt`,
  `TabMarketStockScreen.kt`, `NewOrderBottomSheet.kt`.
- **13 fragments migrated:** see the per-tier table above.
- **4 build flags added:** `FEATURE_PMP_CENTER_HOME`,
  `FEATURE_PMP_CENTER_WATCHLIST`, `FEATURE_PMP_CENTER_P1`,
  `FEATURE_PMP_CENTER_P2`. Defaults: all `false`. Removed in T5.
- **Risk:** Medium. The center extensions are the highest-risk change
  (`PMPNode.submitRequest` is called by every migrated screen). The fragment
  migrations are low-risk individually because the feature flag enables
  side-by-side QA.

## Open Questions

- **Is `PMPUpdateKind.USSO` needed?** iOS doesn't have it; it's
  Android-specific (the USSO options order entry flow uses raw FID-keyed data).
  The current `NewOrderBottomSheet` works with the unaliased `data` field
  without needing a discriminator. Decision: include `USSO` for explicitness
  and to enable future iOS parity; mark as `SHOULD` not `MUST` in the spec.
- **Should `subscribeForHistory` be `suspend fun` or `fun`?** The current
  `subscribe()` is `suspend fun` because it loads `PMPSettingModel` from Room
  on `Dispatchers.IO`. `subscribeForHistory()` should match. Decision: yes,
  `suspend fun`.
- **Ref-count on the historical URL node.** The historical URL is a separate
  URL pool, so the historical `PMPNode` has its own `topicRefCounts`. No new
  state in `PMPNode` is required — the URL is the key, and the ref-count is
  per-node. Decision: confirmed by reading `PMPNode.subscribe()` at line 725.

## Spec Inventory

The technical depth is in the spec files under `specs/`:

- `specs/pmp-update-contract.md` — `PMPUpdate` extension
- `specs/pmp-node-submit-request.md` — `PMPNode.submitRequest` rename
- `specs/pmp-center-subscribe-history.md` — `subscribeForHistory` API
- `specs/pmp-viewmodel-contract.md` — `PMPViewModel` API additions
- `specs/fragment-lifecycle-contract.md` — fragment subscribe/detach/unsubscribe

Each spec uses RFC 2119 keywords (MUST/SHOULD/MAY) and is testable.
