## ADDED Requirements

### Requirement: Spreadsheet is the single source of truth for sprint scope
The system SHALL treat the sprint workbook as the single source of truth for the
active sprint. The only required per-sprint configuration SHALL be the
spreadsheet id or URL; the sprint number, sprint dates, issue scope (JQL),
reporting filter, and board SHALL be derivable from that workbook.

#### Scenario: Sprint number and dates come from the workbook title
- **WHEN** the system resolves the active sprint from a spreadsheet
- **THEN** it SHALL parse the sprint number and date range from the workbook
  title (e.g. `Sprint 16 - (08 Jun - 19 Jun)`)
- **AND** it SHALL use those values for filter/board naming and sprint labels

#### Scenario: Issue scope comes from the bucket tabs
- **WHEN** the system builds the sprint JQL
- **THEN** it SHALL derive the issue keys from the workbook bucket tabs
- **AND** it SHALL NOT require a hand-maintained list of issue keys

#### Scenario: Jira ids are optional overrides, not the source
- **WHEN** `JIRA_FILTER_ID` or `JIRA_BOARD_ID` is not configured
- **THEN** the system SHALL resolve the filter and board from the spreadsheet
- **AND** WHEN those ids are configured, the system SHALL treat them as a
  cache/override and SHALL NOT require manual edits each sprint

### Requirement: Resolve the reporting filter and board with find-or-create
The system SHALL resolve the per-sprint reporting filter and board by name
(`Sprint N (<dates>)` / `Sprint N Board`), creating them when they do not exist,
and SHALL return the resolved ids for downstream reporting.

#### Scenario: Filter already exists
- **WHEN** a Jira filter matching the sprint name already exists
- **THEN** the system SHALL reuse its id
- **AND** it SHALL update the filter JQL to the workbook-derived scope on a live run

#### Scenario: Filter does not exist
- **WHEN** no Jira filter matches the sprint name on a live run
- **THEN** the system SHALL create the filter with the workbook-derived JQL and
  sprint name
- **AND** it SHALL return the newly created filter id

#### Scenario: Board already exists
- **WHEN** a board matching the sprint name already exists
- **THEN** the system SHALL reuse its id and verify its issue count

#### Scenario: Board does not exist
- **WHEN** no board matches the sprint name on a live run
- **THEN** the system SHALL create a board backed by the resolved filter
- **AND** it SHALL return the newly created board id

### Requirement: Creation is gated behind live mode
The system SHALL only create or mutate Jira filters and boards when explicitly
running in live mode. Dry-run SHALL be the default and SHALL never write to Jira.

#### Scenario: Dry-run resolves without writing
- **WHEN** resolution runs in dry-run mode
- **THEN** the system SHALL report what it would create or update
- **AND** it SHALL NOT create or modify any Jira filter or board

#### Scenario: Live run performs the writes
- **WHEN** resolution runs in live mode
- **THEN** the system SHALL perform the find-or-create writes
- **AND** it SHALL log the resolved filter and board ids

### Requirement: Report content contract is unchanged
The SSOT resolution SHALL change only how sprint scope is resolved, not how
sprint or person-capacity rows are calculated or laid out.

#### Scenario: Reports consume resolved scope
- **WHEN** a sprint report or person-capacity refresh runs
- **THEN** it SHALL use the resolved filter/board/scope from the spreadsheet
- **AND** the report calculations, sheet layout, and reconciliation rules SHALL
  remain unchanged
