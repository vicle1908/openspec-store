## ADDED Requirements

### Requirement: Board mode selects the board surface, sprint, or both

The system SHALL provide a configurable board mode that selects how the resolved
filter is surfaced: the existing board, an agile scrum sprint, or both. The mode
SHALL default to `kanban` so existing behavior is unchanged.

#### Scenario: Default mode keeps board behavior

- **WHEN** no board mode is configured
- **THEN** the system SHALL resolve the board exactly as before
- **AND** it SHALL NOT create or modify any agile sprint

#### Scenario: Sprint mode skips board creation

- **WHEN** board mode is set to `sprint`
- **THEN** the system SHALL run agile sprint creation after filter resolution
- **AND** it SHALL NOT require the board to exist

#### Scenario: Both mode resolves board and sprint

- **WHEN** board mode is set to `both`
- **THEN** the system SHALL resolve the board AND create the agile sprint

### Requirement: Agile sprint creation runs after filter resolution

When sprint mode is selected, the system SHALL find-or-create an agile scrum
sprint after the reporting filter is resolved. The sprint SHALL be hosted on a
scrum board backed by the resolved filter, found-or-created by canonical name.

#### Scenario: Scrum board does not exist

- **WHEN** sprint mode is selected on a live run and no scrum board backed by the
  resolved filter exists
- **THEN** the system SHALL create a scrum board backed by the resolved filter
- **AND** it SHALL use that board as the sprint origin board

#### Scenario: Scrum board already exists

- **WHEN** a scrum board matching the canonical sprint board name already exists
- **THEN** the system SHALL reuse its id as the sprint origin board

#### Scenario: Sprint already exists

- **WHEN** a sprint matching the canonical sprint name already exists on the board
- **THEN** the system SHALL reuse its id and SHALL NOT create a duplicate sprint

#### Scenario: Sprint does not exist

- **WHEN** no sprint matching the canonical sprint name exists on the board on a
  live run
- **THEN** the system SHALL create the sprint with the workbook-derived name and
  date range
- **AND** it SHALL return the newly created sprint id

#### Scenario: Scrum board name is distinct from the kanban board name

- **WHEN** the system find-or-creates the scrum board backing the sprint
- **THEN** it SHALL use a canonical name distinct from the kanban board name
  (e.g. `Sprint N Board (Scrum)`) so the two boards do not collide

#### Scenario: Created sprint starts in the future state

- **WHEN** the system creates a new sprint
- **THEN** the sprint SHALL be created in the `future` state
- **AND** the system SHALL NOT auto-start or auto-close the sprint

### Requirement: Sprint name and dates derive from the workbook

The system SHALL derive the sprint name and date range from the workbook title
(the same single source of truth used for filter/board naming). When the title
date range omits a year, the system SHALL infer the year so sprint start/end are
valid ISO datetimes.

#### Scenario: Sprint name matches the canonical sprint identity

- **WHEN** the system creates a sprint for `Sprint 16 - (08 Jun - 19 Jun)`
- **THEN** the sprint name SHALL reflect the workbook sprint number and dates

#### Scenario: Year inferred for date range without a year

- **WHEN** the workbook date range has no explicit year
- **THEN** the system SHALL infer the year for sprint start and end datetimes
- **AND** it SHALL roll to the next year only when the inferred range would place
  the sprint wholly in the past

#### Scenario: Title without a parseable date range

- **WHEN** the workbook title has no parseable date range
- **THEN** the system SHALL report the failure as a non-required (fail-soft) stage
- **AND** it SHALL NOT create a sprint with invalid or empty dates

### Requirement: Planned issues are moved into the sprint on live runs

When sprint mode is selected, the system SHALL move the planned (and expanded)
issue keys into the resolved sprint on a live run. Moving issues SHALL be gated
behind live mode.

#### Scenario: Live run populates the sprint

- **WHEN** sprint creation runs in live mode
- **THEN** the system SHALL move the planned issue keys into the sprint

#### Scenario: Dry-run reports without writing

- **WHEN** sprint creation runs in dry-run mode
- **THEN** the system SHALL report the sprint it would create and the issues it
  would move
- **AND** it SHALL NOT create the sprint, create the board, or move any issue

#### Scenario: Dry-run reports intended actions when no board or sprint exists yet

- **WHEN** sprint creation runs in dry-run mode and no scrum board or sprint
  exists
- **THEN** the system SHALL report the scrum board and sprint it would create by
  their canonical names
- **AND** it SHALL report the count of issues it would move without requiring a
  resolved sprint id

#### Scenario: Move is chunked within the agile API limit

- **WHEN** the resolved key set exceeds the agile move-to-sprint per-call limit
- **THEN** the system SHALL move issues in chunks within the limit (≤50 keys per
  call)
- **AND** it SHALL move the full resolved key set across the chunks

### Requirement: Sprint creation reuses the resolved scope

The system SHALL build the sprint from the same resolved issue-key scope used for
the filter and board, including any sheet-merged and linked-ticket expanded keys.

#### Scenario: Sprint scope equals filter scope

- **WHEN** the system creates and populates a sprint
- **THEN** the moved issue keys SHALL be the same resolved key set used to update
  the reporting filter
