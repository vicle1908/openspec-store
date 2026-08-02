# Jira Person Capacity Worklog Mode - Proposal

## Why

The current `Person Capacity` tab in the sprint workbook is computed by iterating over Jira issues in a JQL-defined bucket (sprint or saved filter) and reading each issue's worklogs. This ticket-first approach has a structural limitation: a person's logged time is only visible if **at least one of the issues they worked on** is in the bucket. Worklog author activity on issues outside the bucket is invisible.

The team needs the report to reflect **what each person actually worked on** in the window, not what happened to be inside an issue-scope bucket. Live workspace data shows assignee and worklog author frequently diverge, so any ticket-scope view hides effort attribution.

## What Changes

- Replace the ticket-first `_build_person_capacity` calculation in `jira-daily-reports` with a **person-first** JQL query keyed by `worklogAuthor in (<roster accountIds>)`.
- Load the roster of people from the existing `Person Capacity Mapping` sheet tab and use that as the JQL scope, not the issue bucket.
- Aggregate to per-person rows showing worked-ticket count, total logged time, and per-day logged time.
- Surface unmapped worklog authors as a reconciliation block below the per-person block.
- Drop the legacy `Assigned Tickets` and `Original Estimation Total` columns (and the `JIRA_FILTER_ID` requirement that supported them) in v1.
- Add 429/timeout retry with exponential backoff for the new JQL and `issue_get_worklog` calls.

This is a **replace, not an opt-in**. There is no second CLI command and no feature flag in v1. Re-adding ownership metrics is deferred to a follow-up change.

## Capabilities

### New Capabilities

- `person-capacity-worklog-mode`: Person-first worklog query for the `Person Capacity` sheet tab, with activity-only columns and a reconciliation block for unmapped authors.

### Modified Capabilities

- `person-capacity-report`: The existing v1 capability's column set shrinks. `Assigned Tickets` and `Original Estimation Total` are removed. The capability now exists as the historical v1 contract; the active contract lives in `person-capacity-worklog-mode`.
- `person-capacity-planning-alignment`: The v2 planning-merged columns (`Planned Issues`, `Planned Tasks`, `Planned Estimate`) are removed from the `Person Capacity` tab in v1 but remain a historical reference for the `Sprint Report` tab.

## Impact

- `jira-daily-reports`:
  - NEW: `src/jira_daily_reports/person_worklog_source.py` - JQL-first fetcher, roster loader, aggregate types.
  - MODIFIED: `src/jira_daily_reports/reports/sprint_report_sheet.py` - `_build_person_capacity` rewritten, `build_person_sheet_rows` updated for the activity-only column layout.
  - MODIFIED: `src/jira_daily_reports/delivery/tdt_sheet.py` - column widths adjusted for the new tab layout; pre-flight check no longer requires `JIRA_FILTER_ID`.
  - NEW: `tests/test_person_worklog_source.py` - unit tests.
  - NEW: `tests/test_sprint_report_sheet_person_capacity.py` - integration tests for the new contract.
  - MODIFIED: `tests/test_sprint_report_sheet.py` and `tests/test_tdt_sheet.py` - aligned to the activity-only contract.
  - MODIFIED: `.agents/skills/jira-daily-reports/SKILL.md` - Day-1 documentation update.
- `tdt-core`:
  - UNCHANGED: `src/tdt_core/clients/jira.py` - `PatchedJira.jql()` and `issue_get_worklog()` are reused as-is.
- `jira-skill`:
  - UNCHANGED: `CapacitySignal` Pydantic model is not wired into the v1 activity-only flow. Deferred to a follow-up change.
