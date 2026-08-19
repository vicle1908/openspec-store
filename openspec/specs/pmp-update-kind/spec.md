## Purpose

Extend `PMPUpdate` with a `kind: PMPUpdateKind` field and a
`chartData: List<String>?` field. Support the historical-chart use case in
`WatchListTab` and any other chart-consuming fragment. Unify the four
legacy callback variants (`mOnSubscribedCallback`,
`mOnSubscribedCallbackAllData`, `onSubscribedCallbackAllData`,
`onSubscribedUSSOCallback`) into a single typed event with a kind
discriminator.

## Requirements

### Requirement: PMPUpdate carries a kind discriminator

`PMPUpdate` SHALL be a `data class` with the following shape:

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
        when (kind) {
            PMPUpdateKind.LIVE -> {
                require(data != null) { "LIVE update must have non-null data" }
                require(chartData == null) { "LIVE update must have null chartData" }
                require(indices.isNotEmpty()) { "LIVE update must have at least one index" }
            }
            PMPUpdateKind.QUERY -> {
                require(data == null) { "QUERY update must have null data" }
                require(chartData != null) { "QUERY update must have non-null chartData" }
                // indices MAY be empty (chart for one topic with no counter sharing it).
                // However, when indices is non-empty, the fragment MUST iterate them
                // (same fan-out semantic as LIVE).
            }
            PMPUpdateKind.USSO -> {
                require(data != null) { "USSO update must have non-null data" }
                require(chartData == null) { "USSO update must have null chartData" }
                require(indices.isNotEmpty()) { "USSO update must have at least one index" }
            }
        }
    }
}
```

`kind` SHALL be the first parameter (no default value). All other fields'
nullability depends on `kind`.

#### Scenario: Constructing a LIVE update with null data throws

- **WHEN** a caller constructs `PMPUpdate(kind = LIVE, topic, indices, data = null, chartData = null, isAllDataReturned)`
- **THEN** the `init {}` block throws `IllegalArgumentException` with the message "LIVE update must have non-null data"

#### Scenario: Constructing a QUERY update with null chartData throws

- **WHEN** a caller constructs `PMPUpdate(kind = QUERY, topic, indices, data = null, chartData = null, isAllDataReturned)`
- **THEN** the `init {}` block throws `IllegalArgumentException` with the message "QUERY update must have non-null chartData"

#### Scenario: Constructing a LIVE update with empty indices throws

- **WHEN** a caller constructs `PMPUpdate(kind = LIVE, topic, indices = emptyList(), data, chartData = null, ...)`
- **THEN** the `init {}` block throws `IllegalArgumentException` with the message "LIVE update must have at least one index"

### Requirement: data field aliasing preserved for LIVE

For LIVE updates, `PMPViewModel.aliasFields()` SHALL rewrite raw server
FID keys (e.g., "9") to canonical `WatchListColumnsSettingModel.value`
strings (e.g., "9,F009,P23") before emission. This behavior is unchanged
from the previous MR (`android-pmp-connection-center`).

For QUERY and USSO updates, no aliasing SHALL be applied: `chartData` is
the raw list of `dayClose` strings (QUERY), and `data` is raw FID-keyed
(USSO).

#### Scenario: LIVE update data is aliased

- **WHEN** a PMP server tick arrives for topic "ABC" with raw field "9" = "123.45"
- **AND** the subscribe fields include `WatchListColumnsSettingModel(value = "9,F009,P23")`
- **THEN** `PMPViewModel` emits `PMPUpdate(kind = LIVE, topic = "ABC", indices = [...], data = {"9,F009,P23" -> "123.45"}, chartData = null, isAllDataReturned = ...)`

#### Scenario: QUERY update chartData is not aliased

- **WHEN** a PMP server query response arrives for history topic "\D\SG\HKSE\2800" with raw chart data
- **THEN** `PMPViewModel` emits `PMPUpdate(kind = QUERY, topic = "\D\SG\HKSE\2800", indices = [...], data = null, chartData = [raw dayClose values], isAllDataReturned = true)`
- **AND** `chartData` SHALL be the sub-sampled `List<String>` of `dayClose` values (matching the legacy `PMPUtilViewModel.historyChartCallback` semantic, which uses `index % SEGMENT_HISTORICAL_CHART == 0` sub-sampling)

#### Scenario: QUERY update indices fan out to every sharing counter

- **WHEN** the QUERY token's priceUpdates flow emits `("\D\SG\HKSE\2800", ["1.0", "2.0", "3.0"])`
- **AND** `mChartTopicIndexMap["\D\SG\HKSE\2800"] = [0, 5]` (two counters share this topic — same stock in two watchlists)
- **THEN** `PMPViewModel` emits TWO `PMPUpdate(QUERY, ...)` events:
  - `PMPUpdate(kind = QUERY, topic = "\D\SG\HKSE\2800", indices = [0, 5], data = null, chartData = ["1.0", "2.0", "3.0"], isAllDataReturned = true)`
- **AND** the fragment's `handleQuery` SHALL iterate `update.indices` and call the per-index handler twice (once for index 0, once for index 5)
- **AND** this fan-out semantic SHALL match the legacy `PMPUtilViewModel.historyChartCallback` which calls `mOnQueryCallback(index, list)` once per `listIndexOfCounter`

This is the same fan-out semantic as LIVE: one topic → many indices.

### Requirement: Emission rate matches server tick

`PMPViewModel` SHALL emit one `PMPUpdate` per PMP server tick per topic.

For LIVE tokens: the server emits a price tick every ~1s per topic. The
ViewModel emits one `PMPUpdate(kind = LIVE, ...)` per topic per tick.

For QUERY tokens: the server emits a single response per topic (one-shot).
The ViewModel emits one `PMPUpdate(kind = QUERY, ...)` per topic, then the
flow goes silent for that token.

#### Scenario: isAllDataReturned is true on the last LIVE emission of a batch

- **WHEN** `emissionCounter >= expectedTopicCount` for a LIVE token
- **THEN** the corresponding `PMPUpdate` has `isAllDataReturned = true`
- **AND** the next emission resets `emissionCounter` to 0

#### Scenario: isAllDataReturned is always true for QUERY

- **WHEN** a QUERY emission occurs
- **THEN** `isAllDataReturned = true` (QUERY is one-shot per topic; no batch sentinel needed)
