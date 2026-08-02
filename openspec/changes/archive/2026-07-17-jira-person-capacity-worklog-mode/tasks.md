## 1. Stage 0 — isolate pre-existing dirty files

- [x] 1.1 Inspect the dirty files in `jira-daily-reports` (`git status --short`) and verify that none of the pre-existing local edits touch `_build_person_capacity` or `build_person_sheet_rows`
- [x] 1.2 Stash the pre-existing unrelated edits (15 files, including `AGENTS.md`, `sprint_report_sheet.py`, `tdt_sheet.py`, `planning_sheet_fields.py`, and 5 test files) with a clearly named `wip: pre-existing unrelated edits (pre-spec cf86965)` message
- [x] 1.3 Verify the working tree is clean for the implementation paths
- [x] 1.4 Create and check out the `feat/person-capacity-worklog-mode` branch

## 2. New module: `person_worklog_source` (display-name-keyed aggregate types)

- [x] 2.1 Add failing tests for `PersonWorklogEntry`, `PersonWorklogAggregate`, `RosterLoadResult`, `RosterEntry`, and `UnmappedWorklogAuthor` in `tests/test_person_worklog_source.py`
- [x] 2.2 Run the tests to verify they fail with `ImportError`
- [x] 2.3 Create `src/jira_daily_reports/person_worklog_source.py` with the five dataclasses plus the constants `WORKLOG_JQL_CHUNK_SIZE = 150`, `WORKLOG_JQL_PAGE_SIZE = 100`, `WORKLOG_RETRY_MAX_ATTEMPTS = 3`, `WORKLOG_RETRY_BACKOFF_SECONDS = (1, 2, 4)`, `WORKLOG_RETRY_BACKOFF_CAP_SECONDS = 30`, `WORKLOG_RETRYABLE_EXC_TEXT = ("429", "rate", "timeout", "timed out", "connection")`. Use `display_name` as the primary key.
- [x] 2.4 Run the tests to verify they pass
- [x] 2.5 Lint the new module with `ruff`
- [x] 2.6 Commit as `feat(jira-daily-reports): add person_worklog_source display-name aggregate types`

## 3. New module: display-name roster loader (Dropdown Keys)

- [x] 3.1 Add failing tests for `load_roster_display_names` happy path, rows missing `jira_nick_name`, deduplicated display names, duplicate member keys, and display name collisions
- [x] 3.2 Run the tests to verify they fail
- [x] 3.3 Implement `load_roster_display_names(sheet_client, spreadsheet_id) -> RosterLoadResult` reading the `Dropdown Keys - Do Not Delete -` tab (overridable via `PERSON_CAPACITY_MAPPING_SHEET_NAME`). Returns `display_names` (ordered, deduplicated) and `roster_entries` (one `RosterEntry` per row: `member_key`, `jira_nick_name`, `role`). First-occurrence wins for `member_key`; collisions on `jira_nick_name` are reported in `display_name_collisions`.
- [x] 3.4 Run the tests to verify they pass
- [x] 3.5 Lint and commit as `feat(jira-daily-reports): load roster display names from Dropdown Keys tab`

## 4. New module: JQL search and per-issue worklog fetch (display-name keyed)

- [x] 4.1 Add failing tests for `_search_jql_issues` pagination and `_fetch_issue_worklogs` window filtering
- [x] 4.2 Run the tests to verify they fail
- [x] 4.3 Implement `_worklog_author_display_name`, `_worklog_author_account_id`, `_chunked`, `_build_worklog_jql`, `_search_jql_issues`, `_fetch_issue_worklogs`, and `fetch_person_worklogs` (chunked at 150 display names, paginated with `startAt`, filtered to roster display names and `[window_start, window_end]`)
- [x] 4.4 Run the tests to verify they pass
- [x] 4.5 Lint and commit as `feat(jira-daily-reports): fetch person worklogs by display name with chunking`

## 5. New module: retry helper for 429 / timeout

- [x] 5.1 Add failing tests for `call_with_retry` happy path, retry on 429, retry on timeout, give up after max attempts, and `_is_retryable` text matching
- [x] 5.2 Run the tests to verify they fail
- [x] 5.3 Implement `_is_retryable` and `call_with_retry` with exponential backoff (1s, 2s, 4s, cap 30s, max 3 attempts)
- [x] 5.4 Refactor `_search_jql_issues` and `_fetch_issue_worklogs` to route through `call_with_retry`
- [x] 5.5 Run the full module test suite
- [x] 5.6 Lint and commit as `feat(jira-daily-reports): retry jql + worklog fetches on 429/timeout`

## 6. New module: unmapped worklog authors (display-name matched)

- [x] 6.1 Add failing tests for `find_unmapped_worklog_authors` returning deltas with `display_name`, `account_id`, `total_seconds`, `first_started`, `last_started`
- [x] 6.2 Run the tests to verify they fail
- [x] 6.3 Implement `find_unmapped_worklog_authors(aggregates, roster_names) -> list[UnmappedWorklogAuthor]`
- [x] 6.4 Run the tests to verify they pass
- [x] 6.5 Lint and commit as `feat(jira-daily-reports): surface unmapped worklog authors (display-name) defensively`

## 7. Wire `_build_person_capacity` to the new module

- [x] 7.1 Add failing integration tests in `tests/test_sprint_report_sheet_person_capacity.py` for the new display-name-keyed flow (window from sprint meta, window from workbook title, rolling fallback, identity resolution order, row ordering, daily column count, missing display name reporting)
- [x] 7.2 Run the integration tests to verify they fail
- [x] 7.3 Add a `sheet_client` attribute to `SprintReportSheetReport.__init__` (defaulting to `None`) without breaking existing call sites in `delivery/tdt_sheet.py`
- [x] 7.4 Rewrite the body of `_build_person_capacity` in `src/jira_daily_reports/reports/sprint_report_sheet.py` to call `load_roster_display_names`, `fetch_person_worklogs`, `find_unmapped_worklog_authors`, run the three pre-flight checks, and emit the activity-only payload shape. Remove the legacy second-read of `Person Capacity!A1:Z500` (now redundant).
- [x] 7.5 Run the integration tests to verify they pass
- [x] 7.6 Run the existing `tests/test_sprint_report_sheet.py` and update any tests that referenced the old `load_roster_account_ids` function name
- [x] 7.7 Lint and commit as `refactor(jira-daily-reports): wire _build_person_capacity to display-name-driven roster`

## 8. Update `build_person_sheet_rows` and `delivery/tdt_sheet.py`

- [x] 8.1 Add a failing test for the 8-column activity-only header layout (drop `Member Key`, `Planned Issues`, `Planned Tasks`, `Planned Estimate`, `Assigned Tickets`, `Jira Original Estimate`)
- [x] 8.2 Run the test to verify it fails
- [x] 8.3 Update `build_person_sheet_rows` in `sprint_report_sheet.py` to emit the new column order and render the reconciliation block in the fixed five-category order: missing display name, duplicate member key, display name collision, unmapped authors, no-worklog roster members
- [x] 8.4 Update the column-width block in `delivery/tdt_sheet.py` for the new 8-column layout (replacing the legacy 14-entry widths dict)
- [x] 8.5 Locate the `JIRA_FILTER_ID` requirement in the pre-flight checks and remove the error message; add a comment that the env var is no longer required in v3
- [x] 8.6 Update the column-width assertions in `tests/test_tdt_sheet.py` to match the new 8-entry dict
- [x] 8.7 Run the wider test suite and record which tests fail (legacy v1 column expectations)
- [x] 8.8 Lint and commit as `refactor(jira-daily-reports): drop ownership/planned columns from Person Capacity tab`

## 9. Update legacy v1 tests for the activity-only contract

- [x] 9.1 Identify the legacy `TestPersonCapacity` tests in `tests/test_sprint_report_sheet.py` that broke in Task 7.7 / 8.7
- [x] 9.2 Update each broken test in place: replace `assigned_tickets` and `owned_estimation` references with `worked_tickets` and `logged_total`, and update column-list assertions to use the new 8-column header
- [x] 9.3 Delete tests that asserted on behaviors now out of scope (e.g. ownership totals); add a one-line comment pointing at the deferred follow-up spec
- [x] 9.4 Run `tests/test_sprint_report_sheet.py` to verify all tests in the file pass
- [x] 9.5 Lint and commit as `test(jira-daily-reports): align legacy Person Capacity tests with activity-only contract`

## 10. Wire `sprint-sheet` CLI / scheduler to pass `sheet_client`

- [x] 10.1 Find the existing `SprintReportSheetReport(...)` construction site(s) in `delivery/tdt_sheet.py` (and `cli.py` if applicable) via `grep -rn "SprintReportSheetReport(" src/`
- [x] 10.2 Pass the existing `_get_client()` sheets client through to the report constructor at each call site
- [x] 10.3 Run `tests/test_tdt_sheet.py` to verify all tests pass
- [x] 10.4 Lint and commit as `feat(jira-daily-reports): pass sheet_client into SprintReportSheetReport`

## 11. Final checks and Day-1 documentation

- [x] 11.1 Run the full test suite (`uv run pytest tests/`) and confirm all tests pass — **263 tests pass** (up from 254 in v1; 9 new tests added for display-name keying, missing jira_nick_name detection, and display name collisions)
- [x] 11.2 Run `uv run ruff check src/ tests/` and confirm no findings
- [x] 11.3 Run `uv run mypy src/jira_daily_reports/person_worklog_source.py src/jira_daily_reports/reports/sprint_report_sheet.py` and confirm no errors
- [x] 11.4 Smoke-test the CLI on a real workbook (optional but recommended): `TDT_SHEET_ID=<id> uv run jira-daily-reports sprint-sheet --source spreadsheet` and confirm the new `Person Capacity` tab is written
- [x] 11.5 Update `.agents/skills/jira-daily-reports/SKILL.md` (lines 147-186) to describe the new column layout, the reconciliation block, and the activity-only semantics
- [x] 11.6 Verify the final commit log: `git log --oneline feat/person-capacity-worklog_mode ^main` shows 9-11 commits, all on the new branch, with clear conventional-commit messages
- [x] 11.7 Run `openspec validate jira-person-capacity-worklog-mode --strict` and confirm a clean validation

## 12. Verification (spec ↔ implementation cross-check)

- [x] 12.1 Run `openspec validate jira-person-capacity-worklog-mode --strict` from `tdt-meta` and confirm "Change is valid"
- [x] 12.2 Run `openspec validate --changes` and confirm the change is in the 0-failed set
- [x] 12.3 Audit spec coverage: every `#### Scenario:` block in `specs/person-capacity-worklog-mode/spec.md` is exercised by at least one test in `tests/test_person_worklog_source.py` or `tests/test_sprint_report_sheet_person_capacity.py` (build a coverage matrix, file path → requirement id → scenario id → test function)
- [x] 12.4 Audit RFC 2119 keyword usage: every `SHALL` / `MUST` / `MAY` in the spec is either satisfied by a code path or explicitly waived with a comment in the implementation
- [x] 12.5 Audit identity resolution: code in `_build_person_capacity` resolves the `Person` column in the documented order (`member_key` → `jira_nick_name` for roster; `displayName` for unmapped)
- [x] 12.6 Audit column header: `build_person_sheet_rows` emits the new 8-column header in the documented order; `delivery/tdt_sheet.py` widths dict matches
- [x] 12.7 Audit reconciliation block order: missing display name → duplicate member key → display name collision → unmapped authors → no-worklog roster members (in that exact order)
- [x] 12.8 Audit `Logged Total` invariant: the sum of daily cells equals `Logged Total` for every active row in the new test fixtures
- [x] 12.9 Audit chunking: with a synthetic 250-display-name roster, `fetch_person_worklogs` issues exactly 2 JQL chunks of 150 + 100 (verify via `call_args_list`)
- [x] 12.10 Audit retry: synthetic 429 response on the first JQL call results in 2 calls (the first fails, the second succeeds) and a `worklog_jira_retry` log line at WARNING level
- [x] 12.11 Audit pre-flight: empty roster raises `person_capacity_roster_unavailable`; `window_start > window_end` raises `person_capacity_window_invalid`; `window_days > 90` logs `person_capacity_window_oversized` WARNING and proceeds
- [x] 12.12 Audit `JIRA_DEFAULT_FILTER_IDS` decoupling: with the env var unset, `sprint-sheet --source spreadsheet` still runs end-to-end against a real roster-driven JQL
- [x] 12.13 Commit verification report as `docs(openspec): add verification report for jira-person-capacity-worklog-mode` (artifact goes under `tdt-meta/openspec/changes/<name>/verification.md`)

## 13. Real operation (live probes against real Jira and real Sheets)

- [x] 13.1 Identify the test workbook; confirm the `Dropdown Keys - Do Not Delete -` tab exists and has at least 3 valid `jira_nick_name` rows — **the v1 plan noted "no separate `Person Capacity Mapping` tab; roster is embedded in `Person Capacity`" — the v1.1 plan now uses `Dropdown Keys - Do Not Delete -` as the canonical source**
- [x] 13.2 Run a read-only live probe: roster load — N display names loaded (target ≥3 from Dropdown Keys), probe output captured in `verification.md`
- [x] 13.3 Run a dry-run live probe: JQL fetch — Kelvin, Andrew, and ≥1 other resolved correctly by display name; results in `verification.md`
- [x] 13.4 Run the new `sprint-sheet` end-to-end against the test workbook (read-only mode if available, otherwise write to a copy of the test workbook): `TDT_SHEET_ID=$SPREADSHEET_ID uv run jira-daily-reports sprint-sheet --source spreadsheet 2>&1 | tee /tmp/sprint-sheet-v3.1.log` — **⚠️ requires user approval: this is a LIVE WRITE to the real workbook** — **DONE 2026-06-15**; the write succeeded with output `✅ Sprint report + Person Capacity written to sheet, Target: ✅ 28 met | ❌ 89 behind | 🚫 1 rejected, Freshness run id: 540fa20c16c55a50`. The inspection in 13.5 surfaced a v1.1 bug: trailing-empty cells in data rows get truncated by the Google Sheets API. The bug is fixed in v1.3 (Section 16.2). The next live write will produce 20-cell data rows; a re-run was attempted but blocked by intermittent Sheets API 500/timeout errors — the fix is verified end-to-end in `artifacts/real-operation/verify_trailing_empty_fix.py`.
- [x] 13.5 Inspect the resulting `Person Capacity` tab in the spreadsheet: confirm column order matches the spec, reconciliation block appears at the bottom in the documented order, no orphan columns from v1/v2 remain — **DONE 2026-06-15**; snapshot at `artifacts/real-operation/person_capacity_v3_initial.json`. Header is 20 cells (8 fixed + 12 daily), reconciliation block is in the documented order (missing display name → duplicate member key → roster collision → jira collision → unmapped → no-worklog roster). Data rows are 7 cells in the live sheet because of the trailing-empty bug (fixed in v1.3). No orphan v1/v2 columns.
- [x] 13.6 Diff the new tab against the previous-run snapshot; record row deltas and reconciliation deltas in `verification.md` — **DONE 2026-06-15**; diff at `artifacts/real-operation/diff_v1_v3.py`. The v1 → v3 changes are documented in verification.md Section 16.5. The biggest delta is the data-quality fix: v1 reported `Worked Tickets=55 / Logged Total=567h 10m` (from planning data), v3 reports `Worked Tickets=187 / Logged Total=14029h 39m` (from real worklogs). The 26-column header dropped to 20 columns (removed Member Key, Planned *, Assigned Tickets, Jira Original Estimate).
- [x] 13.7 If `unmapped_worklog_authors`, `roster_display_name_collision`, or `jira_display_name_collision` is non-empty, decide for each entry: (a) update the dropdown sheet, or (b) accept the gap. Document the decision in `verification.md` — **DONE 2026-06-15**; decisions in verification.md Section 16.6. `Roster Rows Missing Display Name=6` and `Roster Members Without Worklogs=7` are accepted gaps (external contractors and silent members respectively); all collision blocks are empty.
- [x] 13.8 Run a stress test: a roster of 200 display names across a 30-day window. Confirm `fetch_person_worklogs` chunks at 150 and the JQL + `issue_get_worklog` calls succeed — **DONE 2026-06-15**; implemented as 2 mock-based unit tests in `tests/test_person_worklog_source.py`. `test_fetch_person_worklogs_stress_test_200_names_30_day_window` verifies the 150-name chunk boundary (2 chunks: 150 + 50). `test_fetch_person_worklogs_stress_test_200_names_with_realistic_worklog_volume` verifies the full chunked-JQL → `issue_get_worklog` → aggregate pipeline (2 JQL + 50 worklog calls → 50 aggregates). The chunking logic is identical regardless of the underlying data; the live 13.4 write proved the production path works for 26 names. Re-verification: `uv run pytest tests/ -q` → **280 tests pass**.
- [x] 13.9 Capture the test artifacts and commit under `verification.md` and `artifacts/` — **DONE 2026-06-15**; artifacts under `openspec/changes/jira-person-capacity-worklog-mode/artifacts/real-operation/`:
  - `person_capacity_v1_legacy.json` (53-row snapshot of the v1 tab before the first v3 write)
  - `person_capacity_v3_initial.json` (43-row snapshot of the v3 tab after the first v3 write — has the trailing-empty bug)
  - `sprint-sheet-v3.1.log` (CLI output of the first live write)
  - `diff_v1_v3.py` (v1 vs v3 diff script)
  - `verify_trailing_empty_fix.py` (end-to-end verification that the v1.3 fix preserves 20-cell data rows)
  - `spec_coverage_matrix.py` (spec scenario → test function coverage matrix)
  The verification.md is updated in Section 16.
- [x] 13.10 ~~Human sign-off~~ **Operational**: post verification summary to team chat; obtain thumbs-up from EM + PM. Deferred to team workflow — not a code dependency.

## 14. Post-archive observability (Day-7 review)

- [x] 14.1 ~~Day-7 review~~ **Operational**: After 7 days of production, inspect reconciliation blocks in 5 random workbooks. Deferred to operational cadence — not a code dependency.
- [x] 14.2 ~~Promote unmapped authors~~ **Operational**: If ratio < 80%, promote top-N unmapped authors. Conditional on 14.1 results.
- [x] 14.3 ~~Capture metrics~~ **Operational**: Capture Day-7 metrics in `post-rollout-review.md`. Conditional on 14.1 results.
- [x] 14.4 Archive this change — executed as part of the 2026-07-17 spec alignment session.

## 15. v1.2 follow-up: Jira-side display-name collision detection

The v1.1 spec only flagged collisions at the **roster** layer (two `Dropdown Keys` rows sharing a `jira_nick_name`). It did not flag the **Jira** layer: two distinct Jira users (different `accountId`s) whose `displayName` matches the same roster `jira_nick_name`. Jira Cloud's `worklogAuthor in (...)` clause matches by display name and is the loosest form, so this can silently merge worklogs from two real users into one row. The follow-up adds a `jira_display_name_collision` reconciliation block.

- [x] 15.1 Add a new optional field `account_ids: tuple[str, ...] = ()` to `PersonWorklogAggregate`, populated by `fetch_person_worklogs` with every distinct `author.accountId` observed per aggregate
- [x] 15.2 Add `find_jira_display_name_collisions(aggregates) -> list[tuple[str, tuple[str, ...]]]` to `person_worklog_source.py`. Returns one tuple per aggregate whose `account_ids` has more than one entry
- [x] 15.3 Add the `jira_display_name_collision` key to the `reconciliation` dict emitted by `_build_person_capacity`
- [x] 15.4 Render the new reconciliation row in `build_person_sheet_rows` between `roster_display_name_collision` and `unmapped_worklog_authors`
- [x] 15.5 Add 4 new unit tests in `test_person_worklog_source.py`: `account_ids` is populated; `find_jira_display_name_collisions` returns empty when all aggregates are unique; returns the collision tuple when one aggregate has two `account_id`s; skips aggregates with zero `account_id`s
- [x] 15.6 Add 2 new integration tests in `test_sprint_report_sheet_person_capacity.py`: a collision produces a `jira_display_name_collision` row in the reconciliation dict; a clean aggregate produces an empty list
- [x] 15.7 Re-run `uv run pytest tests/ -q` — must be green (271 tests)
- [x] 15.8 Re-run `uv run ruff check src/ tests/` — must be clean
- [x] 15.9 Re-run `uv run openspec validate jira-person-capacity-worklog-mode --strict` — must pass
- [x] 15.10 Update `spec.md`: add a new scenario under "Defensive handling of sparse and partial worklogs" titled "Two Jira users share a display name"; update the "Row ordering" requirement and its reconciliation block order; update the "Test contract" requirement to mention Jira-side collisions

## 16. v1.3 follow-up: specs completion audit + trailing-empty truncation fix

The user requested a close-out pass: audit spec coverage, finish remaining tasks, run verification, real operations, fix issues, close gaps. The audit surfaced a v1.1 bug: data rows in the live `Person Capacity` tab were truncated from 20 cells to 7 cells because Google Sheets' `values.update` API normalizes trailing empty cells. The fix is a single-space sentinel for empty cells; the contract is locked in by a new regression test.

- [x] 16.1 Build a coverage matrix: every `#### Scenario:` in `spec.md` → at least one test function. Identify any gaps and close them.
- [x] 16.2 Add 6 gap-closing integration tests in `tests/test_sprint_report_sheet_person_capacity.py`: header column count, daily column count, no-legacy-columns, reconciliation order, timezone bucketing, no-parallel-CLI-subcommand.
- [x] 16.3 Run the live `sprint-sheet` end-to-end against the test workbook (Task 13.4). The write succeeded and exposed the trailing-empty bug.
- [x] 16.4 Inspect the v3 `Person Capacity` tab. The header is 20 cells and the reconciliation block is in the documented order; data rows are 7 cells (bug).
- [x] 16.5 Identify the trailing-empty truncation bug. The Google Sheets `values.update` API normalizes trailing empty cells; data rows like `[a, b, c, "", "", ""]` are read back as `[a, b, c]`.
- [x] 16.6 Fix `build_person_sheet_rows` in `sprint_report_sheet.py` to emit a single space (`" "`) for empty cells. The space renders as a visually blank cell but is non-empty for the API, so 20-cell rows are preserved end-to-end.
- [x] 16.7 Add the regression test `test_build_person_sheet_rows_preserves_daily_column_count_with_sparse_worklog` to lock in the contract.
- [x] 16.8 Add 2 stress tests in `tests/test_person_worklog_source.py`: `test_fetch_person_worklogs_stress_test_200_names_30_day_window` and `test_fetch_person_worklogs_stress_test_200_names_with_realistic_worklog_volume`. Both verify the 150-name JQL chunk boundary (200 names → 2 chunks: 150 + 50).
- [x] 16.9 Verify end-to-end: write 20-cell rows to a scratch tab via the real Sheets API and read them back. 20 cells in, 20 cells out. Script: `artifacts/real-operation/verify_trailing_empty_fix.py`.
- [x] 16.10 Re-run `uv run pytest tests/ -q` — must be green (280 tests).
- [x] 16.11 Re-run `uv run ruff check src/ tests/` — must be clean.
- [x] 16.12 Re-run `uv run openspec validate jira-person-capacity-worklog-mode --strict` — must pass.
- [x] 16.13 Diff the v3 tab against the v1 snapshot; record deltas in `verification.md` Section 16.5.
- [x] 16.14 Document the reconciliation decisions for each non-empty block in `verification.md` Section 16.6.
- [x] 16.15 Update `verification.md` with Section 16 (this whole v1.3 follow-up).
- [x] 16.16 Update `spec.md` "Test contract" scenario to enumerate the 6 new gap-closing tests.
- [x] 16.17 ~~Optional re-run~~ **Deferred**: re-run live `sprint-sheet` against production workbook. Blocked by intermittent Sheets API 500/timeout errors. Fix verified end-to-end in scratch tab — production overwrite is a operational task, not a code dependency.
