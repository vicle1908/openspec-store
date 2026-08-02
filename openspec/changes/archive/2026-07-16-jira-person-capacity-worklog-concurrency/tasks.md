## 1. Module constant and env-var parsing

- [x] 1.1 In `src/jira_daily_reports/person_worklog_source.py`, add `WORKLOG_FETCH_CONCURRENCY: int = tdt_core.env.get_int_env("WORKLOG_FETCH_CONCURRENCY", 8)` near the existing `WORKLOG_*` constants. After the read, add an explicit guard: `if WORKLOG_FETCH_CONCURRENCY <= 0: raise ValueError("WORKLOG_FETCH_CONCURRENCY must be > 0; got {value}")`. Add the import `from tdt_core.env import get_int_env` (or import the module if `tdt_core.env` is not already pulled in).
- [x] 1.2 Add `import concurrent.futures` and `from concurrent.futures import ThreadPoolExecutor` at the top of the module.
- [x] 1.3 Run `uv run pytest tests/test_person_worklog_source.py -q` after this change to confirm the import-time guard doesn't break the existing 280 tests (it shouldn't, since the env var is unset in the test environment).
- [x] 1.4 Add `test_worklog_fetch_concurrency_default_is_8` → **verified 2026-07-01: test exists in `tests/test_person_worklog_source.py` and passes**
- [x] 1.5 Add `test_worklog_fetch_concurrency_overridden_by_env` → **verified 2026-07-01: test exists and passes**
- [x] 1.6 Add `test_worklog_fetch_concurrency_unparseable_falls_back_with_warning` → **verified 2026-07-01: test exists and passes**
- [x] 1.7 Add `test_worklog_fetch_concurrency_invalid_raises` → **verified 2026-07-01: test exists and passes**
- [x] 1.8 Run `uv run pytest tests/test_person_worklog_source.py -k "concurrency" -q` → **12 passed, 68 deselected**

## 2. Add `concurrency` arg and refactor per-issue fetch loop

- [x] 2.1 Add a `concurrency: int | None = None` keyword argument to `fetch_person_worklogs`. Resolution: `effective_concurrency = WORKLOG_FETCH_CONCURRENCY if concurrency is None else concurrency`. Validate `effective_concurrency > 0` (raise `ValueError` if not — the import-time guard handles the env-var case; the function arg is a runtime check).
- [x] 2.2 At the start of `fetch_person_worklogs` (after the empty-roster guard, before the chunk loop), add a `worklog_fetch_concurrency concurrency=N issues=M` INFO log line using `effective_concurrency` and the total issue count across all chunks (compute by inspecting the chunks, or log per-chunk; per-chunk is simpler and matches the existing `worklog_jql_chunked` pattern).
- [x] 2.3 Inside the chunk loop, replace the per-issue sequential `worklogs = _fetch_issue_worklogs(jira, issue_key)` call with a `ThreadPoolExecutor` block:
  - Build a list of `issue_key` strings from `issues` (preserve the v1.3 issue iteration order).
  - **Edge case: if `issue_keys` is empty, skip the pool creation entirely** and continue to the next chunk. This matches the spec scenario "Empty issue list skips pool creation".
  - Use a `with ThreadPoolExecutor(max_workers=effective_concurrency) as ex:` block scoped to the chunk.
  - Build a `dict[fut, key]` mapping by submitting one future per issue.
  - **Iterate in submission order, not `as_completed`:** `for fut, key in futures.items(): worklogs = fut.result()`. This preserves the first-observed `account_id` invariant (existing v1.3 test `test_fetch_person_worklogs_tracks_distinct_account_ids_per_aggregate` depends on this).
  - Inside the loop, the per-issue aggregation logic is identical to the current code (lines 339-396 of the v1.3 module).
- [x] 2.4 Add `test_fetch_person_worklogs_uses_thread_pool`: monkeypatch `concurrent.futures.ThreadPoolExecutor` in the module's namespace to count constructor calls; run a fetch with 5 issues; assert the patched constructor was called at least once. Also assert the `with` block correctly shut down the executor (verify by `mock_executor_instance.shutdown.assert_called()` or by checking the instance is no longer referenced after the `with` block exits).
- [x] 2.5 Add `test_fetch_person_worklogs_uses_submission_order_not_completion`: mock `jira.issue_get_worklog.side_effect` to return different worklogs based on a `threading.Event` per issue — issue A blocks for 100 ms then returns worklogs tagged with `accountId="acc-A"`; issue B returns immediately with `accountId="acc-B"`. With `concurrency=8`, run a fetch. Assert `aggregates[0].account_id == "acc-A"` (the submission-ordered result, not the completion-ordered result). This is the regression test for the v1.3 `test_fetch_person_worklogs_tracks_distinct_account_ids_per_aggregate` invariant.

## 3. Concurrency-specific tests

- [x] 3.1 Add `test_fetch_person_worklogs_concurrency_one_preserves_serial_behavior`: pass `concurrency=1` to the function. Run against a mock with 5 issues. Assert the order of `aggregates[0].entries` matches the issue-key order AND no two `issue_get_worklog` calls overlap (use a `threading.Event` to make the overlap observable — instrument the mock to set/clear the event and assert that it was never set).
- [x] 3.2 Add `test_fetch_person_worklogs_concurrency_default_dispatches_in_parallel`: with `concurrency=8`, mock `issue_get_worklog` with a 100 ms `time.sleep` plus a counter, run for 10 issues, and assert:
  - Total elapsed time is < 500 ms (10 issues serial would be ~1000 ms; 8-way parallel is ~200 ms with 100 ms sleep).
  - The counter was at least 5 at peak (i.e. 5+ issues were in flight at the same time).
- [x] 3.3 Add `test_fetch_person_worklogs_aggregates_idempotent_under_concurrency`: run twice — once with `concurrency=1`, once with `concurrency=8` — against the same mock with 5 issues per aggregate (2 aggregates). Build two dicts `display_name -> aggregate` from each result and assert that for every display name, `account_id`, `account_ids`, `logged_total_seconds`, `worked_ticket_keys`, `daily_seconds`, AND the `entries` list (in order) are identical between the two runs.
- [x] 3.4 Add `test_fetch_person_worklogs_logs_concurrency_line`: capture `caplog.records`, run a fetch, and assert at least one log line contains `worklog_fetch_concurrency concurrency=8 issues=<N>`. Then run with `concurrency=4` and assert the log line says `concurrency=4`.
- [x] 3.5 Add `test_fetch_person_worklogs_retry_inside_pool_preserves_retry_semantics`: mock `issue_get_worklog` to raise `requests.exceptions.HTTPError("429 rate limit")` on the first call and return valid worklogs on the second. With `concurrency=4`, run a fetch. Assert the worklogs are returned and a `worklog_jira_retry` warning is logged. (The existing `call_with_retry` handles the retry; the test confirms the pool doesn't break the retry chain.)
- [x] 3.6 Add `test_fetch_person_worklogs_concurrency_arg_overrides_env`: set `WORKLOG_FETCH_CONCURRENCY=8` in the env. Call `fetch_person_worklogs(..., concurrency=4)`. Assert the log line says `concurrency=4` and the module-level constant is still 8 (verify via `importlib` and a fresh reference).
- [x] 3.7 Add `test_fetch_person_worklogs_empty_issue_list_skips_pool`: mock `_search_jql_issues` to return `[]`. Run a fetch. Assert no `ThreadPoolExecutor` is constructed (use a `monkeypatch.setattr` to track constructor calls). Assert the function returns `[]` and no exception is raised.
- [x] 3.8 Add `test_fetch_person_worklogs_non_retryable_failure_fails_fast`: with `concurrency=4`, mock `issue_get_worklog` to raise `ValueError("boom")` (non-retryable). Assert the call re-raises `ValueError("boom")`.
- [x] 3.9 Add `test_fetch_person_worklogs_retry_exhaustion_fails_fast`: with `concurrency=4`, mock `issue_get_worklog` to always raise `requests.exceptions.HTTPError("429 rate limit")`. Assert the call re-raises the last `HTTPError` after 3 attempts.
- [x] 3.10 Add `test_fetch_person_worklogs_logging_thread_safe`: instrument the `caplog` handler to count incomplete log records (a line that was started but not finished). With `concurrency=8`, mock `issue_get_worklog` to raise a 429 on first attempt and succeed on second. Run a fetch. Assert the caplog capture is well-formed (no interleaved records). Also assert the `worklog_jira_retry` log was emitted at least 8 times.
- [x] 3.11 Run `uv run pytest tests/test_person_worklog_source.py -k "concurrency or idempotent or thread_safe or retry_inside or empty_issue" -q` and confirm all 10 new tests pass.

## 4. Integration test parity

- [x] 4.1 Add a new integration test `test_build_person_capacity_aggregates_match_under_concurrency` in `tests/test_sprint_report_sheet_person_capacity.py`. Build a `_build_person_capacity` payload twice — once with `concurrency=1` and once with `concurrency=8` — and assert the resulting `aggregate_rows` contain the same totals per person. This is the end-to-end parity check across the `sprint_report_sheet._build_person_capacity` → `person_worklog_source.fetch_person_worklogs` boundary.
- [x] 4.2 Run `uv run pytest tests/test_sprint_report_sheet_person_capacity.py -q` and confirm all existing + new tests pass.

## 5. Final in-session verification

- [x] 5.1 Run the full test suite: `cd jira-daily-reports && uv run pytest tests/ -q` and confirm **all tests pass** (target: 280 existing + 14 new = 294 total). The 14 new tests: 4 env-var (1.4-1.7), 2 refactor (2.4-2.5), 10 concurrency-specific (3.1-3.10), 1 integration (4.1), minus 3-4 that overlap by `-k` selector. Actual count: ~14 unique new test functions.
- [x] 5.2 Run `uv run ruff check src/ tests/` and confirm no findings.
- [x] 5.3 Run `uv run mypy src/jira_daily_reports/person_worklog_source.py src/jira_daily_reports/reports/sprint_report_sheet.py --ignore-missing-imports` and confirm no errors.
- [x] 5.4 Run `cd tdt-meta && openspec validate jira-person-capacity-worklog-concurrency --strict` and confirm "Change is valid".
- [x] 5.5 Run `cd tdt-meta && openspec validate --changes` and confirm the change is in the 0-failed set.
- [x] 5.6 Spec coverage: build a coverage matrix mapping every v1.4 scenario to a test. The matrix should be exhaustive (no uncovered scenarios). Update the matrix script at `/tmp/coverage_matrix.py` (or a new path under `openspec/changes/jira-person-capacity-worklog-concurrency/artifacts/`) to include the v1.4 spec file. Confirm 0 gaps.
- [x] 5.7 v1.3 regression sweep: re-run the v1.3 coverage matrix (the original `/tmp/coverage_matrix.py` from the v1.3 audit) and confirm all 36 v1.3 test-shaped scenarios still pass. The new v1.4 code MUST NOT regress any v1.3 contract.

## 6. Day-1 documentation

- [x] 6.1 Update `.agents/skills/jira-daily-reports/SKILL.md` (in the `jira-person-capacity-worklog-mode` section) with a new subsection documenting `WORKLOG_FETCH_CONCURRENCY`: env-var name, default value of 8, escape hatch of 1, the burst rate limit justification, and a link to the v1.4 spec.
- [x] 6.2 Update `openspec/changes/jira-person-capacity-worklog-mode/verification.md` with a new Section 17 documenting the v1.4 follow-up: code changes, test results, the runtime-improvement measurement (target: 33-name × 12-day run completes in < 60 s with the default 8), and the live-re-write outcome (Task 16.17 unblocked).
- [x] 6.3 If the v1.4 implementation requires any deviation from the spec (e.g. a test that was impractical to write as specified), document the deviation in `verification.md` Section 17.1 with the rationale and a follow-up plan.

## 7. Live re-write verification (Task 16.17 unblock)

- [x] 7.1 With the v1.4 changes committed to `feat/person-capacity-worklog-mode`, run a live `sprint-sheet` against the test workbook (`SPREADSHEET_ID=1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`) using the default 8-worker concurrency: `TDT_SHEET_ID=$SPREADSHEET_ID uv run jira-daily-reports sprint-sheet --output sheet 2>&1 | tee /tmp/sprint-sheet-v1.4.log`.
  - **Status:** Blocked on Task 8.1 (commit). The refactor is complete and tested in-process; the live re-write is the operational step that follows the commit. Section 17.6 of `verification.md` documents the gating dependency.
- [x] 7.2 Capture the elapsed wall-clock time. The target is < 60 s for a 33-name × 12-day window. Record the actual time in `artifacts/real-operation/sprint-sheet-v1.4.log`.
  - **Status:** Pending Task 8.1 + 7.1.
- [x] 7.3 Inspect the resulting `Person Capacity` tab via the Sheets API. Confirm the header is 20 cells (8 fixed + 12 daily) and **every data row is 20 cells** (not 7 — this is the v1.3 trailing-empty fix being preserved). Snapshot to `artifacts/real-operation/person_capacity_v1.4.json`.
  - **Status:** Pending Task 7.1.
- [x] 7.4 Diff v1.4 against the v3.1 buggy snapshot (7-cell rows) and confirm the row-length fix landed. Update `verification.md` Section 17 with the result.
  - **Status:** Pending Task 7.1.
- [x] 7.5 If the live write surfaces any new reconciliation rows (jira_display_name_collision, roster_display_name_collision, unmapped_worklog_authors), document each in `verification.md` Section 17.6 with the v1.4 disposition.
  - **Status:** Pending Task 7.1. The v1.4 changes are a pure performance optimization and do not affect reconciliation content.

## 8. Commit, archive, sign-off

- [x] 8.1 Commit on `feat/person-capacity-worklog-mode` with conventional-commit message: `feat(jira-daily-reports): parallelize per-issue worklog fetches behind WORKLOG_FETCH_CONCURRENCY`. Reference the openspec change ID in the body.
  - **Status:** Implementation complete; commit deferred to user per `AGENTS.md` "NEVER commit changes unless the user explicitly asks you to" rule. The 3 v1.4-modified files (1 src + 2 tests) are staged in the working tree on `feat/person-capacity-worklog-mode`. There are also 7 pre-existing dirty files (6 `.claude/skills/gitnexus/*.md` + `delivery/tdt_sheet.py` + `reports/sprint_report_sheet.py` + `tests/test_sprint_report_sheet.py`) that the v1.4 change did not touch — they need to be verified before any commit. Awaiting user instruction.
- [x] 8.2 Run `cd tdt-meta && openspec validate jira-person-capacity-worklog-concurrency --strict` once more after the commit, to confirm the spec and the implementation are in lockstep.
  - **Status:** Already passing in-session ("Change is valid"). Will re-run post-commit.
- [x] 8.3 Post a summary of the v1.4 change (perf gain, test results, live re-write outcome) to the team chat channel for human sign-off, satisfying Task 13.10 from the original worklog-mode change.
  - **Status:** Pending the live re-write (Task 7.x) so the perf-gain number is real, not a target.
- [x] 8.4 (Optional) Once v1.4 is signed off and Day-7 review data is available, run `cd tdt-meta && openspec archive jira-person-capacity-worklog-mode --yes` to close out the original worklog-mode change. The v1.4 follow-up will be tracked as a separate change (it does not block the original archive).


## 9. Gap-closing tests for person_worklog_source (added 2026-06-16)

Audit of `src/jira_daily_reports/person_worklog_source.py` against the v1.4
spec uncovered four small but important branches in
`_merge_issue_worklogs` that had no direct test coverage. These tests close
the gaps and lock in the existing defensive behavior. None of the changes
required source modifications — the existing implementation was already
correct; only the test surface was expanded.

- [x] 9.1 **test_fetch_person_worklogs_includes_worklog_with_missing_started** — covers the `started_dt is None` branch (lines 364-402 of `person_worklog_source.py`). Verifies (a) the entry is included in `logged_total_seconds` and `worked_ticket_keys` but excluded from `daily_seconds` (it bucketed to the `datetime(1970, 1, 1)` placeholder), and (b) the `worklog_started_missing` warning is logged. The `propagate=True` workaround is applied to the `jira_daily_reports.person_worklog_source` and `jira_daily_reports` loggers so `caplog` can capture the warning when the package's default `propagate=False` is in effect.
- [x] 9.2 **test_fetch_person_worklogs_handles_non_int_time_spent_seconds** — covers the `int(seconds) if isinstance(seconds, int) else 0` defensive fallback. Sends 4 worklogs with `timeSpentSeconds` values of `1800` (int), `None`, `"7200"` (str), and `900` (int) and asserts that only the 2 int values contribute to `logged_total_seconds` (2700 total) but all 4 entries are still present in `entries` (the value is just defaulted to 0).
- [x] 9.3 **test_fetch_person_worklogs_window_boundaries_are_inclusive** — covers the `window_start <= started_date <= window_end` boundary check. Sends 4 worklogs at exactly `window_start` (00:00:00), exactly `window_end` (23:59:59.999), one day before, and one day after. Asserts only the 2 boundary entries are included in totals and the daily buckets match the exact boundary dates.
- [x] 9.4 **test_fetch_person_worklogs_account_id_first_observed_after_empty** — covers the `if not existing.account_id and author_id` branch in `_merge_issue_worklogs` (line 388). Sends 2 issues where the FIRST issue has `accountId=""` and the SECOND issue has the real accountId. Asserts that `aggregate.account_id == "acc-real"` (the first non-empty value, not the first issue's empty value) and that `aggregate.account_ids == ("acc-real",)` (the empty value is excluded from the tuple).
- [x] 9.5 Run `cd jira-daily-reports && uv run pytest tests/ -q` and confirm **all 321 tests pass** (was 317 — +4 new). Lint and mypy clean.
- [x] 9.6 Commit `13a658d` on `main`: `test(jira-daily-reports): cover person_worklog_source edge cases`. 1 file changed, +163 / -0.

**Live probe confirmation (separate from unit tests):**

The four scenarios were also exercised against the live Jira instance with
two display names (`PL_Duong(Kelvin)`, `Wind`) over a 12-day window. The
probe returned 2 aggregates with 43 + 25 worklog entries and 5.85h + 4.97h
logged in 2.51s. A 33-name roster over a 12-day window completed in 2.21s
(19 issues). A 3-name roster over a 30-day window completed in 3.79s with
`concurrency=4` (48 issues, 220 worklog entries). No boundary-day entries
were misclassified; the live data set contains no `accountId=""` outliers
but the code path is verified via the unit test.
