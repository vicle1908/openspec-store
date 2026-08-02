## 1. Module scaffolding and shared helpers

- [x] 1.1 Create `src/jira_daily_reports/dev_performance/` package with empty `__init__.py`
- [x] 1.2 Add `stale_thresholds.py` with `StaleThresholds.from_env()` loader (returns per-status day thresholds; default 7 days for unknown statuses, `False` not-stale; emits one-time-per-run warning for unknown statuses)
- [x] 1.3 Add `metrics.py` pure helpers: `compute_in_progress_at(changelog, ownership_period)`, `compute_reopen_count(changelog, ownership_period, done_statuses)`, `compute_cycle_time(in_progress_at, first_deploy_at)`, `compute_last_status_change_days(changelog, now)`, `compute_stale_flag(status, last_change, thresholds)`
- [x] 1.4 Add unit tests for `stale_thresholds.py` and `metrics.py` covering all default fallbacks and edge cases

## 2. Jira and GitLab source facades

- [x] 2.1 Add `source.py` with `JiraSource.search_dev_tickets(roster_account_ids, lookback_hours, dev_in_charge_field_id)` — wraps `PatchedJira.jql(...)` (the shared `_jql_paginated` helper), chunks `IN (...)` at 150 accountIds, returns `(issue_key, issue_payload)` tuples
- [x] 2.2 Add `JiraSource.fetch_changelog(issue_key, paginate=True)` — full changelog with status + Dev in Charge field histories
- [x] 2.3 Add `JiraSource.fetch_remote_links(issue_key)` — returns list of `git.ecomedic.vn` URLs from `/rest/api/3/issue/{key}/remotelink`
- [x] 2.4 Add `JiraSource.resolve_dev_in_charge(issue_payload, dev_in_charge_field_id, roster)` — handles null, group expansion, and roster membership check; returns list of `(account_id, display_name)` tuples for valid attribution plus an `unmapped` flag
- [x] 2.5 Add `GitlabSource.find_project_by_key(project_key)` — returns matching GitLab project ID or None
- [x] 2.6 Add `GitlabSource.find_mr_by_branch_regex(project_id, issue_key)` — scans `merge_requests?source_branch=~^{KEY}-.*`
- [x] 2.7 Add `GitlabSource.fetch_mr(project_id, mr_iid)` and `GitlabSource.fetch_deployments(project_id, mr_iid, environment_name)`
- [x] 2.8 Wire retry semantics: Jira via existing `call_with_retry` from `person_worklog_source` (3 attempts, exp backoff capped 30s); GitLab single-attempt retry only

## 3. Join layer and metric aggregation

- [x] 3.1 Add `join.py` with `resolve_linked_mrs(issue_key, remote_links, gitlab_source, project_key)` — remote-link precedence, branch regex fallback, MR dedup by `id`, returns `(linked_mrs, join_method, deployments)`
- [x] 3.2 Add unit tests for `join.py` covering both paths, dedup, and the missing-MR case
- [x] 3.3 Add `row_builder.py` with `build_row(developer, ticket, changelog, linked_mrs, deployments, thresholds, done_statuses, now)` returning a `RowPayload` (cols 1–20 + `evidence` JSON)
- [x] 3.4 Add `row_builder.compute_merge_ranges(sorted_rows)` returning a list of `MergeRange` (start_row, end_row, cols 1–7) for developers with ≥2 tickets
- [x] 3.5 Add `summary_builder.py` with `build_footer_rows(sorted_rows, done_statuses)` returning per-developer aggregates (median, p90 for cycle time and reopens, plus counts)
- [x] 3.6 Add unit tests for `row_builder.py` and `summary_builder.py` with fixture data

## 4. SQLite diff cache

- [x] 4.1 Add `diff_cache.py` with `DiffCache(path)` context manager that opens SQLite, runs `BEGIN IMMEDIATE` advisory lock, yields the handle, commits on exit
- [x] 4.2 Add `DiffCache.fetch(developer_account_id, issue_key)` returning the cached payload or None
- [x] 4.3 Add `DiffCache.upsert(developer_account_id, issue_key, payload)` writing the JSON payload + `written_at` timestamp
- [x] 4.4 Add `DiffCache.evict_older_than(seconds)` called at run start with `25 * 3600`
- [x] 4.5 Add `DiffCache.handle_corruption()` — drops the cache table and emits `dev_performance_cache_reset reason=corruption`
- [x] 4.6 Add unit tests for `diff_cache.py` covering: idempotent skip, change detection, corruption recovery, concurrent-run lock rejection

## 5. Sheet writer and CLI entry

- [x] 5.1 Add `sheet_writer.py` with `write_tab(sheets_client, spreadsheet_id, tab_name, sorted_rows, footer_rows, reconciliation_rows, merge_ranges, header_row)` using `SheetsClient.write(...)` for cell data, `SheetsClient.write_with_links(...)` for `=HYPERLINK(...)` formulas, and `SheetsClient.batch_update(...)` for `mergeCells` + `updateSheetProperties` (frozen row 1) + `updateDimensionProperties` (column widths)
- [x] 5.2 Add tab gid resolution via `SHEET_LINKS` parsing (matching `catalog/Writer._resolve_gid_from_env`); persist new gid back to `SHEET_LINKS` when the tab is auto-created
- [x] 5.3 Add `sheet_writer` cell-format application: number format for `In Progress → Deploy` (`Xh Ym`), date-time format for timestamp columns, hyperlink formula for `Jira Ticket` (`=HYPERLINK("...","KEY")`)
- [x] 5.4 Add column widths: `Developer` 140px, ticket-list columns 360px, aggregate columns 90px, `Jira Account ID` 200px
- [x] 5.5 Add `cli.py` with `typer` command `dev-performance` and the orchestration function: load roster → JQL → fetch changelog + remote links + GitLab MR/deployments → join → row build → summary build → diff → write
- [x] 5.6 Wire `cli.py` to emit one `dev_performance_summary` INFO log line per run with all named counters
- [x] 5.7 Add `cli.py` `--prune-cache` flag that triggers `DiffCache.handle_corruption()` then exits

## 6. Schedule registration (canonical _CRON_* pattern)

- [x] 6.1 Add `"dev-performance": ("0 * * * *", "Developer performance to sheet (hourly)")` to `src/jira_daily_reports/schedule.py` `SCHEDULES` dict
- [x] 6.2 Add `_CRON_DEV_PERFORMANCE = "0 * * * *"` constant to `src/jira_daily_reports/dbos_scheduling.py`
- [x] 6.3 Add `_make_workflow("dev-performance", _CRON_DEV_PERFORMANCE, engine=engine)` and `registered.append("jira-dev-performance")` to `register_all_schedules` in `dbos_scheduling.py`
- [x] 6.4 Update `agent-core/deployments/scheduler/generators/jira.py` `_JIRA_CMDS` tuple list to include `("dev-performance", "dev-performance")`
- [x] 6.5 Update `tests/test_dbos_scheduling.py::TestScheduleCount::test_expected_count_is_*` to append `"jira-dev-performance"` to the expected list
- [x] 6.6 Update `tests/test_dbos_scheduling.py::TestCronExpressions::test_all_13_crons_match_schedule_dict` (or its successor with a renamed test method) to expect 14 entries including `dev-performance`

## 7. Integration tests and regression coverage

- [x] 7.1 Add `tests/integration/dev_performance/test_cli_end_to_end.py` running the full CLI against fixture-backed mocks for Jira / GitLab / Sheets (mocking `SheetsClient`)
- [x] 7.2 Add `tests/integration/dev_performance/test_diff_after_no_change.py` — two consecutive runs with identical fixture data → second run writes 0 cells
- [x] 7.3 Add `tests/integration/dev_performance/test_diff_after_status_change.py` — fixture triggers UPDATE for the affected row
- [x] 7.4 Add `tests/integration/dev_performance/test_empty_roster.py` — empty `Dropdown Keys - Do Not Delete -` → exit code, no sheet write
- [x] 7.5 Add `tests/integration/dev_performance/test_full_repull_after_cache_eviction.py` — cache rows >25h old → full re-pull
- [x] 7.6 Add regression test `tests/regression/test_person_capacity_tab_unchanged.py` confirming `Person Capacity` tab contract from `person-capacity-worklog-mode` is preserved
- [x] 7.7 Add regression test `tests/regression/test_sprint_report_tab_unchanged.py` confirming `Sprint Report` tab contract is preserved

## 8. Lint, types, validation

- [x] 8.1 Run `ruff check src/jira_daily_reports/dev_performance tests/dev_performance tests/integration/dev_performance --fix && ruff format .` from the `jira-daily-reports` repo root
- [x] 8.2 Run `mypy src/jira_daily_reports/dev_performance/ --strict` — exit 0 required
- [x] 8.3 Run `pytest -x tests/dev_performance tests/integration/dev_performance tests/regression/test_person_capacity_tab_unchanged.py tests/regression/test_sprint_report_tab_unchanged.py tests/test_dbos_scheduling.py` — all green
- [x] 8.4 Run `openspec validate --strict jira-developer-performance-tab` from the workspace root — exit 0 required

## 9. Deployment and rollout (ordered to avoid manifest drift)

- [x] 9.1 Update `jira-daily-reports/README.md` with the `dev-performance` subcommand usage and the new env var table
- [x] 9.2 Run `bash scripts/deploy.sh` from `~/Developer/tdt/jira-daily-reports` to ship the new module + schedule constants + test updates FIRST (so the agent-core generator sees the new `_CRON_DEV_PERFORMANCE` constant)
- [x] 9.3 Run `bash scripts/deploy.sh` from `~/Developer/tdt/agent-core` to ship the updated `_JIRA_CMDS` tuple list (it picks up the new constant on the next manifest generation)
- [x] 9.4 Restart the scheduler container (or run `python -m agent_core.scheduler_setup --apply`) so DBOS picks up the new manifest
- [x] 9.5 Verify `~/.tdt/schedules/jira-daily-reports.yaml` contains the `jira-dev-performance` entry
- [x] 9.6 First live run is a dry-run against a copy of the live spreadsheet: verify row counts match the `unmapped_dev_in_charge` reconciliation
- [x] 9.7 Flip the schedule from dry-run to live write
- [x] 9.8 Rollback plan documented: drop the `jira-dev-performance` entry from DBOS via `SchedulerClient.delete_scheduled_workflow("jira-dev-performance")`; the `Developer Performance` tab is left in place (idempotent re-runs); `Sprint Report` and `Person Capacity` tabs are unaffected (see `jira-daily-reports/docs/dev-performance-rollout.md`)