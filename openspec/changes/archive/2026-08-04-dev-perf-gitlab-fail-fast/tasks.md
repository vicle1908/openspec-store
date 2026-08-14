# Tasks — dev-perf-gitlab-fail-fast

## Implementation

- [x] [historical] 1. Add `validate_gitlab_auth` helper to
  `jira-daily-reports/src/jira_daily_reports/dev_performance/source.py`
  with single-attempt auth probe + logger.error message + optional raise.
- [x] [historical] 2. Add `joined_via_none` counter to `JoinMethod` tally in
  `jira-daily-reports/src/jira_daily_reports/dev_performance/cli.py`
  and include it in the `dev_performance_summary` log payload.
- [x] [historical] 3. Add `_gitlab_required_mode()` helper that reads
  `DEV_PERFORMANCE_GITLAB_REQUIRED` env var (default False) and
  passes result to `_validate_gitlab_auth` in `cli.py`.
- [x] [historical] 4. Document new env var in
  `jira-daily-reports/config/env-sample.env` and
  `tdt-meta/docs/workflows/dev-performance-runbook.md` (new doc).

## Tests

- [x] [historical] 5. Add `tests/dev_performance/test_source_validation.py` with
  5 unit tests covering: success, 401 warn, 401 raise, empty user
  attribute, summary counter.

## Validation

- [x] [historical] 6. Run `ruff check . --fix && ruff format .` in
  `jira-daily-reports/`.
- [x] [historical] 7. Run `mypy jira-daily-reports --strict` in tdt-meta.
- [x] [historical] 8. Run `pytest -x` in `jira-daily-reports/tests/dev_performance/`.
- [x] [historical] 9. Run `openspec validate --strict dev-perf-gitlab-fail-fast`.
- [x] [historical] 10. Live dry-run: `cd jira-daily-reports && uv run dev-performance
  --dry-run` — confirm `joined_via_none` key appears in summary.

## Documentation

- [x] [historical] 11. Create `tdt-meta/docs/workflows/dev-performance-runbook.md` with
  "GitLab authentication" section explaining the new env knob and the
  fail-fast ERROR line operators should grep for.
- [x] [historical] 12. Cross-link the new runbook from
  `tdt-meta/.agents/modules/coding.md` and
  `jira-daily-reports/README.md` if present.

## Cleanup

- [x] [historical] 13. Commit the changes with body referencing
  `Part-of: dev-perf-gitlab-fail-fast`.
- [x] [historical] 14. Once all tasks check out, run `opsx:archive` to move
  the change to `openspec/changes/archive/`.

## Follow-up: ~/.tdt/.env shell-source tripwire

Surfaced 2026-07-13 while restoring `GITLAB_PAT` — `bash -c 'set -a; source
~/.tdt/.env; set +a'` spammed `Jira: command not found` and split
`JIRA_DEV_IN_CHARGE_TRIGGER_STATUS=In Progress` into `In` (the word "Progress"
was attempted as a command). Same tripwire for any operator who naively
sources the file. Quoting the two affected lines in `~/.tdt/.env` is
necessary but not sufficient — both `SHEET_LINKS` persistence writers in
`jira-daily-reports` re-write the line **unquoted**, which would re-introduce
the tripwire on the next gid-append.

- [x] [historical] 15. Add `jira_daily_reports/_env_quoting.py` with
  `format_sheet_links_line(entries)` and `parse_sheet_links_value(stripped)`
  helpers. `format_*` MUST wrap the value in `"..."`; `parse_*` MUST tolerate
  both quoted and unquoted values for backward compatibility with old
  `.env` files and `.env.backup.*` snapshots.
- [x] [historical] 16. Update `jira-daily-reports/src/jira_daily_reports/dev_performance/sheet_writer.py`
  `persist_gid_to_sheet_links` to call `format_sheet_links_line()` on the
  final entries.
- [x] [historical] 17. Update `jira-daily-reports/src/jira_daily_reports/catalog/writer.py`
  `Writer._persist_gid_to_sheet_links` to call `format_sheet_links_line()`.
- [x] [historical] 18. Add `jira-daily-reports/tests/test_env_quoting.py` covering:
  unquoted parse, quoted parse, format-with-multiple-entries, format+parse
  round-trip, idempotent re-format.
- [x] [historical] 19. Run `ruff check . --fix && ruff format .` and `pytest -x
  tests/test_env_quoting.py` in `jira-daily-reports/`.
- [x] [historical] 20. Manually verify: `bash -c 'set -a; source ~/.tdt/.env; set +a;
  echo "$JIRA_DEV_IN_CHARGE_TRIGGER_STATUS"'` prints `In Progress` with no
  `command not found` errors.

## Follow-up: logging-propagation regression + time-sensitive test data

Surfaced 2026-07-14 while validating the scheduler end-to-end after the
`GITLAB_PAT` restoration. Five pre-existing test failures cluster into two
root causes:

- Four `caplog`-based tests in `tests/dev_performance/test_stale_thresholds.py`
  and `tests/dev_performance/test_metrics.py` fail whenever an earlier test
  imports `jira_daily_reports.cli`. Root cause:
  `jira_daily_reports/logging_config.py:configure_logging()` sets
  `jira_daily_reports.propagate = False`, which silently breaks pytest
  caplog (and any external log sink) for the entire `jira_daily_reports.*`
  logger tree.
- `tests/catalog/test_joiner.py::test_join_custom_fields_tracked_with_usage_and_metadata`
  asserts `status == Status.ACTIVE` for `last_seen=datetime(2026, 6, 10)`.
  On 2026-07-14 the elapsed time is ~34 days, which `_compute_status`
  correctly classifies as `STALE` (the 31-90 day band). The test data is
  stale; production behavior is correct.

- [x] [historical] 21. Update `jira-daily-reports/src/jira_daily_reports/logging_config.py`
  `configure_logging()` to remove the `root.propagate = False` line and
  instead set the *handler* level to INFO (or leave it at the default
  NOTSET). Add a docstring explaining why propagation must stay on so
  external log sinks (pytest caplog, Datadog, ELK) keep working.
- [x] [historical] 22. Add `jira-daily-reports/tests/test_logging_config.py` covering:
  propagation is True after import, WARNING records from a child logger
  reach the root logger, double-call is idempotent.
- [x] [historical] 23. Update `jira-daily-reports/tests/catalog/test_joiner.py`
  `test_join_custom_fields_tracked_with_usage_and_metadata` to use
  `datetime.now(UTC) - timedelta(days=5)` for `last_seen`, matching the
  pattern in `test_join_labels_sets_correct_usage_fields` so the test is
  not time-sensitive.
- [x] [historical] 24. Run the full combined suite in the order pytest picks by default:
  `cd jira-daily-reports && uv run pytest tests/catalog/ tests/dev_performance/ tests/test_env_quoting.py tests/test_logging_config.py`.
  Confirm 0 failures.
- [x] [historical] 25. Run `ruff check . --fix && ruff format .` and `mypy
  jira-daily-reports --strict` on the changed files.
- [x] [historical] 26. Run `openspec validate --strict dev-perf-gitlab-fail-fast`.


---

> **Historical record:** This change was archived with 26 incomplete task(s) (0/26 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
