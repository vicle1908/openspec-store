# Jira Daily Reports — JQL Pagination Fix (Silent Data Loss)

**Status:** Draft
**Date:** 2026-06-16
**Author:** lekhanhvinh
**Predecessor:** `jira-person-capacity-worklog-concurrency` (which fixed the same bug in `person_worklog_source._search_jql_issues`)

---

## Why

`jira-person-capacity-worklog-concurrency` (commit `46e9ddf`) fixed an
**infinite-loop / data-loss bug** in the worklog JQL fetch path:
`person_worklog_source._search_jql_issues` was using a `startAt`-based loop
against the new `/rest/api/3/search/jql` endpoint (deployed by Atlassian on
2026-05-21), which silently ignores `startAt` and signals end-of-results via
`isLast: true` and `nextPageToken`. The fix replaced the loop with a
`nextPageToken` cursor following `isLast` (per `PatchedJira.jql()`).

**However, two sibling helpers in `jira-daily-reports` still have the same
bug class** — they call `jira.jql(...)` exactly once and return the first
page:

- `src/jira_daily_reports/client.py::jql_search` (line 29)
- `src/jira_daily_reports/reports/base.py::ReportBase._search` (line 46)

`jql_search` is the public JQL helper. `ReportBase._search` is the base
class used by **12 daily reports** (`wip_age`, `cycle_time`, `code_review`,
`missing_info`, `blocked`, `standup`, `velocity`, `wip`, `priority`,
`sprint_health`, `platform`, plus the implicit base). Each calls
`self._search(jql, fields=..., max_results=N)` with `N ∈ {100, 200}` and
trusts the result is the **complete** set.

The bug is **silent data loss**: when a JQL matches more than `max_results`
issues (common for any non-trivial sprint with >100 in-flight tickets, or
the `velocity` report which scans current+previous sprints), the report sees
only the first page and emits a misleading partial view. The bug does not
hang (unlike the worklog-mode predecessor), so it has been shipping partial
data for every daily run since the endpoint migration.

## What Changes

- Add a single internal helper `_jql_paginated(jira, jql, *, fields, limit,
  page_size=100)` in `src/jira_daily_reports/client.py` that loops over
  `jira.jql(...)` calls following `nextPageToken` / `isLast` and returns a
  **deduplicated** `list[dict[str, Any]]` of all matching issues. Termination
  rules mirror `person_worklog_source._search_jql_issues` exactly:
  empty page, `isLast: true`, missing token after token-based paging, or
  `page_new_count == 0` (defensive).
- Rewrite `jql_search` and `ReportBase._search` to delegate to
  `_jql_paginated`. Public signatures unchanged: `jql_search(jira, jql, *,
  fields, max_results)` returns the full set; `ReportBase._search(jql,
  fields, max_results)` likewise. The `max_results` parameter is renamed
  semantically to **page size** internally — it controls the per-call
  `limit`, not the cap on total results.
- Add a `value`, `default=100` keyword for `max_results` to be honored
  (preserved). Default page size is 100 to match the prior implicit behavior.
- Add 8 new unit tests in `tests/test_client_delivery_schedule.py` and
  `tests/test_reports_pagination.py` (new file): single page, two pages via
  token, three pages, `isLast: True` after page 1, `isLast: None` with
  missing token (defensive stop), duplicate-key dedup across pages, empty
  page, non-dict response handling, and the existing "non-dict response"
  path through `jql_search`.
- Update `.agents/skills/jira-daily-reports/SKILL.md` with a new
  `## JQL pagination contract` section that codifies the rule for all
  future helpers and reports: "Jira Cloud's `/rest/api/3/search/jql`
  paginates via `nextPageToken` and signals end-of-results with
  `isLast: true`. The `startAt` parameter is silently ignored. Every
  `jira.jql(...)` call site MUST loop on `nextPageToken` and check `isLast`."
- Add a new capability `jira-daily-reports` spec (`spec.md`) with a
  `JQL pagination` requirement codifying the contract.

**No breaking changes.** Public signatures of `jql_search` and
`ReportBase._search` are preserved. The new behavior is strictly additive:
report outputs now contain the full result set instead of the first page.

## Capabilities

### New Capabilities
- `jira-daily-reports`: A new `JQL pagination` requirement codifies that
  every `jira.jql(...)` consumer in `jira-daily-reports` MUST follow the
  `nextPageToken` / `isLast` cursor protocol and MUST NOT trust a single
  page to be the full result.

### Modified Capabilities
- *(none)*

## Impact

- **`jira-daily-reports`** (only):
  - `src/jira_daily_reports/client.py`: add `_jql_paginated`, rewrite
    `jql_search` to delegate.
  - `src/jira_daily_reports/reports/base.py`: rewrite `ReportBase._search`
    to delegate to `jira_daily_reports.client._jql_paginated`.
  - `tests/test_client_delivery_schedule.py`: update 2 existing
    `jql_search` tests to match the new (paginated) call shape; add 1 test
    for multi-page response handling.
  - `tests/test_reports_pagination.py` (new file): add 7 tests for
    `ReportBase._search` covering single page, multi-page via token,
    `isLast`, dedup, empty page, non-dict, and a happy-path end-to-end
    through a real `Report` subclass.
  - `.agents/skills/jira-daily-reports/SKILL.md`: add `JQL pagination
    contract` section.

- **`tdt-core`**: **unchanged**. `PatchedJira.jql()` is already correct;
  the bug is purely consumer-side in `jira-daily-reports`.
- **`jira-epic-report`**: **unchanged** — its `_jql_paginated` helper in
  `epic_report/collector.py` (lines 490-557) already implements the same
  cursor loop and was the reference implementation.
- **`jira-skill`**: **unchanged** — does not call `jira.jql()` directly.
- **Operational**: each daily report now scans the full Jira result set
  (was capped at 100 or 200 depending on the report). For typical
  project sizes this is a non-event (<5% of projects exceed a single
  page of 100), but for the high-volume `velocity` and `wip` reports
  the data is now correct. No new infra, no new deps.

### Non-goals
- **No async refactor.** The 12 daily reports are batch-style and run on
  the DBOS scheduler. Cursor pagination is a small in-process loop, not
  a hot path.
- **No adaptive rate limiting.** The current `PatchedJira.jql()` already
  handles 429 with backoff inside the client; cursor pagination does
  not change the per-call rate.
- **No rewrite of `person_worklog_source` pagination.** That helper was
  already fixed in `jira-person-capacity-worklog-concurrency`; this change
  does not touch it.

### Out-of-scope
- Adding pagination to `webhook-receiver` / `ai-review` Jira consumers
  (they do not call `jira.jql()` directly; they use `jira.issue(...)`
  per key).
- Replacing the 12 daily reports' JQL queries with a unified batch
  endpoint. (Atlassian does not expose one; out of scope.)
