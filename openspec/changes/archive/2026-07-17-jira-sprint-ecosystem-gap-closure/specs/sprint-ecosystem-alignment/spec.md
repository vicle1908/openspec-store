## ADDED Requirements

### Requirement: Resolved sprint context is the integration contract
The sprint pipeline SHALL produce a single resolved sprint context that represents the active spreadsheet-derived sprint scope and SHALL pass that context to downstream report, board/sprint, and dashboard stages.

#### Scenario: Context includes all resolved sprint objects
- **WHEN** the pipeline resolves the active sprint spreadsheet
- **THEN** the resolved context SHALL include the spreadsheet id, workbook title, sprint number, sprint date range, issue keys, filter name, filter id, board name, board id when available, sprint id when available, dashboard id when available, and project key
- **AND** missing optional objects SHALL be represented as absent rather than fake ids

#### Scenario: Downstream stages consume the same context
- **WHEN** the report refresh, board/sprint stage, or dashboard stage runs after scope resolution
- **THEN** each stage SHALL consume the resolved context from the prior stage
- **AND** it SHALL NOT recompute a narrower issue scope when context issue keys are present

### Requirement: Dashboard behavior is explicit and shared-engine backed
The system SHALL make per-sprint dashboard behavior explicit. If a pipeline stage creates or rebuilds a dashboard, it SHALL use the shared `jira-skill.dashboard` layout engine and validation workflow. If a stage only creates a dashboard shell for linking, it SHALL report that behavior as link-only and provide the canonical build command.

#### Scenario: Pipeline builds a configured dashboard
- **WHEN** the sprint pipeline is configured to build a per-sprint dashboard on a live run
- **THEN** it SHALL use the shared `jira-skill.dashboard` layout engine with the resolved filter id
- **AND** it SHALL validate the dashboard gadget configuration by readback before reporting success

#### Scenario: Pipeline creates only a dashboard link target
- **WHEN** the sprint pipeline only find-or-creates a dashboard shell for report linking
- **THEN** it SHALL label the result as link-only
- **AND** it SHALL surface the `jira-skill dashboard create` or `jira-skill dashboard rebuild` command needed to populate the dashboard

#### Scenario: Dry-run does not mutate dashboard state
- **WHEN** dashboard handling runs in dry-run mode
- **THEN** it SHALL report the dashboard name, resolved filter id, selected layout or link-only mode, and planned actions
- **AND** it SHALL NOT create, rebuild, or delete dashboard gadgets

### Requirement: Sprint report links reflect resolved context
The sprint report SHALL render links from the resolved context so the Google Sheet and markdown outputs point to the exact filter, board, sprint, and dashboard resolved during the same pipeline run.

#### Scenario: All resolved links are rendered consistently
- **WHEN** the resolved context contains filter id, board id, sprint id, dashboard id, and project key
- **THEN** the report SHALL render corresponding links in both Google Sheet and markdown outputs
- **AND** the links SHALL target the same resolved ids

#### Scenario: Optional links are omitted safely
- **WHEN** the resolved context omits an optional sprint id or dashboard id
- **THEN** the report SHALL omit only the unavailable link
- **AND** it SHALL still render all available links without failing the report refresh

### Requirement: Active docs and skills describe canonical ownership
Active documentation and agent skills SHALL describe the current sprint ecosystem ownership split and SHALL NOT instruct operators to manually maintain per-sprint filter or board ids as the primary source of truth.

#### Scenario: Agent asks for sprint report logic
- **WHEN** an agent or operator reads the sprint reporting guidance
- **THEN** the guidance SHALL identify `jira-daily-reports` as the active sprint report/person-capacity output path
- **AND** it SHALL identify spreadsheet-derived resolved context as the sprint scope input

#### Scenario: Agent asks for sprint dashboard creation
- **WHEN** an agent or operator reads dashboard guidance
- **THEN** the guidance SHALL identify `jira-skill.dashboard` as the canonical dashboard builder and validator
- **AND** it SHALL explain whether the KBS/report path builds a configured dashboard or only creates a link target

#### Scenario: Agent asks for board or sprint creation
- **WHEN** an agent or operator reads board/sprint guidance
- **THEN** the guidance SHALL identify the spreadsheet-derived filter as the source for board and sprint creation
- **AND** it SHALL describe dry-run/live gating for Jira mutations

### Requirement: Validation evidence covers dry-run, live readback, and cleanup
The change SHALL include validation evidence showing that the active sprint ecosystem resolves consistently and that any live probe objects are cleaned up.

#### Scenario: Dry-run validation proves planned actions
- **WHEN** validation runs in dry-run mode against an active sprint spreadsheet
- **THEN** the evidence SHALL show the planned issue scope, filter, board/sprint, dashboard mode, and report refresh without Jira mutation

#### Scenario: Live validation reads back resolved objects
- **WHEN** live validation is performed
- **THEN** the evidence SHALL include readback of the resolved Jira filter, board or sprint, dashboard behavior, and report output links
- **AND** it SHALL state whether objects were reused or created

#### Scenario: Temporary validation objects are cleaned up
- **WHEN** validation creates temporary Jira objects
- **THEN** the evidence SHALL list those object ids and confirm cleanup before the change is marked complete
