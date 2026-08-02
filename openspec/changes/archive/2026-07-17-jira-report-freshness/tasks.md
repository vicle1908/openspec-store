## 1. Freshness orchestration contract

- [x] 1.1 Define the refresh trigger contract and source enum for schedule, webhook, manual, and fallback refreshes
- [x] 1.2 Explicitly model `Sprint Report` and `Person Capacity` as a single refresh unit
- [x] 1.3 Document the debounce/deduplication boundary, keyed on the report target (sprint/workbook), NOT the issue key
- [x] 1.4 Specify the narrow Jira event classes that can request freshness refreshes (scope/sprint, ownership, estimate, status, worklog)
- [x] 1.5 Define the shared freshness marker (run id + timestamp) and where it lives: both the generated tabs/execution record and a local state file

## 2. Scheduler integration

- [x] 2.1 Preserve existing `jira-daily-reports schedule` cron generation as the durable fallback path
- [x] 2.2 Wire scheduled refreshes to call the existing `sprint-sheet` execution path without changing report output semantics
- [x] 2.3 Ensure scheduled runs always refresh both tabs together from the same snapshot
- [x] 2.4 Add logging/telemetry for scheduled refresh success and failure

## 3. Webhook-triggered refresh path

- [x] 3.1 Add a report-refresh dispatch boundary in `webhook-receiver` that spawns a non-blocking background `sprint-sheet` subprocess (mirrors cron invocation; NO new HTTP endpoint on `jira-daily-reports`, NO inline computation)
- [x] 3.2 Implement a freshness debouncer keyed on the report target so bursty events across multiple issues coalesce into one refresh request (do not reuse `ReviewDebouncer`'s per-`mr_iid` keying as-is)
- [x] 3.3 Add a dedicated freshness-relevance predicate that inspects the changelog for any relevant field; do NOT reuse the status-only `jira_guard/events.py:parse_webhook_payload`
- [x] 3.4 Keep webhook-triggered refreshes non-blocking and resilient to transient failures
- [x] 3.5 Add an in-flight guard so an arriving request coalesces/skips when a refresh for the same target is already running
- [x] 3.6 Ensure webhook-triggered runs update both tabs atomically or not at all

## 4. Observability and recovery

- [x] 4.1 Surface the last refresh mode/source (schedule/webhook/manual/fallback) in logs and operational output
- [x] 4.2 Add health/status visibility for last refresh source + run id + timestamp via the existing `/health` output
- [x] 4.3 Persist last refresh source/run id/timestamp in a local state file so dedupe and the in-flight guard survive process restarts
- [x] 4.4 Preserve cron-only operation as a rollback path when webhook refresh is disabled
- [x] 4.5 Report freshness at the pair level, not as separate independently driven tabs
- [x] 4.6 Ensure pair-level freshness checks fail closed when only one tab appears updated

## 5. Verification and documentation

- [x] 5.1 Add tests for schedule-driven refresh, webhook-triggered refresh, per-target debounce coalescing, and ignored-event behavior
- [x] 5.2 Add a test that a non-status changelog field (assignee/estimate/worklog/sprint) is treated as freshness-relevant
- [x] 5.3 Add a test that a refresh arriving while one is in flight does not start a concurrent overlapping run
- [x] 5.4 Validate end-to-end freshness with a live scheduled run and a controlled webhook-triggered refresh
- [x] 5.5 Verify both tabs are refreshed together from the same snapshot and share the same run id in live and test paths
- [x] 5.6 Update runbook/docs to explain when to use cron, webhook, or both for report freshness
