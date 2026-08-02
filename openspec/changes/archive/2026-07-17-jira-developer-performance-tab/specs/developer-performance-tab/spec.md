## ADDED Requirements

### Requirement: Generate a Developer Performance worksheet tab

The system SHALL generate a `Developer Performance` worksheet tab in the existing sprint-report spreadsheet when the `jira-daily-reports dev-performance` CLI subcommand runs. The tab SHALL be written in addition to — never in place of — the existing `Sprint Report` and `Person Capacity` tabs.

The tab name SHALL be configurable via `DEV_PERFORMANCE_TAB_NAME` and SHALL default to `Developer Performance`.

#### Scenario: Tab is written on a successful run
- **WHEN** `jira-daily-reports dev-performance` completes successfully
- **THEN** the spreadsheet SHALL contain a `Developer Performance` tab populated with per-developer ticket rows

#### Scenario: Existing tabs remain intact
- **WHEN** the developer performance report runs
- **THEN** the existing `Sprint Report` and `Person Capacity` tabs SHALL remain unchanged

### Requirement: Render one row per (developer, ticket) with merged identity columns

The system SHALL emit one row per `(developer, ticket)` tuple. For each developer group in the output, the system SHALL merge columns 1 through 7 (Developer, Jira Account ID, Role, Window Start, Window End, Tickets Assigned (group), Last Activity (group)) vertically across that developer's ticket rows using Google Sheets `mergeType: MERGE_ALL`. Columns 8 through 20 SHALL remain unmerged.

(`MERGE_ROWS` was previously used but does NOT merge cells vertically — it merges only within each row, which would leave each ticket row with its own trivial merge of columns A:G instead of one merge spanning the developer's ticket block. `MERGE_ALL` is the correct type for the multi-row block merge.)

Each run SHALL additionally query the live sheet for any pre-existing merges that don't match the desired ranges and SHALL emit `unmergeCells` requests so the sheet converges to the correct state even when a previous run (or manual edits) left stale merges in place.

If a ticket's `Dev in Charge` field changed hands during the reporting window, the system SHALL emit one row per `(developer, ownership-period, ticket)`.

#### Scenario: Single-ticket developer group has no merge
- **WHEN** a developer has exactly one ticket in the window
- **THEN** the system SHALL write a single data row
- **AND** no merge range SHALL be emitted for that developer's columns 1–7

#### Scenario: Multi-ticket developer group is merged across columns 1–7
- **WHEN** a developer has two or more tickets in the window
- **THEN** the system SHALL write one row per ticket
- **AND** it SHALL emit a merge range covering columns 1–7 across the developer's contiguous data rows
- **AND** the merged cell value SHALL be the developer's identity value

#### Scenario: Right-hand columns are never merged
- **WHEN** the developer performance tab is rendered
- **THEN** columns 8 through 20 SHALL each contain one value per row
- **AND** no merge range SHALL cover any of columns 8–20

#### Scenario: Ownership change produces one row per developer-period
- **WHEN** a ticket's `Dev in Charge` field changes from developer A to developer B during the reporting window
- **THEN** the system SHALL emit two rows for that ticket
- **AND** each row SHALL be merged into its respective developer's identity group

### Requirement: Lock the row sort order

The system SHALL sort rows in this exact order:

1. `Developer` ascending
2. `First Deploy To Dev At` descending, NULLs last
3. `First MR Merged At` descending, NULLs last
4. `In Progress At` descending, NULLs last
5. `Jira Ticket` ascending

The system SHALL compute merge ranges from the sorted row order — never re-sort during rendering. Two runs with identical input data SHALL produce identical row order.

#### Scenario: Sort is stable across runs
- **WHEN** the same set of `(developer, ticket)` tuples is fetched on two consecutive runs
- **THEN** the rows SHALL appear in the same order in both runs

#### Scenario: Merge ranges follow sorted rows
- **WHEN** developer A appears before developer B in the sort
- **THEN** all of developer A's ticket rows SHALL appear contiguously before any of developer B's ticket rows
- **AND** the merge range for developer A SHALL cover only developer A's rows

### Requirement: Resolve Jira tickets to GitLab MRs and deployments

For each Jira ticket in the result set, the system SHALL resolve linked GitLab MR(s) using this precedence:

1. **`GET /rest/api/3/issue/{key}/remotelink`** — any URL field pointing at `git.ecomedic.vn` is treated as a GitLab MR remote link.
2. **Branch-name regex fallback** — if no remote links are found, the system SHALL query GitLab projects matching the issue's project key and search `merge_requests?source_branch=~^{KEY}-.*` per project.

For each MR found, the system SHALL fetch `GET /merge_requests/{iid}/deployments` and capture the earliest deployment whose `environment` matches `DEV_PERFORMANCE_DEPLOY_ENVIRONMENT` (default `dev`).

When the only link to GitLab came from the branch-name fallback path, the system SHALL increment the `joined_via_branch_regex` reconciliation counter for the run.

#### Scenario: merged_at fallback fills deploy gap when Deployments API returns no results

- **WHEN** an MR is found and is in `merged` state
- **AND** `GET /merge_requests/{iid}/deployments` returns an empty list (or 404)
- **AND** `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK` is set to a truthy value (`true`, `1`, `yes`, `on`, case-insensitive; defaults to `true`)
- **THEN** the system SHALL use `merged_at` as the `First Deploy To Dev At` signal
- **AND** the `merged_at_fallback` counter SHALL be incremented
- **AND** the `missing_first_deploy` counter SHALL NOT be incremented
- **AND** the system SHALL emit `dev_performance_merged_at_fallback issue=<key> merged_at=<timestamp>` at INFO level

- **WHEN** `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK` is set to a falsy value (`false`, `0`, `no`, `off`, or empty)
- **AND** `GET /merge_requests/{iid}/deployments` returns no results
- **THEN** the `First Deploy To Dev At` column SHALL be empty
- **AND** the `In Progress → Deploy` cycle time SHALL be empty
- **AND** the `missing_first_deploy` counter SHALL be incremented

> **Rationale**: GitLab's Deployments API (`/deployments`) is a separate feature that must be explicitly enabled per project. Many instances do not use it. Without this fallback, tickets with valid merged MRs show empty cycle times even though a real deploy-to-dev happened. The `merged_at` timestamp is a reasonable proxy when the deployments feature is unavailable.

#### Scenario: GitLab auth failure is soft-failed by default

- **WHEN** the GitLab auth probe (`GET /user`) returns HTTP 401 or 403
- **AND** `DEV_PERFORMANCE_GITLAB_REQUIRED` is unset or falsy (default)
- **THEN** the system SHALL emit `dev_performance_gitlab_unavailable` at ERROR level
- **AND** the system SHALL continue the run with all joins resolving to `join_method="none"`
- **AND** `joined_via_none` SHALL be incremented for every ticket

- **WHEN** `DEV_PERFORMANCE_GITLAB_REQUIRED` is set to a truthy value (`true`, `1`, `yes`, `on`, case-insensitive)
- **THEN** the system SHALL exit with a non-zero status on auth failure
- **AND** the system SHALL NOT retry the auth probe

#### Scenario: Remote-link path finds the MR
- **WHEN** the issue has a remote link to `git.ecomedic.vn/.../merge_requests/{iid}`
- **THEN** the system SHALL use that URL as the MR link
- **AND** the join method SHALL be recorded as `remote_link` in the row's evidence payload
- **AND** the `joined_via_branch_regex` counter SHALL NOT be incremented

#### Scenario: Branch regex fallback finds the MR
- **WHEN** the issue has no GitLab remote link
- **AND** a GitLab project query + `merge_requests?source_branch=~^{KEY}-.*` returns at least one match
- **THEN** the system SHALL use the regex-found MR(s) as the link
- **AND** the join method SHALL be recorded as `branch_regex` in the row's evidence payload
- **AND** the `joined_via_branch_regex` counter SHALL be incremented by 1

#### Scenario: No MR is found
- **WHEN** neither path yields an MR for an issue
- **THEN** the `First MR Merged At`, `First Deploy To Dev At`, `In Progress → Deploy`, and `Linked MR(s)` columns SHALL be empty for that row
- **AND** the issue SHALL contribute to the `missing_first_deploy` reconciliation counter
- **AND** the issue SHALL contribute to the `joined_via_none` counter

### Requirement: Read the Dev in Charge field via a configurable field ID

The system SHALL resolve the `Dev in Charge` Jira custom field ID from the env var `DEV_PERFORMANCE_DEV_IN_CHARGE_FIELD`, which SHALL default to `customfield_11520` (matching `jira_skill.scripts.configure_dev_fields.DEV_IN_CHARGE_ID`).

When a Jira ticket's `Dev in Charge` field is empty, missing, or null, the system SHALL skip that ticket for per-developer rows but SHALL still count it toward the `unmapped_dev_in_charge` reconciliation counter.

When the `Dev in Charge` field is a group (i.e. an `AccountGroup` object with nested child user accounts), the system SHALL expand the group into its child user accounts and attribute the ticket to each child. If all child accounts are absent from the roster, the system SHALL count the ticket toward the `unmapped_dev_in_charge` counter.

#### Scenario: Field ID is read from env
- **WHEN** `DEV_PERFORMANCE_DEV_IN_CHARGE_FIELD=customfield_99999`
- **THEN** the system SHALL read `fields.customfield_99999` from each issue payload
- **AND** it SHALL NOT fall back to `customfield_11520`

#### Scenario: Dev in Charge is null on the ticket
- **WHEN** an issue's `Dev in Charge` field is null
- **THEN** the system SHALL NOT emit a per-developer row for that ticket
- **AND** it SHALL contribute +1 to the `unmapped_dev_in_charge` counter

#### Scenario: Dev in Charge is a group
- **WHEN** an issue's `Dev in Charge` field is an `AccountGroup` with two child users A and B
- **AND** A is in the roster but B is not
- **THEN** the system SHALL emit one row attributed to A
- **AND** it SHALL contribute +1 to the `unmapped_dev_in_charge` counter for B

### Requirement: Compute per-(developer, ticket) metrics from changelog and MR data

The system SHALL compute the following metrics for each `(developer, ticket)` tuple, clipped to the developer's ownership period:

| Metric | Computation |
|--------|-------------|
| `In Progress At` | Earliest changelog entry on the ticket where `field == "status"` and `toString == "In Progress"` |
| `First MR Merged At` | `min(mr.merged_at for mr in linked_mrs)` |
| `First Deploy To Dev At` | `min(d.created_at for d in deployments if d.environment matches DEV_PERFORMANCE_DEPLOY_ENVIRONMENT)` |
| `In Progress → Deploy` | `(First Deploy To Dev At) - (In Progress At)` if both present |
| `Reopen Count` | Count of changelog entries where `fromString ∈ DEV_PERFORMANCE_DONE_STATUSES` and `toString == "In Progress"` |
| `Last Status Change (days)` | `(NOW - max(changelog.created for changelog in T where field=="status")) / 1 day` |
| `Stale?` | TRUE iff `(NOW - last status change) > DEV_PERFORMANCE_STALE_<status>_DAYS` |

The default `DEV_PERFORMANCE_DONE_STATUSES` SHALL be `Done,Closed,Resolved,Deployed to Production`.

#### Scenario: Reopen count uses configurable DONE_STATUSES
- **WHEN** `DEV_PERFORMANCE_DONE_STATUSES` is set to `Done,Closed`
- **THEN** the `Reopen Count` for a ticket SHALL count only transitions whose `fromString` is one of `Done` or `Closed`

#### Scenario: Reopen count clips to the developer's ownership period
- **WHEN** a ticket's `Dev in Charge` field changed from developer A to developer B during the window
- **AND** a status transition `Closed → In Progress` occurred while developer A owned the ticket
- **THEN** developer A's row SHALL count that reopen
- **AND** developer B's row SHALL NOT count it

#### Scenario: Cycle time is empty when deploy is missing
- **WHEN** a ticket has an `In Progress At` but no `First Deploy To Dev At`
- **THEN** the `In Progress → Deploy` column SHALL be empty for that row

### Requirement: Configurable stale thresholds and lookback window

The system SHALL support per-status stale thresholds via environment variables:

| Env Var | Default | Status |
|---------|---------|--------|
| `DEV_PERFORMANCE_STALE_IN_PROGRESS_DAYS` | `3` | `in progress` |
| `DEV_PERFORMANCE_STALE_CODE_REVIEW_DAYS` | `5` | `code review` |
| `DEV_PERFORMANCE_STALE_IN_QA_DAYS` | `7` | `in qa` |
| `DEV_PERFORMANCE_STALE_DEPLOY_IN_DEV_DAYS` | `14` | `deploy in dev` |

An unknown status SHALL use the default `FALSE` (not stale) with a one-time-per-run warning.

The system SHALL support a configurable ticket lookback window via `DEV_PERFORMANCE_LOOKBACK_HOURS` (default: `720` = 30 days). This controls the JQL `updated >= -<lookback_hours>h` filter that scopes which tickets are considered.

#### Scenario: Stale flag uses per-status thresholds
- **WHEN** a ticket's current status is `In Progress` and the last status change was 4 days ago
- **AND** `DEV_PERFORMANCE_STALE_IN_PROGRESS_DAYS=3`
- **THEN** the `Stale?` column SHALL be `TRUE`

#### Scenario: Unknown status uses default not-stale
- **WHEN** a ticket's current status does not appear in the stale-threshold table
- **THEN** the `Stale?` column SHALL be `FALSE`
- **AND** the system SHALL emit a one-time-per-run `dev_performance_stale_threshold_default` warning naming the unknown status

### Requirement: Always rewrite the footer and reconciliation block, even on diff cache hit

The system SHALL always rewrite the per-developer footer rows and the four-row reconciliation block on every run, regardless of whether the diff cache reports data-row changes. When the diff cache produces zero changed data rows, the system SHALL:

1. Skip the data-section write entirely (so existing sheet state is preserved).
2. Still write the footer block (one row per developer) and the four reconciliation rows at the row indices immediately after `num_data_rows` (the size of the full data set this run).

Without this, stale aggregate counts (median cycle time, stale ticket count, etc.) persist in the sheet across runs even when nothing else changed. The footer writes are idempotent: re-writing 20-cell rows produces identical cell values, so the operation is safe to repeat on every cron tick.

#### Scenario: Footer is rewritten on diff cache hit
- **WHEN** the diff cache reports zero changed data rows
- **AND** the live sheet currently has 100 data rows + 5 footer rows + 4 reconciliation rows
- **THEN** the system SHALL emit a `client.write` call to the footer row range (e.g. `A105:T113`)
- **AND** the existing 100 data rows SHALL remain untouched
- **AND** the footer values SHALL reflect the latest run's aggregates (e.g. updated stale count)

#### Scenario: Trailing empty cells are tolerated
- **WHEN** a footer row has values only in cells 1-15 and cells 16-20 are empty strings (e.g. aggregate columns that don't apply to a per-developer summary)
- **THEN** the Google Sheets `values.update` API SHALL strip the trailing empty cells at write time
- **AND** subsequent reads SHALL return a row with `len == 15` rather than `len == 20`
- **AND** the system SHALL NOT treat this as a write failure (it is expected Sheets behaviour)

### Requirement: Render a per-developer aggregate footer block

The system SHALL render a per-developer aggregate footer block below the data rows, separated by one blank row. For each developer group that appears in the data rows, the system SHALL emit exactly one footer row containing:

- `Developer` (column 1) — the developer's identity
- `Median Cycle Time` (column 8) — median of the developer's `In Progress → Deploy` durations
- `p90 Cycle Time` (column 9) — 90th percentile
- `Median Reopens/Ticket` (column 10) — median of the developer's `Reopen Count` values
- `p90 Reopens/Ticket` (column 11) — 90th percentile
- `Tickets Deployed to Dev` (column 12) — count where `First Deploy To Dev At` is not null
- `Tickets Merged` (column 13) — count where `First MR Merged At` is not null
- `Reopens (sum)` (column 14) — sum of `Reopen Count`
- `Stale Tickets` (column 15) — count where `Stale? == TRUE`

#### Scenario: Footer block appears below data rows
- **WHEN** the tab is rendered
- **THEN** data rows SHALL appear first
- **AND** the aggregate footer block SHALL appear after one blank separator row
- **AND** there SHALL be exactly one footer row per developer that appeared in the data rows

#### Scenario: Aggregates use only the developer's own tickets
- **WHEN** computing developer A's median cycle time
- **THEN** the system SHALL use only `In Progress → Deploy` values from rows belonging to developer A
- **AND** it SHALL NOT include developer B's rows in developer A's aggregates

### Requirement: Render a reconciliation footer block

The system SHALL render a reconciliation block below the aggregate footer block, separated by one blank row, containing:

- `roster_without_tickets` — one row per roster member who has zero tickets in the window
- `unmapped_dev_in_charge` — count + sample issue keys of issues whose `Dev in Charge.displayName` is not in the roster
- `missing_first_deploy` — count + sample issue keys of issues with at least one merged MR but no deployment event matching `DEV_PERFORMANCE_DEPLOY_ENVIRONMENT`
- `joined_via_branch_regex` — total count of issues whose GitLab link came from the branch-name fallback path

The reconciliation block SHALL appear directly below the aggregate footer block, separated by one blank row.

#### Scenario: Roster members with no tickets are listed
- **WHEN** a roster member has zero tickets in the reporting window
- **THEN** that member SHALL appear in the `roster_without_tickets` block
- **AND** all metric columns SHALL be empty for that row

#### Scenario: Unmapped Dev in Charge is counted
- **WHEN** an issue has a `Dev in Charge` whose `displayName` is not in the roster
- **THEN** that issue SHALL contribute +1 to the `unmapped_dev_in_charge` count
- **AND** its issue key SHALL appear in the sample-keys list

### Requirement: Use the Jira Cloud API v3 and GitLab API v4 via shared factories

The system SHALL retrieve Jira data via `tdt_core.clients.jira.JiraClientFactory` and SHALL use `PatchedJira.jql(...)` (which calls the shared `_jql_paginated` helper from `jira_daily_reports.client`) for all JQL queries. The system SHALL retrieve GitLab data via `tdt_core.clients.gitlab.GitlabClientFactory`. The system SHALL NOT use raw Jira or GitLab SDK clients or shell out to `acli` / `glab`.

The JQL `IN (...)` clause for the `Dev in Charge` roster SHALL be chunked at 150 accountIds per query to respect Jira Cloud's IN-clause size limit.

#### Scenario: JQL uses the paginated helper
- **WHEN** the system issues a JQL query for tickets
- **THEN** it SHALL call `PatchedJira.jql(...)` (or `ReportBase._search(...)` which delegates to `_jql_paginated`)
- **AND** it SHALL NOT call `jira.jql(...)` directly

#### Scenario: Roster is chunked at 150 accountIds
- **WHEN** the roster contains 200 accountIds
- **THEN** the system SHALL issue two JQL queries, each with at most 150 accountIds in the `IN (...)` clause
- **AND** it SHALL merge the result sets into one list

### Requirement: Write to Google Sheets via the tdt_sheets SDK with cached service-account auth

The system SHALL construct a `SheetsClient(ServiceAccountAuth.from_env())` instance and SHALL use it for every spreadsheet write. The system SHALL NOT call `googleapiclient.discovery.build("sheets", "v4", ...)` directly.

The system SHALL resolve the new tab's gid by parsing `SHEET_LINKS` from `~/.tdt/.env` (matching the `jira_daily_reports.catalog.writer.Writer._resolve_gid_from_env` pattern). When the tab is auto-created, the system SHALL persist the new gid back to `SHEET_LINKS`.

The system SHALL write cell data via `SheetsClient.write(spreadsheet_id, range_ref, values)`, HYPERLINK formulas via `SheetsClient.write_with_links(spreadsheet_id, tab_name, [(row, col, url, label), ...])`, and `mergeCells` + frozen-header + column-width requests via `SheetsClient.batch_update(spreadsheet_id, requests)`.

The system SHALL fail fast with an actionable credentials-path error if `ServiceAccountAuth.from_env()` raises (no service-account JSON found).

#### Scenario: ServiceAccountAuth resolves a credential
- **WHEN** `ServiceAccountAuth.from_env()` returns a valid `Credentials` object
- **THEN** the system SHALL construct a `SheetsClient` from that credential
- **AND** it SHALL NOT call `googleapiclient.discovery.build("sheets", "v4", ...)` directly

#### Scenario: Service-account JSON is absent
- **WHEN** `ServiceAccountAuth.from_env()` raises `BackendNotAvailableError` or `FileNotFoundError`
- **THEN** the system SHALL exit with a non-zero status
- **AND** it SHALL log a message instructing the operator to set `GOOGLE_SERVICE_ACCOUNT_PATH` in `~/.tdt/.env`

#### Scenario: Tab gid is resolved from SHEET_LINKS
- **WHEN** `SHEET_LINKS` contains an entry matching `DEV_PERFORMANCE_TAB_NAME`
- **THEN** the system SHALL parse the `gid=<n>` URL fragment
- **AND** it SHALL use that gid for the `batch_update` `sheetId` field

#### Scenario: Tab gid is absent and the tab is auto-created
- **WHEN** the tab is missing from `SHEET_LINKS`
- **THEN** the system SHALL create the tab via `SheetsClient.ensure_sheet(...)`
- **AND** it SHALL persist the new gid back to `SHEET_LINKS` (the env var)

### Requirement: Use a SQLite diff cache for incremental updates

The system SHALL maintain a SQLite cache at `DEV_PERFORMANCE_CACHE_PATH` (default `~/.tdt/state/jira-daily-reports/dev_performance_cache.sqlite`, computed via `tdt_core.paths.tdt_state_path("jira-daily-reports", "dev_performance_cache.sqlite")`) keyed by `(developer_account_id, issue_key)`. Each cache row SHALL store the full row payload as JSON plus the `written_at` timestamp.

On each run, the system SHALL:

1. Open an `BEGIN IMMEDIATE` advisory transaction to block concurrent runs.
2. Evict cache rows where `written_at < NOW() - 25h`.
3. For each new row, compare against the cached payload. If identical, skip the Sheets write. If different, emit a `UPDATE` for that row.
4. Insert new cache rows for any new `(developer_account_id, issue_key)` tuple.
5. On commit, release the advisory lock.

If the cache file is corrupted (`sqlite3.DatabaseError`), the system SHALL drop the cache table, treat the run as a full re-pull, and emit a `dev_performance_cache_reset` log line.

#### Scenario: Idempotent re-run produces zero Sheets writes
- **WHEN** two consecutive runs use identical input data
- **THEN** the second run SHALL NOT call the Sheets API `update` endpoint for any row
- **AND** it SHALL still touch the cache (touch the `written_at` timestamp)

#### Scenario: Status change triggers a row update
- **WHEN** a Jira ticket's status transitions from `In Progress` to `Code Review`
- **THEN** on the next run the system SHALL detect the diff in that row's `Status` and `Stale?` columns
- **AND** it SHALL emit a Sheets API update for that row only

#### Scenario: Cache corruption triggers a reset
- **WHEN** the cache file raises `sqlite3.DatabaseError` on read
- **THEN** the system SHALL drop the cache table
- **AND** treat the run as a full re-pull
- **AND** emit a `dev_performance_cache_reset reason=corruption` log line

#### Scenario: Concurrent run is rejected
- **WHEN** a second `jira-daily-reports dev-performance` process starts while a first one holds the advisory lock
- **THEN** the second process SHALL fail fast with exit code 4
- **AND** it SHALL emit a `dev_performance_lock_held` log line

### Requirement: Handle Jira and GitLab transient failures with bounded retry

Jira JQL and changelog calls SHALL retry on retryable failures (HTTP 429, "rate", "timeout", "timed out", "connection") using exponential backoff at 1s, 2s, 4s, capped at 30s, for a maximum of 3 attempts. GitLab API calls SHALL retry at most once.

Authentication failures (HTTP 401, HTTP 403) SHALL NOT retry; the system SHALL exit with a non-zero status and log an actionable error pointing at `JIRA_API_TOKEN` or `GITLAB_TOKEN` in `~/.tdt/.env`.

#### Scenario: Jira 429 retries succeed
- **WHEN** the first Jira call raises `requests.exceptions.HTTPError` containing `429`
- **THEN** the system SHALL sleep 1s and re-invoke the call
- **AND** it SHALL return the second attempt's result

#### Scenario: Jira 401 fails fast
- **WHEN** a Jira call raises `requests.exceptions.HTTPError` containing `401`
- **THEN** the system SHALL exit with a non-zero status
- **AND** it SHALL NOT retry
- **AND** it SHALL log an actionable error referencing `JIRA_API_TOKEN` in `~/.tdt/.env`

### Requirement: Emit one reconciliation log line per run

The system SHALL emit one INFO log line per run with the prefix `dev_performance_summary` containing: assigned ticket count (`rows`), footer row count (`footer_rows`), cell write count (`cells_written`), merge range count (`merged_ranges`), `unmapped_dev_in_charge`, `joined_via_branch_regex`, `joined_via_none`, `merged_at_fallback`, `missing_first_deploy`, `changelog_fetches`, and `remote_link_lookups`.

The `joined_via_none` counter reflects tickets with no GitLab MR from either the remote-link path or the branch-regex fallback. The `merged_at_fallback` counter reflects tickets where `merged_at` was used as the deploy signal because the GitLab Deployments API returned no results.

#### Scenario: Summary log line is present
- **WHEN** a run completes
- **THEN** the log output SHALL contain exactly one `dev_performance_summary` line
- **AND** that line SHALL include all named counters

### Requirement: Wrapper subprocess retries transient errors with exponential backoff

The ``_run_report`` wrapper inside ``dbos_scheduling.py`` MUST retry the CLI subprocess on transient failures before propagating the error to DBOS. Without this, every hourly cron tick that hits a slow Google Sheets API or a concurrent-SQLite lock will wake the operator for nothing.

The wrapper SHALL classify failures by inspecting the subprocess ``stderr`` for these patterns:

- ``TimeoutError``, ``Read timed out`` — Google Sheets read timeouts
- ``database is locked`` — concurrent SQLite contention from a previous run still flushing
- ``ConnectionError``, ``ConnectionResetError`` — transient network blips
- ``503``, ``502``, ``504`` — upstream service-unavailable
- ``rate``, ``too many requests`` — API rate limiting

The wrapper SHALL:

1. Attempt the subprocess up to 3 times.
2. Sleep ``2 ** attempt`` seconds between retries (2s, 4s, 8s).
3. Hard-cap each attempt at 600 seconds (10 minutes) via ``subprocess.run(timeout=600)``.
4. Emit a ``dbos_scheduling.subprocess_failed command=<cmd> attempt=<n> exit=<code> transient=<bool>`` warning line on every failure.
5. Emit a ``dbos_scheduling.subprocess_retry_success command=<cmd> attempt=<n>`` info line when a retry succeeds.
6. Surface non-transient failures (auth errors, application bugs) immediately — no retry.

#### Scenario: Sheets timeout retried successfully
- **WHEN** the first subprocess attempt exits non-zero with `stderr` containing "TimeoutError"
- **AND** the second attempt exits zero
- **THEN** the wrapper SHALL return successfully
- **AND** no exception SHALL propagate to DBOS

#### Scenario: SQLite lock contention retried
- **WHEN** the subprocess fails with "OperationalError: database is locked"
- **THEN** the wrapper SHALL sleep and retry up to 3 times
- **AND** a `dev_performance_lock_held` log line SHALL be emitted by the CLI itself

#### Scenario: All retry attempts exhausted
- **WHEN** all 3 transient-failure attempts exit non-zero
- **THEN** the wrapper SHALL raise ``subprocess.CalledProcessError``
- **AND** DBOS SHALL mark the workflow as failed

#### Scenario: Non-transient failure not retried
- **WHEN** the subprocess fails with ``ImportError`` or ``SyntaxError``
- **THEN** the wrapper SHALL raise immediately on the first attempt
- **AND** no retry sleep SHALL occur

#### Scenario: Subprocess wall-clock timeout
- **WHEN** the subprocess exceeds the 600-second ``timeout=`` limit
- **THEN** the wrapper SHALL treat the timeout as transient
- **AND** it SHALL retry the subprocess (up to the 3-attempt budget)

### Requirement: Register the dev-performance schedule via the _CRON_* constant pattern

The system SHALL register the `dev-performance` schedule by adding a `_CRON_DEV_PERFORMANCE` module-level constant to `jira_daily_reports.dbos_scheduling` and a matching entry to `jira_daily_reports.schedule.SCHEDULES`, then calling `_make_workflow("dev-performance", _CRON_DEV_PERFORMANCE, engine=engine)` from `register_all_schedules`. The constant value SHALL be `"0 * * * *"` (top of every hour).

The cron timezone SHALL be pinned from `workspace_timezone_name()` and SHALL never be `None` (matching every other schedule in the file).

The `agent-core/deployments/scheduler/generators/jira.py` `_JIRA_CMDS` tuple list SHALL include `("dev-performance", "dev-performance")` so the regenerated `~/.tdt/schedules/jira-daily-reports.yaml` manifest contains the new schedule.

The `automatic_backfill` flag SHALL be `False`, matching every other jira-daily-reports schedule.

#### Scenario: Schedule constant is exported
- **WHEN** `dbos_scheduling._CRON_DEV_PERFORMANCE` is read
- **THEN** it SHALL equal `"0 * * * *"`

#### Scenario: Schedule is registered with DBOS
- **WHEN** `register_all_schedules(engine=engine)` runs
- **THEN** the returned registered names list SHALL include `"jira-dev-performance"`
- **AND** the `engine.scheduled_workflow(...)` decorator SHALL have been invoked with `name="jira-dev-performance"` and `cron=_CRON_DEV_PERFORMANCE`

#### Scenario: Generator picks up the new constant
- **WHEN** `agent-core/deployments/scheduler/generators/jira.py:jira_manifest()` runs against the deployed `jira-daily-reports` source tree
- **THEN** the emitted manifest's `schedules` list SHALL include an entry with `name: jira-dev-performance`
- **AND** that entry's `cron` SHALL equal `_CRON_DEV_PERFORMANCE`
- **AND** that entry's `automatic_backfill` SHALL be `False`
- **AND** that entry's `timezone` SHALL equal `dbos_scheduling.TZ`

#### Scenario: Existing test schedule count is updated
- **WHEN** the `tests/test_dbos_scheduling.py::TestScheduleCount::test_expected_count_is_*` test runs
- **THEN** the expected schedules list SHALL include `"jira-dev-performance"`
- **AND** the count SHALL match the number of `_make_workflow(...)` calls in `register_all_schedules` plus one for `run-all` plus one for `catalog-refresh`

#### Scenario: Schedule cron timezone is pinned
- **WHEN** `register_all_schedules(engine=engine)` runs against any engine (mocked or real)
- **THEN** the registered `jira-dev-performance` workflow SHALL be called with a non-`None` cron timezone
- **AND** the cron timezone SHALL equal `dbos_scheduling.TZ`