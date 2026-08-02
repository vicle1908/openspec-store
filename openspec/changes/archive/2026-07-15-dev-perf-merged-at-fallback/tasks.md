# Tasks — dev-perf-merged-at-fallback

## Implementation

- [x] 1. Add `ENV_USE_MERGED_AT_FALLBACK` constant and `_use_merged_at_fallback()` helper to
  `jira-daily-reports/src/jira_daily_reports/dev_performance/join.py`.
- [x] 2. Add `_apply_deploy_fallback()` helper to `join.py` that applies the fallback
  and returns the updated `(first_deploy_at, merged_at_fallback_count)` tuple.
- [x] 3. Add `merged_at_fallback_count: int = 0` field to `JoinResult` dataclass
  in `join.py`.
- [x] 4. Call `_apply_deploy_fallback()` at both `resolve_linked_mrs` return sites
  (remote-link path and branch-regex path) with the pre-computed
  `first_deploy_at` and `first_mr_merged_at` values.
- [x] 5. Export `ENV_USE_MERGED_AT_FALLBACK` in `join.py`'s `__all__`.
- [x] 6. Add `merged_at_fallback_count` accumulator to `_run_dev_performance` in
  `cli.py`, accumulating `join_result.merged_at_fallback_count` per issue.
- [x] 7. Add `merged_at_fallback=N` to the `dev_performance_summary` INFO log dict
  in `cli.py`.
- [x] 8. Run `ruff check . --fix && ruff format .` in `jira-daily-reports/`.

## Tests

- [x] 9. Add `tests/dev_performance/test_join.py::TestMergedAtFallback` with 4 cases:
  fallback applies when deployments empty, fallback NOT applied when deployments exist,
  fallback disabled via env var, fallback NOT applied when MR not merged.
- [x] 10. Add `tests/dev_performance/test_join.py::TestUseMergedAtFallback` with 3 cases:
  default is True, truthy values, falsy values.
- [x] 11. Run full test suite: `cd jira-daily-reports && uv run pytest tests/dev_performance/ tests/test_logging_config.py tests/test_env_quoting.py tests/catalog/test_joiner.py -v`.
  Confirm 0 failures.

## Documentation

- [x] 12. Document `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK` in
  `jira-daily-reports/README.md` env var table.
- [x] 13. Add `dev-performance-merged-at-fallback` section to
  `tdt-meta/docs/workflows/dev-performance-runbook.md` explaining the fallback
  and the `merged_at_fallback` counter in log output.
- [x] 14. Run `openspec validate --strict dev-perf-merged-at-fallback`.

## Validation

- [x] 15. Trigger a live `jira-dev-performance` run and verify:
  - `dev_performance_merged_at_fallback` INFO log lines appear (one per issue
    where fallback applied).
  - `dev_performance_summary` log line contains `merged_at_fallback=N`.
  - `In Progress → Deploy` column shows non-empty values for rows with merged MRs.
  - `missing_first_deploy` count is lower than before (reflects only unmerged MRs).
- [x] 16. Verify `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK=false` disables fallback:
  set to false, trigger a run, confirm `merged_at_fallback=0` and
  `missing_first_deploy` is high.
