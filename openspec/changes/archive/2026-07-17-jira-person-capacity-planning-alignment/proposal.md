## Why

The current `Person Capacity` tab is Jira-only: it groups Jira assignees and worklog authors, but it does not use the sprint workbook's member mapping or current-sprint team activity tabs where planned effort is actually maintained. Live research on spreadsheet `1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8` shows the workbook has a canonical member-key mapping and planned-effort rows that must be reconciled with Jira ownership and worklog activity before the report can answer capacity questions reliably.

## What Changes

- Scope this change to the `Person Capacity` worksheet/report semantics only; the existing `Sprint Report` ticket extraction and target-vs-actual logic remain unchanged except that their bucket scope is reused as an input.
- Add a mapping-sheet-driven person identity layer using a writable `Person Capacity Mapping` tab as the primary workbook identity bridge, with `Dropdown Keys - Do Not Delete -` (`MEMBERS` → `JIRA Nick Name`) as the protected fallback.
- Promote the existing bucket-tab extraction result into a shared sprint-ticket scope object used by both `Sprint Report` and `Person Capacity` in the same run.
- Expand that seed scope through Jira subtask and issue-link traversal (`Blocks` / blocked-by, plus split-style links where configured) so Jira fetch sees the fuller ticket graph while planning totals still key off the original bucket seed set.
- Reuse and/or extract common spreadsheet primitives already present in the ecosystem (`jira-kanban-from-spreadsheet` reader/parser/JQL patterns) instead of creating one-off person-capacity parsing code.
- Add a current-sprint planning crawler for the live team activity tabs (`Kelvin's Team Activites New`, `Andrew's Team Activites New`, `VuVuong's Team Activites New`) that reads detail rows instead of stale summary formulas.
- Fill `Person Capacity` only from the same sprint ticket set extracted for `Sprint Report`; planning rows outside that ticket set are reconciliation warnings, not capacity totals.
- Extend `Person Capacity` from two ledgers to three ledgers:
  - workbook planned capacity from team activity rows,
  - Jira ownership from issue assignee + original estimate,
  - Jira actual activity from worklog authors.
- Merge all person rows by workbook `member_key` when possible, with explicit fallback buckets for unmapped Jira people and unassigned planning effort.
- Add a visible reconciliation/data-quality section that reports mapping gaps, scope mismatches, summary-formula drift, and unassigned planning rows instead of silently hiding them.
- Define a Google Sheets hyperlink policy for Jira ticket references:
  - `Sprint Report` issue keys remain pure `HYPERLINK(...)` formulas,
  - `Person Capacity` `Worked Ticket Links` becomes the canonical clickable multi-ticket field with one pure hyperlink formula per line,
  - `Daily Ticket Details` becomes a readable diagnostic breakdown rather than relying on mixed inline text-plus-formula fragments in one cell.
- Preserve the existing Jira-only ownership/activity logic as inputs; do not replace Jira worklog aggregation or original-estimate-only rules.

## Capabilities

### New Capabilities

- `person-capacity-planning-alignment`: Mapping-sheet-driven planned capacity crawling and reconciliation for Jira person-capacity reporting.

### Modified Capabilities

- `person-capacity-report`: Extend the existing person capacity report contract so its rows can merge workbook planned effort, Jira ownership, and Jira actual worklog activity by a shared member identity.

## Impact

- `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py`: update only the `person_capacity` summary and `Person Capacity` row rendering; preserve existing sprint ticket extraction and `Sprint Report` behavior.
- `jira-daily-reports/src/jira_daily_reports/delivery/sheet.py`: share one sprint-ticket scope snapshot across `Sprint Report` and `Person Capacity`, then read mapping and team activity tabs before writing `Person Capacity`.
- New helper module, likely `jira-daily-reports/src/jira_daily_reports/planning_sheet_fields.py`, for mapping parsing, current-sprint tab crawling, row inheritance, reconciliation, and tests.
- `tdt-core` or an existing shared workspace library may receive lightweight Google Sheets/value-grid helpers if needed to avoid duplicating logic already implemented in `jira-kanban-from-spreadsheet`.
- `jira-daily-reports/tests/`: add parser, merge, reconciliation, and sheet-row tests.
- `jira-daily-reports/README.md` and `.agents/skills/jira-daily-reports/SKILL.md`: document planned-vs-owned-vs-actual semantics and live verification runbook.
- `tdt-meta/openspec/changes/jira-person-capacity-report/`: remains v1 historical baseline; this change defines v2 behavior.
