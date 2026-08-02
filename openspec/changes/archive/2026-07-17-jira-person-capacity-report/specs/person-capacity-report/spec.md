## ADDED Requirements

> **Status note (2026-06-27):** This capability reflects the **v1 owner-of-original-spec
> contract**. The active implementation contract lives in
> [`jira-person-capacity-worklog-mode`](../jira-person-capacity-worklog-mode/specs/person-capacity-worklog-mode/spec.md),
> which superseded the v1 column layout and identity resolution in 2026-06 by
> adopting a person-first worklog-aggregation model.
>
> Requirements below are preserved for the historical record and for the
> follow-up ownership-metrics change that will reintroduce
> `Assigned Tickets` / `Original Estimation Total` after the worklog-mode
> rollout is fully validated. The MUSTs in this spec are **NOT currently
> binding**; the worklog-mode spec is the active source of truth.

### Requirement: Generate a person capacity worksheet tab
The system SHALL generate an additional worksheet tab for person-centric capacity reporting in the same spreadsheet used for sprint reporting when `sprint-sheet` runs. The active column layout is defined in the `person-capacity-worklog-mode` spec and supersedes the v1 layout below.

#### Scenario: Person tab is written in the same run
- **WHEN** `jira-daily-reports sprint-sheet` runs successfully
- **THEN** the system SHALL write both `Sprint Report` and `Person Capacity` tabs from the same Jira snapshot
- **AND** CLI sheet mode SHALL not perform a separate preliminary Jira report run before the sheet writer

#### Scenario: Worksheet tab is created
- **WHEN** the person capacity report runs successfully
- **THEN** the spreadsheet SHALL contain a `Person Capacity` tab with person-centric metrics

#### Scenario: Existing sprint tab remains intact
- **WHEN** the person capacity report runs
- **THEN** the existing `Sprint Report` tab SHALL remain unchanged and continue to be written separately

### Requirement: Configure person tab naming independently
The system SHALL allow the person capacity tab name and report title to be overridden independently from the sprint tab using environment variables, while defaulting to `Person Capacity` and a sprint-aware person title.

#### Scenario: Defaults are used
- **WHEN** no person-tab naming environment variables are set
- **THEN** the system SHALL use `Person Capacity` as the tab name

#### Scenario: Overrides are provided
- **WHEN** person-tab naming environment variables are set
- **THEN** the system SHALL use those overrides without changing the sprint tab naming

### Requirement: Aggregate by canonical person identity

The system MUST aggregate all person-level metrics by a canonical person identity derived from Jira accountId when available and normalized displayName otherwise.

> **Status note:** The active identity model is roster-driven
> (`jira_nick_name` keyed against the `Person Capacity Mapping` sheet
> tab) per the `person-capacity-worklog-mode` spec. The `accountId`
> preference described below remains the v1 contract and will be
> revisited if/when ownership metrics return.

The system SHALL aggregate all person-level metrics by a canonical person identity derived from Jira accountId when available and normalized displayName otherwise.

#### Scenario: Display name variants merge
- **WHEN** the same Jira user appears with different display-name formatting
- **THEN** the system SHALL group those records into one person row

#### Scenario: Stable identity is used
- **WHEN** Jira returns accountId for assignee or worklog author
- **THEN** the system SHALL prefer accountId as the canonical identity key

### Requirement: Track ownership metrics per person

The system SHALL calculate ownership metrics from the issue assignee field, including assigned ticket count and total original estimation. The visible ownership columns SHALL be `Assigned Tickets` and `Original Estimation Total`.

> **Status note:** Deferred. The active `person-capacity-worklog-mode` spec
> deliberately drops `Assigned Tickets` and `Original Estimation Total`
> from the visible column layout (see its proposal: "Drop the legacy
> `Assigned Tickets` and `Original Estimation Total` columns ...
> Re-adding ownership metrics is deferred to a follow-up change"). This
> v1 requirement remains as the historical contract that the follow-up
> change MUST satisfy when ownership metrics return.

The system SHALL calculate ownership metrics from the issue assignee field, including assigned ticket count and total original estimation. The visible ownership columns SHALL be `Assigned Tickets` and `Original Estimation Total`.

Original estimation SHALL be retrieved only from Jira original estimate (`timeoriginalestimate` or `timetracking.originalEstimateSeconds`). The system SHALL NOT use story-point custom fields or remaining estimate (`timeestimate`) as fallbacks for capacity totals.

#### Scenario: Owned estimates are summed
- **WHEN** a person is the assignee of multiple issues with original estimates
- **THEN** the system SHALL sum the original estimates into that person’s ownership total

#### Scenario: Story points are ignored for ownership totals
- **WHEN** an issue has story points but no original estimate
- **THEN** the issue SHALL count as missing or unavailable estimation for capacity reporting

#### Scenario: Unassigned issues are tracked explicitly
- **WHEN** an issue has no assignee
- **THEN** the system SHALL include it under an explicit unassigned person bucket

### Requirement: Use a fixed person row layout

The system SHALL render person rows with the following visible column order before daily date columns: `No.`, `Person`, `Assigned Tickets`, `Original Estimation Total`, `Worked Tickets`, `Logged Total`.

> **Status note:** The active column layout is defined in
> `person-capacity-worklog-mode` ("8-column activity-only layout"). The
> v1 layout below is preserved for the historical record and MUST be
> matched again if/when the deferred ownership-metrics follow-up change
> is implemented.

The system SHALL render person rows with the following visible column order before daily date columns: `No.`, `Person`, `Assigned Tickets`, `Original Estimation Total`, `Worked Tickets`, `Logged Total`.

#### Scenario: Person row layout is stable
- **WHEN** the sheet is rendered
- **THEN** the person tab SHALL keep the same column order on every run

### Requirement: Sort person rows by activity first
The system SHALL sort person rows by `Logged Total` descending, then by `Worked Tickets` descending, then by `Person` ascending.

#### Scenario: Highest activity appears first
- **WHEN** multiple people have data in the same report
- **THEN** the person with the highest logged total SHALL appear before lower-activity people

### Requirement: Track activity metrics per person from worklog authors
The system SHALL calculate person activity from worklog author entries, including worked ticket count, logged total, and per-day logged totals. The visible activity columns SHALL be `Worked Tickets` and `Logged Total`.

#### Scenario: Worked ticket count is de-duplicated per person
- **WHEN** one person logs multiple worklog rows on the same issue
- **THEN** the system SHALL count that issue once in that person’s worked ticket count

#### Scenario: Multi-author issue contributes to multiple people
- **WHEN** multiple people log work on one issue
- **THEN** the system SHALL attribute logged time and worked-ticket membership to each author independently

### Requirement: Track daily logged time per person
The system SHALL calculate logged time per person per day from worklogs authored by that person within the selected reporting window.

#### Scenario: Logs are grouped by day
- **WHEN** a person logs time on multiple days
- **THEN** the system SHALL place the logged seconds into the matching daily columns for each day

#### Scenario: Worklog author is preserved
- **WHEN** a worklog author differs from the issue assignee
- **THEN** the system SHALL attribute the logged time to the worklog author, not the assignee

#### Scenario: Daily buckets use worklog started date
- **WHEN** a worklog has a `started` timestamp
- **THEN** the system SHALL bucket logged time by that started date in the report timezone

### Requirement: Retrieve complete worklogs for aggregation
The system SHALL aggregate from complete issue worklog sets, not partial pages, when the Jira payload indicates more worklogs exist.

#### Scenario: Worklog list is paginated
- **WHEN** Jira indicates worklog total exceeds inline worklog entries
- **THEN** the system SHALL fetch additional worklog pages before computing person metrics

### Requirement: Support a configurable reporting window
The system SHALL derive the daily worklog columns from the sprint date range when available and SHALL fall back to a configurable rolling date window when sprint dates are unavailable. The date window SHALL be configurable via `PERSON_CAPACITY_WINDOW_DAYS` and default to 14 days.

#### Scenario: Sprint dates are available
- **WHEN** the live board exposes sprint start and end dates
- **THEN** the system SHALL use that sprint window to determine the daily columns

#### Scenario: Sprint dates are unavailable
- **WHEN** the live board does not support sprint metadata
- **THEN** the system SHALL use the configured rolling date window to determine the daily columns


### Requirement: Include a visible included-ticket counter and stable row ordering
The system SHALL include a `No.` counter column in the person capacity output and SHALL sort rows using a stable, documented ordering. The visible person label SHALL remain human-readable only; `accountId` SHALL be used internally for grouping.

#### Scenario: Counter column is present
- **WHEN** the sheet is rendered
- **THEN** the first column of the person rows SHALL be `No.`

#### Scenario: Row order is stable
- **WHEN** multiple people have data in the same report
- **THEN** the system SHALL sort rows deterministically so repeated runs produce the same ordering for the same source data

### Requirement: Reconcile person activity totals
The system SHALL guarantee that each person row's logged total equals the sum of the daily logged cells in that row.

#### Scenario: Daily totals reconcile
- **WHEN** person rows are generated
- **THEN** each row SHALL satisfy `logged_total == sum(daily_columns)` within integer-second precision


### Requirement: Use spreadsheet timezone for day bucketing

The system SHALL bucket daily worklog totals using the spreadsheet timezone so the report dates align with the workbook calendar.

> **Status note:** The active timezone fallback chain is implemented in
> `person_worklog_source._parse_report_timezone`. The chain matches the
> v1 spec (`PERSON_CAPACITY_TIMEZONE` → `TDT_TIMEZONE` → `TZ` → host
> workspace → `UTC`) but the spreadsheet-timezone step (the *first*
> preference in v1) is not yet wired up. The follow-up change
> `jira-person-capacity-worklog-mode` lists it as a known gap. This
> requirement is preserved as the active target.

The system SHALL bucket daily worklog totals using the spreadsheet timezone so the report dates align with the workbook calendar.

#### Scenario: Spreadsheet timezone is known
- **WHEN** the spreadsheet timezone is available
- **THEN** the system SHALL use it for daily bucket boundaries

#### Scenario: Spreadsheet timezone is missing
- **WHEN** spreadsheet timezone cannot be read
- **THEN** the system SHALL fall back to configured `PERSON_CAPACITY_TIMEZONE`, `TDT_TIMEZONE`, `TZ`, host workspace timezone, or `UTC` in that order

### Requirement: Avoid baked-in workspace IDs in runtime code
Runtime report commands SHALL retrieve Jira filter and board IDs from `~/.tdt/.env` via the shared typed Jira config and SHALL fail fast with a config error when required IDs are absent.

#### Scenario: Shared filter is absent
- **WHEN** a report command needs `JIRA_FILTER_ID` and it is not configured
- **THEN** the command SHALL fail with an actionable message telling the operator to set `JIRA_FILTER_ID` in `~/.tdt/.env`

#### Scenario: Sprint board is absent
- **WHEN** `sprint-sheet` needs board capabilities and `JIRA_BOARD_ID` is not configured
- **THEN** the command SHALL fail with an actionable message telling the operator to set `JIRA_BOARD_ID` in `~/.tdt/.env`

### Requirement: Support service-account JSON authentication for sheet writes
The system SHALL support live sheet writes via the Google Sheets API v4 using service-account credentials loaded from a configured JSON file.

#### Scenario: OAuth token is expired or revoked
- **WHEN** `GOOGLE_SERVICE_ACCOUNT_PATH` or `GOOGLE_APPLICATION_CREDENTIALS` points to a readable service-account JSON file
- **THEN** the system SHALL load Google service-account credentials from that file for Google Sheets/Drive scopes
- **AND** it SHALL build a Sheets API v4 client directly in Python without shelling out to `gws`

#### Scenario: Standard application credentials are provided
- **WHEN** `GOOGLE_APPLICATION_CREDENTIALS` is set
- **THEN** the system SHALL allow it as an alternative service-account JSON path
- **AND** it SHALL still prefer `GOOGLE_SERVICE_ACCOUNT_PATH` when both are configured
