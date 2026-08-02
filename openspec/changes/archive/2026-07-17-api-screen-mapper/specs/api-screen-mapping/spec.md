## ADDED Requirements

### Requirement: Service-Level Endpoint Indexing

The system SHALL parse Android `*Service.kt` files to extract Retrofit annotation paths (`@GET("path")`, `@POST("path")`, etc.) grouped by the service file name, and SHALL parse iOS `EndPoints.swift` to extract `static let name = "/path"` declarations grouped by the containing struct name.

#### Scenario: Android indexing
- **WHEN** `index_android.py` reads `poems-mobile3-android/app/src/main/java/com/tdt/pmobile3/network/service/TradeService.kt`
- **THEN** the output maps `TradeService` to a list of all literal paths in `@GET`/`@POST`/etc. annotations, normalised via the same PATTERN_MAP_PATH_URL rules

#### Scenario: Android no Service files
- **WHEN** no `*Service.kt` files are found in the Android repo path
- **THEN** the indexer returns an empty dict and logs `[WARN: android-no-service-files]`

#### Scenario: iOS indexing
- **WHEN** `index_ios.py` reads `poems-mobile3-ios/Pmobile3/Services/Network/Common/EndPoints/EndPoints.swift`
- **THEN** the output maps each struct (e.g., `TradeEndpoint`) to a list of all `static let name = "/path"` string values, normalised via PATTERN_MAP_PATH_URL

#### Scenario: iOS EndPoints.swift not found
- **WHEN** `EndPoints.swift` is not found at the expected path
- **THEN** the indexer exits with code 2 and prints the precise path it looked for

### Requirement: Path Normalisation

The system SHALL normalise all extracted paths using the PATTERN_MAP_PATH_URL regex rules already defined in the iOS `EndPoints.swift` source, so that dynamic paths (e.g., `/st/counter/1`) match their normalised api-map equivalents (e.g., `/st/counter/{id}`).

#### Scenario: Dynamic path normalised
- **WHEN** an Android `*Service.kt` contains `@GET("st/counter/123")`
- **THEN** the path is normalised to `/st/counter/{id}` and matched against the api-map using the normalised form

#### Scenario: Literal path unchanged
- **WHEN** a path has no matching normalisation rule
- **THEN** the path is used as-is for matching

### Requirement: Service-to-Screen Mapping

The system SHALL read the `screen_service_mapping` section of `~/.tdt/api-screen-mapper.yaml` to map service names to screen names, and SHALL use this mapping to expand matched services into a list of screen names per api-map row.

#### Scenario: Android screen mapping
- **WHEN** `TradeService` appears in `screen_service_mapping.android.MeScreen`
- **THEN** the Android screen list for that endpoint includes `MeScreen`

#### Scenario: iOS screen mapping
- **WHEN** `TradeEndpoint` appears in `screen_service_mapping.ios.MeViewController`
- **THEN** the iOS screen list for that endpoint includes `MeViewController`

#### Scenario: Service not in mapping
- **WHEN** a service name has no entry in the screen mapping
- **THEN** the service name itself is used as the screen name (with a `[unmapped-service]` WARN line)

### Requirement: Sheet Write

The system SHALL read the api-map tab, compute the Android and iOS screen lists for each row, and write a `2 × N` matrix to `api-map!C:D` (columns C and D), leaving columns A and B unchanged.

#### Scenario: Successful write
- **WHEN** the join completes without error
- **THEN** `sheets.write("api-map!C1:D{rows+1}", matrix)` is called with the computed values

#### Scenario: Pre-write snapshot
- **WHEN** a write is about to occur
- **THEN** the current C:D contents are read to `~/.tdt/state/api-screen-mapper/<ts>/cd_pre.json` before the write

### Requirement: No New External Dependencies

The system SHALL NOT introduce any new Python package beyond what is already in the workspace venvs. The implementation SHALL use `gspread`, `google-auth`, `pyyaml`, and the existing `tdt-sheets` `SheetsClient`.

#### Scenario: Dependency check
- **WHEN** `uv sync` is run against the new `pyproject.toml` (if any)
- **THEN** no new packages are resolved

### Requirement: Config via TDT_HOME

The system SHALL read its configuration from `$TDT_HOME/api-screen-mapper.yaml` (with `~` expansion for `TDT_HOME`). If `TDT_HOME` is unset, it SHALL fall back to `~/.tdt/api-screen-mapper.yaml`.

#### Scenario: Config file not found
- **WHEN** `~/.tdt/api-screen-mapper.yaml` does not exist
- **THEN** the script exits with code 2 and prints the expected config shape

### Requirement: Run Log

The system SHALL write a run log to `~/.tdt/state/api-screen-mapper/<ts>/run.log` containing: timestamp, matched-row count per platform, WARN lines, and the spreadsheet ID used.

#### Scenario: WARN on unmapped service
- **WHEN** a service name has no screen mapping entry
- **THEN** the log contains `[WARN: unmapped-service: TradeService]`

### Requirement: Restore from Snapshot

The system SHALL provide a `restore_cd.py` script that reads `~/.tdt/state/api-screen-mapper/<ts>/cd_pre.json` and writes its contents back to `api-map!C:D`.

#### Scenario: Restore success
- **WHEN** `python restore_cd.py 2026-07-07T10-45-00Z` is run and the snapshot exists
- **THEN** the script writes the snapshot to the sheet and prints `[restored to 2026-07-07T10-45-00Z]`

#### Scenario: Snapshot not found
- **WHEN** `python restore_cd.py <ts>` is run and no snapshot exists for that timestamp
- **THEN** the script exits with code 5 and prints `[error: no snapshot for <ts>]`
