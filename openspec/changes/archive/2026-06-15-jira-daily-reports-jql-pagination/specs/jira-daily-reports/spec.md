# Jira Daily Reports — Specification

**Capability:** jira-daily-reports
**Status:** New
**Date:** 2026-06-16
**Version:** 1.0

This is the **initial** spec for the `jira-daily-reports` repo as a
codified capability. It captures the cross-cutting contracts that all
Jira-facing code in the repo MUST follow. Existing per-report specs
(e.g. `person-capacity-worklog-mode`) remain authoritative for
report-specific behavior.

---

## ADDED Requirements

### Requirement: JQL pagination

Every `jira.jql(...)` call site in `jira-daily-reports` SHALL follow the
`/rest/api/3/search/jql` cursor pagination protocol: the response is
**not** guaranteed to be the complete result set; the caller MUST loop
on `nextPageToken` and SHALL stop when (any of) `isLast: true` is
present, the page is empty, `nextPageToken` is missing after a
token-based page was previously returned, or no new issues were seen
on the current page (defensive).

The shared helper `jira_daily_reports.client._jql_paginated` implements
this contract. New code SHALL use this helper instead of calling
`jira.jql(...)` directly. The two existing entry points
(`jql_search` in `client.py` and `ReportBase._search` in
`reports/base.py`) delegate to it.

The `limit` parameter on `_jql_paginated` controls the per-call page
size, not a cap on the total result set.

#### Scenario: Single-page response returns all matching issues
- **WHEN** the JQL response contains `{"issues": [...], "isLast": true}`
  on the first call
- **THEN** the helper SHALL return all issues from that single page
- **AND** `jira.jql` SHALL be called exactly once

#### Scenario: Multi-page response follows the cursor
- **WHEN** page 1 contains `{"issues": [...], "isLast": false, "nextPageToken": "tok-1"}`
- **AND** page 2 contains `{"issues": [...], "isLast": true}` (or
  `nextPageToken` is absent)
- **THEN** the helper SHALL return the union of both pages
- **AND** the second call SHALL pass `next_page_token="tok-1"`

#### Scenario: isLast stops the loop
- **WHEN** a page contains `isLast: true`
- **THEN** the helper SHALL stop after that page
- **AND** it SHALL NOT issue another `jira.jql(...)` call

#### Scenario: Missing token after token-based paging stops the loop
- **WHEN** page 1 contains `nextPageToken: "x"`
- **AND** page 2 contains `isLast: false` but `nextPageToken: null`
- **THEN** the helper SHALL stop after page 2
- **AND** it SHALL return the union of both pages

#### Scenario: Empty page stops the loop
- **WHEN** a page contains `"issues": []`
- **THEN** the helper SHALL stop after that page
- **AND** it SHALL return the union of all prior pages (which may be
  empty)

#### Scenario: Duplicate keys across pages are deduplicated
- **WHEN** a key appears in more than one page
- **THEN** the helper SHALL return each key exactly once
- **AND** the dedup SHALL be tracked via an in-memory `seen_keys` set
  scoped to the call

#### Scenario: Non-dict response stops the loop defensively
- **WHEN** `jira.jql(...)` returns a value that is not a `dict`
  (e.g. `None` on a transient error that was caught upstream)
- **THEN** the helper SHALL stop the loop
- **AND** it SHALL return the issues collected so far (which may be
  empty)

#### Scenario: page_size controls the per-call limit
- **WHEN** the caller passes `limit=50` to `_jql_paginated`
- **THEN** the per-call `jira.jql(...)` SHALL be invoked with
  `limit=50` as the `maxResults` (or equivalent) parameter
- **AND** the total result set SHALL NOT be capped at 50 — the
  helper SHALL continue paginating until exhaustion

#### Scenario: A log line is emitted per page
- **WHEN** the helper is in a multi-page run
- **THEN** it SHALL emit a `client_jql_paginate jql=... fetched=N token=set|none`
  INFO log line once per loop iteration
- **AND** operators SHALL be able to confirm pagination progress from
  the `jira-run-all` log output

### Requirement: No direct `jira.jql(...)` call sites in new code

New report code SHALL call `jira_daily_reports.client._jql_paginated`
(or the `jql_search` / `ReportBase._search` public helpers that
delegate to it) instead of calling `jira.jql(...)` directly. Existing
direct call sites outside `jira_daily_reports` (e.g.
`person_worklog_source._search_jql_issues`, `epic_report.collector`)
are acceptable as long as they implement the same cursor protocol
locally; they are owned by their respective OpenSpec changes.

#### Scenario: A new report uses the public helper
- **WHEN** a new `ReportBase` subclass needs to query Jira
- **THEN** it SHALL call `self._search(jql, ...)` (the public base
  class method)
- **AND** it SHALL NOT instantiate a direct `jira.jql(...)` call

#### Scenario: A direct `jira.jql(...)` call is caught in code review
- **WHEN** a PR introduces a new `jira.jql(...)` call site in
  `jira-daily-reports`
- **THEN** the reviewer SHALL require it to be replaced with a call
  to `jql_search` / `_jql_paginated` / `ReportBase._search`
- **AND** the reviewer SHALL cite this requirement as the rationale
