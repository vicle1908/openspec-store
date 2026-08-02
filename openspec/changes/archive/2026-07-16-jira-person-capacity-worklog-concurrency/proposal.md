# jira-daily-reports Person Worklog Concurrency

## Why

Person worklog fetches in jira-daily-reports were serial, causing slow `sprint-sheet` runs (33-name roster over 12 days → ~33 JQL searches × ~50 issues × ~50 worklogs = sequential bottleneck). `ThreadPoolExecutor` was added with configurable `WORKLOG_FETCH_CONCURRENCY` to parallelize per-issue worklog fetching.

## What Changes

- Added `WORKLOG_FETCH_CONCURRENCY` env var (default 8) in `person_worklog_source.py`
- Added `ThreadPoolExecutor` with submission-order iteration for thread-safe worklog aggregation
- Full concurrency test suite: 15 new tests covering thread-safety, retry semantics, empty-issue handling, idempotency
- Integration test confirming serial vs parallel output equivalence
- All 321 tests passing; lint + mypy clean
- Live probe confirmed: 33-name roster over 12-day window completes in 2.21s (vs estimated ~60s serial)

## Metadata

- **Completed:** 2026-07-14
- **Tasks:** all done
