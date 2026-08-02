# API Endpoint → Screen Mapper — Design

## Context

The POEMS Mobile 3 Android app uses Retrofit; the iOS app uses `EndPoints.swift` string constants. Both apps have a `PATTERN_MAP_PATH_URL` dict (iOS) / `PATTERN_MAP_PATH_URL`-equivalent logic that normalises dynamic paths (e.g., `/st/counter/1` → `/st/counter/{id}`) — so api-map paths are already normalised.

Android: each `*Service.kt` file is injected via Hilt into screens. A single service (`TradeService.kt`) has ~100 endpoints. Every screen that injects `TradeService` can reach any of those 100 endpoints.

iOS: each endpoint declaration lives in a `struct` inside `EndPoints.swift`. HTTP method is not in the struct name — it is resolved at the call site. The endpoint struct → service file → view controller chain needs a manual mapping.

**The correct join is service-level, not endpoint-level.**

## Goals / Non-Goals

**Goals:**
- Join api-map endpoint paths to the Android/iOS services that define them.
- Map services to the screens that inject/use them (via `screen_service_mapping.yaml`).
- Write the resulting screen lists to `api-map!C:D`.
- Run on-demand from the laptop. No schedule. No Slack.

**Non-Goals:**
- Endpoint-level granularity. Service-level is sufficient and correct.
- Auto-discovery of screen → service injection. Hand-maintained mapping.
- Confidence classification. All regex matches are high-confidence.
- gitnexus dependency.
- Idempotent retry loop (Sheets API is reliable enough).

## Decisions

### D1. Service-level join, not endpoint-level

**Why**: `TradeService.kt` has ~100 endpoints. Matching at endpoint level means `TradeService` gets listed 100 times for 100 endpoints on the same screen. Service-level means each screen that injects `TradeService` sees all its endpoints listed once per screen. The sheet user can filter by service name if needed.

**Alternatives**: Endpoint-level join was rejected — too much noise from multi-endpoint services.

### D2. `screen_service_mapping.yaml` for screen → service mapping

**Why**: Auto-discovering which screen injects which service requires static analysis of every Kotlin/Swift file's dependency injection (Hilt on Android, `init()` or property injection on iOS). That is a separate static analysis problem that is out of scope. A hand-maintained YAML is simple, auditable, and correct.

**Alternatives**: Full DI static analysis was rejected — too complex for a first pass.

### D3. Same path normalisation regexes as in the iOS code

**Why**: The iOS `PATTERN_MAP_PATH_URL` already contains ~50 regex patterns for normalising dynamic paths. Android has the same logic. We copy the normalisation into the tool to ensure api-map paths (which are already normalised) match the indexed paths.

**Alternatives**: Using a generic `{id}` normalisation was rejected — the existing patterns are already correct and comprehensive.

### D4. Pre-write snapshot only (no retry loop)

**Why**: Google Sheets API write reliability is high. Partial writes are rare. A pre-write snapshot (`~/.tdt/state/api-screen-mapper/<ts>/cd_pre.json`) gives a simple one-line restore path. A retry loop adds complexity without proportional value.

**Alternatives**: The retry loop in the draft spec was rejected.

### D5. `index_android.py` and `index_ios.py` as separate scripts

**Why**: Android and iOS have completely different indexing strategies (Retrofit annotations vs. Swift struct properties). Keeping them separate makes each script independently testable and avoids cross-contamination.

**Alternatives**: A unified indexer was rejected — the parsing logic is too different.

### D6. Config in `~/.tdt/api-screen-mapper.yaml`

**Why**: TDT convention is that config lives under `~/.tdt/`. The config holds: spreadsheet ID, screen→service mapping, abbreviations (future). No hardcoded values in scripts.

**Alternatives**: Env vars were rejected — the YAML is easier to audit and edit without touching env.

### D7. No confidence column

**Why**: All regex-matched literal paths are high-confidence. The draft spec's 3-tier confidence system cannot fire in practice. Removing it reduces complexity with no loss of functionality.

## Data Flow

```
1. load ~/.tdt/api-screen-mapper.yaml
   → spreadsheet_id, screen_service_mapping

2. sheets.read(spreadsheet_id, "api-map!A1:B191")
   → [[module, endpoint], ...]

3. index_android.py poems-mobile3-android/
   → { "TradeService": ["/st/order/today", "/st/order/history", ...], ... }

4. index_ios.py poems-mobile3-ios/
   → { "TradeEndpoint": ["/st/order/today", ...], ... }

5. join(api_map_rows, android_index, ios_index, screen_service_mapping)
   → for each api_map row:
       find endpoint path in android_index → list of services
       for each service → list of screens from mapping
       same for iOS

6. snapshot: sheets.read("api-map!C:D") → cd_pre.json

7. sheets.write("api-map!C1:D191", matrix)
   → 191 rows × 2 cols

8. log: matched counts, WARN lines to stderr + run.log
```

## Module layout

```
tdt-meta/scripts/api_screen_mapper/
├── index_android.py       # parse *Service.kt → {service: [paths]}
├── index_ios.py           # parse EndPoints.swift → {struct: [paths]}
├── build_api_map.py       # orchestrator: read → index → join → write
├── restore_cd.py          # restore from cd_pre.json snapshot
├── normalize_paths.py     # shared: PATTERN_MAP_PATH_URL normalisation
└── README.md
```

```
~/.tdt/api-screen-mapper.yaml   # config (in TDT_HOME)
~/.tdt/state/api-screen-mapper/  # per-run state (created by build_api_map.py)
```

## Config shape

```yaml
spreadsheet_id: "1abc...xyz"   # from the Google Sheet URL

screen_service_mapping:
  # Android: screen folder → service files
  MeScreen:
    - MeService
    - NotificationService
  TradeTicketScreen:
    - TradeService
  WatchListScreen:
    - WatchListService
  ProfileScreen:
    - MeService
    - MeSettingService

  # iOS: view controller → service files
  MeViewController:
    - MeService
    - MeAlertService
  TradeBuySellViewController:
    - TradeService
    - TradeEndpoint
```

## `PATTERN_MAP_PATH_URL` normalisation (copied from iOS source)

These regexes normalise dynamic paths before joining against api-map. They are already in the iOS codebase at `EndPoints.swift` lines 1003–1055:

```python
NORMALIZATION_RULES = [
    (r"^/global/watchlist/\d+$", "/global/watchlist/[param]"),
    (r"^/NFX/watchlist/\d+$", "/NFX/watchlist/[param]"),
    (r"^/usso/order/details/[^/]+$", "/usso/order/details/[param]"),
    (r"^/bo/article/[^/]+$", "/bo/article/[param]"),
    # ... ~50 patterns total
]
```

The same rules apply to Android. The Android codebase has equivalent normalisation in its `PATTERN_MAP_PATH_URL` dict.

## Failure modes

| Failure | Detection | Behavior |
|---|---|---|
| `api-map` tab missing | Sheets read returns 0 rows | Exit 2, print available tabs |
| `*Service.kt` file not found | glob returns [] | Skip platform, log WARN |
| `EndPoints.swift` not found | file read fails | Exit 2, precise error |
| Config missing spreadsheet_id | YAML key not found | Exit 2, print config template |
| Auth failure | `gspread` raises `APIError` | Exit 2, print recovery steps |
| Partial write | Not detected (no retry loop) | Sheets version history is the backstop |

## Rollback

```bash
python restore_cd.py 2026-07-07T10-45-00Z
# reads ~/.tdt/state/api-screen-mapper/2026-07-07T10-45-00Z/cd_pre.json
# writes back to api-map!C:D
# prints [restored to 2026-07-07T10-45-00Z]
```

If the restore script fails: Sheets → File → Version history → restore previous version.
