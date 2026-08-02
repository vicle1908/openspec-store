# jira-daily-reports JQL Pagination Fix

## Why

The JQL search in jira-daily-reports used single-page API calls that truncated results when Jira returned >50 or >100 issues. A `_jql_paginated` helper was added to follow `nextPageToken` cursor pagination, ensuring all matching issues are fetched regardless of result set size.

## What Changes

- Added `_jql_paginated(jira, jql, *, fields, limit)` helper in `client.py` following `nextPageToken` cursor
- Rewrote `jql_search` to delegate to `_jql_paginated`
- Rewrote `ReportBase._search` to delegate to `_jql_paginated`
- Updated existing `jql_search` tests for pagination behavior
- All tests passing

## Metadata

- **Completed:** 2026-07-14
- **Tasks:** all done
