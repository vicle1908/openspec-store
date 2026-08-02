# Capability: sprint-switch

## Purpose

Provide a single CLI command that rotates the TDT ecosystem to a new sprint workbook, updating all config files, clearing stale state, creating Jira objects, and validating the result. Eliminate the need for manual multi-file config editing during sprint transitions.

## ADDED Requirements

### Requirement: `sprint-switch` command SHALL accept a spreadsheet URL or ID

The CLI SHALL accept either a full Google Sheets URL (`https://docs.google.com/spreadsheets/d/<id>/edit`) or a raw spreadsheet ID as a positional argument.

#### Scenario: Valid spreadsheet URL

- **WHEN** the user runs `jira-daily-reports sprint-switch "https://docs.google.com/spreadsheets/d/1_Nc_6H7KoKTD_gMQoItK6PSLUnIr9kDArTfsx_iFdto/edit"`
- **THEN** the command SHALL extract the spreadsheet ID `1_Nc_6H7KoKTD_gMQoItK6PSLUnIr9kDArTfsx_iFdto`
- **AND** SHALL proceed with the rotation workflow

#### Scenario: Valid raw spreadsheet ID

- **WHEN** the user runs `jira-daily-reports sprint-switch "1_Nc_6H7KoKTD_gMQoItK6PSLUnIr9kDArTfsx_iFdto"`
- **THEN** the command SHALL treat the input as a spreadsheet ID directly

#### Scenario: Missing argument

- **WHEN** the user runs `jira-daily-reports sprint-switch` without a spreadsheet argument
- **THEN** the command SHALL exit with code 2 and print usage guidance

### Requirement: `sprint-switch` SHALL parse the workbook title to derive sprint metadata

The command SHALL call `read_spreadsheet_title()` to get the workbook title, then parse it using `parse_sprint_number()` and `parse_sprint_dates()` from `tdt_core.sprint_scope`.

#### Scenario: Valid title format "Sprint N (DD Mon – DD Mon YYYY)"

- **WHEN** the workbook title is "Sprint 19 (20 Jul – 31 Jul 2026)"
- **THEN** the command SHALL extract sprint_number=19, start=2026-07-20, end=2026-07-31

#### Scenario: Invalid title format

- **WHEN** the workbook title does not match the expected pattern
- **THEN** the command SHALL exit with code 3 and print: "Error: could not parse sprint number and dates from workbook title '<title>'. Expected format: 'Sprint N (DD Mon – DD Mon YYYY)'"

### Requirement: `sprint-switch` SHALL update `config.toml` as the single source of truth

The command SHALL update the following keys in `~/.tdt/config.toml`:

1. `current_sprint` — set to the new sprint number
2. `[google_sheets] sprint_spreadsheet_id` — set to the new spreadsheet ID
3. `[sprint_sheets.sprint_<new>]` — create with `spreadsheet_id`, `created_at`
4. `[sprint_sheets.sprint_<prev>]` — add `archived_at` timestamp to the previous sprint section
5. `[jira]` section — updated after sprint-bootstrap resolves filter/board IDs

#### Scenario: First run with no previous sprint

- **WHEN** `config.toml` has no `current_sprint` key
- **THEN** the command SHALL set `current_sprint` and create the sprint section without archiving

#### Scenario: Subsequent run with existing sprint

- **WHEN** `config.toml` has `current_sprint = 18`
- **THEN** the command SHALL add `archived_at` to `[sprint_sheets.sprint_18]`
- **AND** set `current_sprint = 19`
- **AND** create `[sprint_sheets.sprint_19]`

### Requirement: `sprint-switch` SHALL derive `.env` updates from `config.toml`

The command SHALL update `~/.tdt/.env` with:

1. `SPREADSHEET_ID="<new_id>"` — the new spreadsheet ID
2. `SHEET_LINKS=""` — cleared so gids are re-discovered on first run
3. `JIRA_DEFAULT_FILTER_IDS="<new_filter_id>"` — set after bootstrap resolves the filter
4. Sprint comment on line 1 — updated to reflect new sprint

#### Scenario: Stale SHEET_LINKS

- **WHEN** `SHEET_LINKS` contains gids from the old spreadsheet
- **THEN** the command SHALL clear it to empty string
- **AND** SHALL log: "Cleared SHEET_LINKS — gids will be re-discovered on first run"

### Requirement: `sprint-switch` SHALL delete stale freshness state

The command SHALL delete `~/.tdt/state/jira-daily-reports/freshness/<old_spreadsheet_id>.json` if it exists.

#### Scenario: Freshness file exists for old spreadsheet

- **WHEN** the old spreadsheet ID has a freshness marker
- **THEN** the command SHALL delete it
- **AND** SHALL log: "Deleted stale freshness marker for <old_id>"

### Requirement: `sprint-switch` SHALL run `sprint-bootstrap --live`

After updating config files, the command SHALL invoke `sprint-bootstrap --spreadsheet <new_id> --live` to:

1. Read the workbook title (already parsed)
2. Find-or-create the Jira filter (`Sprint N (dates)`)
3. Find-or-create the Jira board (`Sprint N Board`)
4. Write Sprint Report + Person Capacity tabs

#### Scenario: Bootstrap succeeds

- **WHEN** sprint-bootstrap creates filter and board successfully
- **THEN** the command SHALL update `config.toml` `[jira]` section with resolved `filter_id` and `board_id`
- **AND** SHALL print a summary with sprint number, dates, filter ID, board ID

#### Scenario: Bootstrap fails

- **WHEN** sprint-bootstrap encounters an error
- **THEN** the command SHALL print the error
- **AND** SHALL NOT roll back config changes (partial state is recoverable by re-running)

### Requirement: `sprint-switch` SHALL support dry-run mode

The `--dry-run` flag SHALL show all proposed changes without writing anything.

#### Scenario: Dry-run with valid spreadsheet

- **WHEN** the user runs `jira-daily-reports sprint-switch <url> --dry-run`
- **THEN** the command SHALL print:
  - What config.toml sections would be added/modified
  - What .env values would change
  - What freshness files would be deleted
  - What Jira objects would be created
- **AND** SHALL NOT write to any file or call any Jira API

### Requirement: `load_sprint_config()` bridge SHALL inject config.toml values into os.environ

The `tdt_core.config.load_sprint_config()` function SHALL:

1. Read `~/.tdt/config.toml`
2. Look up `current_sprint` → find `[sprint_sheets.sprint_<N>]`
3. Set `os.environ.setdefault("SPREADSHEET_ID", spreadsheet_id)`
4. Set `os.environ.setdefault("JIRA_DEFAULT_FILTER_IDS", default_filter_ids)`
5. Set `os.environ.setdefault("JIRA_PROJECT_KEY", project_key)`
6. Set defaults for `PERSON_CAPACITY_*`, `DEV_PERFORMANCE_*`, `REPORT_FRESHNESS_*`

**Timing constraint:** The bridge MUST run before any consumer reads `SPREADSHEET_ID`. In the webhook-receiver, `Settings.__init__()` calls `load_tdt_env()` which calls `load_sprint_config()`. In the Docker scheduler, `scheduler_setup.py` calls `load_tdt_env()` at startup. The bridge uses `os.environ.setdefault()` so values injected by `.env` (via Docker env_file) take precedence during migration.

#### Scenario: config.toml has new schema

- **WHEN** `config.toml` contains `current_sprint = 19`
- **THEN** `load_sprint_config()` SHALL inject all sprint-critical values into `os.environ`
- **AND** SHALL use `setdefault` so existing `.env` values still override

#### Scenario: config.toml has no current_sprint

- **WHEN** `config.toml` lacks the `current_sprint` key
- **THEN** `load_sprint_config()` SHALL be a no-op
- **AND** consumers SHALL continue reading from `.env` as before

#### Scenario: config.toml doesn't exist

- **WHEN** `~/.tdt/config.toml` doesn't exist
- **THEN** `load_sprint_config()` SHALL be a no-op with no error

### Requirement: `sprint-switch` SHALL update `config.yaml` to keep SchedulerSettings in sync

The command SHALL update `~/.tdt/config.yaml` `sprint_report.spreadsheet_url` to the new spreadsheet URL. This is necessary because `tdt_core.scheduler.settings.SchedulerSettings` loads from `config.yaml` independently of `config.toml`.

#### Scenario: config.yaml exists with sprint_report section

- **WHEN** `config.yaml` has `sprint_report.spreadsheet_url`
- **THEN** the command SHALL update the URL to the new spreadsheet
- **AND** SHALL preserve all other keys in the file

### Requirement: Docker compose.yaml SHALL NOT hardcode PERSON_CAPACITY_MAPPING_SHEET_NAME

The hardcoded `PERSON_CAPACITY_MAPPING_SHEET_NAME` in `agent-core/compose.yaml` OVERRIDES config.toml values. This MUST be removed so config.toml is the single source of truth.

#### Scenario: After migration

- **WHEN** `PERSON_CAPACITY_MAPPING_SHEET_NAME` is set in `config.toml [person_capacity]`
- **THEN** the Docker compose.yaml SHALL NOT set this env var
- **AND** the container SHALL read it from config.toml via the bridge

### Requirement: SHEET_LINKS gid cache mechanism SHALL be deleted

The entire SHEET_LINKS system (gid caching in `.env`, write-back loops, `_env_quoting.py` module) SHALL be removed and replaced with dynamic tab ID discovery via the Sheets API.

#### Scenario: Tab ID discovery

- **WHEN** a consumer needs to resolve a tab by name (e.g. "Developer Performance", "Jira Catalog")
- **THEN** the system SHALL call `sheets.get_metadata(spreadsheet_id)` to discover tab IDs dynamically
- **AND** SHALL NOT read from `SHEET_LINKS` env var
- **AND** SHALL NOT write gid values back to `.env`

#### Scenario: SHEET_LINKS env var is absent

- **WHEN** `SHEET_LINKS` is not set in `.env`
- **THEN** all tab discovery SHALL work via dynamic API calls
- **AND** no error or warning SHALL be emitted

### Requirement: Legacy `.env` backup files SHALL be deleted

The following stale backup files SHALL be deleted:
- `~/.tdt/.env.backup.20260527_085942`
- `~/.tdt/.env.bak`
- `~/.tdt/.env.bak.sprint16_20260608_210442`
- `~/.tdt/.env.bak2`

#### Scenario: Backup files exist from previous sprint transitions

- **WHEN** `~/.tdt/` contains `.env.bak*` or `.env.backup.*` files
- **THEN** `sprint-switch` SHALL delete all such files
- **AND** SHALL log: "Deleted N stale .env backup files"

### Requirement: Legacy state migration code SHALL be removed

The `migrate_legacy_state_file` and `migrate_legacy_state_dir` calls in `tdt_sheet.py` and `webhook-receiver/settings.py` are dead code (migration completed). They SHALL be removed.

#### Scenario: After removal

- **WHEN** the application starts
- **THEN** no legacy state migration SHALL be attempted
- **AND** existing canonical state files SHALL remain untouched

### Requirement: Stale config.toml sprint entries SHALL be archived

Sprint entries older than the previous sprint (sprint 14–17) SHALL be removed from `config.toml`. Only the current sprint and one archived sprint SHALL be retained.

#### Scenario: After cleanup

- **WHEN** `config.toml` is inspected
- **THEN** `sprint_sheets` SHALL contain at most 2 entries: the current sprint and the immediately previous sprint
- **AND** older entries SHALL be removed
