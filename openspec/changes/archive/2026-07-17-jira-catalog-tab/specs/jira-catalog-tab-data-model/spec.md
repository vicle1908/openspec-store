# jira-catalog-tab-data-model Specification

## Purpose

Define the column schema, the row shape, and the primary-key contract for the `Jira Catalog` tab in the Sprint 16 workbook. The catalog is a flat single-tab dataset: one row per Jira metadata item (label, custom field, priority, resolution, component, fix version, issue type), with a discriminator column that tells the team which kind of item the row describes. The tab is the contract between the `jira-daily-reports.catalog` writer and the humans who own the documentation columns.

## Requirements

## ADDED Requirements

### Requirement: The catalog tab MUST live in the Sprint 16 workbook as a single flat sheet

The catalog SHALL be rendered as a single Google Sheets worksheet named per the `JIRA_CATALOG_TAB_NAME` env var (default `"Jira Catalog"`) inside the same spreadsheet identified by `SPREADSHEET_ID` in `~/.tdt/.env` (the Sprint 16 workbook). The tab MUST NOT be split into per-kind sub-tabs.

#### Scenario: Catalog tab is found in the Sprint 16 workbook

- **WHEN** the writer calls `SheetsClient.list_worksheets()` on the Sprint 16 spreadsheet
- **THEN** it SHALL find a worksheet whose title equals `JIRA_CATALOG_TAB_NAME`
- **AND** that worksheet SHALL be the only target the writer reads or writes.

#### Scenario: Catalog tab does not yet exist on a fresh workbook

- **WHEN** the writer calls `SheetsClient.list_worksheets()` and finds no worksheet named `JIRA_CATALOG_TAB_NAME`
- **THEN** the writer SHALL call `SheetsClient.add_worksheet(name=JIRA_CATALOG_TAB_NAME, rows=2000, cols=20)`
- **AND** SHALL append the new gid to the comma-separated `SHEET_LINKS` value in `~/.tdt/.env`
- **AND** SHALL emit a `catalog.tab_created` log line carrying the new gid.

### Requirement: Each catalog row MUST encode exactly one Jira metadata item keyed by (Kind, Name)

The primary key of a catalog row SHALL be the tuple `(Kind, Name)`. The `Kind` column MUST be one of: `Label`, `Custom Field`, `Priority`, `Resolution`, `Component`, `Fix Version`, `Issue Type`. The `Name` column MUST be the display name of the metadata item as returned by the Jira API. For custom fields, the `Field ID` column MUST carry the Jira `customfield_NNNNN` string and is an alternate key that the differ MUST honor when `Name` changes.

#### Scenario: A custom field row carries both Name and Field ID

- **WHEN** the catalog includes a custom field whose Jira display name is `Severity` and whose ID is `customfield_10016`
- **THEN** the row MUST set `Kind = Custom Field`, `Name = Severity`, `Field ID = customfield_10016`
- **AND** the differ MUST treat `(Kind, Field ID)` as a stable key for that row even if a human later edits `Name`.

#### Scenario: Two rows can share a Name when their Kind differs

- **WHEN** a label named `mobile` exists in Jira AND a component named `mobile` exists in Jira
- **THEN** the catalog SHALL contain two rows: one with `(Kind=Label, Name=mobile)` and one with `(Kind=Component, Name=mobile)`
- **AND** the differ MUST classify them independently.

### Requirement: The catalog MUST define a fixed column schema with machine-owned and human-owned halves

The catalog tab MUST use the following column order, frozen in the spec so the writer and humans agree on cell positions:

| # | Column           | Owner    | Description                                                                 |
|---|------------------|----------|-----------------------------------------------------------------------------|
| A | Kind             | machine  | One of the seven allowed values above.                                      |
| B | Name             | machine  | Jira display name; the human-owned alternate for custom fields.            |
| C | Field ID         | machine  | Jira `customfield_NNNNN` for custom fields; empty otherwise.               |
| D | Type             | machine  | Jira schema type (e.g. `option`, `string`, `priority`); empty for labels.   |
| E | Description      | human    | Free-text description; team-owned.                                         |
| F | Purpose          | human    | When/why the team uses this; team-owned.                                   |
| G | Owner            | human    | Team member or group accountable; team-owned.                              |
| H | Notes            | human    | Free-form annotations; team-owned.                                         |
| I | Allowed Values   | machine  | Newline-separated list of allowed values; empty when not applicable.       |
| J | Usage Count      | machine  | Count of distinct tickets in the lookback window that carry this item.     |
| K | First Seen       | machine  | ISO-8601 date of the earliest ticket in the window carrying this item.     |
| L | Last Seen        | machine  | ISO-8601 date of the most recent ticket in the window carrying this item.   |
| M | Jira Updated     | machine  | ISO-8601 timestamp of the item's last change in Jira metadata.             |
| N | Status           | machine  | `Active` (seen ≤ 30d), `Stale` (31-89d), or `Removed` (not in window).      |
| O | Source Project   | machine  | Comma-separated project keys that contributed usage data.                  |
| P | Issue Keys       | machine  | Comma-separated, sorted, deduplicated list of issue keys that carry this label or tracked custom field in the lookback window; empty for all other kinds. |

The writer MUST treat columns A, C, D, I, J, K, L, M, N, O, P as **machine-owned** and SHALL overwrite them on every refresh. The writer MUST treat columns E, F, G, H as **human-owned** and SHALL NOT overwrite them on a refresh.

#### Scenario: A refresh updates only machine-owned columns on a changed row

- **WHEN** the differ classifies a row as `changed` because `Usage Count` rose from 3 to 5
- **THEN** the writer MUST overwrite cells in columns A, C, D, I, J, K, L, M, N, O, P for that row
- **AND** MUST leave cells in columns E, F, G, H untouched
- **AND** the human-edited `Description`, `Purpose`, `Owner`, `Notes` values SHALL be preserved exactly.

#### Scenario: A refresh marks a row Removed but does not delete it

- **WHEN** the differ classifies a row as `removed` because no ticket in the lookback window carries that label
- **THEN** the writer MUST set column N (`Status`) to `Removed`
- **AND** MUST set column L (`Last Seen`) to the previous value
- **AND** MUST NOT delete the row.

### Requirement: The Issue Keys column MUST list the tickets that carry a label or tracked custom field

The `Issue Keys` column (P) MUST be populated for `Label` rows and for tracked `Custom Field` rows (custom fields listed in `JIRA_CATALOG_TRACKED_FIELDS`). For all other kinds (`Priority`, `Resolution`, `Component`, `Fix Version`, untracked `Custom Field`, `Issue Type`) the column MUST be empty.

The cell value MUST be the comma-separated, lexicographically sorted, deduplicated list of issue keys (e.g. `PUB-42, PUB-43, PUB-51`) drawn from the JQL lookback window. Order is determined by sorting the issue-key strings; the writer MUST NOT preserve any insertion order from the JQL pagination.

#### Scenario: A label row lists every ticket that carries the label

- **WHEN** the joiner emits a Label row for the label `mobile-ios` and the JQL window contains issues `PUB-42`, `PUB-43`, and `PUB-51` that carry this label
- **THEN** the row's column P MUST read exactly `PUB-42, PUB-43, PUB-51` (sorted, dedup, comma-separated)
- **AND** no other column on that row MUST include an issue-key list.

#### Scenario: A tracked custom field row lists every ticket that has any value for the field

- **WHEN** the joiner emits a tracked Custom Field row for `Severity` and the JQL window contains issues `PUB-7, PUB-8, PUB-9` that carry any value for the `Severity` custom field
- **THEN** the row's column P MUST read exactly `PUB-7, PUB-8, PUB-9` (sorted, dedup, comma-separated).

#### Scenario: A system-kind row has an empty Issue Keys column

- **WHEN** the joiner emits a Priority row for `Highest`
- **THEN** the row's column P MUST be empty.
- **AND** the same MUST hold for Resolution, Component, Fix Version, Issue Type, and untracked Custom Field rows.

### Requirement: The first row of the tab MUST be a header row with frozen formatting

The first row SHALL contain the column names from the table above, in the listed order, with `sheetProperties.gridProperties.frozenRowCount = 1` so the header stays visible while the team scrolls. The first row MUST NOT contain any data.

#### Scenario: A fresh catalog tab has a frozen header row

- **WHEN** the writer creates the catalog tab
- **THEN** it MUST write the 15 column names to row 1
- **AND** it MUST freeze the first row via `SheetsClient.set_frozen_rows(1)`.

