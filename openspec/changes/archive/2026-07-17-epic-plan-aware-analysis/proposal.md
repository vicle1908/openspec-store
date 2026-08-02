## Why

The current epic report explains Jira execution status but cannot show the stakeholder-authored delivery plan that gives that status meaning: planned development sprints and dates, target release version and date, and an optional API deployment window. The authoritative `Epic Plan` tab already contains most of this information, but it is not parsed, is not linked reliably to Jira epics, and can currently be removed by generated-sheet structure synchronization.

## What Changes

- Add a read-only `Epic Plan` snapshot parser for the dedicated epic-report workbook.
- Configure explicit Jira-epic-to-plan-activity mappings in `~/.tdt/epic-report-config.toml`; do not use fuzzy title matching.
- Extract the mapped activity's APP development window and all intersecting merged sprint-header ranges.
- Extract the containing release version and target date while preserving exact-day, month-only, and unspecified date precision.
- Extract API deployment only from an explicit child activity row with its own valid Start/End values; report `Not specified in Epic Plan` when absent.
- Extract release-level UAT and Beta windows as supporting target-release context.
- Reconcile authoritative plan data with authoritative Jira actuals in a plan-aware epic analysis result with source provenance and actionable diagnostics.
- Add a generated `Delivery Plan Analysis` spreadsheet tab while preserving `Epic Plan` and every other stakeholder-owned input tab.
- Continue Jira-only report generation when plan access, mapping, or parsing is unavailable; expose the degraded state instead of guessing values.

### Non-Goals

- Editing, normalizing, or auto-fixing the `Epic Plan` tab.
- Fuzzy matching Jira summaries to plan activity titles.
- Inferring API deployment from APP completion, QA, UAT, Beta, or public release dates.
- Treating colors, formula summaries, or person-day totals as actual Jira progress.
- Building effort-burn forecasting, historical plan-variance trends, or automatic release rescheduling in the initial version.
- Changing the DBOS schedule cadence or scheduled-run orchestration established by `scheduled-epic-report`.
- Changing iOS or Android application code.

## Capabilities

### New Capabilities

- `epic-plan-extraction`: Read, validate, map, and normalize authoritative Epic Plan structures into provenance-bearing plan contexts while protecting source tabs.
- `plan-aware-epic-analysis`: Reconcile normalized plan context with Jira epic actuals and present development sprint/time, target release, optional API deployment, release gates, alignment state, and diagnostics.

### Modified Capabilities

- `tdt-sheets-library`: Add a public, typed, read-only grid snapshot operation for the SDK backend so consumers can obtain selected grid cell values, merge ranges, sheet identity, locale, and timezone through `SheetsClient` without reaching into private backend or raw Google service objects. Unsupported backends fail explicitly.

The change consumes the existing official `scheduled-epic-report` behavior without changing its requirements. Older active epic-report generation and presentation changes remain separate; this change adds a new planning input and analysis domain rather than reopening their collection or blocking-analysis scope.

## Impact

- **`jira-epic-report`**: configuration, plan models/parser/matcher, analysis orchestration, report model, spreadsheet reporter, CLI/scheduled-run behavior, tests, README, and configuration documentation.
- **`tdt-sheets` / Google Sheets API**: additive public `SheetsClient.read_grid_snapshot(...)` capability backed by a bounded `spreadsheets.get` read on the SDK backend; no new external dependency is expected.
- **`~/.tdt/epic-report-config.toml`**: optional `[epic_plan]` configuration and explicit per-epic activity mappings.
- **Epic report workbook**: `Epic Plan` remains stakeholder-owned input; `Delivery Plan Analysis` becomes managed output. Generated-sheet synchronization must distinguish managed output tabs from protected/unmanaged tabs.
- **Scheduler container**: existing bind-mounted `jira-epic-report` code and credentials are reused; no schedule manifest or DBOS workflow contract change is expected.
- **Mobile apps**: no direct code or release-process change; their release plan is surfaced as reporting context only.
