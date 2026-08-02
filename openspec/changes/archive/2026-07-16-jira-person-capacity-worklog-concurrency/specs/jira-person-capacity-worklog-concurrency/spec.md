# jira-daily-reports Person Worklog Concurrency

## ADDED Requirements

### Requirement: Concurrent Worklog Fetching

The `fetch_person_worklogs()` function in `person_worklog_source.py` SHALL fetch worklogs for multiple issues concurrently using `ThreadPoolExecutor` with configurable `WORKLOG_FETCH_CONCURRENCY` (default 8). Iteration order SHALL be preserved (submission order, not completion order) to maintain the first-observed `account_id` invariant.

---

#### Scenario: Concurrent fetch preserves account_id invariant

- **WHEN** `fetch_person_worklogs` is called with `concurrency=N`
- **THEN** the first-observed `account_id` for each display name SHALL be preserved as in the serial execution
- **AND** no two worklog fetches shall share state

---

#### Scenario: Concurrency respects worklog retry semantics

- **WHEN** a worklog fetch raises `HTTPError 429`
- **THEN** the retry logic SHALL be applied within the thread pool
- **AND** the call SHALL re-raise after exhaustion

---

#### Scenario: Empty issue list skips pool creation

- **WHEN** the issue list is empty
- **THEN** no `ThreadPoolExecutor` SHALL be constructed
- **AND** the function SHALL return `[]` without error
