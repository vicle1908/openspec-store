# Tasks — dev-performance-sprint-scoping

## Implementation

### Phase 1: Core logic

- [x] 1. Modify `_lookback_hours()` in `jira-daily-reports/src/jira_daily_reports/dev_performance/cli.py` to check sprint dates first, then fall back to lookback_hours
- [x] 2. Add `--lookback-days` CLI flag to dev-performance callback in `cli.py`
- [x] 3. Update `config.toml` schema: add `sprint_scoped = true` to `[dev_performance]` section

### Phase 2: Data collection

- [x] 4. Modify `_run_dev_performance()` to pass sprint window to `JiraSource.search_dev_tickets()`
- [x] 5. Update `JiraSource.search_dev_tickets()` to accept optional sprint window parameter
- [x] 6. Update JQL query construction to use sprint dates when available
- [x] 7. Update `window_start`/`window_end` calculation to use sprint dates when available

### Phase 3: Tests

- [x] 8. Add unit tests for `_lookback_hours()` with various config combinations
- [x] 9. Add unit tests for sprint window calculation
- [x] 10. Add integration test with mock sprint dates
- [x] 11. Manual test: run dev-performance with sprint 19 dates — verified JQL filter uses absolute dates

### Phase 4: Documentation

- [x] 12. Update design doc with implementation details
- [x] 13. Update runbook with sprint-scoping behavior
- [x] 14. Update OpenSpec spec with final requirements
