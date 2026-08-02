# Jira Person Capacity Report - Proposal

## Why

The current sprint report is ticket-centric, but the practical question for planning is person-centric: who owns how much work, and how much time did they actually log each day? Live Jira samples in this workspace show worklog authors often differ from assignees, so a ticket-only view can mislead capacity planning and obscure actual effort attribution.

## What Changes

- Add a new person-centric report for Jira sprint work.
- Generate a new worksheet tab focused on people, not tickets.
- Aggregate rows by canonical person identity across both assignee and worklog-author records.
- Show owned work using assignee-based metrics and actual activity using worklog-author-based metrics.
- Include original estimation totals and daily logged time columns per person.
- Retrieve capacity estimates only from Jira original estimate (`timeoriginalestimate`
  or `timetracking.originalEstimateSeconds`); do not use story-point custom fields
  or remaining estimate as fallbacks.
- Keep the existing sprint summary tab intact and separate from the new person view.
- Keep the person tab additive: a single issue may contribute to more than one person row when multiple people touched it.
- Ship the first version as an execution-ready, lean report: no variance columns, no raw audit tab.

## Capabilities

### New Capabilities

- `person-capacity-report`: Person-centric capacity reporting with per-person owned estimate, logged time, and daily activity columns.

### Modified Capabilities

- None.

## Impact

- `jira-daily-reports`: new CLI/report path, new sheet-tab writer, shared aggregation helpers, and updated tests.
- `work_item_fields.py`: likely needs additional helpers for canonical person identity and daily worklog aggregation.
- `README.md`, skill docs, and OpenSpec docs: must describe the new person-centric report and the ownership-vs-activity distinction.
- Google Sheets workbook layout: adds a new tab for person capacity tracking without replacing the existing sprint summary tab.
