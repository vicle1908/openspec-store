## ADDED Requirements

### Requirement: Optional Epic Plan configuration
The system SHALL load optional Epic Plan settings from `[epic_plan]` in `~/.tdt/epic-report-config.toml`, including `enabled`, `sheet_name`, tab-relative bounded `snapshot_range` (default `A1:ZZ500`), and explicit mappings keyed by Jira epic key. Existing configurations without `[epic_plan]` MUST remain valid and MUST retain Jira-only report behavior.

#### Scenario: Epic Plan configuration is absent
- **WHEN** the TOML file contains no `[epic_plan]` section
- **THEN** plan extraction is disabled without a configuration error
- **AND** existing manual and scheduled Jira report behavior remains unchanged

#### Scenario: Explicit mapping is loaded
- **WHEN** `[epic_plan.epics."RMD-4160"]` sets `activity = "DLC Visibility"`
- **THEN** the configuration maps normalized Jira key `RMD-4160` to that exact plan activity

#### Scenario: Optional release disambiguator is loaded
- **WHEN** an epic mapping also sets `release_version = "3.3.56"`
- **THEN** the matcher uses that exact release version to disambiguate duplicate exact activity names

#### Scenario: Snapshot range is invalid
- **WHEN** `snapshot_range` is unbounded, malformed, or names a tab other than configured `sheet_name`
- **THEN** configuration validation fails with an actionable error before any Sheets request

### Requirement: Authenticated read-only plan access
The system SHALL read the configured plan tab from the same dedicated epic-report workbook identified by the resolved existing `[output].spreadsheet_url` configuration. Scheduled environment overrides MUST continue to resolve through `AppConfig` before plan access. The plan reader MUST use the public `tdt-sheets` `SheetsClient` API and existing service-account path; it MUST NOT access private backend members, construct a second raw Google client, log credentials, or write to the plan tab.

#### Scenario: Authorized plan read succeeds
- **WHEN** Epic Plan enrichment is enabled and the configured service account can read the workbook
- **THEN** the system reads the plan values and required spreadsheet metadata through the existing authenticated client path

#### Scenario: Plan access is denied
- **WHEN** the service account cannot read the workbook or plan tab
- **THEN** the system marks plan data unavailable with an authentication or authorization diagnostic
- **AND** it does not expose credential values
- **AND** it allows Jira-only report generation to continue

#### Scenario: Report run is read-only for plan source
- **WHEN** plan-aware report generation completes
- **THEN** no Sheets write, clear, format, rename, or delete request targets the configured plan tab

### Requirement: Coherent plan snapshot and structural discovery
The system SHALL read one coherent, bounded plan snapshot per report run through the public `tdt-sheets` grid-snapshot operation. The snapshot MUST include selected cells' effective and formatted values with coordinates, selected sheet identity and bounds, merge ranges, spreadsheet locale, and spreadsheet timezone without exposing the raw Google response. The parser SHALL discover required structural anchors from normalized headers and merge metadata rather than depending only on fixed coordinates. Required concepts MUST include release version, activity number, major activity, team/phase, resources, person-days, Start, End, the date axis, and sprint header ranges.

#### Scenario: Current Epic Plan shape is parsed
- **WHEN** the tab contains merged sprint labels above a daily calendar, merged release groups, numbered major activities, and child phase rows
- **THEN** the system builds one snapshot containing sprint ranges, release groups, activities, phases, release gates, and source references

#### Scenario: Required header is missing
- **WHEN** a required structural header cannot be resolved by normalized exact alias matching
- **THEN** the snapshot is marked unavailable for semantic extraction
- **AND** a diagnostic identifies the missing concept and source tab
- **AND** the parser does not guess a fixed replacement column

#### Scenario: Multiple configured epics share a run
- **WHEN** one report run contains multiple mapped Jira epics
- **THEN** the bounded plan grid and metadata are read once and reused for all mappings in that run

#### Scenario: Snapshot backend is unsupported
- **WHEN** grid snapshot access is requested through a backend that cannot return the complete typed contract
- **THEN** the client fails explicitly with a backend-unavailable or not-implemented error
- **AND** it does not return partial data as a valid snapshot
- **AND** epic reporting translates the failure to `SOURCE_UNAVAILABLE`

#### Scenario: Snapshot may be truncated by configured bound
- **WHEN** a non-empty selected cell touches the final row or column of `snapshot_range`
- **THEN** extraction emits `SNAPSHOT_BOUNDARY_REACHED` with the configured range
- **AND** operators can expand the bound without changing code

### Requirement: Formatting and summaries are non-authoritative
The system MUST derive plan semantics from cell values, merge hierarchy, headers, and validated dates. It MUST NOT derive business events from background colors, borders, formulas, notes, summary totals, hidden fields, or visual proximity alone.

#### Scenario: Weekend cells have colored backgrounds
- **WHEN** calendar cells use blue background formatting for weekends
- **THEN** the parser does not interpret those cells as milestones or deployments

#### Scenario: Highlighted date header is present
- **WHEN** a date header has a distinct fill color
- **THEN** the parser does not treat the color as release or API deployment semantics

#### Scenario: Formula or summary disagrees with detail rows
- **WHEN** a formula, total, or summary value conflicts with validated detail-row values
- **THEN** detail-row values remain authoritative
- **AND** the conflict MAY be emitted as a diagnostic but does not replace extracted data

### Requirement: Exact configured epic-to-activity matching
The system SHALL match each configured Jira epic to a plan major activity using normalized whitespace and case-insensitive exact equality. It MUST NOT use substring, token, edit-distance, or semantic fuzzy matching. Matching outcomes MUST distinguish `MATCHED`, `UNMAPPED`, `NOT_FOUND`, and `AMBIGUOUS`.

#### Scenario: Exact activity match exists once
- **WHEN** `RMD-4160` maps to `DLC Visibility` and exactly one normalized major activity has that name
- **THEN** the matcher returns `MATCHED` with that activity and its containing release group

#### Scenario: Epic has no configured mapping
- **WHEN** a requested Jira epic has no `[epic_plan.epics.<key>]` entry
- **THEN** the matcher returns `UNMAPPED`
- **AND** it does not attempt fuzzy title matching

#### Scenario: Configured activity is absent
- **WHEN** the configured activity has no normalized exact match
- **THEN** the matcher returns `NOT_FOUND` with an actionable diagnostic

#### Scenario: Duplicate activity names are unresolved
- **WHEN** the configured activity matches multiple release groups and no release disambiguator is configured
- **THEN** the matcher returns `AMBIGUOUS`
- **AND** it does not choose the first row silently

#### Scenario: Release disambiguator resolves duplicate
- **WHEN** duplicate exact activities exist and one belongs to the configured exact `release_version`
- **THEN** the matcher returns only that activity as `MATCHED`

### Requirement: Planned development window extraction
For a matched major activity, the system SHALL identify exactly one APP development child row and extract valid Start and End dates as the planned development window. A non-empty normalized activity-number cell starts the next major activity, a non-empty Version cell starts the next release group, and child-row inheritance MUST stop at either boundary. It SHALL retain planned resources, person-days, and daily allocations as supporting plan evidence without treating them as Jira actual progress.

#### Scenario: APP development row is valid
- **WHEN** a matched activity has a child row with phase `APP`, Start `7-Jul`, End `30-Jul`, 4 resources, and 53 person-days
- **THEN** the development context contains the exact normalized start/end dates and those supporting values with source provenance

#### Scenario: APP row is absent
- **WHEN** a matched activity has no APP development child row
- **THEN** development is marked unspecified
- **AND** a missing-development diagnostic identifies the activity

#### Scenario: Multiple APP rows are present
- **WHEN** a matched activity contains more than one APP child row before the next activity or release boundary
- **THEN** the system does not choose or merge them silently
- **AND** development is marked invalid with source-located ambiguity diagnostics

#### Scenario: APP date interval is invalid
- **WHEN** the APP End precedes Start or either value is an invalid sentinel such as `0-Jan`
- **THEN** the system does not create a development window
- **AND** it emits an invalid-development-window diagnostic with source location

#### Scenario: Planned effort differs from Jira actuals
- **WHEN** planned person-days or daily allocations disagree with Jira task progress or logged work
- **THEN** the plan values remain separate supporting fields
- **AND** they do not alter Jira completion calculations

### Requirement: Development sprint overlap derivation
The system SHALL derive every planned development sprint by inclusive interval intersection between the APP development window and validated merged sprint-header date ranges. Each result MUST retain the full sprint range and the actual overlap range.

#### Scenario: Development spans two sprints
- **WHEN** development runs from 2026-07-07 through 2026-07-30, Sprint 18 runs from 2026-07-06 through 2026-07-17, and Sprint 19 runs from 2026-07-20 through 2026-07-31
- **THEN** the result includes Sprint 18 overlap 2026-07-07 through 2026-07-17
- **AND** it includes Sprint 19 overlap 2026-07-20 through 2026-07-30

#### Scenario: Development does not intersect a sprint
- **WHEN** a sprint range has no date intersection with the development window
- **THEN** that sprint is excluded from development sprint overlaps

#### Scenario: Sprint header range is malformed
- **WHEN** a merged sprint label lacks a valid start or end date on the calendar axis
- **THEN** that sprint is excluded
- **AND** a source-located sprint-range diagnostic is emitted

### Requirement: Target release extraction with date precision
The system SHALL extract target release version and date from the matched activity's containing release group. It MUST preserve date precision as `DAY`, `MONTH`, or `UNSPECIFIED`, use effective calendar values, formatted release labels, merge hierarchy, and spreadsheet timezone/calendar continuity, and MUST NOT fabricate missing day precision or use the runtime/report year as a fallback. A year MAY be assigned only when the containing release span or same-release dated phases/gates yield one unique chronological candidate; otherwise the date MUST remain unspecified with `RELEASE_YEAR_AMBIGUOUS`.

#### Scenario: Exact-day release target
- **WHEN** the containing release label is `3.3.56 (05-Sep)` and its year resolves from the sheet calendar to 2026
- **THEN** the target version is `3.3.56`, the target date is 2026-09-05, and precision is `DAY`

#### Scenario: Month-only release target
- **WHEN** the containing release label is `3.3.58 (Oct)`
- **THEN** the target version is `3.3.58`, precision is `MONTH`, and no specific day is fabricated

#### Scenario: Release is not ready
- **WHEN** the containing release label is `Not ready yet`
- **THEN** release date precision is `UNSPECIFIED`
- **AND** no target date is fabricated

#### Scenario: Calendar crosses year boundary
- **WHEN** formatted date labels cross from December to January
- **THEN** the parser uses ordered effective calendar values and validated same-release continuity to retain the correct year

#### Scenario: Release year is ambiguous
- **WHEN** the same target month has multiple possible years and containing-release evidence does not select exactly one candidate
- **THEN** precision is `UNSPECIFIED`
- **AND** no target date is fabricated
- **AND** a `RELEASE_YEAR_AMBIGUOUS` diagnostic identifies the release group

### Requirement: Explicit optional API deployment extraction
The system SHALL create an API deployment window only from an explicit child activity row whose normalized label matches an approved configured alias and whose own Start and End are valid. Absence of such a row is a valid optional state. The system MUST NOT infer API deployment from APP completion, QA, UAT, Beta, cut-off, or public release.

#### Scenario: Explicit API deployment row exists
- **WHEN** a matched activity has a child row labeled `API Deployment` with valid Start and End
- **THEN** the API deployment context contains that exact window and source row

#### Scenario: API deployment is absent
- **WHEN** the matched activity has no explicit API deployment child row
- **THEN** API deployment is absent without an error
- **AND** consumers can render `Not specified in Epic Plan`

#### Scenario: Explicit API row has invalid dates
- **WHEN** an API deployment child row exists but Start or End is missing or invalid
- **THEN** no API deployment window is created
- **AND** an invalid-api-deployment diagnostic identifies the row

#### Scenario: APP development ends before release
- **WHEN** APP development has an end date and no explicit API deployment row exists
- **THEN** the APP end is not copied or inferred as API deployment

### Requirement: Release gate extraction
The system SHALL extract release-level UAT and Beta windows from explicitly labeled release-gate activities and their dated child rows. These windows SHALL remain release context and MUST NOT be represented as epic development or API deployment.

#### Scenario: UAT and Beta gates are present
- **WHEN** release 3.3.56 has UAT QA work from 2026-08-20 through 2026-08-26 and Beta QA work from 2026-08-27 through 2026-09-02
- **THEN** both windows are attached to the release context with their distinct gate types and provenance

#### Scenario: Gate parent row delegates dates to child
- **WHEN** a labeled UAT or Beta parent row has no dates but its following QA child row has valid Start and End
- **THEN** the gate uses the child row's dates and retains both source references

#### Scenario: Gate is absent
- **WHEN** the containing release group has no UAT or Beta activity
- **THEN** that gate remains unspecified without being inferred

### Requirement: Provenance and diagnostics
Every extracted or unavailable plan field SHALL carry enough provenance to identify its source tab and row/range. Diagnostics MUST use stable codes and severity and MUST include actionable location context without dumping the entire workbook.

#### Scenario: Field is extracted
- **WHEN** a development or release field is returned
- **THEN** its provenance identifies `Epic Plan` and the source row/range used

#### Scenario: Invalid value is encountered
- **WHEN** a source date, interval, mapping, or hierarchy is invalid
- **THEN** a diagnostic includes stable code, severity, source tab, row/range, safe raw value, and reason

#### Scenario: API row is simply absent
- **WHEN** no explicit API deployment row exists
- **THEN** the absence is represented as informational optional state rather than an error diagnostic

### Requirement: Preserve stakeholder-owned workbook tabs
The system SHALL distinguish explicitly managed `jira-epic-report` output tabs from protected or unmanaged workbook tabs. Sheet synchronization MUST add, replace, or delete only managed output tabs and MUST preserve `Epic Plan` and every unknown/unmanaged tab.

#### Scenario: Epic Plan exists during report refresh
- **WHEN** spreadsheet report generation synchronizes generated tabs
- **THEN** `Epic Plan` remains present with unchanged values, formatting, merges, and metadata

#### Scenario: Unknown stakeholder tab exists
- **WHEN** the workbook contains a tab not listed as a managed epic-report output
- **THEN** synchronization does not delete or rewrite that tab

#### Scenario: Obsolete static managed output exists
- **WHEN** an obsolete tab title is positively identified in the reporter's static managed-output allow-list
- **THEN** synchronization MAY remove that managed tab without affecting protected or unmanaged tabs

#### Scenario: Stale dynamic epic tab exists
- **WHEN** a prior run left a human-readable per-epic tab that is not a current target and has no durable ownership marker
- **THEN** synchronization preserves the tab
- **AND** it does not infer ownership from a Jira-key-like title pattern alone
