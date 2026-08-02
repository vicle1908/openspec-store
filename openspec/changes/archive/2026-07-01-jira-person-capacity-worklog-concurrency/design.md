## Context

The `jira-person-capacity-worklog-mode` v1.3 flow ships the data quality fix (trailing-empty truncation) and the Jira-side display-name collision detection. Live re-write verification (Task 16.17) is blocked by the per-issue worklog fetch being serial — for a 33-name × 12-day window (~187 issues) the run takes 3-7 minutes and frequently hits upstream 500/timeout on the long tail. The v1.3 code is correct; the bottleneck is structural.

The Atlassian Cloud platform enforces a **per-tenant, per-endpoint token-bucket burst rate limit** with documented steady-state defaults:
- `GET /rest/api/3/search` — 100 RPS
- `GET /rest/api/3/issue/{issueIdOrKey}` — 150 RPS

API-token-authenticated traffic is **explicitly exempt** from the March 2026 points-based hourly quota. We currently run at ~3 RPS (single serial `requests.Session.get()`). Headroom is ~50×, so a thread pool of 8 workers per invocation is conservative: 2 simultaneous `sprint-sheet` invocations would consume ~16% of the steady-state quota for the worklog endpoint.

The implementation is read-only and the aggregation is post-fetch (no shared-state mutation in the hot path). This is a clean target for parallelism: the only writes to the `aggregates_by_name` dict happen after each `issue_get_worklog` call returns, in the main thread, and the dict is local to the function call.

The `call_with_retry` helper wraps each call and is fully thread-safe (stateless except for the `time.sleep` and `logger.warning` per-attempt). It will continue to work inside a thread pool.

The downstream v1.3 fix (single-space sentinel) is already in place, so this change is a pure performance optimization with no behavior delta.

## Goals / Non-Goals

**Goals:**
- Reduce wall-clock for the typical `sprint-sheet` invocation against a 33-name × 12-day roster from 3-7 min to **under 60 s**.
- Keep the public API of `person_worklog_source` unchanged.
- Keep the v1 retry semantics intact (429 / timeout / connection errors, exponential backoff).
- Keep chunking behavior intact (≤150 display names per JQL, chunks run sequentially).
- Make the concurrency level **configurable and observable** (env var, log line on startup).
- Pass `WORKLOG_FETCH_CONCURRENCY=1` to preserve v1.3 behavior exactly (escape hatch).
- Pass the existing 280 tests unchanged + add ≥3 new tests covering the new path.

**Non-Goals:**
- Async / asyncio refactor of `tdt-core` or `jira-daily-reports`.
- JQL chunk parallelism (spec mandates sequential chunks).
- Adaptive rate limiting / circuit breaker (existing 429 retry is sufficient at 8 RPS/worker).
- Cross-tenant or cross-invocation coordination (each `sprint-sheet` invocation is independent).
- Changing the Sheets write path (not the bottleneck; bounded by Sheets API latency not Jira).
- Replacing the 280-test suite with new tests. The change is additive.

## Decisions

### 1. Thread pool over asyncio

**Decision:** `concurrent.futures.ThreadPoolExecutor(max_workers=N)`.

**Rationale:**
- The `atlassian-python-api` SDK is synchronous (`requests.Session` under the hood). Async would require a separate `httpx.AsyncClient` and rewriting the entire call chain in `tdt-core` — out of scope and a much larger change.
- Threads release the GIL during blocking I/O, so this gives true parallelism for HTTP calls.
- `ThreadPoolExecutor` is stdlib, well-tested, and matches the existing module's import style.

**Alternatives considered:**
- `multiprocessing` — overkill for I/O-bound work; pays process-spawn cost per chunk.
- `asyncio` + `aiohttp` — would force a parallel async path in `tdt-core`; big surgery for a 6-15× speedup we can get with threads.
- `grequests` / `requests-futures` — third-party dependencies for what `concurrent.futures` does in stdlib.

### 2. Per-issue parallelism, not per-chunk

**Decision:** Parallelize the inner per-issue loop. Keep chunks (JQL groups of ≤150 names) serial.

**Rationale:**
- The spec says "the fetcher SHALL run each chunk sequentially" — keeping that is the cleanest contract preservation.
- With 33 names there's only 1 chunk today, so chunk-level parallelism would not help the typical case. It would only help the 200+ name stress case, and even then only ~2 chunks.
- Per-issue is the dominant cost: `len(issues)` HTTP calls vs. `len(chunks)` JQL calls.
- Per-issue parallelism gives ~10-15× speedup at 8 workers, well under the 100 RPS burst limit.

**Alternatives considered:**
- Parallelize both chunks and issues inside chunks — more code, marginal additional speedup, harder to reason about ordering.
- Parallelize JQL pagination only — much smaller win (the JQL response for a 12-day window typically fits in one page).

### 3. Default concurrency = 8

**Decision:** `WORKLOG_FETCH_CONCURRENCY = 8` (configurable via `WORKLOG_FETCH_CONCURRENCY` env var).

**Rationale:**
- 8 workers × ~300 ms per request = ~24 RPS effective. Comfortably under the 100 RPS burst steady-state.
- Even 4-6 simultaneous `sprint-sheet` invocations from different operators stay under 50 RPS.
- Empirically, 8 is the sweet spot in similar Python `ThreadPoolExecutor` patterns for I/O-bound Atlassian API work.
- Setting to `1` is the documented escape hatch that reproduces v1.3 behavior exactly.

**Alternatives considered:**
- `4` — too conservative; speedup is only ~4×, not enough to unblock 16.17.
- `16` — eats 50% of burst budget per invocation; 2 simultaneous runs would start throttling.
- `32` — exceeds 100 RPS, will hit 429s.

### 4. Aggregation stays single-threaded, in submission order

**Decision:** Pool submits `(jira, issue_key)` jobs; main thread iterates the `future_to_key` mapping **in submission (insertion) order**, not in completion order. Each future's result is processed before the next one is awaited.

**Rationale:**
- The `aggregates_by_name` dict is local to the function. If multiple threads wrote to it, we'd need a lock and a key-mutation protocol. Cleaner to keep aggregation single-threaded.
- The dict-mutation work is trivial compared to the network I/O (microseconds vs. hundreds of ms).
- Processing in submission order (issue-key order) **preserves the v1.3 invariants**: (a) the `PersonWorklogAggregate` list iteration order matches issue-key order, (b) the first non-empty `author.accountId` observed for an aggregate is the one from the earliest-submitted issue's worklog response, and (c) the `entries` list of an aggregate is in submission order. Without this guarantee, the existing v1.3 test `test_fetch_person_worklogs_tracks_distinct_account_ids_per_aggregate` (which asserts `agg.account_id == "acc-1"` — first observed) would fail under parallel dispatch.
- Note: we deliberately avoid `concurrent.futures.as_completed()` for the consume-side loop. `as_completed` is the right tool when only wall-clock matters; here we need deterministic order in addition to wall-clock.

**Alternatives considered:**
- `as_completed()` for the consume loop — gives completion-order semantics (which would be non-deterministic for real-network calls). Rejected because it would break the first-observed `account_id` invariant.
- Per-worker dicts merged at the end — would let us avoid the lock but adds complexity and uses more memory, and still leaves the first-observed ambiguity (which worker saw what first).
- A `defaultdict` with `threading.Lock` — same single-threaded cost; the lock adds overhead for no benefit.

### 5. Retry semantics preserved per-call

**Decision:** `call_with_retry` wraps each `jira.issue_get_worklog` invocation. Inside the thread pool, each future's target is `lambda: call_with_retry(logger, jira.issue_get_worklog, args=(key,))`.

**Rationale:**
- The 429 / timeout retry logic is unchanged. If a worker thread gets a 429, it sleeps and retries *within its own thread*; other workers are unaffected.
- The `worklog_jira_retry` warning is logged with the issue key, so the diagnostic stays useful.
- Worst case: 8 workers all hit 429 simultaneously → 8 independent backoff cycles. The 1s/2s/4s schedule means the first retry wave fires in 1-4s, well within the burst window.

**Alternatives considered:**
- A shared `RateLimiter` instance with token-bucket semantics — would be the right move at 30+ workers, overkill at 8.
- A circuit breaker — not needed at this concurrency level; the existing 3-attempt retry is enough.

### 6. `WORKLOG_FETCH_CONCURRENCY` env var via `tdt_core.env.get_int_env`, plus a `concurrency` arg on the function

**Decision:** Read the module-level default via `tdt_core.env.get_int_env("WORKLOG_FETCH_CONCURRENCY", 8)`. The function `fetch_person_worklogs` SHALL also accept a `concurrency: int | None = None` keyword argument; when not `None`, it overrides the env-var-derived default for that call only.

**Rationale:**
- `tdt_core.env.get_int_env` is the project standard for integer env-var parsing (used by `delivery/email.py` for `SMTP_PORT` and elsewhere). The workspace `AGENTS.md` says: "For shared config coercion, prefer `tdt_core.env.get_bool_env()`, `get_int_env()`, `get_float_env()`, and `get_path_env()` over ad-hoc `os.getenv()` parsing in new code." The current module's other constants use raw `os.getenv()` but those are unparseable-safe strings; this is the first integer env var in the module, so the standard helper is the right choice.
- `get_int_env` already handles three of the four cases the spec needs: (1) unset → fall back to default, (2) unparseable → log WARNING and fall back, (3) empty string → fall back to default. It does NOT handle the `0` or negative case, so we add an explicit `<= 0` guard.
- The `concurrency` keyword argument gives tests a clean way to override the env var for a single call without re-importing the module. `importlib.reload` is fragile and order-dependent across test files; a function arg is the right test seam.
- Operators tune the env var once per environment, not per call. The function arg is for tests + advanced use (e.g. a future caller that wants to throttle based on backlog).

**Alternatives considered:**
- Raw `os.getenv` + `int(...)` — the original choice in the v1.3 work. Rejected because it requires a custom parser for the unparseable case AND the `0`/negative case AND the empty-string case. `get_int_env` covers three of those for free.
- Module-level reload via `importlib.reload` in tests — works but is fragile: pytest's import order matters, other test files may have already imported the module, and re-loading invalidates the module's singletons (the logger, etc.). Function-arg override is cleaner.

## Risks / Trade-offs

- **[Risk] Concurrent calls to a shared `PatchedJira` instance could fail** if the SDK holds a non-thread-safe state (e.g. a `requests.Session` with connection pooling that mutates a connection pool counter). → **Mitigation:** `PatchedJira` extends `atlassian.AtlassianCloud` which uses `requests.Session()` per instance. `Session.get()` is thread-safe. We have not observed thread-safety bugs in the v1.0-v1.3 development history. Stress test (Task 16.8) verified 50 concurrent `issue_get_worklog` calls in a single process work; the stress test used the same `MagicMock` so a follow-up live stress test on a real Jira tenant is recommended.
- **[Risk] 8 concurrent requests to a single tenant may still trigger burst 429s** if the operator runs `sprint-sheet` repeatedly in a tight loop. → **Mitigation:** the existing `call_with_retry` will catch the 429, sleep 1-4 s, and retry. The `worklog_jira_retry` log line gives operators visibility. If 429s become a production problem, the env var can be lowered to 4 or 2.
- **[Risk] Resource exhaustion if 100+ operators run `sprint-sheet` simultaneously.** → **Mitigation:** documented in the SKILL.md and proposal. The Burst API rate limit is per-tenant, not per-process, so simultaneous invocations compound. For the current team size (~5 operators), this is not a concern.
- **[Risk] Memory pressure from queueing 187 futures at once.** → **Mitigation:** `ThreadPoolExecutor` does not pre-queue. It runs up to `max_workers` futures and starts the next one as a worker frees. Peak memory is `max_workers * (typical response payload)`, which is ~MBs.
- **[Risk] `WORKLOG_FETCH_CONCURRENCY=0` would crash.** → **Mitigation:** the explicit `<= 0` guard at module import time raises `ValueError` with a clear message. The constant is a hard requirement, not a soft default.
- **[Risk] `WORKLOG_FETCH_CONCURRENCY=-1` (negative) would also crash.** → **Mitigation:** same `<= 0` guard catches it. `ThreadPoolExecutor` itself raises on `max_workers <= 0` but the import-time guard fails faster and with a more actionable error.
- **[Risk] Non-retryable failure in one worker during parallel fetch** would discard partial results from other workers in the same chunk. → **Mitigation:** this is fail-fast behavior, identical to v1.3 (where a single failure aborts the loop). The spec scenarios "Non-retryable failure in one worker fails the whole fetch" and "Retry exhaustion in one worker fails the whole fetch" document this. The user re-runs after fixing the upstream cause.
- **[Risk] `as_completed` would break the v1.3 first-seen `account_id` invariant.** → **Mitigation:** the implementation uses **submission-order iteration** (`for fut, key in future_to_key.items()`) instead of `as_completed`. This is enforced by the spec scenario "Aggregates are idempotent under concurrency" and the existing v1.3 test `test_fetch_person_worklogs_tracks_distinct_account_ids_per_aggregate`.
- **[Risk] Log lines from multiple workers could interleave.** → **Mitigation:** Python's `logging` module is thread-safe by default (it uses a `RLock` internally and serializes writes to each handler). The `worklog_jira_retry` log line and the new `worklog_fetch_concurrency` line are both written via the standard `logger.warning/info` API, so the GIL + the logging RLock together guarantee atomic line emission.

## Migration Plan

- No data migration. No schema changes. No API changes.
- Deploy via the standard `jira-daily-reports/scripts/deploy.sh` (no changes to the deploy script).
- Rollback: `WORKLOG_FETCH_CONCURRENCY=1` reproduces v1.3 behavior exactly. The rollback knob is a single env var.
- Monitoring: the `person_capacity_window_oversized` and `worklog_jira_retry` log lines already exist; no new observability surface is needed for v1.4.
- Day-1 sign-off: re-run the live `sprint-sheet` with the new default, confirm <60 s wall-clock for the 33-name × 12-day case, capture log in `artifacts/real-operation/sprint-sheet-v1.4.log`.

## Open Questions

- **None blocking.** All design decisions are based on the current spec, the existing module structure, and the Atlassian rate-limit docs. The 8-worker default can be tuned later based on production telemetry.
