## ADDED Requirements

### Requirement: Merge planned capacity with Jira ownership and activity
The `Person Capacity` report SHALL merge workbook planned capacity, Jira ownership, and Jira actual activity into one person-centric output keyed by workbook member identity when available.

This requirement applies only to the `Person Capacity` worksheet/report. It SHALL NOT change the existing `Sprint Report` target-vs-actual worksheet semantics.

#### Scenario: Mapped Jira person joins workbook member
- **WHEN** a Jira assignee or worklog author display name matches a `JIRA Nick Name` from the mapping sheet
- **THEN** the system SHALL merge that Jira ownership or activity data into the corresponding workbook `member_key` row
- **AND** it SHALL preserve the Jira `accountId` as the durable Jira user identifier for that row

#### Scenario: Jira person is not mapped
- **WHEN** a Jira assignee or worklog author cannot be resolved to a workbook `member_key`
- **THEN** the system SHALL keep that Jira data in an explicit unmapped person row
- **AND** it SHALL use `accountId` when available to flavor the unmapped row key
- **AND** it SHALL report the missing mapping in reconciliation output

### Requirement: Preserve separate ledger semantics
The person capacity report SHALL keep planned capacity, Jira ownership, and Jira actual activity as separate visible concepts and SHALL NOT collapse them into one total.

#### Scenario: Person row is rendered
- **WHEN** a person capacity row is rendered
- **THEN** it SHALL show planned effort from workbook activity rows separately from Jira original estimate assigned to the person
- **AND** it SHALL show Jira logged work separately from both planned effort and Jira original estimate

#### Scenario: Planned ledger is scoped to sprint report tickets
- **WHEN** planned capacity is calculated from team activity tabs
- **THEN** only planning rows whose issue keys are present in the existing Sprint Report bucket issue set SHALL contribute to planned person totals
- **AND** planning rows outside that ticket set SHALL be reported only in reconciliation output

#### Scenario: Shared ticket scope is reused
- **WHEN** `Person Capacity` filters planned rows or merges Jira ownership/activity rows
- **THEN** it SHALL use the same extracted sprint-ticket scope that was used for `Sprint Report` in the same run
- **AND** it SHALL NOT perform a separate bucket read or maintain a second implementation of sprint ticket extraction

#### Scenario: Original estimate is computed
- **WHEN** Jira ownership totals are calculated
- **THEN** the system SHALL continue using only Jira original estimate fields (`timeoriginalestimate` or `timetracking.originalEstimateSeconds`)
- **AND** it SHALL NOT use story points or remaining estimate as capacity fallbacks

### Requirement: Render planning-aligned person rows
The `Person Capacity` worksheet SHALL include planning identity and planned-effort columns before Jira ownership and actual activity columns.

#### Scenario: Planning-aligned row layout is used
- **WHEN** planning data is available
- **THEN** each person row SHALL include `Member Key`, `Person`, `Jira Account ID`, `Role`, `Planned Issues`, `Planned Tasks`, `Planned Estimate`, `Assigned Tickets`, `Jira Original Estimate`, `Worked Tickets`, and `Logged Total`

#### Scenario: Planning data is unavailable
- **WHEN** mapping or planning tabs cannot be read
- **THEN** the report SHALL fall back to the existing Jira-only person-capacity rows
- **AND** it SHALL mark planned capacity as unavailable in the reconciliation section

### Requirement: Render Jira ticket hyperlinks in sheet-safe cells
The system SHALL render Jira ticket references as Google Sheets `HYPERLINK(...)` formulas only in cells whose primary contract is clickable navigation, and SHALL avoid making mixed prose/detail cells depend on multiple inline formula fragments.

#### Scenario: Sprint report issue cell is rendered
- **WHEN** the `Sprint Report` worksheet renders an issue key cell
- **THEN** the cell SHALL contain a pure Jira `HYPERLINK(...)` formula to the issue browse URL

#### Scenario: Person Capacity worked ticket links are rendered
- **WHEN** the `Person Capacity` worksheet renders `Worked Ticket Links`
- **THEN** the cell SHALL contain one Jira `HYPERLINK(...)` formula per listed ticket
- **AND** multiple tickets SHALL be separated by newlines without degrading each ticket into plain text labels
- **AND** this field SHALL be the canonical clickable multi-ticket navigation surface for the person row

#### Scenario: Daily ticket details are rendered
- **WHEN** the `Person Capacity` worksheet renders `Daily Ticket Details`
- **THEN** the cell SHALL prioritize readable per-day diagnostics
- **AND** it SHALL NOT require mixed inline text-plus-formula fragments as the only way to navigate Jira tickets for that row
- **AND** clickable per-ticket navigation for the row SHALL be satisfied by `Worked Ticket Links`
- **AND** implementations MAY include plain Jira keys in daily details for readability, but SHALL NOT make daily-details clickability a release requirement for this change

#### Scenario: Guaranteed per-day clickable detail is required in the future
- **WHEN** product requirements require every day-level ticket reference to be directly clickable
- **THEN** the system SHALL add a normalized secondary details section or table with one hyperlink cell per ticket reference
- **AND** it SHALL NOT rely on mixed prose cells with many inline `HYPERLINK(...)` fragments as the primary contract

### Requirement: Include person-capacity reconciliation output
The `Person Capacity` worksheet SHALL include a reconciliation section that makes source-data gaps visible.

#### Scenario: Reconciliation section is rendered
- **WHEN** the person capacity worksheet is written
- **THEN** the worksheet SHALL include counts and samples for unmapped Jira people, mapping rows without Jira nicknames, unresolved planning effort, bucket-only issues, planning-only issues, and formula drift

#### Scenario: Reconciliation has warnings
- **WHEN** any reconciliation warning exists
- **THEN** the CLI summary SHALL mention that `Person Capacity` was written with warnings
- **AND** the worksheet SHALL still be written with the available parsed data

### Requirement: Keep source workbook tabs read-only
The report SHALL only read mapping, bucket, and team activity tabs and SHALL NOT modify them during report generation.

#### Scenario: Report writes sheet output
- **WHEN** `sprint-sheet` writes generated output
- **THEN** it SHALL only clear and write generated report tabs such as `Sprint Report` and `Person Capacity`
- **AND** it SHALL NOT write to `Dropdown Keys - Do Not Delete -`, bucket tabs, team activity tabs, `Capacity of Resource`, or `RawData`
