# Person Capacity Worklog Mode - Specification (Delta)

**Capability:** person-capacity-worklog-mode
**Status:** Added
**Date:** 2026-06-15
**Version:** 1.1 (display-name-keyed v3 — replaces accountId-keyed v3)

---

## ADDED Requirements

### Requirement: Person-first worklog query
The system SHALL provide a `jira_daily_reports.person_worklog_source` module that owns the JQL-first worklog fetcher and the roster loader. The fetcher SHALL query Jira for worklogs whose `worklogAuthor` matches a display name from the roster (loaded from the `Dropdown Keys - Do Not Delete -` sheet tab) inside the reporting window, instead of iterating over Jira issues in a bucket.

#### Scenario: Module is importable
- **WHEN** the implementation imports `jira_daily_reports.person_worklog_source`
- **THEN** the public API SHALL expose `load_roster_display_names`, `fetch_person_worklogs`, and `find_unmapped_worklog_authors`

#### Scenario: Existing helpers are reused
- **WHEN** the module needs to format values, parse Jira datetimes, or parse a worklog started date
- **THEN** it SHALL reuse `format_value` and `parse_jira_datetime` from `jira_daily_reports.work_item_fields` and `find_column_index` from `jira_daily_reports.sheet_primitives` instead of re-implementing them

### Requirement: Roster loader
The system SHALL load the roster of people from the `Dropdown Keys - Do Not Delete -` sheet tab. The sheet tab name MAY be overridden via the `PERSON_CAPACITY_MAPPING_SHEET_NAME` environment variable; the default is `Dropdown Keys - Do Not Delete -`. The reader SHALL look for a `MEMBERS` column and an `EMAIL/Teams ID` (a.k.a. `Jira Nick Name`) column and use the `jira_nick_name` value as the display name.

#### Scenario: Roster is loaded from the Dropdown Keys tab
- **WHEN** `load_roster_display_names(sheet_client, spreadsheet_id)` runs
- **THEN** it SHALL return a `RosterLoadResult` whose `display_names` list contains the `jira_nick_name` values from the Dropdown Keys tab
- **AND** the `roster_entries` tuple SHALL contain one `RosterEntry` per row, carrying `member_key`, `jira_nick_name`, and `role`

#### Scenario: Row with empty jira_nick_name is excluded
- **WHEN** a roster row has a `member_key` but an empty `jira_nick_name`
- **THEN** the system SHALL exclude that row from the `display_names` list and from `roster_entries`
- **AND** it SHALL append the `member_key` to the `missing_display_name_rows` tuple in the reconciliation payload

#### Scenario: Duplicate member key is reported
- **WHEN** two roster rows share the same `member_key`
- **THEN** the first occurrence SHALL win
- **AND** the second occurrence SHALL be excluded from `display_names` and `roster_entries`
- **AND** a `duplicate_member_key_rows` reconciliation entry SHALL be emitted for the duplicate

#### Scenario: Display names are deduplicated
- **WHEN** the `display_names` list is built
- **THEN** it SHALL contain each display name at most once (set semantics)
- **AND** if two `member_keys` share the same `jira_nick_name`, a `display_name_collisions` reconciliation entry SHALL be emitted for the duplicate

### Requirement: JQL-first worklog fetch
The system SHALL execute a JQL query of the form `worklogAuthor in (<displayNames>) AND worklogDate >= "<start>" AND worklogDate <= "<end>"` and SHALL filter the returned worklogs to the roster display-name set and to the `[window_start, window_end]` interval on `started`.

#### Scenario: JQL is keyed by worklogAuthor with display names
- **WHEN** the fetcher runs with `display_names = ["Alice N.", "Bob N.", ...]` and a window
- **THEN** it SHALL issue a JQL whose `worklogAuthor in (...)` clause contains exactly those display names (as quoted strings)
- **AND** the `worklogDate` range SHALL match the requested window

#### Scenario: Worklogs outside the window are excluded
- **WHEN** an issue has worklog entries with `started` outside `[window_start, window_end]`
- **THEN** those entries SHALL be excluded from the aggregate

#### Scenario: Worklogs from non-roster authors are excluded
- **WHEN** an issue has worklog entries whose `author.displayName` is not in the roster
- **THEN** those entries SHALL be excluded from the aggregate

#### Scenario: Roster is chunked at 150 display names
- **WHEN** the roster contains more than 150 display names
- **THEN** the fetcher SHALL split the JQL into chunks of at most 150 display names
- **AND** it SHALL run each chunk sequentially
- **AND** it SHALL merge the results into a single list of `PersonWorklogAggregate`
- **AND** it SHALL log a `worklog_jql_chunked chunk=N total=M` line for each chunk

#### Scenario: JQL is paginated
- **WHEN** the JQL response indicates more results exist (e.g. `startAt + len(page) < total`)
- **THEN** the fetcher SHALL continue paginating with `startAt` until all results are exhausted
- **AND** it SHALL respect the `PatchedJira.jql()` pagination contract from `tdt_core.clients.jira`

### Requirement: Retry on rate limit and timeout
JQL pagination calls and `issue_get_worklog` calls SHALL retry on retryable failures (HTTP 429, "rate", "timeout", "timed out", "connection") with exponential backoff: 1s, 2s, 4s, capped at 30s, for a maximum of 3 attempts.

#### Scenario: Retry succeeds on the second attempt
- **WHEN** the first call to `jira.jql()` raises a `requests.exceptions.HTTPError` whose message contains "429"
- **THEN** `call_with_retry` SHALL sleep for 1s and re-invoke the callable
- **AND** the second attempt result SHALL be returned to the caller

#### Scenario: Retry gives up after max attempts
- **WHEN** all 3 attempts fail with a retryable error
- **THEN** `call_with_retry` SHALL re-raise the last exception
- **AND** it SHALL log a `worklog_jira_retry` warning on each retry

#### Scenario: Non-retryable errors are not retried
- **WHEN** the callable raises an exception whose message does not match the retryable token set
- **THEN** `call_with_retry` SHALL re-raise it immediately without sleeping

### Requirement: Pre-flight checks
The fetcher SHALL run three pre-flight checks before any Jira call. The `JIRA_FILTER_ID` environment variable SHALL NOT be required for the activity-only flow.

#### Scenario: Empty roster fails fast
- **WHEN** `load_roster_display_names` returns a `RosterLoadResult` with empty `display_names`
- **THEN** the fetcher SHALL fail with a `person_capacity_roster_unavailable` log
- **AND** it SHALL raise an actionable error pointing at the Dropdown Keys tab name

#### Scenario: Invalid window fails fast
- **WHEN** `window_start > window_end`
- **THEN** the fetcher SHALL fail with a `person_capacity_window_invalid` log
- **AND** it SHALL raise an actionable error naming the window bounds

#### Scenario: Oversized window warns but proceeds
- **WHEN** `window_days > 90`
- **THEN** the fetcher SHALL log a `person_capacity_window_oversized` warning
- **AND** it SHALL continue execution

#### Scenario: JIRA_FILTER_ID is not required
- **WHEN** `sprint-sheet` runs without `JIRA_FILTER_ID` set
- **THEN** the pre-flight check SHALL NOT raise the legacy `JIRA_FILTER_ID is required` error
- **AND** the activity-only flow SHALL proceed using the roster-driven JQL

### Requirement: Unmapped worklog authors
The fetcher SHALL surface unmapped worklog authors via `find_unmapped_worklog_authors(aggregates, roster_names)`. The function SHALL return one `UnmappedWorklogAuthor` per worklog-author `displayName` that is not in `roster_names` and that has at least one entry.

#### Scenario: Unmapped author is reported
- **WHEN** a worklog author with `displayName = "X"` appears in the JQL results
- **AND** `"X"` is not in the roster
- **THEN** `find_unmapped_worklog_authors` SHALL return one `UnmappedWorklogAuthor` with `display_name = "X"`
- **AND** the entry SHALL include the total seconds, the first `started`, the last `started`, and the `account_id` (if available from the worklog author)

#### Scenario: Roster members are not flagged as unmapped
- **WHEN** a worklog author with `displayName = "Y"` appears in the JQL results
- **AND** `"Y"` is in the roster
- **THEN** `find_unmapped_worklog_authors` SHALL NOT return an entry for `"Y"`

#### Scenario: Authors with no entries are not reported
- **WHEN** a displayName has zero `PersonWorklogEntry` items in the window
- **THEN** it SHALL NOT appear in the unmapped list

### Requirement: Activity-only Person Capacity tab layout
The `Person Capacity` tab SHALL contain, in this order, the columns: `No.`, `Person`, `Jira Account ID`, `Role`, `Worked Tickets`, `Logged Total`, `Worked Ticket Links`, `Daily Ticket Details`, then one column per day in the window. The `Jira Account ID` column SHALL carry the worklog `author.accountId` (best-effort enrichment, may be empty for authors whose accountId Jira did not return).

#### Scenario: Removed columns are absent
- **WHEN** the sheet is written
- **THEN** the tab SHALL NOT contain `Assigned Tickets`, `Original Estimation Total`, `Planned Issues`, `Planned Tasks`, or `Planned Estimate`

#### Scenario: Worked ticket links are readable
- **WHEN** a person has worked on issue keys `K1, K2, K3`
- **THEN** the `Worked Ticket Links` cell SHALL contain the keys as plain text, one key per line (e.g. `K1\nK2\nK3`), so the user can copy/paste them into Jira search
- **AND** the `Daily Ticket Details` cell SHALL contain a human-readable diagnostic text in the form `YYYY-MM-DD: K1 (Xs), K2 (Ym), ...` (one line per day, with seconds summed per issue)
- **AND** the per-day cells SHALL carry both the worked ticket keys AND the time labels (e.g. `K1 (1h), K2 (30m)` for a day with two issues, or `K1 (1h)` for a single-issue day), matching the v1.0 legacy contract

#### Scenario: Per-day cell is the daily logged tickets diagnostic
- **WHEN** a person has logged work on day `YYYY-MM-DD` across one or more issues `K1, K2, ..., Kn`
- **THEN** the per-day cell for that date SHALL be `K1 (Xs), K2 (Ym), ..., Kn (Zs)` (issues sorted by key, seconds summed per (day, issue), comma-separated, with time labels via `format_seconds`)
- **AND** the time labels SHALL be in `Xh Ym` format (e.g. `1h`, `30m`, `1h 30m`) consistent with the `Logged Total` column
- **AND** multiple worklog entries on the same (day, issue) SHALL be summed before formatting
- **AND** days with zero worklogs SHALL render as a single space (the v1.3 trailing-empty fix)

#### Scenario: Clickable links are available via the per-day bucket cells
- **WHEN** a user wants to click through to a specific issue worked on a specific day
- **THEN** the per-day bucket cell for that day SHALL carry the issue keys + time labels as plain text (e.g. `K1 (1h), K2 (30m)`)
- **AND** the report header SHALL carry the report's filter and board links as clickable `=HYPERLINK(...)` formulas
- **AND** the `Worked Ticket Links` and `Daily Ticket Details` cells SHALL carry plain-text keys (one cell, one formula constraint)

> **Note:** Google Sheets cells can only carry one working formula. Embedding
> multiple `=HYPERLINK(...)` in a single cell (joined by `\n`) does not work:
> only the first one is clickable, and the rest become plain text starting
> with `=`. The clickable surface is the report header links; the per-day
> cells, `Worked Ticket Links`, and `Daily Ticket Details` cells all carry
> plain text. Users can copy/paste the issue keys from `Worked Ticket Links`
> into Jira search for click-through.

#### Scenario: Logged Total reconciles with daily cells
- **WHEN** a person has a `Logged Total` value of `N` seconds
- **THEN** the sum of the daily cells for that row SHALL equal `N` (the v1 reconciliation invariant is preserved)

#### Scenario: Daily column count matches window
- **WHEN** the reporting window spans `D` days
- **THEN** the tab SHALL contain exactly `D` daily columns, one per day in the window

### Requirement: Identity resolution for the Person column
For roster members, the `Person` column SHALL resolve in the order: `member_key` (preferred) → `jira_nick_name` (display name). For unmapped worklog authors (no roster match), the `Person` column SHALL display the `displayName` from the worklog author.

#### Scenario: Roster member with member_key
- **WHEN** a roster row has `member_key = "alice"` and `jira_nick_name = "Alice Nguyen"`
- **THEN** the `Person` column SHALL display `alice`

#### Scenario: Roster member with empty member_key
- **WHEN** a roster row has an empty `member_key` but a non-empty `jira_nick_name = "Alice Nguyen"`
- **THEN** the row SHALL be skipped by `load_roster_display_names` (member_key is required for the roster)

#### Scenario: Unmapped worklog author
- **WHEN** a worklog author with `displayName = "Ghost"` is not in the roster
- **THEN** the `Person` column SHALL display `Ghost`

### Requirement: Row ordering
Active rows (roster members with worklogs) SHALL be sorted by `Logged Total` desc, then by `Worked Tickets` desc, then by `Person` asc. Roster members without worklogs SHALL be rendered in a separate visual block, sorted by `Person` asc. Reconciliation rows SHALL be rendered in a single block at the bottom, in the fixed order: `roster_row_missing_display_name`, `roster_row_duplicate_member_key`, `roster_display_name_collision`, `jira_display_name_collision`, `unmapped_worklog_authors`, `roster_without_worklogs`.

#### Scenario: Active rows are sorted by Logged Total desc
- **WHEN** multiple roster members have worklogs
- **THEN** the row with the highest `Logged Total` SHALL appear first
- **AND** ties SHALL be broken by `Worked Tickets` desc, then by `Person` asc

#### Scenario: Reconciliation block order is fixed
- **WHEN** reconciliation rows are rendered
- **THEN** the block SHALL appear in the order: missing display name, duplicate member key, display name collision (roster), display name collision (Jira), unmapped authors, no-worklog roster members

### Requirement: Window resolution is preserved
The workbook title parsing, sprint window derivation, timezone handling, and daily column layout logic SHALL NOT change. The activity-only flow reuses the v1 window resolver unchanged.

#### Scenario: Sprint window is used when available
- **WHEN** the workbook title or Jira sprint metadata provides a start and end date
- **THEN** the window SHALL be the sprint start and end dates

#### Scenario: Rolling window is the fallback
- **WHEN** no sprint metadata is available
- **THEN** the window SHALL be a rolling `PERSON_CAPACITY_WINDOW_DAYS`-day window ending on the report generation date

#### Scenario: Timezone handling is unchanged
- **WHEN** the worklog `started` timestamp is in a non-UTC timezone
- **THEN** daily bucketing SHALL use the same timezone resolver as the v1 flow (`PERSON_CAPACITY_TIMEZONE` → `TDT_TIMEZONE` → `TZ` → host → `UTC`)

### Requirement: Defensive handling of sparse and partial worklogs
The fetcher SHALL tolerate sparse and partial worklog data without raising.

#### Scenario: started is null or unparseable
- **WHEN** a worklog entry has a null or unparseable `started`
- **THEN** that entry SHALL be excluded from per-day bucketing
- **AND** it SHALL be counted in `Logged Total` and `Worked Tickets`
- **AND** a `worklog_started_missing issue_key=X count=N` warning SHALL be logged

#### Scenario: timeSpentSeconds is 0 or null
- **WHEN** a worklog entry has `timeSpentSeconds = 0` or null
- **THEN** that entry SHALL be counted as 0 seconds (existing behavior)

#### Scenario: Worklog author displayName is empty
- **WHEN** a worklog entry has an `author.accountId` but an empty `author.displayName`
- **THEN** the fetcher SHALL use the `accountId` as the label for the aggregate

#### Scenario: Two roster rows share a jira_nick_name
- **WHEN** two roster rows have the same `jira_nick_name`
- **THEN** a `roster_display_name_collision` reconciliation entry SHALL be emitted naming both `member_key`s
- **AND** the JQL still uses the single display name, so the JQL aggregates them; downstream display warns the user

#### Scenario: Two Jira users share a display name
- **WHEN** worklogs from two distinct Jira users (different `accountId`s) are bucketed under the same roster display name
- **THEN** the fetcher SHALL populate `aggregate.account_ids` with both `accountId`s
- **AND** `find_jira_display_name_collisions` SHALL return a tuple `(display_name, (account_id_1, account_id_2, ...))` for that aggregate
- **AND** the `Person Capacity` reconciliation block SHALL list the collision as a `jira_display_name_collision` row naming both `accountId`s

### Requirement: Test contract
The change SHALL ship with unit tests, integration tests, and a regression test.

#### Scenario: Unit tests cover the public API
- **WHEN** `tests/test_person_worklog_source.py` runs
- **THEN** it SHALL cover: roster happy path, rows missing jira_nick_name, duplicate member keys, deduplicated display names, display name collisions (roster-side), Jira-side display name collisions (two Jira users sharing a display name), JQL pagination, JQL chunking, retry on 429, window filtering, per-day bucketing, and `find_unmapped_worklog_authors` deltas

#### Scenario: Integration tests cover the new tab
- **WHEN** `tests/test_sprint_report_sheet_person_capacity.py` runs
- **THEN** it SHALL cover: the new tab is written, columns match the new layout, identity resolution maps display_name to member_key, missing display_name rows are reported, `jira_display_name_collision` reconciliation row is emitted when two Jira users share a display name, the new 8-column header is rendered without legacy `Member Key` / `Planned *` / `Assigned Tickets` columns, the daily column count matches the window length, the reconciliation block appears in the documented fixed order, time-zone bucketing uses the configured `person_timezone`, and `Logged Total` reconciles with the daily sum

#### Scenario: Regression test protects the Sprint Report tab
- **WHEN** the planning-merged flow runs alongside the activity-only flow
- **THEN** the `Sprint Report` tab SHALL remain unchanged
- **AND** the planning-merged columns SHALL NOT appear on the `Person Capacity` tab

### Requirement: Out-of-scope guarantees
The v1 contract SHALL NOT re-introduce ownership columns, SHALL NOT add a second CLI command or feature flag, and SHALL NOT wire the activity-only flow into the `CapacitySignal` Pydantic model in `jira-skill`.

#### Scenario: No second CLI command
- **WHEN** `jira-daily-reports sprint-sheet` runs
- **THEN** it SHALL run the activity-only flow as the default
- **AND** it SHALL NOT expose a second subcommand or a feature flag for the legacy flow

#### Scenario: CapacitySignal is unaffected
- **WHEN** the activity-only flow runs
- **THEN** the `CapacitySignal` Pydantic model in `jira-skill` SHALL NOT be touched
- **AND** the model SHALL continue to use the v1 issue-scope contract

### Requirement: Unicode NFC normalization for display names (v1.4.5)
The fetcher SHALL NFC-normalize display names at every boundary (roster
load, Jira author read, JQL emission) so that a roster entry in NFC
form matches a Jira author in NFD form (and vice versa). Without this
normalization, Vietnamese-named members whose roster entry was entered
via a non-Apple device and whose Jira account was created via macOS
input would be silently dropped from the report.

#### Scenario: Roster NFC matches Jira NFD
- **WHEN** the roster has `jira_nick_name = "Vũ Văn Tuân"` (NFC, 11 chars, precomposed)
- **AND** Jira returns `author.displayName = "Vũ Văn Tuân"` (NFD, 12 chars, with combining diacritics)
- **THEN** the worklog SHALL be attributed to the roster member
- **AND** the aggregate's `display_name` SHALL be the NFC form
- **AND** the per-day buckets SHALL reflect the entry's time

#### Scenario: Roster loader normalizes to NFC
- **WHEN** the `Dropdown Keys - Do Not Delete -` sheet contains an NFD-form name
- **THEN** `load_roster_display_names` SHALL NFC-normalize the value before storing it
- **AND** the resulting `RosterEntry.jira_nick_name` SHALL equal the canonical NFC form

#### Scenario: JQL emission uses NFC
- **WHEN** `_build_worklog_jql` is called with display names
- **THEN** each name in the emitted JQL string SHALL be NFC-normalized
- **AND** the resulting JQL SHALL match Jira's storage form (which accepts both NFC and NFD)

### Requirement: Report-tz windowing (v1.4.5)
The fetcher SHALL accept a `report_timezone` parameter and convert each
worklog's `started` to that timezone before evaluating the window filter
and computing per-day buckets. This ensures that a worklog at
`2026-06-10 17:00 UTC` (= `2026-06-11 00:00 +07`) is bucketed under
`2026-06-11` when the report timezone is `Asia/Ho_Chi_Minh`, not under
`2026-06-10` (the raw UTC date).

#### Scenario: Window filter uses local-tz date
- **WHEN** `fetch_person_worklogs` is called with `report_timezone="Asia/Ho_Chi_Minh"`
- **AND** a worklog's `started` is `2026-06-10T17:00:00.000+0000`
- **THEN** the worklog SHALL be considered as happening on `2026-06-11` in the report's local timezone
- **AND** the entry's `started` SHALL be converted to `+07:00` before being stored in the aggregate

#### Scenario: Per-day bucket uses local-tz date
- **WHEN** the per-day bucketing loop iterates entries in `_build_person_capacity`
- **THEN** the date key SHALL be the local-tz date of the entry's `started`
- **AND** the date key SHALL be stored as an ISO string (`"2026-06-11"`) so it matches `result["date_keys"]`

#### Scenario: Default behavior preserved when no timezone is provided
- **WHEN** `fetch_person_worklogs` is called without `report_timezone`
- **THEN** the merge path SHALL fall back to UTC
- **AND** the behavior SHALL be backward compatible with the v1.4.3 windowing contract

#### Scenario: Invalid timezone falls back to UTC with warning
- **WHEN** `report_timezone` is a name that `zoneinfo` does not recognize
- **THEN** `_parse_report_timezone` SHALL return UTC
- **AND** it SHALL log a `worklog_invalid_timezone tz=<name>` warning

#### Scenario: A documented IANA alias resolves without warning
- **WHEN** `report_timezone` is `Asia/Saigon` (an obsolete IANA alias rejected by modern `zoneinfo` since tzdata 2018c)
- **THEN** `_parse_report_timezone` SHALL resolve it to `Asia/Ho_Chi_Minh` via the alias map
- **AND** the worklog timestamp bucketing SHALL use `Asia/Ho_Chi_Minh` for the whole run
- **AND** the `worklog_invalid_timezone` warning SHALL NOT be emitted

### Requirement: Tests for v1.4.5 fixes
The change SHALL ship with regression tests that fail without the
v1.4.5 fixes and pass with them.

#### Scenario: NFC/NFD regression test
- **WHEN** `tests/test_person_worklog_source_v145.py` runs
- **THEN** `test_fetch_person_worklogs_matches_nfc_roster_to_nfd_jira` SHALL pass
- **AND** the aggregate's `display_name` SHALL be the NFC form
- **AND** `logged_total_seconds` SHALL equal the worklog's `timeSpentSeconds`

#### Scenario: Report-tz regression test
- **WHEN** `tests/test_person_worklog_source_v145.py` runs
- **THEN** `test_merge_issue_worklogs_window_uses_local_tz_at_midnight_boundary` SHALL pass
- **AND** a worklog at `2026-06-10T17:00:00.000+0000` SHALL be included in the window
- **AND** its `started` SHALL be stored in the local timezone
