## ADDED Requirements

### Requirement: Each sprint has its own dashboard created in the pipeline

The system SHALL find-or-create a per-sprint Jira dashboard backed by the
resolved reporting filter on a live run, named by a canonical per-sprint name
(e.g. `Sprint N Dashboard`). The dashboard SHALL be distinct per sprint so each
sprint has its own dashboard rather than sharing a single global dashboard.

#### Scenario: Dashboard created when missing on a live run

- **WHEN** the pipeline resolves the reporting filter on a live run and no
  dashboard with the canonical per-sprint name exists
- **THEN** the system SHALL create a dashboard backed by the resolved filter
- **AND** it SHALL use the canonical per-sprint dashboard name

#### Scenario: Dashboard reused when it already exists

- **WHEN** a dashboard with the canonical per-sprint name already exists
- **THEN** the system SHALL reuse its id and SHALL NOT create a duplicate

#### Scenario: Dry-run does not create the dashboard

- **WHEN** the pipeline runs in dry-run mode
- **THEN** the system SHALL report the dashboard it would create
- **AND** it SHALL NOT create or modify any dashboard

#### Scenario: Dashboard creation is non-required

- **WHEN** dashboard find-or-create fails
- **THEN** the system SHALL record the error and continue
- **AND** it SHALL still write the sprint report and person capacity

### Requirement: Resolved object ids are handed off to the report

The system SHALL hand off the resolved filter id, board id, sprint id, and board
project key to the report refresh through an explicit handoff so the report can
render links to the exact objects created or resolved in this run, rather than
re-deriving them. The dashboard is find-or-created within the report-refresh
stage itself, so its id need not be handed off.

#### Scenario: Handoff carries the resolved ids

- **WHEN** the pipeline triggers the report refresh after resolving the sprint
  objects
- **THEN** the handoff SHALL include the resolved filter id, board id, sprint id,
  and board project key when those objects were resolved

#### Scenario: Missing optional ids are omitted, not faked

- **WHEN** an object was not created or resolved (e.g. no sprint in kanban mode)
- **THEN** the handoff SHALL omit that id
- **AND** the report SHALL render only the links it has ids for

### Requirement: Sprint report header renders filter, board, sprint, and dashboard links

The sprint report header SHALL render hyperlinks to the resolved filter, board,
sprint, and dashboard when their ids are available. When an id is unavailable,
the report SHALL omit that link without error.

#### Scenario: All four links rendered when ids are present

- **WHEN** the report is built with filter, board, sprint, and dashboard ids
- **THEN** the header SHALL render a hyperlink for each: the filter
  (`/issues/?filter={id}`), the board
  (`/jira/software/c/projects/{project}/boards/{id}`), the sprint
  (the board URL scoped to `?sprint={id}`), and the dashboard
  (`/jira/dashboards/{id}`)

#### Scenario: Link omitted when its id is missing

- **WHEN** the report is built without a sprint id or dashboard id
- **THEN** the header SHALL render the available links
- **AND** it SHALL omit the missing link without raising an error

#### Scenario: Sheet and markdown headers stay consistent

- **WHEN** the report is rendered as a Google Sheet and as markdown
- **THEN** both header formats SHALL reflect the same set of available links
