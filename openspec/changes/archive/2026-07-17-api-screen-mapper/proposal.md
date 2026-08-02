# API Endpoint → Screen Mapper

## Why

The POEMS Mobile 3 team needs to answer "which screens call which endpoint?" when scoping features, triaging bugs, or planning regression tests. The information lives in two places: the `api-map` Google Sheet (endpoint definitions) and the mobile code (which services/screens actually call each endpoint).

The bottleneck is that `TradeService.kt` alone has 100 Retrofit endpoints, and every screen that injects `TradeService` can reach any of those endpoints. The correct join is at the **service level**: find which services contain a given endpoint path, then look up which screens inject each service. Doing this by hand takes 5–15 minutes per endpoint.

This change builds the join once and writes it to `api-map!C:D`. The pre-edit gate fires because the implementation lives in `tdt-meta/`.

## What Changes

### 1. Tool: `tdt-meta/scripts/api_screen_mapper/` (3 scripts + 1 config)

- **`index_android.py`** — reads all `*Service.kt` files in `poems-mobile3-android/`, extracts `@GET`/`@POST`/etc. literal-path annotations with their containing service file name. Applies the same path-normalisation regexes already defined in `PATTERN_MAP_PATH_URL` in `EndPoints.swift` to handle dynamic paths (e.g., `/st/counter/1` → `/st/counter/{id}`).
- **`index_ios.py`** — reads `EndPoints.swift`, extracts `static let name = "/path"` declarations with their containing struct name (e.g., `TradeEndpoint`). Applies the same `PATTERN_MAP_PATH_URL` regexes for normalised matching.
- **`build_api_map.py`** — reads api-map from Google Sheets, joins endpoints to services, looks up services in a screen→service mapping file, writes C/D columns back. Includes pre-write snapshot and restore script.
- **`screen_service_mapping.yaml`** — hand-maintained mapping of screen names to service files. This is the only manual input the tool needs; it needs to be written once and updated when a new screen is created.

### 2. Output

- `api-map!C` (Android): comma-separated list of Android screen names that can reach this endpoint via their injected services.
- `api-map!D` (iOS): comma-separated list of iOS screen names that can reach this endpoint via their injected services.

Display format is the screen folder name (e.g., `MeScreen`, `SwitchAccountSheet`) as-is. No transformation.

### 3. Run mode

On-demand only. Run from laptop. No schedule, no Slack.

## Capabilities

### New Capabilities

- `api-screen-mapping`: On-demand pipeline joining the `api-map` Google Sheet with Android/iOS service-layer call graphs, writing screen lists to columns C and D. Uses pre-write snapshot for rollback. No gitnexus dependency, no confidence classification.

### Modified Capabilities

- None.

## Impact

| Area | Impact |
|------|--------|
| **`tdt-meta/scripts/api_screen_mapper/`** | NEW — 3 scripts, 1 YAML config, 1 restore helper. |
| **`poems-mobile3-android/`** | READ-ONLY — `*Service.kt` files are read only. |
| **`poems-mobile3-ios/`** | READ-ONLY — `EndPoints.swift` is read only. |
| **Google Sheet `api-map`** | MODIFIED — columns C and D written; A and B untouched. |
| **`tdt-sheets` (existing)** | REUSED — `SheetsClient` used for read/write. |
| **`~/.tdt/api-screen-mapper.yaml`** | NEW — spreadsheet ID + screen mapping config. |
| **External dependencies** | NONE — `gspread`, `google-auth`, `pyyaml` already in workspace. |
| **gitnexus** | NOT USED — removed from draft spec. |
| **confidence classifier** | NOT USED — removed from draft spec. |

## Non-Goals

- **Not mapping at the individual endpoint level** — the join is at the service level. If `TradeService` is injected in 5 screens, all 100 endpoints in `TradeService` are listed under each of those 5 screens. Deduplication in the sheet is a manual follow-up.
- **Not auto-discovering screen → service injection** — the `screen_service_mapping.yaml` is hand-maintained.
- **Not gitnexus-based** — uses only regex parsing and the hand-maintained mapping.
- **Not scheduled** — on-demand only.
- **Not handling iOS HTTP method inference** — all iOS paths are listed as available; method is not surfaced in the sheet.
- **Not deduplicating screen names per row** — if a screen injects two services that both contain the same endpoint, the screen name appears twice. Manual dedupe in the sheet.
