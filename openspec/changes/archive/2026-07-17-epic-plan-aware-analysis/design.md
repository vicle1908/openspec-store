## Context

`jira-epic-report` currently builds an execution snapshot from Jira and renders generated tabs into a dedicated Google workbook. The same workbook contains a stakeholder-owned `Epic Plan` tab that expresses the target delivery sequence as a release-grouped Gantt chart.

Live inspection on 2026-07-16 established this source shape:

- row 4 contains merged sprint labels such as `Sprint 18` over date columns;
- row 5 contains the calendar axis;
- column A contains merged release groups such as `3.3.56 (05-Sep)`;
- a numbered major activity row identifies a deliverable such as `DLC Visibility`;
- child rows identify APP development and QA phases through the `Teams` column;
- Start, End, resources, person-days, and daily allocations are present on phase rows;
- release-level UAT and Beta activities are represented as parent rows followed by dated QA child rows;
- no API deployment row or field currently exists for `DLC Visibility`;
- there are no formulas, notes, named ranges, hidden fields, or developer metadata carrying deployment semantics;
- blue fill is weekend formatting and orange header fill marks selected dates, so color is not a business-data source.

For the configured mapping `RMD-4160 -> DLC Visibility`, the source currently states APP development from 2026-07-07 through 2026-07-30 across Sprint 18 and Sprint 19, target release 3.3.56 on 2026-09-05, UAT from 2026-08-20 through 2026-08-26, Beta from 2026-08-27 through 2026-09-02, and no specified API deployment.

The report must combine this authoritative plan with authoritative Jira actuals without collapsing their different measures. Plan person-days are planned allocation; Jira statuses, tasks, blockers, and progress remain actual execution evidence.

## Goals / Non-Goals

**Goals:**

- Parse the stakeholder-owned `Epic Plan` tab read-only through existing authenticated Sheets facilities.
- Resolve configured Jira epic keys to exact plan activities without fuzzy matching.
- Produce a typed, provenance-bearing plan context for development, sprint overlaps, target release, optional API deployment, UAT, and Beta.
- Reconcile plan context with existing Jira epic analysis and expose alignment states and diagnostics.
- Add a managed `Delivery Plan Analysis` tab without deleting or rewriting stakeholder-owned tabs.
- Keep manual and scheduled report runs behaviorally consistent.
- Degrade to Jira-only output when plan data is unavailable or invalid.

**Non-Goals:**

- Editing the plan, adding Jira keys to it, or repairing invalid source cells.
- Inferring API deployment from another phase or milestone.
- Using formatting, formulas, or summary totals as authoritative plan semantics.
- Converting planned person-days into actual progress.
- Predictive rescheduling, burn forecasting, historical trend storage, or mobile application changes.
- Changing DBOS schedule registration, cadence, or retry policy.

## Decisions

1. **The Epic Plan remains the authoritative plan source and Jira remains the authoritative actual source**

   The parser records plan values separately from Jira actuals. The analyzer compares them but does not overwrite one with the other. Planned person-days and resources remain plan metadata; they do not affect Jira completion percentage.

   Alternative considered: copy plan values into existing `Epic.target_version`, `cut_off_date`, and `sprint_allocations` fields. Rejected because those fields do not encode source, date precision, release gates, or parse diagnostics and would blur plan and actual ownership.

2. **Introduce plan-specific typed models with one result per requested epic**

   Add small models conceptually equivalent to:

   ```text
   PlanSourceRef(tab, row, range, raw_value)
   PlanDiagnostic(code, severity, message, source)
   PlanDate(value, precision, raw_value)
   PlanWindow(start, end, source)
   SprintOverlap(name, sprint_start, sprint_end, overlap_start, overlap_end)
   ReleaseTarget(version, date, date_precision, source)
   EpicPlanContext(epic_key, activity, development, target_release,
                   api_deployment, release_gates, provenance, diagnostics)
   PlanAwareEpicAnalysis(epic_key, state, plan_context, signals,
                         readiness, as_of, timezone, diagnostics)
   ```

   Date precision is `DAY`, `MONTH`, or `UNSPECIFIED`. Optional values remain absent rather than receiving sentinel dates. The orchestration returns one `PlanAwareEpicAnalysis` for every requested Jira epic whenever the feature is enabled; business states are never represented by `None`. `EpicPlanContext` exists only for a successful `MATCHED` result, while `UNMAPPED`, `NOT_FOUND`, `AMBIGUOUS`, `SOURCE_UNAVAILABLE`, and `PARSE_INVALID` remain explicit analysis states with diagnostics.

3. **Use an optional `[epic_plan]` TOML section with explicit mappings**

   The initial configuration shape is:

   ```toml
   [epic_plan]
   enabled = true
   sheet_name = "Epic Plan"
   snapshot_range = "A1:ZZ500"

   [epic_plan.epics."RMD-4160"]
   activity = "DLC Visibility"
   # release_version = "3.3.56" # optional duplicate-title disambiguator
   ```

   The existing `[output].spreadsheet_url` identifies the workbook for both input and output. `snapshot_range` is a tab-relative bounded A1 range with conservative default `A1:ZZ500`; configuration can expand it without code changes. The reader rejects ranges naming another tab and emits `SNAPSHOT_BOUNDARY_REACHED` when non-empty cells touch the configured final row or column, because the source may have outgrown the bound. Mapping keys are normalized as Jira keys; activity matching uses normalized whitespace and case-insensitive exact equality. No token, substring, or semantic fuzzy match is allowed. An optional release version resolves otherwise duplicate exact activity names.

   Alternative considered: add a Jira key column to the plan. Rejected for this iteration because the operator chose config mapping and the source workbook should remain unchanged.

4. **Read one coherent, bounded workbook snapshot through a public `tdt-sheets` API**

   Extend the canonical `tdt-sheets` client with a typed `read_grid_snapshot(spreadsheet_id, range_ref)` operation. Its SDK implementation performs one bounded `spreadsheets.get` request with the requested A1 range and a field mask sufficient for spreadsheet locale/timezone, selected sheet identity/grid bounds, merge ranges, and each selected cell's `effectiveValue` and `formattedValue`. The returned transport-neutral `GridSnapshot` preserves cell coordinates and does not expose the raw Google response. `jira-epic-report` consumes only this public client operation; it does not access `SheetsClient._backend`, `_get_sheets_service()`, or construct a second raw Google client.

   The SDK backend is the supported snapshot backend. Other backends MUST raise `BackendNotAvailableError` or `NotImplementedError` explicitly rather than returning an incomplete snapshot. Existing read/write methods and backend-equivalence guarantees remain unchanged because this is an additive SDK capability.

   The plan collector performs this one snapshot read before analysis and reuses it for every configured epic. Effective numeric values are authoritative for daily calendar cells and phase Start/End dates. Formatted labels remain authoritative for declared release precision (`05-Sep` is `DAY`, `Oct` is `MONTH`, and `Not ready yet` is `UNSPECIFIED`) and remain provenance/display evidence. The report run does not issue one full-sheet read per epic.

5. **Discover structural anchors from headers, then validate explicit row boundaries**

   The parser locates required headers using case-folded, collapsed-whitespace exact aliases for `Version`, `No`, `Majors Activities`/`Major Activities`, `Teams`, `# Resource Involved`, `Total MD`, `Start`, and `End`. It identifies the daily date-axis columns to the right of Start/End, sprint labels through merged ranges above that axis, release groups through merged or inherited Version values, and numbered major activities.

   A non-empty normalized `No` value starts a new major activity. A non-empty Version value starts a new release group. Rows with an empty `No` and inherited/empty Version belong to the current activity until either boundary occurs. UAT and Beta release-gate parent activities use their immediately following dated QA child row within the same release group. A row cannot be inherited across a release-group boundary.

   A missing required anchor makes plan extraction unavailable with diagnostics. The parser does not silently fall back to fixed coordinates, though test fixtures may preserve the current row/column layout. Required header aliases and API deployment aliases are versioned defaults in code; configuration may add aliases but cannot remove the defaults.

6. **Derive development sprint membership by interval intersection**

   APP child rows are authoritative development phases. Their valid Start/End values define the development window. Every sprint range intersecting that inclusive window becomes a `SprintOverlap`, with overlap start/end retained. Daily allocation cells, resources, and person-days are supporting plan evidence and validation, not substitutes for Start/End.

   For the current DLC fixture this produces Sprint 18 overlap 2026-07-07 through 2026-07-17 and Sprint 19 overlap 2026-07-20 through 2026-07-30.

7. **Parse target release from the containing release group with explicit precision and deterministic year resolution**

   The version label is split into version and parenthesized date text. Exact day labels such as `05-Sep` or `3 Oct` become `DAY`; month-only labels such as `Oct` become `MONTH`; `Not ready yet` or missing labels become `UNSPECIFIED` without a date; other unparseable labels become `UNSPECIFIED` with a diagnostic. The parser must not fabricate a day for month-only targets.

   The effective-value calendar axis defines an ordered sequence of actual dates, including year transitions. For a day-level or month-level release label, candidate calendar years are taken from axis dates with the same month in the containing release group's visible span; when exactly one candidate exists it is used. If no unique candidate exists, continuity with the closest dated phase/gate in the same release group MAY resolve the year only when that produces exactly one chronological candidate. Otherwise the target remains `UNSPECIFIED` and emits `RELEASE_YEAR_AMBIGUOUS`; the runtime year or report `as_of` year is never used as a fallback.

8. **API deployment requires an explicit child activity row**

   Only an explicit child row matching configured, documented aliases such as `API Deployment` or `API Deployment Work`, with valid Start and End, creates an API deployment window. Absence is a valid optional state rendered as `Not specified in Epic Plan`. An explicit row with invalid/missing dates produces an invalid-data diagnostic and no inferred window.

   Alternative considered: infer deployment from APP end, QA start, UAT, Beta, or release date. Rejected because the live workbook provides no evidence that any of these are equivalent.

9. **UAT and Beta are release-level context, not epic-level API deployment**

   Release-level UAT/Beta parent activities inherit dates from their dated QA child rows. They are attached to each epic in the containing release group as release gates with source provenance. They do not become development or API windows.

10. **Matching, source, and parser failures are explicit per-epic states**

    Result states are `MATCHED`, `UNMAPPED`, `NOT_FOUND`, `AMBIGUOUS`, `SOURCE_UNAVAILABLE`, or `PARSE_INVALID`. If the source read fails, every requested epic receives `SOURCE_UNAVAILABLE`; if required structural parsing fails globally, every requested epic receives `PARSE_INVALID`; per-activity malformed fields remain a matched context with field-level diagnostics unless the activity cannot be identified safely. Parse diagnostics carry stable codes, severity, tab, row/range, raw value where safe, and an actionable message. No plan failure blocks Jira collection or the existing report tabs. Authentication and authorization continue through the existing service-account/`tdt-sheets` path; credentials are never logged.

11. **Plan-aware analysis is additive, conservative, and time-deterministic**

    A new analyzer consumes existing Jira `Epic` data plus the per-epic plan result. It reports planned phase/time, current Jira status/progress, target release, gates, optional deployment, and alignment signals such as development-window-not-started, development-window-overrun, release-target-passed, and plan-data-unavailable. Signals are evidence-based and include one run-level `as_of` timestamp.

    Date comparisons use `_resolve_workspace_timezone()` as the canonical analysis timezone, matching scheduled-run behavior. Spreadsheet timezone is retained as source metadata and is used to interpret source cell dates. If source and workspace timezones differ, the run emits an informational diagnostic; it does not silently switch the scheduler/reporting timezone. `as_of` is captured once after configuration resolution and injected into parsing/analysis/tests so manual and scheduled runs are reproducible. The analyzer does not mutate Jira or the plan.

12. **Spreadsheet ownership is explicit and deletion requires positive evidence**

    `Delivery Plan Analysis` joins the static managed generated-tab allow-list with `Executive Summary`, `Epic Overview`, `Blocking Dependencies`, `Sprint Report`, `Person Capacity`, `Risks`, and `Blocking Bugs`. `Epic Plan` and every tab not positively identified as managed are protected/unmanaged. Structure synchronization may add, clear, format, or replace only current managed output tabs and may delete only obsolete titles from the static managed allow-list.

    Existing per-epic tabs have dynamic human-readable titles and no durable ownership marker. This iteration MAY create/update the exact per-epic titles computed for the current report, but it MUST preserve stale dynamic epic tabs because title-pattern matching cannot prove ownership safely. Automatic stale dynamic-tab cleanup is deferred until generated tabs carry durable developer metadata or another positive ownership marker. This intentionally narrows the legacy reporter behavior to prevent stakeholder data loss.

13. **Scheduled and manual runs share the same pipeline**

    Plan enrichment occurs inside the existing `generate` path used by direct CLI and `scheduled-run`. The scheduler workflow remains a thin subprocess wrapper. A plan-read failure is logged with structured diagnostics and does not change the scheduler manifest or DBOS workflow contract.

14. **No new external dependency**

    Use existing Python standard-library date/zone facilities, existing Pydantic/dataclass patterns, and `tdt-sheets`/Google API capabilities already present in the scheduler image. If implementation proves a new dependency necessary, stop and obtain approval before adding it.

## Data Flow

```text
~/.tdt/epic-report-config.toml
├─ schedule.epics
└─ epic_plan.epics.<JIRA_KEY> -> exact activity (+ optional release)

Dedicated epic-report workbook
└─ Epic Plan values + merges + spreadsheet timezone
   └─ EpicPlanSnapshotCollector
      └─ EpicPlanParser
         ├─ sprint calendar
         ├─ release groups and gates
         ├─ major activities and phase rows
         └─ diagnostics

Jira Cloud API v3
└─ existing EpicCollector -> Epic actual snapshot

EpicPlanMatcher(plan snapshot, config mapping)
└─ explicit extraction state per requested Jira epic

DeliveryPlanAnalyzer(Epic actual, extraction state, as_of)
└─ PlanAwareEpicAnalysis per requested Jira epic

Existing reporters
├─ existing generated tabs/formats
└─ Delivery Plan Analysis (managed output)

Epic Plan and unknown workbook tabs remain untouched
```

## Error Handling And Observability

- Emit one structured plan-run summary event at `INFO` using logger `epic_report.plan` and event name `epic_plan_run_summary`: workbook identifier (non-secret ID), tab, rows parsed, release groups, activities, requested epics, counts for every result state, diagnostics by severity, and read/parse/match/analyze/output durations in milliseconds. `output_duration_ms` measures the complete Phase 4 generation/write wall time for the selected format; the event is emitted exactly once after output handling.
- Managed spreadsheet synchronization, clear, and write failures MUST propagate to the report command rather than being suppressed or converted into an apparent successful refresh. A failed refresh MUST NOT be described as complete.
- Emit per-epic mapping/analysis status without credentials or full sheet dumps.
- Treat authentication denial, missing tab, missing required headers, malformed dates, invalid intervals, duplicate matches, and absent API deployment as distinct codes.
- Authentication denial and parser-unavailable states produce Jira-only output and a visible plan availability warning.
- An absent API row is informational, not an error.
- Tests must assert no write request targets `Epic Plan` and no delete request targets unmanaged tabs.

## Risks / Trade-offs

- **[Risk] Workbook structure drifts** -> Detect normalized headers and merge hierarchy, validate anchors, and emit source-located diagnostics instead of returning guessed values.
- **[Risk] Config title mapping becomes stale** -> Require exact matching and surface `NOT_FOUND`; do not silently choose a similar title.
- **[Risk] Duplicate activity titles appear in different releases** -> Return `AMBIGUOUS` unless optional `release_version` selects one exact release group.
- **[Risk] Date labels omit years** -> Use raw/effective values, spreadsheet timezone, and calendar continuity; retain precision and reject unresolved ambiguity.
- **[Risk] Month-only targets invite false precision** -> Model and render month precision explicitly.
- **[Risk] API deployment is often absent** -> Render a clear optional-state message; never infer it.
- **[Risk] Plan enrichment slows every scheduled run** -> Read one bounded snapshot per run, reuse it across epics, and log duration.
- **[Risk] Existing structure sync deletes stakeholder data** -> Restrict deletion to explicitly managed generated tabs and add destructive-operation regression tests.
- **[Risk] Plan data creates false confidence** -> Show provenance, diagnostics, as-of time, and separate plan measures from Jira actuals.

## Migration Plan

1. Add the public typed grid-snapshot model/client/backend operation in `tdt-sheets`, with SDK tests and explicit unsupported-backend behavior.
2. Harden spreadsheet ownership synchronization before enabling live output; preserve unknown and stale dynamic tabs unless positive ownership evidence exists.
3. Add config models and fixtures while defaulting plan enrichment off when `[epic_plan]` is absent.
4. Add plan models/reader/parser/matcher with unit tests built from sanitized live-sheet shapes.
5. Add the `RMD-4160 -> DLC Visibility` operator mapping in `~/.tdt` only after code supports it; do not commit local config.
6. Add plan-aware analyzer and report model integration behind `epic_plan.enabled`.
7. Add `Delivery Plan Analysis`, documentation, and skill guidance.
8. Run unit, integration, lint, strict type, OpenSpec, and Docker dependency checks in both affected Python repositories.
9. Rebuild the scheduler with `docker compose up --build -d scheduler` and verify a manual scheduled-run plus the next natural tick/readback.

Rollback:

- Set `[epic_plan].enabled = false` or remove the section to return to Jira-only behavior.
- Keep the new models optional so existing JSON/report consumers remain compatible.
- If output rendering causes issues, omit the managed `Delivery Plan Analysis` tab while retaining source-tab protection.
- Rollback must never delete or rewrite `Epic Plan`.

## Open Questions

Resolved for apply-ready status:

- Planning source: the existing `Epic Plan` tab is authoritative.
- Identity: explicit mapping in `~/.tdt/epic-report-config.toml` is authoritative; no Jira-key column is required.
- API deployment: explicit child row only.
- Missing API deployment: render `Not specified in Epic Plan`.
- Release date precision: exact-day, month-only, and unspecified are distinct.
- Output: add a managed `Delivery Plan Analysis` tab and preserve all source/unmanaged tabs.

No blocking questions remain. Alias lists and exact visible column ordering may be refined during implementation without changing these behavioral contracts.
