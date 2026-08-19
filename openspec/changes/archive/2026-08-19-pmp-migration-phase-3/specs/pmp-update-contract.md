# Spec: PMPUpdate contract (SPEC-PMP-UPDATE-001, SPEC-PMP-UPDATE-002)

**Status:** Draft
**Related change:** `pmp-migration-phase-3`
**Related files:** `app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUpdate.kt`

## Purpose

Define the canonical shape of `PMPUpdate`, the data class emitted through
`PMPViewModel.pmpDataFlow`. The class MUST be extended with a `kind` field
and a `chartData` field to support the historical-chart use case in
`WatchListTab` and any other chart-consuming fragment.

## SPEC-PMP-UPDATE-001 — PMPUpdate data class extension

### 1.1 Shape (MUST)

The `PMPUpdate` data class MUST have the following shape:

```kotlin
enum class PMPUpdateKind { LIVE, QUERY, USSO }

data class PMPUpdate(
    val kind: PMPUpdateKind,                      // MUST be non-null, first parameter
    val topic: String,                            // MUST be non-null
    val indices: List<Int>,                       // MUST NOT be empty for LIVE; MAY be empty for QUERY
    val data: LinkedHashMap<String, String>?,    // MUST be non-null for LIVE and USSO; MUST be null for QUERY
    val chartData: List<String>?,                // MUST be non-null for QUERY; MUST be null for LIVE/USSO
    val isAllDataReturned: Boolean,               // MUST reflect batch completion sentinel
) {
    init {
        // Invariants enforced at construction time
        when (kind) {
            PMPUpdateKind.LIVE -> {
                require(data != null) { "LIVE update must have non-null data" }
                require(chartData == null) { "LIVE update must have null chartData" }
                require(indices.isNotEmpty()) { "LIVE update must have at least one index" }
            }
            PMPUpdateKind.QUERY -> {
                require(data == null) { "QUERY update must have null data" }
                require(chartData != null) { "QUERY update must have non-null chartData" }
            }
            PMPUpdateKind.USSO -> {
                require(data != null) { "USSO update must have non-null data" }
                require(chartData == null) { "USSO update must have null chartData" }
            }
        }
    }
}
```

### 1.2 Constructor parameter order (MUST)

`kind` MUST be the first parameter (after `kind`, the order is:
`topic`, `indices`, `data`, `chartData`, `isAllDataReturned`).

**Rationale:** `kind` is the discriminator; all other fields' nullability
depends on it. Putting `kind` first makes the contract self-documenting
at every call site.

### 1.3 Backwards compatibility (MUST)

The constructor change is binary-incompatible. The 4 already-migrated
screens MUST be updated in T1 of `pmp-migration-phase-3` to pass `kind`
explicitly:

- `MarketTopBaseFragment.kt` → `kind = PMPUpdateKind.LIVE`
- `MarketTopDetailBaseScreen.kt` → `kind = PMPUpdateKind.LIVE`
- `IndicesDetailScreen.kt` → `kind = PMPUpdateKind.LIVE` (extends
  `MarketTopDetailBaseScreen`)
- `TabMarketStockScreen.kt` → `kind = PMPUpdateKind.LIVE`
- `NewOrderBottomSheet.kt` → `kind = PMPUpdateKind.USSO`

No default value for `kind` — the contract requires every call site to
specify the kind explicitly.

### 1.4 `data` field aliasing (MUST, existing behavior preserved)

For LIVE updates, `PMPViewModel.aliasFields()` rewrites raw server FID
keys (e.g., "9") to canonical `WatchListColumnsSettingModel.value` strings
(e.g., "9,F009,P23") before emission. This behavior is unchanged.

For QUERY updates, no aliasing — `chartData` is the raw list of `dayClose`
strings from `PMPNode`'s query response.

For USSO updates, no aliasing — `data` is raw FID-keyed, used by
`NewOrderBottomSheet`.

## SPEC-PMP-UPDATE-002 — Emission semantics

### 2.1 Emission rate (MUST)

`PMPViewModel` MUST emit one `PMPUpdate` per PMP server tick per topic.

For a given `PMPToken`:

- LIVE token: the server emits a price tick every ~1s per topic.
  `PMPViewModel` emits one `PMPUpdate(kind=LIVE, ...)` per topic per tick.
- QUERY token: the server emits a single response per topic (one-shot).
  `PMPViewModel` emits one `PMPUpdate(kind=QUERY, ...)` per topic, then
  the flow goes silent for that token.

### 2.2 `isAllDataReturned` semantics (MUST)

For LIVE:

- `true` if this is the last item in the current subscription batch.
- "Last" is defined as `emissionCounter >= expectedTopicCount` (existing
  logic in `PMPViewModel.onTokenReady()`).
- Multiple counters may share one topic (via `mHashmapIndexOfCounter`
  dedup); `expectedTopicCount` correctly captures the post-dedup
  distinct topic count.

For QUERY:

- `true` on every emission (QUERY is one-shot per topic; no batch sentinel
  needed).

For USSO:

- `true` if this is the last item in the current subscription batch
  (same as LIVE; `NewOrderBottomSheet` uses 2 topics — option contract
  and underlying stock).

### 2.3 Field semantics by kind (MUST)

| Field | LIVE | QUERY | USSO |
|-------|------|-------|------|
| `kind` | `PMPUpdateKind.LIVE` | `PMPUpdateKind.QUERY` | `PMPUpdateKind.USSO` |
| `topic` | PMP topic string | History chart topic | PMP topic string |
| `indices` | Counter indices sharing this topic (≥1) | Empty (chart is one-shot) | Counter indices (1 or 2 for USSO) |
| `data` | Aliased FID-keyed map (non-null) | `null` | Raw FID-keyed map (non-null) |
| `chartData` | `null` | `List<String>` of `dayClose` values (non-null) | `null` |
| `isAllDataReturned` | Batch sentinel | `true` (always) | Batch sentinel |

## Acceptance criteria

### Unit tests (MUST pass)

1. `PMPUpdateTest.LIVE invariants`:
   - Constructing `PMPUpdate(LIVE, ...)` with `data == null` throws `IllegalArgumentException`.
   - Constructing with `chartData != null` throws.
   - Constructing with `indices.isEmpty()` throws.

2. `PMPUpdateTest.QUERY invariants`:
   - Constructing with `data != null` throws.
   - Constructing with `chartData == null` throws.

3. `PMPUpdateTest.USSO invariants`:
   - Constructing with `data == null` throws.
   - Constructing with `chartData != null` throws.

4. `PMPUpdateTest.kind is first parameter`:
   - All call sites in the codebase use `PMPUpdate(kind = ..., topic = ..., ...)`.
   - Verified by `git grep "PMPUpdate(" -- '*.kt' | grep -v "kind ="` returning
     zero results after T1 lands.

### Manual QA (MUST pass for each migrated screen)

1. Open screen → prices/charts appear within 3s.
2. The values rendered on screen match the legacy `PMPUtilViewModel` path
   when the feature flag is toggled.
3. Switching screens preserves state (no double-subscribe).

## Migration impact on existing code

The 4 already-migrated screens MUST be updated in T1 to add `kind = ...` to
each `PMPUpdate(...)` constructor call. The change is mechanical:

```kotlin
// Before
PMPUpdate(topic, indices, data, isAllDataReturned)

// After (MarketTopBaseFragment, MarketTopDetailBaseScreen, TabMarketStockScreen)
PMPUpdate(kind = PMPUpdateKind.LIVE, topic, indices, data, isAllDataReturned)

// After (NewOrderBottomSheet)
PMPUpdate(kind = PMPUpdateKind.USSO, topic, indices, data, isAllDataReturned)
```

The `chartData` parameter is `null` for these existing consumers, so the
invariants pass.
