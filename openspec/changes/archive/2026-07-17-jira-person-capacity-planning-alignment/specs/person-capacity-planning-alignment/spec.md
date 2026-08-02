## ADDED Requirements

### Requirement: Reuse common spreadsheet primitives
The system SHALL avoid creating person-capacity-specific duplicates of spreadsheet and issue-key utilities that already exist elsewhere in the workspace.

#### Scenario: Spreadsheet values are read
- **WHEN** the implementation needs to read Google Sheets values or metadata
- **THEN** it SHALL reuse an existing shared Sheets runner/reader abstraction when available
- **AND** if no shared abstraction exists, it SHALL isolate the new reader behind a small reusable interface rather than embedding one-off transport-specific Sheets API calls in planning logic

#### Scenario: Headers are matched
- **WHEN** the implementation needs to locate columns such as `MEMBERS`, `EMAIL/Teams ID`, `JIRA ID`, `ASSIGNED TO`, or `ORIGINAL ESTIMATE (hour)`
- **THEN** it SHALL use a shared header-normalization and alias-matching helper
- **AND** person-capacity-specific code SHALL provide aliases, not reimplement normalization mechanics

#### Scenario: Issue keys are extracted
- **WHEN** the implementation needs to parse Jira issue keys from sheet cells
- **THEN** it SHALL use one common issue-key extraction helper for bucket tabs, planning tabs, and reconciliation

#### Scenario: Shared utility ownership is chosen
- **WHEN** a needed helper already exists in `jira-kanban-from-spreadsheet`
- **THEN** the implementation SHALL either extract the stable helper to shared workspace code or document why local reuse is safer for this change
- **AND** it SHALL NOT introduce a direct runtime dependency from `jira-daily-reports` to the `kbs` application package

### Requirement: Use workbook member mapping as planning identity
The system SHALL read the workbook member mapping sheets and use the `MEMBERS` to `EMAIL/Teams ID` mapping as the identity bridge between planning rows and Jira people.

#### Scenario: Dedicated mapping sheet is present
- **WHEN** a writable dedicated mapping sheet is configured (default: `Person Capacity Mapping`)
- **THEN** the system SHALL prefer that sheet as the primary mapping source
- **AND** it SHALL merge the protected `Dropdown Keys - Do Not Delete -` sheet in as a fallback source to backfill missing member rows and empty identity cells
- **AND** primary-sheet values SHALL win when both sheets provide the same member key

#### Scenario: Member mapping is loaded
- **WHEN** `sprint-sheet` reads planning data from the sprint spreadsheet
- **THEN** the system SHALL build a mapping from workbook `member_key` values to Jira display names
- **AND** it SHALL build a normalized reverse mapping from Jira display names to workbook `member_key` values
- **AND** it MAY build a reverse mapping from Jira `accountId` to workbook `member_key` when a `Jira Account ID` column is provided

#### Scenario: Mapping row lacks email / Teams identifier
- **WHEN** a workbook member has no `EMAIL/Teams ID` value
- **THEN** the system SHALL exclude that member from planning-aligned person rows
- **AND** it SHALL report that the member cannot be merged with Jira people until the identifier is filled

### Requirement: Crawl current sprint team activity tabs
The system SHALL read current-sprint team activity tabs at detail-row level to compute planned capacity by workbook member.

#### Scenario: Current sprint tabs are read
- **WHEN** `sprint-sheet` runs with planning alignment enabled
- **THEN** the system SHALL read `Kelvin's Team Activites New`, `Andrew's Team Activites New`, and `VuVuong's Team Activites New` from the same spreadsheet
- **AND** it SHALL detect the sprint title, required headers, issue keys, assigned member keys, original estimate hours, and daily effort columns

#### Scenario: Required headers are absent
- **WHEN** a team activity tab does not contain required headers such as `JIRA ID`, `ASSIGNED TO`, or `ORIGINAL ESTIMATE (hour)`
- **THEN** the system SHALL mark that tab as unavailable for planning aggregation
- **AND** it SHALL include an actionable reconciliation warning naming the tab and missing headers

### Requirement: Reuse existing bucket scope for person-capacity fill
The system SHALL reuse the existing bucket-sheet sprint-ticket extraction flow as the authoritative seed ticket set for `Person Capacity` Jira issue scope and planning fill.

#### Scenario: Jira fetch expands seed scope one hop only
- **WHEN** `sprint-sheet` prepares the Jira issue query for a run
- **THEN** it SHALL load the original bucket seed issues from the 3 bucket sheets
- **AND** it SHALL include only directly related blocker/split tickets discovered from those seed issues
- **AND** it SHALL include `Blocks` link type in both directions (inward and outward)
- **AND** it SHALL include `Work item split` link type in both directions by default
- **AND** it SHALL include additional split-style linked issues when `PERSON_CAPACITY_SPLIT_LINK_TYPES` env var is set (comma-separated list)
- **AND** it SHALL NOT recursively traverse parents, subtasks, or multi-hop link chains
- **AND** it SHALL dedupe repeated keys and guard against self-links
- **AND** it SHALL keep the original bucket seed scope as the reconciliation baseline for planned-capacity filtering

#### Scenario: Link expansion is bounded
- **WHEN** Jira traversal encounters a link type other than a configured sprint-relevant split/blocking link
- **THEN** the system SHALL ignore that link for fetch expansion
- **AND** it SHALL record the skipped link type in reconciliation diagnostics when available

#### Scenario: Jira sprint scope is needed
- **WHEN** `sprint-sheet` needs to query Jira issues for sprint reporting
- **THEN** the system SHALL use the existing bucket issue keys extracted from the bucket tabs
- **AND** it SHALL keep the existing fallback to `filter = $JIRA_FILTER_ID` when bucket keys are unavailable

#### Scenario: Shared scope is created
- **WHEN** sheet-mode `sprint-sheet` reads bucket tabs
- **THEN** the system SHALL create one shared sprint-ticket scope containing the extracted issue keys and target statuses
- **AND** the same scope SHALL be used by both `Sprint Report` and `Person Capacity` generation in that run

#### Scenario: Planning parser needs ticket scope
- **WHEN** the planning parser filters current-sprint activity rows
- **THEN** it SHALL receive the shared sprint-ticket scope as input
- **AND** it SHALL NOT independently read bucket tabs or implement separate ticket extraction rules

#### Scenario: Planning row matches bucket scope
- **WHEN** a parsed planning detail row has an issue key that exists in the extracted bucket issue set
- **THEN** the system SHALL allow that row to contribute to `Person Capacity` planned metrics

#### Scenario: Bucket issue has no planning rows
- **WHEN** an issue key exists in bucket scope but has no matching parsed planning detail rows
- **THEN** the system SHALL still include that issue in Jira ownership and activity metrics
- **AND** it SHALL report the missing planned rows as bucket-only reconciliation data

#### Scenario: Planning tabs contain additional issue keys
- **WHEN** parsed team activity tabs contain issue keys that are not present in bucket scope
- **THEN** the system SHALL report those keys as planning-only reconciliation items
- **AND** it SHALL NOT add those keys to the Jira sprint query solely because they appear in planning tabs
- **AND** it SHALL NOT include those rows in `Person Capacity` planned totals

#### Scenario: Bucket tabs contain issue keys missing from planning tabs
- **WHEN** bucket scope contains issue keys that are not present in parsed team activity tabs
- **THEN** the system SHALL keep those keys in the Jira sprint query
- **AND** it SHALL report those keys as bucket-only reconciliation items

### Requirement: Parse planning detail rows instead of summary formulas
The system SHALL compute planned capacity from team activity detail rows and SHALL NOT use summary formulas or `SUMIFS` blocks as authoritative source data.

#### Scenario: Summary formulas are present
- **WHEN** a team activity tab contains `TOTAL`, summary, or formula rows
- **THEN** the system SHALL exclude those rows from planned-capacity aggregation
- **AND** it MAY use their evaluated values only as diagnostic evidence for reconciliation

#### Scenario: Formula drift is detected
- **WHEN** a summary formula result disagrees with parsed detail-row totals or contains spreadsheet errors such as `#REF!`
- **THEN** the system SHALL report formula drift in the reconciliation section
- **AND** it SHALL keep using parsed detail rows for planned-capacity totals

### Requirement: Resolve planning row ownership by hierarchy
The system SHALL assign each planned effort row to an effective workbook member using a deterministic hierarchy.

#### Scenario: Row has explicit member
- **WHEN** a planning detail row has an `ASSIGNED TO` member key
- **THEN** the system SHALL attribute that row's planned effort to that member key

#### Scenario: Row inherits group member
- **WHEN** a planning detail row has no `ASSIGNED TO` member key but is under a non-effort group row with an assigned member
- **THEN** the system SHALL attribute that row's planned effort to the group member key

#### Scenario: Row inherits issue member
- **WHEN** a planning detail row has no row member and no group member but the current issue row has an assigned member
- **THEN** the system SHALL attribute that row's planned effort to the issue member key

#### Scenario: Row remains unresolved
- **WHEN** a planning detail row has planned effort but no effective member can be resolved
- **THEN** the system SHALL exclude that effort from named-member planned totals
- **AND** it SHALL include the row in an unresolved planning bucket with tab name, row number, issue key, and planned hours

#### Scenario: Planning-aligned row order is preserved
- **WHEN** planning data is available and multiple mapping rows have `EMAIL/Teams ID` values
- **THEN** the planning-aligned `Person Capacity` rows SHALL preserve the source sheet order from the mapping table
- **AND** the implementation SHALL NOT re-sort those planning-backed rows by Jira activity totals

#### Scenario: Planned rows are aggregated
- **WHEN** multiple planning rows resolve to the same member key
- **THEN** the system SHALL sum their `ORIGINAL ESTIMATE (hour)` values into that member's `Planned Estimate`
- **AND** it SHALL count planned task rows and distinct planned issue keys for that member

#### Scenario: Daily planned cells are filled
- **WHEN** planning rows contain numeric daily effort values under date columns
- **THEN** the system SHALL aggregate those values by member key and date
- **AND** it SHALL keep planned daily effort separate from Jira logged daily effort

### Requirement: Reconcile bucket scope with planning scope
The system SHALL compare sprint bucket issue keys with current-sprint planning issue keys and report mismatches.

#### Scenario: Bucket issue is absent from planning tabs
- **WHEN** an issue key appears in bucket scope but not in parsed team activity tabs
- **THEN** the system SHALL report it as a bucket-only issue in reconciliation output

#### Scenario: Planning issue is absent from bucket scope
- **WHEN** an issue key appears in parsed team activity tabs but not in bucket scope
- **THEN** the system SHALL report it as a planning-only issue in reconciliation output

### Requirement: Prefer dedicated hyperlink fields over mixed inline formulas
The system SHALL define clickable Jira navigation in dedicated hyperlink-oriented cells rather than depending on mixed prose cells with multiple inline formula fragments.

#### Scenario: Person row needs clickable Jira navigation
- **WHEN** a `Person Capacity` row needs to expose clickable Jira ticket navigation
- **THEN** the implementation SHALL use `Worked Ticket Links` as the primary hyperlink surface
- **AND** it SHALL keep `Daily Ticket Details` focused on human-readable per-day diagnostics

#### Scenario: Future detailed navigation is required
- **WHEN** stakeholders require direct clickability for every per-day ticket reference
- **THEN** the implementation SHALL add a normalized detail section or table shape to carry one hyperlink cell per ticket reference
- **AND** it SHALL NOT satisfy that requirement by treating mixed inline formula fragments inside prose cells as the primary supported contract
