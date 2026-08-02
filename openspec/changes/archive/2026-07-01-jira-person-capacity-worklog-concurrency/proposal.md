## Why

The `jira-person-capacity-worklog-mode` v1.3 flow runs `sprint-sheet` end-to-end against the test workbook in **3-7 minutes** when targeting the full 33-name roster × 12-day window. The bottleneck is the per-issue worklog fetch loop in `person_worklog_source.fetch_person_worklogs` (line 338), which issues one synchronous HTTP `GET /rest/api/3/issue/{key}/worklog` per issue, serially. For the 33-name × 12-day probe (187 tickets) this is ~187 round-trips at ~300 ms each, dominating the run.

The spec currently says the fetcher "SHALL run each chunk sequentially" (chunk = a JQL group of ≤150 display names) and is silent on per-issue fetch parallelism. The implementation honors the spec and runs everything serial.

Atlassian's documented burst rate limit for `GET /rest/api/3/issue/{issueIdOrKey}` is **150 RPS steady-state per tenant** with a token-bucket burst buffer, and we are using **API-token auth** (which is explicitly *not* subject to the new points-based hourly quota from March 2026). We are running at ~3 RPS, so we have **~50× headroom** before the burst limit becomes a concern. A bounded thread pool of 8 workers per `sprint-sheet` invocation is conservative: 2 simultaneous invocations still stay at <20% of steady-state.

This change unlocks the live re-write of the production `Person Capacity` tab with the v1.3 trailing-empty fix (Task 16.17), which has been blocked by upstream API timeouts on the serial path. It also brings the run time from "user waits, often times out" to "completes in under a minute" for the typical 12-day / 33-name case, and stays well-behaved for the 200-name / 30-day stress case.

## What Changes

- Add a new constant `WORKLOG_FETCH_CONCURRENCY: int = tdt_core.env.get_int_env("WORKLOG_FETCH_CONCURRENCY", 8)` in `person_worklog_source.py`. An explicit `<= 0` guard at module import time raises `ValueError`. The function `fetch_person_worklogs` also accepts a `concurrency: int | None = None` keyword argument that overrides the env-var default for that call only (used by tests + advanced callers).
- Refactor the per-issue worklog fetch loop in `fetch_person_worklogs` to submit per-issue fetches to a `concurrent.futures.ThreadPoolExecutor` of size `effective_concurrency`. Result aggregation stays single-threaded and **iterates in submission (issue-key) order, not completion order** — this preserves the v1.3 first-observed-`account_id` invariant that the existing test `test_fetch_person_worklogs_tracks_distinct_account_ids_per_aggregate` depends on. The `call_with_retry` wrapper is preserved per call, so the v1 retry semantics (429 / timeout / connection, exponential backoff 1s/2s/4s) are unchanged.
- JQL chunks (≤150 display names) **remain serial** per the v1 spec ("the fetcher SHALL run each chunk sequentially"). Per-issue worklog fetches **within a chunk** are the only parallelism surface.
- Add 14 new tests covering: env-var parsing (default / custom / unparseable / invalid), thread-pool use, submission-order invariant, parallelism observability, idempotence under concurrency, log line emission, retry semantics in pool, concurrency-arg override, empty-issue-skip, non-retryable failure, retry exhaustion, and logging thread-safety.
- Update the `spec.md` for `person-capacity-worklog-mode` with a new `Concurrency` requirement (11 scenarios) and a clarification of the existing `JQL is chunked at 150 display names` requirement to scope "sequential" to *chunks*, not per-issue fetches within a chunk.
- Bump the `WORKLOG_FETCH_CONCURRENCY` env-var documentation in the Day-1 SKILL.md.
- Re-run the live `sprint-sheet` against the test workbook with the new default (8) and confirm the write completes in under 60 s. Capture the run log in `artifacts/real-operation/sprint-sheet-v1.4.log`.

**No breaking changes.** `WORKLOG_FETCH_CONCURRENCY=1` reproduces the v1.3 behavior exactly. The public API of `person_worklog_source` only gains an optional `concurrency` keyword argument.

## Capabilities

### New Capabilities
*(none)*

### Modified Capabilities
- `person-capacity-worklog-mode`: A new `Concurrency` requirement is added. The chunking requirement is clarified to scope "sequential" to chunks, not per-issue fetches. The retry requirement gains a "concurrent callers do not compound backoff" note.

## Impact

- **`jira-daily-reports`** (only):
  - `src/jira_daily_reports/person_worklog_source.py`: add constant, refactor per-issue loop to use `ThreadPoolExecutor`, add new helper for parallel dispatch. Public API unchanged.
  - `tests/test_person_worklog_source.py`: add concurrency tests (parallel dispatch observable, serial mode preserved, idempotent aggregates, retry still works in pool).
  - `tests/test_sprint_report_sheet_person_capacity.py`: add 1-2 integration tests asserting end-to-end parity across concurrency levels.
  - `.agents/skills/jira-daily-reports/SKILL.md`: document the `WORKLOG_FETCH_CONCURRENCY` env var.
- **`tdt-core`**: **unchanged**. `PatchedJira` is thread-safe per Atlassian Python API docs (uses a `requests.Session` per instance); no new client methods.
- **`jira-skill`**: **unchanged**. `CapacitySignal` is not wired into the activity-only flow.
- **Operational**: expected wall-clock for a 33-name × 12-day `sprint-sheet` invocation drops from 3-7 min to 30-60 s. Stress test (200 names × 30 days) drops from >10 min to ~2-3 min. No new infra; no new dependencies (stdlib `concurrent.futures` only).

### Non-goals
- **No async / asyncio refactor.** Sticking with threads keeps the change small and matches the synchronous SDK call style.
- **No JQL chunk parallelism.** Spec mandates sequential chunks; we keep that.
- **No adaptive backoff / circuit breaker.** The existing 429 retry via `call_with_retry` is enough at 8 RPS-per-worker.
- **No request batching.** Atlassian does not expose a batch worklog endpoint; N+1 is unavoidable.
- **No change to the write path.** The Sheets write side is bounded by API latency, not the fetch path, and is not the focus of this change.

### Out-of-scope
- `tdt-core` rate-limiter wrapping: a more sophisticated adaptive limiter could further reduce 429s, but it is a separate, larger change. Tracked separately.
- Async refactor of `tdt-core` clients: not needed for this performance target.
