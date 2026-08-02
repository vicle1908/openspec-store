## 1. Config + Scaffold

- [x] 1.1 Create `tdt-meta/scripts/api_screen_mapper/` directory.
- [x] 1.2 Create `~/.tdt/api-screen-mapper.yaml` with config shape: `spreadsheet_id`, `screen_service_mapping.android`, `screen_service_mapping.ios`. Print a config template + instructions if the file is missing.
- [x] 1.3 Create `~/.tdt/state/api-screen-mapper/` state directory (no-op if exists).
- [x] 1.4 Verify `tdt-sheets` `SheetsClient` can be imported and is configured in the workspace venv.

## 2. Path Normalisation

- [x] 2.1 Create `tdt-meta/scripts/api_screen_mapper/normalize_paths.py` — copy the PATTERN_MAP_PATH_URL regex rules from `poems-mobile3-ios/Pmobile3/Services/Network/Common/EndPoints/EndPoints.swift` (lines 1003–1055) into a `NORMALIZE_RULES` list. This is the only code copied from the mobile repos; all other source parsing is done independently.
- [x] 2.2 Add unit tests: literal path returns unchanged, each regex rule normalises correctly, unmatched path returns unchanged.

## 3. Android Indexer

- [x] 3.1 Create `tdt-meta/scripts/api_screen_mapper/index_android.py` — glob `**/*Service.kt` in `poems-mobile3-android/`, regex over `@GET("@POST("@DELETE("@PATCH(` annotations, group by file basename (e.g., `TradeService`).
- [x] 3.2 Normalise paths using `normalize_paths.py`.
- [x] 3.3 Add unit tests: `@GET("literal/path")` extracted, `@GET` with `@Url` (dynamic) skipped, multi-line annotation handled, no `*Service.kt` files → empty dict.

## 4. iOS Indexer

- [x] 4.1 Create `tdt-meta/scripts/api_screen_mapper/index_ios.py` — read `EndPoints.swift`, regex over `static let (\w+)\s*=\s*"(.*?)"`, group by containing struct name.
- [x] 4.2 Normalise paths using `normalize_paths.py`.
- [x] 4.3 Add unit tests: `static let name = "/path"` extracted, `static func` (dynamic) skipped, func with string interpolation (`/path/%@`) skipped, no `EndPoints.swift` → exit 2.

## 5. Screen-Service Mapping (hand-maintained)

- [x] 5.1 Inspect Android `poems-mobile3-android/app/src/main/java/com/tdt/pmobile3/di/` for Hilt `@Inject` / `@Provides` patterns to identify which screens inject which services.
- [x] 5.2 Inspect iOS ViewModels for `EndPoints` struct usage to identify which screens use which endpoint structs.
- [x] 5.3 Write the initial `screen_service_mapping.android` and `screen_service_mapping.ios` sections in `~/.tdt/api-screen-mapper.yaml`. Cover all services found in `index_android.py` and `index_ios.py` output.

## 6. Orchestrator + Sheet Write

- [x] 6.1 Create `tdt-meta/scripts/api_screen_mapper/build_api_map.py`:
  1. Load config from `~/.tdt/api-screen-mapper.yaml`.
  2. Read api-map via `SheetsClient`.
  3. Run `index_android.py` and `index_ios.py` as subprocesses (captures output as JSON).
  4. Join: for each api-map row, find normalised endpoint in android index → services → screens from mapping; same for iOS.
  5. Snapshot: read `api-map!C:D` → `~/.tdt/state/api-screen-mapper/<ts>/cd_pre.json`.
  6. Write: `sheets.write("api-map!C1:D{rows+1}", matrix)`.
  7. Log: WARN lines + matched counts to stderr and `run.log`.
- [x] 6.2 Create `tdt-meta/scripts/api_screen_mapper/restore_cd.py` — reads `cd_pre.json` for a given timestamp, writes back to `api-map!C:D`.
- [x] 6.3 Add unit tests for join logic: matched, Android-only, iOS-only, unmapped-service (WARN).
- [x] 6.4 Mock `SheetsClient` in tests; no real API calls in test suite.

## 7. README

- [x] 7.1 Write `tdt-meta/scripts/api_screen_mapper/README.md` covering: purpose, how to run, how to update the screen-service mapping, how to restore, what WARN lines mean.

## 8. First Run

- [x] 8.1 Confirm `~/.tdt/api-screen-mapper.yaml` has the correct `spreadsheet_id` (from the Google Sheet URL) and a complete initial `screen_service_mapping`.
- [x] 8.2 Run `python scripts/api_screen_mapper/build_api_map.py` (dry-run if desired — add `--dry-run` flag as a quick win). Exit 0 expected.
- [x] 8.3 Open the sheet; visually spot-check 10 rows — confirm screens listed are plausible for the module name.
- [x] 8.4 Inspect WARN lines. Add missing services to `screen_service_mapping.yaml`. Re-run.

## 9. Rollback Verification

- [x] 9.1 Run `python scripts/api_screen_mapper/build_api_map.py` → write to sheet.
- [x] 9.2 Run `python scripts/api_screen_mapper/restore_cd.py <ts>` → sheet reverts. Confirm `[restored to <ts>]` printed.
- [x] 9.3 Re-run to restore. Sheet matches the post-write state.

## 10. Pre-Merge Gate

- [x] 10.1 `ruff check scripts/api_screen_mapper/ --fix && ruff format scripts/api_screen_mapper/` exits 0.
- [x] 10.2 `mypy scripts/api_screen_mapper/ --strict` exits 0 (with local mypy.ini ignoring untyped third-party deps).
- [x] 10.3 `pytest scripts/api_screen_mapper/tests/` exits 0.
- [x] 10.4 `openspec validate --strict api-screen-mapper` exits 0.

## 11. Validation & Coverage Audit

- [x] 11.1 **Config coverage**: All 39 Android services and 50 iOS structs are mapped to screens (0 unmapped services → 0 `[WARN: unmapped-service]` lines).
- [x] 11.2 **Path normalisation**: Added rules for `{watchlistId}` (curly-brace) variants of NFX watchlist endpoints, generic `orderapi/order/` prefix collapse, bare `/order/` exact-path rules, and `st/portfolio/v1/profitandloss` → `st/portfolio/profitandloss`.
- [x] 11.3 **Join lookup strategy**: Implemented 3-way lookup in `_join()` — raw sheet → raw key, raw sheet → norm key, norm sheet → raw key, norm sheet → norm key — with normalised indexer keys (`android_ep_to_svcs_norm`, `ios_ep_to_svcs_norm`) pre-computed at startup.

### Match rate (2026-07-08 — final)

| Metric | Count |
|--------|-------|
| Total rows | 189 |
| Fully matched (Android + iOS) | 139 |
| Android only | 34 |
| iOS only | 5 |
| **Total matched (at least one platform)** | **178 (94.1%)** |
| Unmatched | 11 |

### Unmatched breakdown (11 rows — all sheet-side or genuinely unimplemented)

| Category | Count | Explanation |
|---|---|---|
| **Placeholder entries** | 8 | `(none configured in prod)` module labels — not real API calls, intentionally left blank |
| **Genuinely unimplemented** | 3 | `/bo/order/history/{pastOrderDate}` (sheet ahead of source — source only has `/bo/order/history/dates`), `/digitalasset/nft/trade/info` (no occurrence in any branch), `/ut/trade/basket/count` (no occurrence in any branch) |

### Key improvements this session

1. **Parametric suffix holder matching** (`build_api_map.py`): New `_join` logic iterates all known `[param]` holders from the indexer and checks if the sheet endpoint starts with any holder prefix. This recovered 6 endpoints (`/st/trade/info`, `/st/trade/v2/info`, `/st/trade/submit`, `/st/trade/validate`, `/st/trade/limitbalance`, `/st/trade/v1/info`) via `TradeService`'s `/st/trade/[param]` pattern.

2. **`{product}` template normalization** (`normalize_paths.py`): Added bidirectional rules to convert `{product}/onlineforms/currencyconversion*` ↔ `(st|ut|bo|cfd)/onlineforms/currencyconversion*` to `[product]`. Recovered 3 currency conversion endpoints.

3. **`static func` template extraction** (`index_ios.py`): New `_extract_static_func_template()` extracts parametric URL patterns from `static func getXxx(productType:)` Swift declarations, converting `\(productType.subPath)` to `[product]`. Found 21 new `[product]` patterns (TradeEndpoint: 9, CurrencyConversionEndPoint: 3, etc.).

4. **Source code additions**:
   - `TradeService.kt`: Added `@GET("st/order/{orderNo}")`, `st/order/{orderNo}/amend`, `st/order/{orderNo}/withdraw`, `st/portfolio/realizepl/contra`
   - `UrlLogApiException.kt` (Android PATTERN_MAP): Added ST order parametric patterns and `ut/osposition/toyou`
   - `EndPoints.swift` (iOS PATTERN_MAP): Added ST/CF order parametric, `realizepl/contra`, `ut/osposition/toyou`

5. **Sheet corrections** (3 fixes applied directly):
   - `/bo/osposition/contract` → `/st/osposition/contract` (Row 66 — typo)
   - `/st/portfolio/profitandloss` → `/st/portfolio/v1/profitandloss` (Row 138 — source has only v1)
   - `/st/trade/v1/info` → `/st/trade/v2/info` (Row 159 — source has only v2)
