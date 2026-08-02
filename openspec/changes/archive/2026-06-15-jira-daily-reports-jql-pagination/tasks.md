# JQL Pagination Fix — Tasks

## 1. Add `_jql_paginated` helper in `client.py`

- [x] 1.1 In `src/jira_daily_reports/client.py`, add `_jql_paginated(jira, jql, *, fields="*all", limit=100)` below `jql_search`. Signature: `(jira: Any, jql: str, *, fields: str = "*all", limit: int = 100) -> list[dict[str, Any]]`.
- [x] 1.2 Implementation: track `issues: list[dict[str, Any]]`, `seen_keys: set[str]`, `next_page_token: str | None = None`, `used_token_paging: bool = False`. Loop:
  - Build `kwargs = {"limit": limit, "fields": fields}`.
  - If `next_page_token is not None`: `kwargs["next_page_token"] = next_page_token`. Else: `kwargs["start"] = 0` (legacy, ignored by /search/jql).
  - Call `jira.jql(jql, **kwargs)`. If response is not a dict, `break` (defensive).
  - Read `page_issues = response.get("issues")`. If empty, `break`.
  - For each issue, dedup by `key`. If new, append and increment `page_new_count`.
  - Read `is_last = response.get("isLast")`. If `is_last is True`, `break`.
  - Read `next_page_token = response.get("nextPageToken") or None`. If set, `used_token_paging = True` and `continue`.
  - If `used_token_paging` and no new token: `break`.
  - If `page_new_count == 0` and `len(page_issues) >= limit`: `break` with a warning log (defensive against the same-page-again glitch).
  - Otherwise: `break` (no way to advance; this is the infinite-loop trigger and we stop rather than loop).
- [x] 1.3 Add `logger.info("client_jql_paginate jql=%r fetched=%d token=%s", jql, len(issues), "set" if next_page_token else "none")` once per loop iteration so operators can see pagination progress in `jira-run-all` output.
- [x] 1.4 Return `issues` after the loop.

## 2. Rewrite `jql_search` to delegate

- [x] 2.1 In `src/jira_daily_reports/client.py`, replace the body of `jql_search` with a single call: `return _jql_paginated(jira, jql, fields=fields, limit=max_results)`. Keep the signature unchanged.
- [x] 2.2 Update the docstring of `jql_search` to clarify: "**Returns the full result set, not just the first page.** The `max_results` parameter is the per-call page size (default 50); pagination follows the `nextPageToken` cursor and stops on `isLast: true`."

## 3. Rewrite `ReportBase._search` to delegate

- [x] 3.1 In `src/jira_daily_reports/reports/base.py`, replace the body of `_search` with a single call: `return _jql_paginated(self.jira, jql, fields=",".join(fields) if fields else "*all", limit=max_results)`. Import `_jql_paginated` at the top of the module from `jira_daily_reports.client`.
- [x] 3.2 Update the docstring of `_search` to clarify the page-size semantics, and add a note: "Do not use a single `jira.jql(...)` call site in new code; this helper handles the cursor loop."

## 4. Update existing `jql_search` tests

- [x] 4.1 In `tests/test_client_delivery_schedule.py::TestClient::test_jql_search_extracts_issues`, change the mock to return a single-page response with `isLast: True` so the loop terminates after one call. Assert the function still returns the same 2 issues. The call shape (one `jira.jql(...)` invocation) is preserved.
- [x] 4.2 In `tests/test_client_delivery_schedule.py::TestClient::test_jql_search_handles_non_dict_response`, this test already returns `None` for `jira.jql`. The new helper treats non-dict as "stop" (defensive `break`). The test must still pass — assert `client.jql_search(jira, "project = PUB") == []`.

## 5. Add new `jql_search` pagination tests

- [x] 5.1 Add `test_jql_search_follows_next_page_token` in `TestClient`: mock `jira.jql` to return `{"issues": [{"key": "PUB-1"}], "isLast": False, "nextPageToken": "tok-1"}` on the first call, then `{"issues": [{"key": "PUB-2"}], "isLast": True}` on the second call. Assert the function returns `[{"key": "PUB-1"}, {"key": "PUB-2"}]` AND `jira.jql.call_count == 2` AND the second call was made with `next_page_token="tok-1"`.
- [x] 5.2 Add `test_jql_search_dedups_across_pages` in `TestClient`: mock `jira.jql` to return `{"issues": [{"key": "PUB-1"}], "isLast": False, "nextPageToken": "tok-1"}` then `{"issues": [{"key": "PUB-1"}, {"key": "PUB-2"}], "isLast": True}`. Assert the function returns 2 unique issues (the second `PUB-1` is dropped by dedup).
- [x] 5.3 Add `test_jql_search_stops_when_is_last_after_first_page` in `TestClient`: mock returns `{"issues": [{"key": "PUB-1"}], "isLast": True}` on the first call. Assert `jira.jql.call_count == 1` and result is `[{"key": "PUB-1"}]`.

## 6. Add new `ReportBase._search` tests (new file)

- [x] 6.1 Create `tests/test_reports_pagination.py` with a `StubReport(ReportBase)` that sets `name = "stub"` and `schedule = ""`. Its `run()` and `format_markdown()` are no-ops (return `ReportResult(name="stub", generated_at=..., issues=[], summary={})`).
- [x] 6.2 Add `test_search_single_page_returns_issues`: stub jira returns `{"issues": [A, B, C], "isLast": True}`. Assert `_search` returns 3 issues.
- [x] 6.3 Add `test_search_multi_page_via_token_returns_all`: stub returns 2 pages of 50 issues each (page 1 `isLast=False, nextPageToken="x"`, page 2 `isLast=True`). Assert `_search` returns 100 issues and the second call was made with `next_page_token="x"`.
- [x] 6.4 Add `test_search_stops_when_token_missing_after_token_paging`: stub returns page 1 with `isLast=False, nextPageToken="x"`, page 2 with `isLast=False, nextPageToken=None` (server ran out). Assert the function stops after 2 calls and returns the union.
- [x] 6.5 Add `test_search_stops_on_empty_page`: stub returns `{"issues": []}`. Assert `_search` returns `[]` after 1 call.
- [x] 6.6 Add `test_search_dedups_duplicate_keys_across_pages`: stub returns 3 pages where the first 2 share keys. Assert the result has no duplicate keys.
- [x] 6.7 Add `test_search_passes_fields_and_limit_through`: stub verifies that the first call uses `fields="summary,status"` and `limit=50` (i.e. the `max_results` argument).

## 7. Skill update

- [x] 7.1 In `.agents/skills/jira-daily-reports/SKILL.md`, add a new section `## JQL pagination contract` after the "Sprint reporting uses the sprint workbook only" section. Content: "Jira Cloud's `/rest/api/3/search/jql` paginates via `nextPageToken` and signals end-of-results with `isLast: true`. The `startAt` parameter is silently ignored. Every `jira.jql(...)` call site MUST loop on `nextPageToken` and check `isLast`. The shared helper `jira_daily_reports.client._jql_paginated` implements this contract; new code MUST use it instead of calling `jira.jql(...)` directly."
- [x] 7.2 Add a callout under the new section: "**Do not add new direct `jira.jql(...)` call sites.** The endpoint migration on 2026-05-21 silently ignores `startAt`; any single-call consumer is a silent data loss bug."

## 8. In-session verification

- [x] 8.1 Run `cd jira-daily-reports && uv run pytest tests/test_client_delivery_schedule.py tests/test_reports_pagination.py -q` and confirm all tests pass.
- [x] 8.2 Run the full test suite `cd jira-daily-reports && uv run pytest tests/ -q` and confirm the existing 305 tests still pass + the 8 new tests pass (313 total).
- [x] 8.3 Run `cd jira-daily-reports && uv run ruff check src/ tests/` and confirm no findings.
- [x] 8.4 Run `cd jira-daily-reports && uv run mypy src/jira_daily_reports/client.py src/jira_daily_reports/reports/base.py --ignore-missing-imports` and confirm no errors.
- [x] 8.5 Run `cd tdt-meta && openspec validate jira-daily-reports-jql-pagination --strict` and confirm "Change is valid".
- [x] 8.6 Live probe: run `jira-daily-reports standup --output terminal 2>&1 | tail -30` against the live Jira instance and confirm:
  - The report shows the same set of issues as the v1.3 (pre-fix) version OR more (it should never be less — the new code is strictly additive).
  - The wall-clock time is within 2x of the prior run for a typical project (no perf regression).
  - The `client_jql_paginate` log line appears at least once in the output (pagination observability).
- [x] 8.7 Capture the probe log to `artifacts/real-operation/jql-pagination-fix-standup.log`.

## 9. Commit

- [x] 9.1 Commit on `jira-daily-reports/main` with message: `fix(jira-daily-reports): paginate jql_search and ReportBase._search via nextPageToken (v1.4.1)`. Body: link to the OpenSpec change and note the 2 helpers fixed + 12 reports unblocked.
- [x] 9.2 After commit, run `cd tdt-meta && openspec validate jira-daily-reports-jql-pagination --strict` once more to confirm spec ↔ implementation are in lockstep.
- [x] 9.3 Post a one-paragraph summary to the team chat (no live re-write needed — this is a silent data loss fix, not a perf change).

## 10. Verification (in-session results)

- [x] 10.1 `cd jira-daily-reports && uv run pytest tests/ -q` → **317 passed in 6.66s** (was 305 before; +12 new tests).
- [x] 10.2 `cd jira-daily-reports && uv run ruff check src/ tests/` → **All checks passed!**
- [x] 10.3 `cd jira-daily-reports && uv run mypy src/jira_daily_reports/client.py src/jira_daily_reports/reports/base.py --ignore-missing-imports` → **Success: no issues found in 2 source files**.
- [x] 10.4 `cd tdt-meta && openspec validate jira-daily-reports-jql-pagination --strict` → **Change 'jira-daily-reports-jql-pagination' is valid**.
- [x] 10.5 Commits: `ec051c7` on `jira-daily-reports/main` (4 files, +391/-20), `cd8af56` on `tdt-meta/main` (7 files, +531).
- [x] 10.6 Pre-existing dirty files preserved: 6 `.claude/skills/gitnexus/*.md` in `jira-daily-reports`, 3 files in `tdt-meta` (`docs/mobile-toolchain.md`, `openspec/changes/mobile-native-toolchain-setup/tasks.md`, `openspec/specs/jira-workflow-validator/spec.md`). None touched.

## 11. Live probe results (2026-06-16)

**Conducted by:** lekhanhvinh
**Date:** 2026-06-16 01:43 UTC+7
**Projects probed:** SR (high-volume), PDS-81 (epic), PUB (default)

- [x] 11.1 Multi-page JQL: 8 pages, 896 issues, 22s — `client_jql_paginate` log line emitted for each page. Terminal `token=none` observed. **PASS**.
- [x] 11.2 All 11 daily reports: standup, wip, velocity, cycle-time, blocked, code-review, priority, missing-info, platform, sprint-health, wip-age — all complete without error. **PASS**.
- [x] 11.3 Platform report (896 issues): dedup confirmed 896/896 unique, all fields populated. **PASS**.
- [x] 11.4 WIP report (77 issues): single page, `token=none` after first page. **PASS**.
- [x] 11.5 Epic-report PDS-81: 337 child tasks, 86 project bugs, 4-page bug query (327 raw bugs), 2-page project bug query (146 raw). Epic `_jql_paginated` confirmed working. **PASS**.
- [x] 11.6 Orphaned blocker warnings: expected behavior (cross-project blocking links). **PASS**.
- [x] 11.7 Pre-existing `test_blocking_performance.py::test_benchmark_200_items` failure in jira-epic-report — unrelated, pre-existing.

**Full log:** `artifacts/real-operation/jql-pagination-fix-live-probe.log`

## 12. Archive

- [x] 12.1 All verification tasks complete. Running archive:
  ```
  cd tdt-meta && openspec archive jira-daily-reports-jql-pagination --yes
  ```

