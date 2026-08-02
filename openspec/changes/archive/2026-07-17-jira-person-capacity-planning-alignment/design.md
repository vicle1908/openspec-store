## Context

This change is specifically a `Person Capacity` report update. `jira-daily-reports sprint-sheet` currently writes `Sprint Report` and `Person Capacity` from one Jira issue snapshot. The v1 `Person Capacity` tab has two ledgers:

- ownership: Jira issue assignee + Jira original estimate,
- activity: Jira worklog author + logged seconds by day.

Live workbook research on `1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8` shows sprint planning data is maintained in the spreadsheet, not only in Jira:

- `Person Capacity Mapping` is the writable primary mapping sheet; `Dropdown Keys - Do Not Delete -` remains the protected fallback and is merged in to backfill missing member rows or empty identity cells (`MEMBERS` → `JIRA Nick Name`).
- Current sprint activity tabs are `Kelvin's Team Activites New`, `Andrew's Team Activites New`, and `VuVuong's Team Activites New`.
- Team activity tabs carry the current sprint title `AGILE SPRINT 15 (25 May - 06 Jun) BURNDOWN CHART`, `ASSIGNED TO` member keys, `ORIGINAL ESTIMATE (hour)`, and daily effort columns.
- Current `Person Capacity` can map 24 of 30 visible Jira person rows back to dropdown members; 6 Jira rows are unmapped.
- Bucket scope and planning scope differ: 66 bucket issue keys, 55 team-activity issue keys, 52 overlap, 14 bucket-only, and 3 planning-only.
- Existing summary formulas are not reliable enough as a source of truth: `Capacity of Resource` has `#REF!` cells and formulas referencing old tab names; detail-row parsing is safer.

Broader ecosystem research shows adjacent reusable pieces already exist:

- `jira-kanban-from-spreadsheet/src/kbs/sheets/reader.py` has backend abstraction for Google Sheets (`gspread` or direct API), spreadsheet metadata discovery, and sheet-name discovery.
- `jira-kanban-from-spreadsheet/src/kbs/sheets/parser.py` has header alias normalization and validated sprint row parsing for bucket-style planning tabs.
- `jira-kanban-from-spreadsheet/src/kbs/jira/jql_builder.py` has deterministic issue-key JQL construction.
- `jira-daily-reports/src/jira_daily_reports/delivery/sheet.py` now uses direct Google Sheets API service-account access plus bucket-scope parsing for `Sprint Report`.

This change should therefore reuse or extract common spreadsheet primitives rather than adding a third isolated parser stack.

The report therefore needs to update `Person Capacity` semantics only: separate planned capacity from Jira ownership and actual logged work while using the workbook member mapping as the merge key. Existing sprint-ticket extraction and target-vs-actual report behavior remain the upstream scope input, not part of this redesign.

## Goals / Non-Goals

**Goals:**

- Use the workbook dropdown mapping as the canonical workbook identity bridge.
- Crawl current sprint team activity tabs at detail-row level and aggregate planned effort by `member_key`.
- Merge planned capacity, Jira ownership, and Jira worklog activity into one person-capacity view.
- Reuse the existing bucket-scope issue extraction for the Jira issue set used by person capacity.
- Avoid duplicating ecosystem spreadsheet/JQL primitives that already exist in `jira-kanban-from-spreadsheet` or can be promoted to shared workspace code.
- Preserve v1 original-estimate-only Jira semantics and complete-worklog aggregation.
- Surface reconciliation warnings instead of silently producing incomplete rows.
- Keep report execution read-only for source tabs and idempotent for generated output tabs.

**Non-Goals:**

- Editing or auto-fixing the planning workbook source tabs.
- Changing `Sprint Report` target-vs-actual behavior or replacing its bucket-tab issue extraction logic.
- Making `jira-daily-reports` depend directly on the `kbs` application package as a runtime app-to-app dependency.
- Treating stale summary formulas as authoritative.
- Replacing Jira worklog actuals with spreadsheet daily cells.
- Building payroll/timesheet-grade accounting.
- Requiring every workbook member to have a Jira account mapping before the report can run.

## Decisions

1. **Canonical merge key is workbook `member_key` when available**
   - Use `Person Capacity Mapping` as the bridge from workbook member key to Jira display name, with `Dropdown Keys - Do Not Delete -` merged in as a protected fallback to preserve full workbook coverage.
   - Build both `member_key -> jira_display_name` and normalized reverse maps for Jira display name and Jira `accountId` when present.
   - Jira `accountId` remains useful inside Jira-only grouping and as the durable Jira user identifier visible in the sheet.
   - Alternative considered: keep Jira accountId as primary. Rejected because planned rows do not always contain accountIds and would remain disconnected from Jira rows.

2. **Team activity tabs are parsed from detail rows, not formula summary blocks**
   - Header-detect columns by names (`JIRA ID`, `ASSIGNED TO`, `ORIGINAL ESTIMATE (hour)`) and detect daily columns from date labels.
   - Ignore `TOTAL` rows and right-side `SUMIFS` summary blocks.
   - Rationale: live formulas include stale references and `#REF!`; detail rows are closer to the planning source of truth.

3. **Existing bucket-scope extraction becomes a shared sprint-ticket scope**
   - Reuse the existing `delivery.sheet.read_bucket_scope()` flow for sprint issue keys and target statuses.
   - Promote its output into a small shared scope structure, conceptually `SprintTicketScope(keys, targets, source_ranges, warnings)`, created once by the sheet delivery flow.
   - Pass the same scope to the existing `Sprint Report` path (`set_bucket_keys()` / `set_targets()`) and to the new `Person Capacity` planning merge.
   - Keep the existing `issuekey in (...)` Jira query path unchanged for Jira issue extraction.
   - Use the same extracted `keys` set to decide which planning rows can fill `Person Capacity` planned metrics.
   - Team activity rows whose issue key is not in the bucket issue set are reconciliation-only and SHALL NOT contribute to `Planned Estimate`, `Planned Issues`, or `Planned Tasks` totals.
   - Team activity tabs are planning inputs and reconciliation inputs; they SHALL NOT replace bucket tabs as the sprint ticket scope.
   - Expand the Jira-side seed scope before fetch as a one-hop graph from seed issues only: follow issue links of type `Blocks` in both directions so blocked/blocking siblings are visible; optionally include other split-style links only when the project config explicitly marks them as sprint-relevant.
   - Apply normalized-key dedupe + self-link guards during expansion so repeated links do not inflate the fetch set.
   - Record skipped link types in reconciliation diagnostics when traversal encounters non-relevant links.
   - Keep planning reconciliation keyed to the original bucket seed set, not the expanded Jira fetch set, so out-of-scope planning rows stay visible as warnings rather than counted as capacity.
   - Alternative considered: derive or union sprint scope from team activity tabs. Rejected because live research found bucket/planning mismatches (bucket-only and planning-only issue keys); unioning would inflate `Person Capacity` with out-of-scope planning rows, while replacing bucket scope would drop valid sprint tickets.

4. **Ticket extraction is not duplicated in the planning parser**
   - The planning parser receives the shared scope keys as an input filter; it does not re-read bucket tabs or infer sprint scope from planning tabs.
   - Any future change to bucket range names, ID column aliases, or target status parsing belongs in the shared scope reader, not in person-capacity planning code.
   - Rationale: one implementation owns sprint ticket extraction; `Person Capacity` consumes it.

5. **Reuse common spreadsheet primitives, do not create app-to-app coupling**
   - Reuse concepts and, where practical, code from `jira-kanban-from-spreadsheet`: backend abstraction, metadata discovery, value-grid conversion, header alias matching, issue-key validation, and deterministic JQL construction.
   - Do not make `jira-daily-reports` import `kbs.*` directly at runtime; both are application projects with independent lifecycles.
   - If code reuse requires moving utilities, extract the smallest stable primitives into a shared internal module such as `tdt_core.sheets` / `tdt_core.spreadsheets` or a local `jira_daily_reports.sheet_primitives` module with an explicit follow-up promotion path.
   - Prefer shared helpers for:
     - direct Sheets API service creation and response normalization,
     - spreadsheet metadata/timezone/sheet-name discovery,
     - header normalization and alias lookup,
     - issue-key extraction and de-duplication,
     - JQL construction from key lists.
   - Keep person-capacity-specific hierarchy parsing (`ASSIGNED TO` inheritance, unresolved effort rows) in the person-capacity planning module.
   - Rationale: reuse stable infrastructure without coupling two application CLIs.

6. **Row assignment uses explicit value, group inheritance, then issue inheritance**
   - If a detail row has `ASSIGNED TO`, use it.
   - Else inherit from the nearest non-effort group row with an assignee.
   - Else inherit from the current issue row assignee.
   - Else record the effort under an unresolved planning bucket and emit a warning.
   - Rationale: Andrew's tab uses blank child rows under issue-level assignees; VuVuong's tab uses platform/group rows.

7. **Person Capacity v2 has three ledgers**
   - Planned ledger: team activity tabs (`Planned Estimate`, planned issue/task counts, optional planned daily effort if present).
   - Jira ownership ledger: Jira assignee + original estimate only.
   - Actual ledger: Jira worklog author + complete worklog seconds by day.
   - Rationale: capacity planning, Jira ownership, and actual activity answer different questions and must not be collapsed.

8. **Reconciliation is part of the report contract**
   - Report mapping gaps, unresolved planned rows, bucket-vs-planning scope mismatch, team sheet parse totals, and stale summary formula indicators.
   - Generated output remains useful even with warnings.
   - Rationale: live workbook data is partially filled; hiding gaps would create false confidence.

9. **Source tabs are read-only**
   - The report reads mapping/planning/bucket tabs and writes only generated output tabs (`Sprint Report`, `Person Capacity`, optional future audit tab if explicitly enabled).
   - Rationale: report execution must be safe and idempotent.

10. **Google Sheets hyperlink policy uses pure formulas only in dedicated hyperlink cells**
   - `Sprint Report` issue-key cells SHALL remain pure `HYPERLINK(...)` formulas because each cell represents a single Jira issue.
   - `Person Capacity` `Worked Ticket Links` SHALL be the canonical clickable multi-ticket surface and SHALL render one pure Jira `HYPERLINK(...)` formula per line so every listed ticket remains independently clickable.
   - `Person Capacity` `Daily Ticket Details` SHALL be treated as a readable diagnostic breakdown, not the primary hyperlink surface, because Google Sheets mixed text plus multiple inline formula fragments in one cell is less robust than pure-formula hyperlink cells.
   - If a future requirement needs every per-day ticket reference to be guaranteed clickable, the system SHOULD add a normalized secondary details section/table with one ticket hyperlink per row instead of embedding many inline formulas inside one prose cell.
   - Alternative considered: embedding multiple `HYPERLINK(...)` fragments inside `Daily Ticket Details`. Rejected as the default contract because mixed-content formula parsing is less predictable and harder to validate than dedicated hyperlink-only cells.

11. **Keep current Jira behavior as fallback**
   - If mapping or planning tabs cannot be read, the report may continue with Jira-only person capacity and mark planning data unavailable.
   - If mapping is readable but some Jira people do not map, keep them as `unmapped:<displayName>` rows.
   - Rationale: current v1 behavior is already validated and should not regress due to workbook gaps.

## Data Flow

```text
Google Sheet snapshot
├─ Dropdown Keys - Do Not Delete -
│  └─ member_key ⇄ Jira display name map
├─ Bucket tabs
│  └─ sprint issue scope + target status
└─ Team activity tabs
   └─ planned task rows + planned hours + planned dates

Jira snapshot
├─ issue assignee + original estimate
└─ complete worklogs + worklog author + started timestamp

Merge
└─ member_key row
   ├─ planned capacity
   ├─ Jira ownership
   ├─ actual worklog activity
   └─ reconciliation warnings
```

## Risks / Trade-offs

- **[Risk] Workbook structure drifts** → Header-detect columns, validate required headers, and emit parser warnings with tab/row references.
- **[Risk] Member mapping is incomplete** → Preserve unmapped Jira rows and unresolved planning rows; report missing mapping counts.
- **[Risk] Scope mismatches confuse totals** → Add explicit bucket-only and planning-only issue counts and samples.
- **[Risk] Formula totals disagree with parsed detail totals** → Treat formulas as diagnostic only; expose drift rather than using formulas for aggregation.
- **[Risk] Wider person tab becomes hard to read** → Keep core columns compact and group daily planned/logged columns behind a documented layout; defer raw audit tab unless needed.
- **[Risk] Unicode names and spacing cause missed joins** → Normalize names with NFKC, whitespace folding, and case-insensitive comparison while preserving display labels.

## Migration Plan

1. Implement read-only mapping parser and tests.
2. Identify reusable spreadsheet/JQL primitives already in `jira-kanban-from-spreadsheet` and either import from a shared extracted module or mirror with tests plus a documented promotion path.
3. Implement current-sprint team activity parser and tests using fixture snippets from live sheet shapes.
4. Add planning capacity input to the existing `sprint-sheet` flow.
5. Merge planned, ownership, and actual ledgers into `person_capacity` summary.
6. Update `Person Capacity` rendering and add reconciliation section.
7. Run targeted unit tests, then live sheet dry/readback verification.
8. Update README and skill runbook.

Rollback:

- Gate planning alignment behind an env toggle during first rollout, or continue Jira-only behavior if mapping/planning read fails.
- Keep `Sprint Report` tab unchanged.

## Open Questions

Resolved for execution:

- v2 starts with compact rows: planned total columns plus existing logged daily columns. Planned daily effort may be parsed and kept in the data model for reconciliation, but it is not required in the first visible row layout because the sheet is already wide.
- `Capacity of Resource` is diagnostic-only for this change. It may be read to detect formula drift, but it SHALL NOT be an authoritative planned-capacity source and SHALL NOT be updated by report generation.
- Unmapped Jira people remain visible in explicit unmapped rows during implementation. Manual dropdown cleanup can happen after the report exposes the gaps; implementation SHALL NOT require full mapping coverage before shipping.

Execution notes:

- Current code state before this change: `jira-daily-reports` has v1 Jira-only person-capacity logic in `SprintReportSheetReport._build_person_capacity()` and row rendering in `build_person_sheet_rows()`; there is no planning parser module yet.
- Current `delivery/sheet.py` already reads bucket scope once, calls `set_bucket_keys()` and `set_targets()`, runs the report, then writes `Sprint Report` and `Person Capacity`. Keep this shape and extend it with a shared scope object plus planning snapshot input; do not add a second Jira run.
- `jira-kanban-from-spreadsheet` has reusable reader/parser/JQL concepts, but `jira-daily-reports` SHALL NOT import `kbs.*` at runtime. Extract stable helpers or implement a small local primitive layer with tests and a documented promotion path.

## Resolved Implementation Notes

The following behavioral decisions were validated against the current implementation:

1. **Planned daily effort columns are stored but not rendered in v1 sheet layout.**
   `PlannedPersonAggregate.daily_hours` is computed by `aggregate_planning_rows()` and stored
   in `PlanningSnapshot.aggregates`, but `build_person_sheet_rows()` in
   `reports/sprint_report_sheet.py` renders only Jira-sourced `daily_issue_seconds` daily
   columns. The planned daily data is present for reconciliation but not visible in the
   generated sheet tab. This is intentional for v1 given the sheet width constraint and
   confirmed in the Open Questions section above. Adding planned daily columns to the visible
   layout is a deferred enhancement.
