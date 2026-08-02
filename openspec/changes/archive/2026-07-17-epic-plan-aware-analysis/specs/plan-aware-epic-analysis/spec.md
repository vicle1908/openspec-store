## ADDED Requirements

### Requirement: Combine plan context with Jira actuals without changing source ownership
When Epic Plan enrichment is enabled, the system SHALL produce exactly one `PlanAwareEpicAnalysis` for every requested Jira Epic snapshot. A successful mapping includes `EpicPlanContext`; unavailable or unmatched conditions use explicit result states rather than `None`. Jira MUST remain authoritative for current status, tasks, blockers, assignments, and progress, while Epic Plan MUST remain authoritative for planned development, release, deployment, and release-gate values.

#### Scenario: Both sources are available
- **WHEN** Jira collection succeeds and a plan mapping is `MATCHED`
- **THEN** the result contains Jira actuals and plan targets in separate typed fields
- **AND** each displayed value identifies its source

#### Scenario: Planned effort conflicts with Jira progress
- **WHEN** Epic Plan person-days or daily allocations do not align with Jira task completion
- **THEN** the system reports the values as different measures
- **AND** it does not use planned effort to overwrite Jira progress

#### Scenario: Jira collection succeeds but plan is unavailable
- **WHEN** Jira data is available and plan read, parse, or mapping fails
- **THEN** the existing Jira analysis still completes
- **AND** each requested epic receives exactly one plan-aware result identifying the relevant unavailable state and diagnostics

### Requirement: Present required delivery-plan fields
For each requested epic, the plan-aware result SHALL expose planned development window, all planned development sprint overlaps, target release version/date with precision, and optional API deployment. It SHALL also expose UAT and Beta as release context when available.

#### Scenario: DLC Visibility plan is matched
- **WHEN** `RMD-4160` is explicitly mapped to `DLC Visibility` in release 3.3.56 using the observed 2026 plan fixture
- **THEN** planned development is 2026-07-07 through 2026-07-30
- **AND** development sprints include Sprint 18 and Sprint 19 with their overlap ranges
- **AND** target release is version 3.3.56 on 2026-09-05 with `DAY` precision
- **AND** UAT is 2026-08-20 through 2026-08-26
- **AND** Beta is 2026-08-27 through 2026-09-02
- **AND** API deployment is `Not specified in Epic Plan`

#### Scenario: Release target has month precision
- **WHEN** a matched plan target has `MONTH` precision
- **THEN** every reporter presents the target as a month-level target
- **AND** no reporter renders an invented day

#### Scenario: Explicit API deployment is available
- **WHEN** plan extraction returns a valid explicit API deployment window
- **THEN** the result presents that window independently from APP, QA, UAT, Beta, and public release

### Requirement: Time-aware alignment signals
The system SHALL compute deterministic plan-alignment signals using one run-level `as_of` timestamp interpreted in the canonical workspace timezone returned by `_resolve_workspace_timezone()`. The workbook timezone SHALL be retained and used to interpret source cell dates; a source/workspace timezone mismatch SHALL be visible as an informational diagnostic and MUST NOT silently change the reporting timezone. Signals MUST be based only on available plan windows and Jira actual evidence and MUST retain supporting facts.

#### Scenario: Development window has started but epic has not
- **WHEN** `as_of` is on or after planned development start, before or on planned development end, and Jira indicates the epic has not started
- **THEN** the result includes a `DEVELOPMENT_NOT_STARTED_ON_PLAN` signal with planned start and Jira status evidence

#### Scenario: Development window has ended with incomplete execution
- **WHEN** `as_of` is after planned development end and Jira completion is below 100 percent
- **THEN** the result includes a `DEVELOPMENT_WINDOW_OVERRUN` signal with planned end and actual completion evidence

#### Scenario: Target release exact date has passed
- **WHEN** the target has `DAY` precision, `as_of` is after that date, and Jira epic execution is incomplete
- **THEN** the result includes a `RELEASE_TARGET_PASSED` signal

#### Scenario: Target release is month-only
- **WHEN** the target has `MONTH` precision
- **THEN** the analyzer does not apply an exact-day overdue signal before the month has ended

#### Scenario: Required plan field is unavailable
- **WHEN** a signal lacks the plan date or Jira evidence required by its rule
- **THEN** the signal is not emitted
- **AND** an availability/diagnostic state may explain why it was not evaluated

#### Scenario: Workbook and workspace timezones differ
- **WHEN** source metadata names a timezone different from the canonical workspace timezone
- **THEN** source dates are decoded using the workbook timezone
- **AND** alignment comparisons use the workspace-local date of the single run-level `as_of`
- **AND** an informational timezone-mismatch diagnostic records both timezone names

### Requirement: Release readiness context
The system SHALL present release target, UAT, Beta, and optional API deployment as distinct milestones/windows and SHALL provide a concise readiness summary based on Jira completion/blocker evidence without claiming that a plan gate is actually completed unless actual evidence supports it.

#### Scenario: Release gates are planned but Jira has blockers
- **WHEN** UAT and Beta windows are present and Jira analysis reports unresolved blockers
- **THEN** the readiness summary shows the planned gates and unresolved blocker evidence
- **AND** it does not mark UAT or Beta complete solely because their planned dates passed

#### Scenario: API deployment is unspecified
- **WHEN** no explicit API deployment exists in plan context
- **THEN** the readiness summary says `Not specified in Epic Plan`
- **AND** it does not substitute public release or development end

#### Scenario: Release target is unspecified
- **WHEN** the release group is `Not ready yet` or has no valid target
- **THEN** readiness identifies the release target as unspecified
- **AND** exact-date release variance is not computed

### Requirement: Plan availability and mapping states are visible
The system SHALL expose plan availability/matching state per epic using at least `MATCHED`, `UNMAPPED`, `NOT_FOUND`, `AMBIGUOUS`, `SOURCE_UNAVAILABLE`, and `PARSE_INVALID`. These states MUST be visible in machine-readable output and the spreadsheet presentation.

#### Scenario: Epic is not mapped
- **WHEN** a requested epic has no explicit config mapping
- **THEN** its plan status is `UNMAPPED`
- **AND** its Jira analysis remains present

#### Scenario: Duplicate plan activity is ambiguous
- **WHEN** matching returns `AMBIGUOUS`
- **THEN** the report identifies that state and recommends a release disambiguator
- **AND** it does not display plan values from an arbitrary match

#### Scenario: Plan source cannot be parsed
- **WHEN** required structural anchors are invalid
- **THEN** affected epics show `PARSE_INVALID` with diagnostics
- **AND** existing Jira report sections still render

### Requirement: Delivery Plan Analysis spreadsheet output
Spreadsheet format SHALL include a managed `Delivery Plan Analysis` tab with one concise epic-level row. Columns MUST appear in this stable order: Jira Key, Jira Link, Summary, Jira Status, Jira Progress, Plan State, Development Window, Development Sprint Overlaps, Target Version, Target Date, Target Precision, API Deployment, UAT, Beta, Readiness, Alignment Signals, Diagnostics, Source As Of, and Source Timezone. Repeated sprint overlaps SHALL be rendered in the single overlaps cell as ordered `Sprint Name: overlap-start to overlap-end` entries separated by line breaks. Existing generated tabs MUST remain compatible unless separately specified.

#### Scenario: Matched epic row is rendered
- **WHEN** a requested epic has matched plan context
- **THEN** its row includes Jira key and link, summary, Jira status/progress, plan mapping status, development dates, sprint overlaps, target version/date/precision, API deployment, UAT, Beta, alignment/readiness, and source freshness

#### Scenario: API deployment is absent
- **WHEN** plan context contains no API deployment
- **THEN** the API deployment cell contains `Not specified in Epic Plan`

#### Scenario: Plan data is unavailable
- **WHEN** an epic has a non-matched plan state
- **THEN** the row remains present with Jira actuals
- **AND** plan columns show the explicit state rather than blank or fabricated values

#### Scenario: Multiple sprint overlaps are rendered
- **WHEN** development intersects more than one sprint
- **THEN** the spreadsheet displays every sprint and its overlap without collapsing to only one sprint

### Requirement: Machine-readable and non-spreadsheet compatibility
The plan-aware result SHALL be available to JSON output with optional additive fields. Non-spreadsheet reporters MAY add equivalent plan sections, but existing fields and report generation MUST remain functional when plan enrichment is disabled or unavailable.

#### Scenario: JSON output includes matched plan
- **WHEN** JSON format is generated for a matched epic
- **THEN** the output includes structured plan context, precision, provenance, alignment signals, and diagnostics as additive fields

#### Scenario: Legacy config generates report
- **WHEN** plan enrichment is disabled or no `[epic_plan]` section exists
- **THEN** existing report formats complete without requiring plan fields

#### Scenario: Consumer ignores additive fields
- **WHEN** an existing consumer reads legacy Jira/report fields only
- **THEN** those fields retain their existing meaning and shape

### Requirement: Manual and scheduled execution parity
The existing `generate` pipeline and `scheduled-run` pipeline SHALL apply the same plan configuration, extraction, matching, analysis, and rendering behavior. This change MUST NOT add a second scheduler workflow or alter the canonical `daily-epic-report` cadence.

#### Scenario: Manual and scheduled runs use same config
- **WHEN** both run against the same Jira snapshot, workbook snapshot, TOML, and `as_of` time
- **THEN** they produce equivalent plan contexts and alignment results

#### Scenario: Scheduled plan read fails
- **WHEN** a scheduled run cannot read Epic Plan but Jira collection and output access remain available
- **THEN** the run produces Jira-only report output with visible plan-source diagnostics
- **AND** it does not fail solely because optional plan enrichment is unavailable

#### Scenario: Scheduler contract remains unchanged
- **WHEN** the feature is enabled
- **THEN** scheduling continues through the existing `daily-epic-report` DBOS workflow and `epic-report scheduled-run`
- **AND** no additional schedule manifest is registered

### Requirement: Structured observability
Each enabled plan-aware run SHALL emit exactly one `INFO` summary event named `epic_plan_run_summary` through logger `epic_report.plan` after enrichment/output handling. The event SHALL cover plan read, parse, mapping, analysis, and output without logging credentials or full workbook contents. Fields MUST include non-secret workbook ID, tab, requested epic count, parsed row/release/activity counts, counts for every result state and diagnostic severity, plus read, parse, match, analyze, output, and total durations in milliseconds.

#### Scenario: Plan analysis completes
- **WHEN** plan enrichment finishes
- **THEN** logs include tab name, parsed release/activity counts, requested epic count, mapping-state counts, diagnostic severity counts, and duration

#### Scenario: Sensitive configuration is present
- **WHEN** service-account credentials and workbook configuration are loaded
- **THEN** logs omit credential contents and do not dump the full plan grid

#### Scenario: One epic has invalid plan data
- **WHEN** one mapped activity has invalid dates and other epics are valid
- **THEN** logs identify the affected epic and diagnostic code
- **AND** valid epics continue through analysis

### Requirement: Verification against sanitized and live plan shapes
The implementation MUST include deterministic unit/integration fixtures for the observed workbook hierarchy and MUST perform a read-only live verification before rollout. Tests MUST cover date precision, sprint intersections, mapping ambiguity, absent/invalid API deployment, degraded fallback, source-tab preservation, and scheduled/manual parity.

#### Scenario: Sanitized DLC fixture is tested
- **WHEN** the observed `DLC Visibility` hierarchy is represented in a sanitized fixture
- **THEN** tests assert the exact development, sprint, release, UAT, Beta, and absent API results defined by this specification

#### Scenario: Workbook preservation is regression-tested
- **WHEN** sheet structure synchronization is tested with `Epic Plan` and an unknown stakeholder tab
- **THEN** neither tab appears in delete or rewrite requests

#### Scenario: Live verification is performed
- **WHEN** implementation is ready for deployment
- **THEN** a read-only run verifies the configured mapping and extracted values against the live workbook
- **AND** a post-write readback verifies only managed output changed

### Requirement: Failed managed output is explicit
Managed spreadsheet synchronization SHALL NOT suppress clear, write, or structure-update failures. A failed managed operation MUST propagate an error to the report command so operators do not mistake stale or partially refreshed output for a successful run.

#### Scenario: Managed clear fails
- **WHEN** clearing a managed output tab fails
- **THEN** report generation fails with the underlying error
- **AND** the failure is logged with the spreadsheet and tab context

#### Scenario: Managed write fails
- **WHEN** writing a managed output range fails
- **THEN** report generation fails with the underlying error
- **AND** it does not return a successful spreadsheet URL

#### Scenario: An epic analysis is unexpectedly absent
- **WHEN** a requested Jira epic has no entry in the plan-analysis result map
- **THEN** `Delivery Plan Analysis` still renders one row for that epic
- **AND** the row contains Jira actuals and an explicit `NO_ANALYSIS` plan state
