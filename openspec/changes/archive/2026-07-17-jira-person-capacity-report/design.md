# Jira Person Capacity Report - Design

## Context

`jira-daily-reports` currently produces a ticket-centric sprint sheet. It is strong for status and risk, but weak for person-level capacity tracking. Live workspace data shows assignee and worklog author frequently diverge, so one-dimensional person attribution creates incorrect conclusions.

Constraints:

- Jira board behavior may be Kanban-like (`Sprint: N/A`), so date windows cannot always depend on sprint metadata.
- Worklogs can be sparse and/or paginated.
- Existing sprint report semantics (`missing` vs `unavailable`) and stable sheet writing behavior must be preserved.
- Existing Sprint Report tab must remain backward-compatible.
- Live data in this workspace shows assignee and worklog author diverge frequently, so the design must not assume one person = one ticket owner.

Stakeholders:

- Engineering managers and tech leads tracking team capacity
- Individual contributors validating workload and logged activity
- Program managers requiring a daily person-level effort view

## Live Research Findings (2026-05-28)

From live probes against spreadsheet `1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8` and Jira scope built from the 3 bucket tabs:

- Bucket scope: 65 issue keys; 64 explicit target statuses.
- Jira issues loaded for scope: 65.
- Worklogs with positive duration: 100 entries.
- Assignee vs worklog-author mismatch: 77/100 logs (77.0%).
- Unique assignees: 21; unique worklog authors: 21.
- Authors not present in assignee set: 8.
- Issues with inline worklog truncation signal (`worklog.total > len(worklogs)`): 2.
- Board capability probe (`board 1067`): sprint metadata unavailable in API response.
- Operational auth finding: unattended real writes should use direct Google Sheets API service-account credentials loaded from `GOOGLE_SERVICE_ACCOUNT_PATH` or `GOOGLE_APPLICATION_CREDENTIALS`.

Implication: person-capacity reporting must separate ownership from activity and must include complete worklog retrieval + rolling-window fallback.


## Live Verification Findings (2026-05-29)

Real operation was rerun against spreadsheet `1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8` with service-account Google Sheets auth and live Jira data:

- `sprint-sheet` completed and wrote both tabs from the same run.
- `Sprint Report` gid: `2031584890`.
- `Person Capacity` gid: `508115400`.
- Included tickets: 65.
- Target status result: 6 met, 58 behind, 1 rejected.
- Person rows: 30 people.
- Assigned tickets: 65; worked tickets: 68.
- Logged total: 289h 38m; ownership total: 428h.

Operational rule: verification must read the sheet back after a write. CLI success alone is insufficient because auth/session drift can leave stale sheet content undetected.

## Goals / Non-Goals

**Goals:**

- Add a person-centric worksheet tab in the same spreadsheet.
- Show per-person owned workload (assignee) and per-person activity (worklog author) explicitly.
- Include per-person original estimate totals from `timeoriginalestimate` /
  `timetracking.originalEstimateSeconds` only.
- Include per-person logged time per day across a defined date window.
- Keep one-snapshot extraction for bucket scope and one report run for both ticket and person tabs.

**Non-Goals:**

- Replacing or removing the existing Sprint Report tab.
- Solving historical worklog data beyond the selected date window.
- Implementing billing/payroll-grade timesheet auditing.
- Changing Jira-side workflows, roles, or assignment policy.

## Decisions

1. **Two-metric person model (ownership vs activity)**
   - Ownership metric uses issue assignee.
   - Activity metric uses worklog author.
   - Rationale: avoids false attribution when authors differ from assignees.

2. **Single additional tab, person-first**
   - Add `Person Capacity` tab (name configurable via env var with sensible default).
   - Rationale: simple adoption, minimal workbook complexity, preserves existing stakeholder flow.

3. **One report snapshot for consistency**
   - Reuse existing bucket-scope snapshot and Jira issue retrieval.
   - Build both ticket and person views from the same in-memory issue set.
   - CLI sheet mode SHALL not pre-run the report before the sheet writer.
   - Rationale: prevents drift and mismatch between tabs.

4. **Date-window fallback strategy**
   - Preferred: sprint start/end when available.
   - Fallback: rolling 14-day window (`PERSON_CAPACITY_WINDOW_DAYS=14`).
   - Rationale: current workbook already tracks two-week sprint windows, and board sprint metadata is not always available in this workspace.
   - Timezone: bucket days using the spreadsheet timezone from the workbook unless an explicit override is added later.

5. **Canonical person identity**
   - Use `accountId` as the canonical key when available.
   - Display a human-readable label derived from `displayName`, with deterministic fallback to `accountId`/`Unassigned`.
   - Do not suffix `accountId` in the visible sheet in v1; keep it internal for grouping stability.
   - Rationale: avoid fragmenting one person into multiple rows due to naming variance while keeping the sheet readable.

6. **Keep report semantics explicit**
   - Show clearly labeled columns for:
     - Assigned Tickets / Owned Estimate Total (assignee-based)
     - Worked Tickets / Logged Total (author-based)
     - Daily logged columns (author-based)
   - Rationale: prevents confusion over metric origin.

7. **Original-estimate-only capacity source**
   - Sprint and person capacity estimation SHALL read only Jira original estimate:
     `timeoriginalestimate` or `timetracking.originalEstimateSeconds`.
   - Story-point custom fields and remaining estimate (`timeestimate`) SHALL NOT be
     used as capacity estimate fallbacks.
   - Rationale: the sprint planning sheet writes effort hours into original
     estimate, so capacity totals must stay in one unit system.

8. **Runtime configuration comes from `~/.tdt/.env`**
   - `JIRA_FILTER_ID` and `JIRA_BOARD_ID` are required runtime inputs from the
     shared typed Jira config.
   - Person timezone resolves from spreadsheet metadata first, then
     `PERSON_CAPACITY_TIMEZONE` / `TDT_TIMEZONE` / `TZ`, then host timezone,
     then `UTC`.
   - Rationale: avoids stale workspace literals as filters/boards rotate per sprint.

9. **Per-person totals are attribution totals, not global totals**
   - If multiple people work on the same issue, that issue can contribute to multiple person rows.
   - Rationale: the sheet is a capacity view, not a conservation-of-estimates ledger.

10. **v1 scope is lean**
   - Do not add variance columns or a raw audit tab in the first execution-ready version.
   - Rationale: keep the first ship focused on reliable capacity visibility and validation.

## Risks / Trade-offs

- **[Risk] Assignee and author mismatch creates interpretation confusion** → Add clear column labels and glossary row in tab header.
- **[Risk] Sparse worklogs make daily trends look empty** → Include coverage counters and explicit "no logs in window" cases.
- **[Risk] Worklog pagination or API limits miss entries** → Implement paginated retrieval path and tests for multi-page aggregation.
- **[Risk] Timezone/date bucketing errors** → Normalize daily buckets using Jira `started` timestamp date in a documented timezone rule.
- **[Risk] Large windows produce very wide sheets** → Cap default window and allow override by env var.
- **[Risk] Google Sheets auth is misconfigured during live ops** → Use direct service-account credentials via the Google Auth Python library and fail with an actionable credentials-path error.

## Migration Plan

1. Add person-capacity aggregation helpers and tests.
2. Add person-capacity sheet row builder and writer.
3. Wire `sprint-sheet` flow to write the extra tab from the same run.
4. Validate with live spreadsheet:
   - ticket-tab counts unchanged
   - person-tab totals reconcile with source worklogs
5. Update docs/skills/specs.

Rollback:

- Disable person-capacity tab write behind config toggle/env var and continue ticket-tab write only.

## Finalized Decisions

- Visible person labels stay human-readable only in v1.
- Variance columns are deferred.
- No raw audit tab in v1.
