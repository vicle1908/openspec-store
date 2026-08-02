# JQL Pagination Fix — Design

## Context

The Atlassian Cloud `/rest/api/3/search/jql` endpoint (the only JQL search
endpoint available since the legacy `/search` was removed on 2026-05-21)
paginates via an opaque `nextPageToken` cursor and signals end-of-results
with `isLast: true`. The endpoint **silently ignores** the legacy
`startAt` parameter.

The `jira-daily-reports` repo has two consumer-side helpers that still
treat a single `jira.jql(...)` response as the complete result set:

1. `src/jira_daily_reports/client.py::jql_search` — public helper used by
   12+ daily reports via `ReportBase._search`.
2. `src/jira_daily_reports/reports/base.py::ReportBase._search` — base
   class method used by 12 report subclasses (one call each, with
   `max_results ∈ {100, 200}`).

A separate helper, `person_worklog_source._search_jql_issues`, was fixed
in `jira-person-capacity-worklog-concurrency` (commit `46e9ddf`). The
fix was to follow the `nextPageToken` cursor and check `isLast`. This
change applies the same fix to the two remaining helpers.

## Goals / Non-Goals

**Goals:**
- Fix silent data loss in 12 daily reports and the public `jql_search`
  helper.
- Preserve public signatures (no breaking changes for callers).
- Pass the existing test suite unchanged + add ≥8 new tests for the
  pagination contract.
- Codify the rule in an OpenSpec capability so future code review can
  flag violations.

**Non-Goals:**
- Changing `tdt-core` (already correct).
- Async / asyncio refactor.
- Adaptive rate limiting.
- JQL chunking changes.
- Changing the 12 reports' JQL queries.

## Decisions

### 1. Single shared helper `_jql_paginated` in `client.py`

**Decision:** Add `_jql_paginated(jira, jql, *, fields, limit, page_size=100)`
in `src/jira_daily_reports/client.py`. Both `jql_search` and
`ReportBase._search` delegate to it.

**Rationale:**
- Single source of truth — one cursor loop to test, one set of
  termination rules to maintain.
- Matches the pattern already used in `epic_report/collector.py` (the
  reference impl) and in `person_worklog_source._search_jql_issues`.
- Keeps the bug fix mechanical: replace single-call bodies with
  `_jql_paginated` calls.

**Alternatives considered:**
- *Inline the loop in both call sites* — rejected: 2 copies of the
  termination logic, drift risk.
- *Make `ReportBase._search` and `jql_search` aliases of each other* —
  rejected: `ReportBase._search` is a method (uses `self`),
  `jql_search` is a function. Different shapes, same helper.

### 2. Termination rules: identical to `person_worklog_source`

**Decision:** Copy the termination conditions from
`person_worklog_source._search_jql_issues` exactly. Four conditions
(OR): empty page; `isLast: true`; missing `nextPageToken` after a
token-based page returned; `page_new_count == 0` defensive guard.

**Rationale:** Consistency. The two helpers in `jira-daily-reports` and
`epic_report` should not disagree on edge cases. If a future bug fix
is needed, it lands in one place and propagates.

### 3. Dedup across pages via `seen_keys`

**Decision:** Track `seen_keys: set[str]` across pages and skip any
issue whose `key` was already collected. This is defensive against
the (rare but observed) server-side dedup glitch where the same page
is returned twice under a stale token.

**Rationale:** A no-cost safety net. The dedup cost is O(1) per issue
via set membership; without it, the caller would silently get duplicate
issues in their report.

### 4. `max_results` keeps its current meaning (page size)

**Decision:** The `max_results` parameter on `jql_search` and
`ReportBase._search` continues to control the per-call `limit` (i.e.
the page size). It is NOT a cap on total results — that would be a
silent data loss bug. We add a docstring note clarifying this.

**Rationale:** Renaming would break callers. Keeping the name but
updating the docstring is the minimum-friction fix.

**Alternatives considered:**
- *Add a new `cap` kwarg and keep `max_results` as the cap.* Rejected:
  callers don't pass it, so the bug never shows up. The correct
  semantics is "page size", and the public name is already misleading
  in the new endpoint world.

### 5. Test surface: 8 new tests across 2 files

**Decision:**
- 3 new tests in `tests/test_client_delivery_schedule.py::TestClient`
  to cover `jql_search` pagination directly (multi-page via token,
  `isLast: True` after page 1, dedup).
- 5 new tests in a new file `tests/test_reports_pagination.py` to
  cover `ReportBase._search` through a concrete subclass (`StandupReport`
  or a test-only `StubReport`): single page, multi-page, `isLast: None`
  with missing token, empty page, and a happy-path end-to-end check
  that the full result is returned.

**Rationale:** 12 reports share the base; testing through a stub is
cheaper than 12 integration tests. The end-to-end test confirms the
helper is wired in correctly without testing the reports themselves.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Infinite loop if a future server returns token + isLast=False + new issues | Low | Defensive `page_new_count == 0` guard + log warning |
| Reports now scan more issues → wall-clock increase | Low–Med | Page size 100 keeps per-call latency low; total scan is bounded by total results, which is correct behavior |
| Dedup drops legit issues with the same key from different pages | Very Low | `seen_keys` set membership is per-fetch; a second copy of a key in a later page is rare and a dedup glitch, not a legitimate case |
| Test for `isLast: None` + missing token is fragile | Low | Pin the expected log warning + cap iteration count via the defensive guard |
| `page_size` default mismatch with existing report calls | Low | Default is 100, matching the smallest of the existing 3 values; all 12 reports continue to work unchanged |

## Test strategy

- Unit tests use `MagicMock` for `jira.jql` to return scripted pages.
- No live Jira calls in tests (CI doesn't have credentials).
- The 2 existing `jql_search` tests (in `test_client_delivery_schedule.py`)
  are updated to use a `MagicMock` that returns a single-page response —
  the assertion shape changes from "called once" to "called once with the
  expected kwargs" (no behavioral break).
- A new test `test_reports_pagination.py::TestReportBaseSearch` exercises
  the helper through a test-only `ReportBase` subclass to confirm the
  base class wiring is correct.

## Rollout

- Single commit on `jira-daily-reports/main`.
- No infra changes; no new env vars; no migration step.
- Daily reports immediately produce the full result set on the next
  scheduled run.
- OpenSpec change is small and self-contained — `archive` is appropriate
  after the in-session verification (tests + lint + mypy + live probe
  of one report).
