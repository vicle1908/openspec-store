# Research Notes — Sprint Ecosystem Gap Closure

## Validation performed in this pass

- Confirmed `jira-sprint-spreadsheet-ssot` is complete via `openspec status --change jira-sprint-spreadsheet-ssot --json`: 33/33 tasks complete, state `all_done`.
- Confirmed `jira-dashboard-automation` is complete via `openspec list --json`: 34/34 tasks complete.
- Confirmed `kbs-extra-sheets-and-linked-tickets` is complete via `openspec list --json`: 60/60 tasks complete.
- Reviewed active sprint report implementation in `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py`.
- Reviewed shared dashboard implementation in `jira-skill/src/jira_skill/dashboard/service.py` and `layout.py`.
- Reviewed `jira-daily-reports/src/jira_daily_reports/delivery/jira_dashboard.py`, which delegates dashboard primitives to `jira_skill.dashboard`.
- Reviewed active OpenSpec contracts for sprint spreadsheet SSOT, KBS sprint links/agile creation/end-to-end orchestration, and dashboard automation.

## Current findings

1. The sprint report path is `jira-daily-reports`, not `jira-skill.sprint.reports`.
2. The sprint report consumes `RESOLVED_SCOPE_KEYS`, `RESOLVED_FILTER_ID`, `RESOLVED_BOARD_ID`, `RESOLVED_SPRINT_ID`, and `RESOLVED_PROJECT_KEY` when provided, then falls back to spreadsheet/title lookup and finally configured filter/board ids.
3. The report builds issue JQL from resolved keys when present; otherwise from bucket keys; otherwise from `filter = <filter_id>`.
4. The per-sprint dashboard logic in `SprintReportSheetReport._resolve_sprint_dashboard()` currently find-or-creates a dashboard shell and stores `dashboard_id` for links. It does not call the shared dashboard build/rebuild path from the report constructor.
5. Full dashboard build/rebuild/validate is available through `jira-skill.dashboard` and through `jira-daily-reports.delivery.jira_dashboard.build_dashboard()`, but the sprint report path does not automatically populate gadgets in the reviewed code.
6. Therefore the follow-up contract should force a decision: either build/validate configured per-sprint dashboards in the pipeline or explicitly label the report-created dashboard as link-only and route build requests to `jira-skill dashboard`.

## Follow-up change created

- Change: `jira-sprint-ecosystem-gap-closure`
- Capability: `sprint-ecosystem-alignment`
- Purpose: close the remaining contract/docs/validation gaps without reopening completed changes.
