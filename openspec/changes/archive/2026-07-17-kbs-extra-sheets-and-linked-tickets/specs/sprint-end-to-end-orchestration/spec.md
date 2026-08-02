## ADDED Requirements

### Requirement: Single command runs the sprint pipeline end to end

The system SHALL provide a single `kbs sync` invocation that runs the full sprint
pipeline in order: resolve the spreadsheet, extract required sheets, extract the
ticket scope, optionally expand linked tickets, build the scope JQL, resolve the
reporting filter, create or update the board surface and/or sprint per board
mode, and refresh the sprint report and person capacity. Each stage SHALL
consume the output of the prior stage.

#### Scenario: Pipeline runs in order from a single command

- **WHEN** `kbs sync` runs
- **THEN** the system SHALL resolve the spreadsheet, extract sheets, extract the
  ticket scope, expand linked tickets (when enabled), build the JQL, resolve the
  filter, apply the board/sprint per board mode, and refresh the reports (when
  enabled) in that order

#### Scenario: A required stage failure stops the pipeline

- **WHEN** a required stage fails (spreadsheet resolution, sheet extraction with
  no usable scope, JQL build, or filter resolution/update)
- **THEN** the system SHALL stop and report the failure with a non-zero exit code
- **AND** it SHALL NOT run the subsequent stages

#### Scenario: A non-required stage failure is reported and does not abort later safe stages

- **WHEN** a non-required stage fails (per-tab read error, board count
  verification mismatch, or report refresh)
- **THEN** the system SHALL record the failure in `SyncResult.errors`
- **AND** it SHALL continue with later stages that do not depend on the failed
  stage's output
- **AND** the final `SyncResult` SHALL report overall success only when no
  required stage failed

### Requirement: Stage classification is explicit

The system SHALL classify each pipeline stage as required (fail-stop) or
non-required (fail-soft) so failure handling is deterministic. Required stages
are: spreadsheet resolution, ticket-scope extraction yielding a usable key set,
JQL build, and reporting-filter resolution/update. Non-required stages are:
individual extra-tab reads, linked-ticket expansion, board count verification,
and report/capacity refresh.

#### Scenario: Linked-ticket expansion failure does not stop the pipeline

- **WHEN** linked-ticket expansion is enabled and the link query fails
- **THEN** the system SHALL record the error in `SyncResult.errors`
- **AND** it SHALL proceed using the unexpanded key set
- **AND** the filter/board stages SHALL still run

#### Scenario: Filter resolution failure stops the pipeline

- **WHEN** the reporting filter cannot be resolved or updated
- **THEN** the system SHALL stop with a non-zero exit code
- **AND** it SHALL NOT create or update any board or sprint and SHALL NOT refresh
  reports

### Requirement: Spreadsheet is resolved from config or an explicit link

The system SHALL resolve the target spreadsheet from configuration or from a
spreadsheet id/URL provided on the command line, accepting a full Google Sheets
URL or a bare id.

#### Scenario: Spreadsheet provided as a URL

- **WHEN** a Google Sheets URL is supplied
- **THEN** the system SHALL extract the spreadsheet id and proceed

#### Scenario: Spreadsheet resolved from config

- **WHEN** no spreadsheet is supplied on the command line
- **THEN** the system SHALL use the configured spreadsheet id

#### Scenario: No spreadsheet available

- **WHEN** no spreadsheet is supplied on the command line and none is configured
- **THEN** the system SHALL stop before any stage with a clear error naming the
  `SPREADSHEET_ID` setting and the `--spreadsheet` option
- **AND** it SHALL NOT query Jira or Google Sheets

### Requirement: Configuration defaults load from the environment with CLI overrides

The system SHALL load pipeline configuration (board mode, linked-ticket
expansion, report refresh, and the spreadsheet) from `~/.tdt/.env` (or a `--config`
YAML when provided) as defaults, and SHALL allow each to be overridden by an
explicit command-line option. Precedence SHALL be, from lowest to highest: model
defaults, then `~/.tdt/.env` / YAML, then explicit CLI options. An unset CLI
option SHALL NOT override the configured value. CLI overrides SHALL be validated
with the same rules as configured values.

#### Scenario: Configured default applies when no CLI override is given

- **WHEN** `BOARD_MODE` (or the equivalent config field) is set and no
  `--board-mode` option is passed
- **THEN** the system SHALL use the configured value

#### Scenario: CLI option overrides the configured default

- **WHEN** a config value is set and the equivalent CLI option is passed with a
  different value
- **THEN** the system SHALL use the CLI option value for that run
- **AND** it SHALL NOT mutate the persisted configuration

#### Scenario: Unset CLI option falls through to configuration

- **WHEN** a CLI option is not passed
- **THEN** the system SHALL fall through to the configured (or default) value
  rather than overriding it with an empty value

#### Scenario: Invalid CLI override is rejected

- **WHEN** a CLI override supplies an invalid value (e.g. an unknown board mode)
- **THEN** the system SHALL reject it with a validation error rather than
  silently degrading

### Requirement: Report and capacity refresh consumes the resolved scope

When report refresh is enabled, the system SHALL refresh the sprint report and
person capacity using the same resolved issue-key scope produced by this pipeline
(the resolved reporting filter and its expanded issue-key set), so the reports
reflect the sheet-merged and linked-ticket-expanded scope rather than a
separately recomputed bucket-only scope.

#### Scenario: Reports use the resolved key scope, not a re-read bucket scope

- **WHEN** report refresh runs after a live sync
- **THEN** the system SHALL drive the sprint report and person capacity from the
  resolved issue-key set used in this run
- **AND** the report write path SHALL NOT discard the pipeline-resolved keys by
  re-reading bucket tabs from the spreadsheet

#### Scenario: Expanded scope is reflected in reports

- **WHEN** linked-ticket expansion or extra sheets added keys to the scope
- **THEN** the refreshed reports SHALL include those keys
- **AND** they SHALL NOT silently fall back to a narrower bucket-only scope

#### Scenario: Report-side link expansion does not narrow or contradict the resolved scope

- **WHEN** the report path performs its own issue-graph expansion
- **THEN** the resolved pipeline key set SHALL be the seed for that expansion
- **AND** the report SHALL NOT exclude any key present in the resolved scope

### Requirement: Report scope handoff is explicit, not implicit

The system SHALL pass the resolved issue-key scope to the report refresh through
an explicit handoff (resolved keys and resolved filter id), and the report write
path SHALL honor a caller-provided key set when one is given instead of
re-deriving scope from bucket tabs. When no caller scope is provided, existing
bucket-derived behavior SHALL be preserved.

#### Scenario: Orchestration provides the resolved key set

- **WHEN** `kbs sync` invokes the report refresh with a resolved key set
- **THEN** the report SHALL build its issue query from that key set
- **AND** the resolved filter id SHALL be supplied so any filter-based fallback
  matches the same scope

#### Scenario: Standalone report run preserves bucket behavior

- **WHEN** the report refresh runs without a caller-provided key set
- **THEN** the system SHALL derive scope from the bucket tabs exactly as before

### Requirement: Person capacity worklogs use the workbook title sprint window

The system SHALL derive the person capacity worklog window from the workbook
title's sprint date range when available, so worklogs are counted only from the
sprint start date through the sprint end date. The report SHALL prefer the
workbook-title dates over board sprint metadata, and SHALL only fall back to the
board sprint dates when the title cannot be parsed.

#### Scenario: Workbook title dates bound the person capacity window

- **WHEN** the workbook title is `Sprint 16 - (08 Jun - 19 Jun)`
- **AND** the board sprint metadata exposes a different date range
- **THEN** the person capacity worklog window SHALL be `2026-06-08` through
  `2026-06-19` when year inference resolves the title to 2026
- **AND** worklogs outside that title-derived window SHALL be excluded from
  person capacity totals

### Requirement: Person capacity only counts mapped members with EMAIL/Teams ID

The system SHALL treat mapping rows with a populated `EMAIL/Teams ID` as the
eligible roster for Person Capacity. Those members MAY have zero planned or
actual effort in a given run, but rows without `EMAIL/Teams ID` SHALL NOT be
counted as roster members for effort rollup and SHALL be reported only in the
reconciliation section.

#### Scenario: Unmapped roster rows are excluded from effort rollup

- **WHEN** the mapping sheet contains a `MEMBERS` row with an empty `EMAIL/Teams ID`
- **THEN** the person capacity roster SHALL not count that row toward planned effort
- **AND** the row SHALL appear only in reconciliation as a missing identity
- **AND** members with populated `EMAIL/Teams ID` SHALL still render even when
  their planned or actual effort is zero

### Requirement: Person capacity ticket details render as plain text

The system SHALL render the aggregated person-capacity ticket detail cells as
plain text ticket keys, not hyperlink formulas. The `Worked Ticket Links` cell
SHALL list ticket keys one per line, the `Daily Ticket Details` cell SHALL
render daily ticket keys as readable plain text grouped by date, and the daily
date columns SHALL show the plain-text ticket keys and durations for that day.

#### Scenario: Aggregate ticket cells use plain text keys

- **WHEN** the person capacity report includes worked tickets for a member
- **THEN** the `Worked Ticket Links` cell SHALL contain plain text issue keys
- **AND** the `Daily Ticket Details` cell SHALL contain plain text issue keys by
  day
- **AND** each daily date column SHALL contain plain text issue keys with their
  logged duration for that day
- **AND** neither cell SHALL depend on multiple hyperlink formulas in one cell

### Requirement: Sprint report and person capacity apply readable sheet formatting

The system SHALL apply a readable presentation pass after writing the sprint
report and person capacity sheets. The report surface SHALL use sheet-specific
column widths that fit the common headers and daily detail columns, and SHALL
enable wrap text with top alignment so long ticket names and worklog entries
flow onto new lines instead of overflowing neighboring columns.

#### Scenario: Long content wraps instead of overflowing

- **WHEN** a report cell contains a long ticket name or daily worklog detail
- **THEN** the system SHALL keep the cell readable by wrapping text onto new
  lines
- **AND** the surrounding column widths SHALL remain tuned for the report layout

### Requirement: Report and capacity refresh is opt-in and live-gated

The system SHALL only refresh the sprint report and person capacity when
explicitly enabled, and SHALL perform the refresh writes only on a live run.
Dry-run SHALL report the intended refresh without writing.

#### Scenario: Refresh disabled by default

- **WHEN** report refresh is not enabled
- **THEN** the system SHALL complete the filter/board/sprint stages
- **AND** it SHALL NOT refresh the sprint report or person capacity

#### Scenario: Dry-run reports intended refresh

- **WHEN** report refresh is enabled and the run is dry-run
- **THEN** the system SHALL report that it would refresh the reports for the
  resolved scope
- **AND** it SHALL NOT write the sprint report or person capacity

#### Scenario: Live run refreshes reports

- **WHEN** report refresh is enabled and the run is live
- **THEN** the system SHALL refresh the sprint report and person capacity for the
  resolved sprint scope on the resolved spreadsheet
