# jira-catalog-diff-and-writer Specification

## Purpose

Define how the `jira-daily-reports.catalog` package diffs a fresh `CatalogSnapshot` against the live `Jira Catalog` tab, and how it writes the resulting delta via `tdt-sheets`. The diff is the contract that lets the team keep their `Description`, `Purpose`, `Owner`, and `Notes` columns intact across daily refreshes, while still keeping `Usage Count`, `Last Seen`, `Status`, and other machine-owned columns current.

## Requirements

## ADDED Requirements

### Requirement: The differ MUST classify every snapshot row against the live tab

The differ SHALL consume a `CatalogSnapshot` (new) and a `list[CatalogRow]` read from the live tab (current), and emit a `CatalogDelta` with three lists: `appended` (rows to insert at the end), `updated` (rows to overwrite machine-owned cells on), and `removed` (rows to mark with `Status = Removed`). The differ MUST NOT classify any row as `deleted` — removed rows are kept with `Status = Removed` so the team retains history.

The primary key for matching is `(Kind, Name)`; for custom fields `(Kind, Field ID)` is an alternate key the differ MUST consult first so that human renames of `Name` on a custom field are treated as updates, not as a remove+insert pair.

#### Scenario: A new label is added to the snapshot

- **WHEN** the snapshot contains a row `(Kind=Label, Name=new-platform, usage_count=4)` that is not present in the live tab
- **THEN** the differ SHALL append it to `CatalogDelta.appended`
- **AND** the writer SHALL insert that row at the end of the tab.

#### Scenario: A custom field's Name is renamed by a human

- **WHEN** the live tab has `(Kind=Custom Field, Field ID=customfield_10016, Name=Severity)` and a human has edited the cell to `Name=Customer Severity`
- **AND** the snapshot has `(Kind=Custom Field, Field ID=customfield_10016, Name=Severity)` (no human-aware metadata; Jira still calls it Severity)
- **THEN** the differ SHALL match the rows on `(Kind, Field ID)`
- **AND** SHALL classify the row as `updated`
- **AND** the writer MUST leave the human-edited `Name` cell untouched
- **AND** MUST update the machine-owned columns (Usage Count, Last Seen, etc.).

#### Scenario: A label was used last week but not this week

- **WHEN** the live tab has `(Kind=Label, Name=qa-hotfix, Status=Active, Usage Count=5)` and the snapshot shows `usage_count=0` for the same `(Kind, Name)` key
- **THEN** the differ SHALL classify the row as `updated`
- **AND** the writer SHALL set `Status = Removed`, `Usage Count = 0`, and leave the human-owned columns unchanged.

#### Scenario: A label is used only by tickets that fell out of the lookback window

- **WHEN** the live tab has `(Kind=Label, Name=old-release, Status=Stale)` and the snapshot has `usage_count=0`
- **THEN** the differ SHALL classify the row as `updated`
- **AND** the writer SHALL set `Status = Removed`.

#### Scenario: A label's issue-key set changes without a usage-count change

- **WHEN** the live tab has `(Kind=Label, Name=qa-hotfix, Issue Keys=PUB-1, PUB-2)` and the snapshot reports the same label with `Issue Keys=PUB-1, PUB-2, PUB-3` (one new ticket in the window)
- **THEN** the differ SHALL classify the row as `updated` because the `Issue Keys` column is a machine-owned column
- **AND** the writer SHALL overwrite column P with `PUB-1, PUB-2, PUB-3`
- **AND** MUST leave the human-owned columns (E, F, G, H) untouched.

### Requirement: The differ MUST dedupe primary-key-remap warnings per `(Kind, Name)` pair

When multiple snapshot rows collide with the same live `(Kind, Name)` row under alternate-key match, the differ SHALL emit the `catalog.diff.primary_key_remap` warning at most once per `(Kind, Name)` pair per refresh. The full set of `field_id`s that triggered each collision SHALL be available on the returned `CatalogDelta` (new field `primary_key_remap_collisions: dict[tuple[str,str], list[str]]`). The differ classification (`appended` / `updated` / `removed`) SHALL NOT change. The CLI surface SHALL print one summary line at the end of the run.

#### Scenario: 200 custom-field rows collide on the same live tab slot

- **WHEN** the snapshot contains 200 `Custom Field` rows that each collide on a single live `(Kind, Name)` slot
- **THEN** `delta.warnings` SHALL contain at most one entry whose message starts with `catalog.diff.primary_key_remap` for that `(Kind, Name)` pair
- **AND** `delta.primary_key_remap_collisions[("Custom Field", "Auto Test Coverage")]` SHALL contain all 200 field_ids
- **AND** the catalog CLI SHALL print one summary line `catalog.diff.primary_key_remap unique_collisions=<M> total_field_ids=<N>` at the end of the run

### Requirement: The writer MUST use tdt-sheets for every read and write of the catalog tab

The writer SHALL obtain its `SheetsClient` via `tdt_sheets.SheetsClient(ServiceAccountAuth.from_env())`. It MUST NOT use `gspread`, `google-api-python-client`, or any other Sheets client directly. Every read of the live tab MUST go through `SheetsClient.read_range(...)`; every write MUST go through `SheetsClient.batch_update(...)` for the machine-owned columns of `updated` rows, and `SheetsClient.append_rows(...)` for `appended` rows.

#### Scenario: The writer uses the canonical Sheets client

- **WHEN** the writer module is imported
- **THEN** it MUST construct the client via `tdt_sheets.SheetsClient(ServiceAccountAuth.from_env())`
- **AND** MUST NOT import `gspread` or `googleapiclient`.

#### Scenario: An updated row's machine-owned columns are written in a single batch_update

- **WHEN** the differ classifies 30 rows as `updated`
- **THEN** the writer SHALL compose a single `batch_update` request with 30 `updateCells` payloads (one per row, columns A, C, D, I, J, K, L, M, N, O, P)
- **AND** MUST NOT issue 30 individual `values_update` calls.

### Requirement: The writer MUST resolve the catalog tab by name and persist the gid on first run

The writer MUST resolve the catalog tab by name via `SheetsClient.get_metadata(spreadsheet_id)` → `SpreadsheetMetadata.sheets` → `get_sheet_by_name(name)`. If the lookup misses, the writer MUST call `SheetsClient.ensure_sheet(spreadsheet_id, JIRA_CATALOG_TAB_NAME)` (which sends a bare `addSheet` request with default dimensions), then re-call `get_metadata()` to read back the newly created sheet's `gid`, write the header row, send a raw `freezeRange` `batch_update` request to freeze row 1, and append the new gid to the comma-separated `SHEET_LINKS` value in `~/.tdt/.env`. On subsequent runs, the writer MUST read the gid directly from the `SHEET_LINKS` entry that matches `JIRA_CATALOG_TAB_NAME`.

#### Scenario: First-time bootstrap creates the tab and persists the gid

- **WHEN** the writer runs and finds no worksheet matching `JIRA_CATALOG_TAB_NAME`
- **THEN** it MUST call `ensure_sheet` with the tab name
- **AND** MUST re-call `get_metadata()` to read back the newly created sheet's `gid`
- **AND** MUST send a `freezeRange` `batch_update` request to freeze row 1
- **AND** MUST read `SHEET_LINKS` from `~/.tdt/.env`
- **AND** MUST append the new gid to the comma-separated list
- **AND** MUST write the updated `SHEET_LINKS` back to `~/.tdt/.env`
- **AND** MUST log `catalog.tab_created` with the new gid.

#### Scenario: Subsequent runs reuse the persisted gid

- **WHEN** the writer runs after the first bootstrap
- **THEN** it MUST scan `SHEET_LINKS` for the entry whose gid maps to a tab titled `JIRA_CATALOG_TAB_NAME`
- **AND** MUST use that gid directly for `read` and `batch_update` calls
- **AND** MUST NOT call `get_metadata()` again on that run (the persisted gid is the source of truth after bootstrap).

### Requirement: The writer MUST refuse to write if a name lookup resolves to multiple tabs

If `get_sheet_by_name(name)` returns more than one sheet with the same title (the sheetId values differ), the writer MUST raise `CatalogTabAmbiguous` with a list of matching gids and MUST NOT write to any of them. The CLI MUST surface the error and exit non-zero.

#### Scenario: Two tabs share the configured name

- **WHEN** `get_metadata().sheets` contains two worksheets named `Jira Catalog` (gids `123` and `456`)
- **THEN** the writer MUST raise `CatalogTabAmbiguous(gids=[123, 456])`
- **AND** MUST NOT perform any write
- **AND** the CLI MUST print a clear error message instructing the operator to rename or delete one of the tabs.

### Requirement: The writer MUST use raw batch_update for all structural sheet operations

All sheet writes (header, appended rows, updated rows, removed rows, clear on build) MUST be expressed as raw `batch_update` requests. The writer MUST use `parse_a1_to_grid_range()` from `tdt_sheets/utils.py` to build grid range objects for `updateCells`, `deleteDimension`, and `freezeRange` requests.

#### Scenario: A refresh writes appended rows by computing the next free row

- **WHEN** the differ classifies N rows as `appended`
- **THEN** the writer MUST call `get_metadata()` to read the tab's `row_count`
- **AND** MUST call `write(spreadsheet_id, f"Catalog!A{row_count + 1}", rows)` with the new row data
- **AND** MUST NOT use `append_rows` (that method does not exist).

#### Scenario: A build clears the data area before writing

- **WHEN** the `build` subcommand runs on an existing tab
- **THEN** the writer MUST send a `batch_update` request with a `deleteDimension` payload covering rows 2 through the last data row
- **AND** MUST write the header and new data rows starting at row 2.

