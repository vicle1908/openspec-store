# person-capacity-worklog-mode Specification

## Purpose

`person-capacity-worklog-mode` is the capability that defines how the `jira-daily-reports` service fetches worklog data from Jira for person-capacity reporting. It covers JQL-based worklog fetching, display-name keying, trailing-empty-row suppression, retry semantics, and concurrency (added in v1.4).
## Requirements
### Requirement: JQL-first worklog fetch
The system SHALL execute a JQL query of the form `worklogAuthor in (<displayNames>) AND worklogDate >= "<start>" AND worklogDate <= "<end>"` and SHALL filter the returned worklogs to the roster display-name set and to the `[window_start, window_end]` interval on `started`. The fetcher SHALL run each **chunk** (a JQL group of at most `WORKLOG_JQL_CHUNK_SIZE` display names) sequentially. Per-issue worklog fetches **within a chunk** MAY be parallelized; see the `Concurrency` requirement.

#### Scenario: JQL is keyed by worklogAuthor with display names
- **WHEN** the fetcher runs with `display_names = ["Alice N.", "Bob N.", ...]` and a window
- **THEN** it SHALL issue a JQL whose `worklogAuthor in (...)` clause contains exactly those display names (as quoted strings)
- **AND** the `worklogDate` range SHALL match the requested window

#### Scenario: Worklogs outside the window are excluded
- **WHEN** an issue has worklog entries with `started` outside `[window_start, window_end]`
- **THEN** those entries SHALL be excluded from the aggregate

#### Scenario: Worklogs from non-roster authors are excluded
- **WHEN** an issue has worklog entries whose `author.displayName` is not in the roster
- **THEN** those entries SHALL be excluded from the aggregate

#### Scenario: Roster is chunked at 150 display names
- **WHEN** the roster contains more than 150 display names
- **THEN** the fetcher SHALL split the JQL into chunks of at most 150 display names
- **AND** it SHALL run each chunk sequentially (chunks are not parallelized)
- **AND** it SHALL merge the results into a single list of `PersonWorklogAggregate`
- **AND** it SHALL log a `worklog_jql_chunked chunk=N total=M` line for each chunk

#### Scenario: JQL is paginated
- **WHEN** the JQL response indicates more results exist (e.g. `startAt + len(page) < total`)
- **THEN** the fetcher SHALL continue paginating with `startAt` until all results are exhausted
- **AND** it SHALL respect the `PatchedJira.jql()` pagination contract from `tdt_core.clients.jira`

### Requirement: Retry on rate limit and timeout
JQL pagination calls and `issue_get_worklog` calls SHALL retry on retryable failures (HTTP 429, "rate", "timeout", "timed out", "connection") with exponential backoff: 1s, 2s, 4s, capped at 30s, for a maximum of 3 attempts. When the fetcher is configured for concurrency > 1, the retry policy SHALL be applied **per call** (per thread) so that one thread's retry does not block other workers; workers MAY be in different backoff phases simultaneously without compounding.

#### Scenario: Retry succeeds on the second attempt
- **WHEN** the first call to `jira.jql()` raises a `requests.exceptions.HTTPError` whose message contains "429"
- **THEN** `call_with_retry` SHALL sleep for 1s and re-invoke the callable
- **AND** the second attempt result SHALL be returned to the caller

#### Scenario: Retry gives up after max attempts
- **WHEN** all 3 attempts fail with a retryable error
- **THEN** `call_with_retry` SHALL re-raise the last exception
- **AND** it SHALL log a `worklog_jira_retry` warning on each retry

#### Scenario: Non-retryable errors are not retried
- **WHEN** the callable raises an exception whose message does not match the retryable token set
- **THEN** `call_with_retry` SHALL re-raise it immediately without sleeping

#### Scenario: Concurrent retries do not compound
- **WHEN** the fetcher is configured for concurrency > 1
- **AND** multiple workers simultaneously hit a retryable failure
- **THEN** each worker SHALL retry on its own backoff schedule
- **AND** one worker's retry sleep SHALL NOT block other workers from making progress

---

### Requirement: Concurrency
The fetcher SHALL bound the number of in-flight `jira.issue_get_worklog` calls per chunk to a configurable value `WORKLOG_FETCH_CONCURRENCY`. The default SHALL be 8. The value SHALL be read from the `WORKLOG_FETCH_CONCURRENCY` environment variable at module import time using `tdt_core.env.get_int_env`. An unset value SHALL fall back to 8 with no warning. A value that cannot be parsed as an integer (e.g. `"abc"`) SHALL fall back to 8 and the fetcher SHALL log an `invalid_integer_env_var` warning at WARNING level. Setting `WORKLOG_FETCH_CONCURRENCY=1` SHALL preserve the v1.3 serial behavior exactly (deterministic, ordered dispatch, no shared-state mutation outside the main thread). Setting `WORKLOG_FETCH_CONCURRENCY` to 0 or a negative number SHALL cause the module to raise `ValueError` at import time with a message naming the offending value. A `concurrency` keyword argument SHALL also be accepted by `fetch_person_worklogs` for testing and advanced use; when provided, it overrides the env-var-derived default.

The fetcher SHALL use a `concurrent.futures.ThreadPoolExecutor` of size `WORKLOG_FETCH_CONCURRENCY`. The executor SHALL be scoped to a single call of `fetch_person_worklogs` (created and shut down within the call); no module-level executor SHALL be created. Per-issue worklog fetches SHALL be **dispatched in submission (issue-key) order** and the **results shall be aggregated in the same order**: each future's worklog list is consumed in the order its issue key was encountered by the chunk loop, not in completion order. This preserves the v1.3 invariants that (a) the `PersonWorklogAggregate` list reflects the issue-key iteration order, (b) the first non-empty `author.accountId` observed for an aggregate is the one returned by the earliest-submitted issue's worklog response, and (c) the `entries` list of an aggregate is in submission order. The aggregation dict SHALL be single-writer on the main thread; the per-fetch worklog lists are read-only after the future resolves.

The fetcher SHALL log a `worklog_fetch_concurrency concurrency=N issues=M` line on entry to `fetch_person_worklogs` so operators can confirm the configured value at runtime.

#### Scenario: Default concurrency is 8 when env var is unset
- **WHEN** `WORKLOG_FETCH_CONCURRENCY` is unset
- **THEN** the fetcher SHALL use a thread pool of size 8
- **AND** it SHALL log `worklog_fetch_concurrency concurrency=8 issues=<N>`

#### Scenario: Custom concurrency is read from env var
- **WHEN** `WORKLOG_FETCH_CONCURRENCY=4` is set in the environment
- **THEN** the fetcher SHALL use a thread pool of size 4
- **AND** it SHALL log `worklog_fetch_concurrency concurrency=4 issues=<N>`

#### Scenario: Unparseable concurrency value falls back with warning
- **WHEN** `WORKLOG_FETCH_CONCURRENCY=abc` is set in the environment
- **THEN** the fetcher SHALL log a WARNING-level `invalid_integer_env_var` line naming the offending value
- **AND** it SHALL fall back to a thread pool of size 8
- **AND** importing the module SHALL NOT raise

#### Scenario: Concurrency of 1 preserves v1.3 serial behavior
- **WHEN** `WORKLOG_FETCH_CONCURRENCY=1` is set
- **THEN** the fetcher SHALL dispatch per-issue calls one at a time
- **AND** the resulting `PersonWorklogAggregate` ordering SHALL match the issue-key order
- **AND** no two `issue_get_worklog` calls SHALL be in flight at the same time
- **AND** the existing 280-test suite SHALL pass unchanged

#### Scenario: Aggregates are idempotent under concurrency
- **WHEN** the fetcher is run with `concurrency=1` and again with `concurrency=8` against the same mocked Jira client
- **THEN** for every `display_name` present in either result, the two runs SHALL produce identical:
  - `account_id` (the first non-empty value observed — invariant because results are aggregated in submission order)
  - `account_ids` (the tuple of distinct `accountId`s observed)
  - `logged_total_seconds` (the sum over all entries)
  - `worked_ticket_keys` (the set of issue keys)
  - `daily_seconds` (the per-day bucket dict)
  - `entries` list order (submission-order, identical between the two runs)
- **AND** the iteration order of the returned `PersonWorklogAggregate` list SHALL be identical between the two runs (because the same first-seen-aggregate insertion order is preserved)

#### Scenario: Invalid concurrency value raises at import time
- **WHEN** `WORKLOG_FETCH_CONCURRENCY=0` (or a negative value) is set
- **THEN** importing `jira_daily_reports.person_worklog_source` SHALL raise `ValueError` with a message naming the offending value

#### Scenario: Executor is scoped to a single call
- **WHEN** `fetch_person_worklogs` is called twice in succession
- **THEN** each call SHALL create and shut down its own `ThreadPoolExecutor`
- **AND** no executor SHALL be created at module import time
- **AND** a unit test that monkeypatches `concurrent.futures.ThreadPoolExecutor` SHALL observe one constructor call per `fetch_person_worklogs` invocation

#### Scenario: Empty issue list skips pool creation
- **WHEN** a JQL chunk returns zero issues
- **THEN** the fetcher SHALL NOT create a `ThreadPoolExecutor` for that chunk
- **AND** the fetcher SHALL continue to the next chunk
- **AND** no error SHALL be raised

#### Scenario: Non-retryable failure in one worker fails the whole fetch
- **WHEN** `jira.issue_get_worklog` raises a non-retryable exception (one whose message does not contain any token in `WORKLOG_RETRYABLE_EXC_TEXT`) in a worker thread
- **THEN** the `fetch_person_worklogs` call SHALL re-raise the original exception to the caller
- **AND** the executor SHALL be shut down before the exception propagates
- **AND** the per-issue fetches for other issues in the same chunk MAY have been started but their results SHALL be discarded

#### Scenario: Retry exhaustion in one worker fails the whole fetch
- **WHEN** `jira.issue_get_worklog` raises a retryable exception in a worker thread and all 3 retry attempts fail
- **THEN** the `fetch_person_worklogs` call SHALL re-raise the last exception to the caller
- **AND** the executor SHALL be shut down before the exception propagates

#### Scenario: Concurrency keyword argument overrides env var
- **WHEN** `fetch_person_worklogs(..., concurrency=4)` is called with `WORKLOG_FETCH_CONCURRENCY=8` set in the environment
- **THEN** the fetcher SHALL use a thread pool of size 4
- **AND** it SHALL log `worklog_fetch_concurrency concurrency=4 issues=<N>`
- **AND** the module-level `WORKLOG_FETCH_CONCURRENCY` constant SHALL remain 8 (the env-var-derived default) — only this call is affected

#### Scenario: Logging is thread-safe
- **WHEN** multiple worker threads log a `worklog_jira_retry` warning simultaneously
- **THEN** the Python `logging` module's built-in thread-safety SHALL ensure each warning line is written to the handler atomically
- **AND** warning lines SHALL NOT be interleaved mid-record
- **AND** the test suite SHALL exercise this by triggering 8 concurrent `worklog_jira_retry` warnings and asserting the log capture is well-formed

