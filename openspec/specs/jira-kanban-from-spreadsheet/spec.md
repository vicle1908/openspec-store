# jira-kanban-from-spreadsheet Specification

## Purpose

Synchronize Jira Kanban/Scrum boards from a Google Sheets sprint workbook. Reads issue keys and metadata from spreadsheet bucket tabs, creates or updates Jira filters and boards, verifies board configuration, and provides backup/restore capabilities for sprint data.

## Requirements

### Requirement: Parse sprint rows from spreadsheet

The system SHALL read bucket tabs from a Google Sheets workbook and extract issue keys, priorities, target statuses, and labels. It SHALL detect headerless tabs (first cell matches a Jira issue key pattern) and parse them without requiring a formal header row.

#### Scenario: Standard bucket tab with headers
- **WHEN** a bucket tab has a header row with `ID`, `Priority`, and `Target Status` columns
- **THEN** the parser extracts issue keys from the `ID` column and metadata from sibling columns

#### Scenario: Headerless tab
- **WHEN** a bucket tab's first cell matches the Jira issue key pattern `[A-Z]+-\d+`
- **THEN** the parser treats column 0 as issue keys and skips metadata columns

### Requirement: Sync Jira filter from spreadsheet

The system SHALL create or update a Jira filter whose JQL matches the issue keys extracted from the spreadsheet. The filter SHALL be shared with authenticated users by default.

#### Scenario: Filter does not exist
- **WHEN** no filter with the configured name exists
- **THEN** the system creates a new filter with JQL `key in (KEY-1, KEY-2, ...)`

#### Scenario: Filter exists
- **WHEN** a filter with the configured name already exists
- **THEN** the system updates the filter's JQL to match the current spreadsheet contents

### Requirement: Create or verify Jira board

The system SHALL create a Kanban or Scrum board linked to the synced filter, or verify an existing board's configuration matches expectations.

#### Scenario: Board does not exist
- **WHEN** no board with the configured name exists
- **THEN** the system creates a new board of the configured type (kanban/sprint/both)

#### Scenario: Board exists
- **WHEN** a board with the configured name exists
- **THEN** the system verifies the board's filter association and reports any drift

### Requirement: Dry-run mode

The system SHALL support a `--dry-run` flag that shows what actions would be taken without executing any Jira writes.

#### Scenario: Dry-run with pending changes
- **WHEN** `--dry-run` is set and the spreadsheet has new issue keys
- **THEN** the system prints the intended JQL, filter name, and board configuration without creating or updating anything

### Requirement: Backup and restore

The system SHALL provide backup commands that export sprint data to local files and restore commands that re-import from backups.

#### Scenario: Backup sprint data
- **WHEN** the operator runs `kbs backup`
- **THEN** the system exports the current sprint spreadsheet contents to a local JSON file

#### Scenario: Restore from backup
- **WHEN** the operator runs `kbs restore --file <path>`
- **THEN** the system re-imports the backup data into the spreadsheet

### Requirement: Configuration via environment

The system SHALL load configuration from `~/.tdt/config.yaml` under the `[kbs]` section and from environment variables. Required configuration includes `SPREADSHEET_ID`, `JIRA_PROJECT_KEY`, and optionally `FILTER_ID`, `BOARD_ID`, `BOARD_NAME`.

#### Scenario: Missing required config
- **WHEN** `SPREADSHEET_ID` or `JIRA_PROJECT_KEY` is not set
- **THEN** the system fails with an actionable error message identifying the missing variable

### Requirement: Sprint scope resolution

The system SHALL resolve the sprint scope (filter, board, spreadsheet) from the spreadsheet title when explicit IDs are not provided. The spreadsheet title encodes the sprint number and date range (e.g., "Sprint 16 - (08 Jun - 19 Jun)").

#### Scenario: Spreadsheet title encodes sprint info
- **WHEN** the spreadsheet title matches the pattern `Sprint N - (DD Mon - DD Mon)`
- **THEN** the system extracts the sprint number and date range from the title

### Requirement: Board verification

The system SHALL verify that a Jira board's configuration matches the expected state: correct filter association, correct board type, and correct project scope.

#### Scenario: Board configuration matches
- **WHEN** the board's filter, type, and project match the expected values
- **THEN** verification passes with a success message

#### Scenario: Board configuration drifts
- **WHEN** the board's filter or type does not match expectations
- **THEN** verification reports the specific mismatches with remediation guidance

### Requirement: JQL construction

The system SHALL build JQL queries from issue keys using the `key in (...)` pattern for small key sets and cursor-based pagination for large key sets (150+ keys).

#### Scenario: Small key set
- **WHEN** the number of issue keys is under 150
- **THEN** the system builds a single `key in (KEY-1, KEY-2, ...)` JQL query

#### Scenario: Large key set
- **WHEN** the number of issue keys exceeds 150
- **THEN** the system chunks the keys and builds paginated JQL queries

### Requirement: Template scaffolding

The system SHALL support team templates that pre-configure board settings, custom fields, and workflow mappings for specific team types (mobile, backend, QA).

#### Scenario: List available templates
- **WHEN** the operator runs `kbs template list`
- **THEN** the system lists all available team templates with descriptions

#### Scenario: Scaffold from template
- **WHEN** the operator runs `kbs template scaffold --team <name>`
- **THEN** the system generates a configuration file pre-populated with the template's defaults
