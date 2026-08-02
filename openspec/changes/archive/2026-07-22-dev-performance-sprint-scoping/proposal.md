# dev-performance-sprint-scoping

## Why

The dev-performance report currently uses a rolling 30-day lookback window (`DEV_PERFORMANCE_LOOKBACK_HOURS=720`), which is NOT aligned with the sprint period. This causes:

1. **Data mismatch** — Dev-performance includes pre-sprint activity (8+ days before Sprint 19 started)
2. **Inconsistent scoping** — Sprint Report and Person Capacity are sprint-scoped, but dev-performance is not
3. **Misleading metrics** — Cycle times, reopens, and deployment metrics include work from previous sprints

Example: Sprint 19 runs 20 Jul – 31 Jul (11 days), but dev-performance collects data from 22 Jun – 22 Jul (30 days) — including 8 days before Sprint 19 started.

## What Changes

1. **Default to sprint period** — Dev-performance uses sprint dates from `config.toml` (via workbook title) as the default window
2. **Add override mechanism** — `--lookback-days` CLI flag, `DEV_PERFORMANCE_LOOKBACK_HOURS` env var, or `sprint_scoped = false` in config.toml
3. **Backward compatible** — Existing `DEV_PERFORMANCE_LOOKBACK_HOURS` still works as override
4. **Consistent scoping** — All three reports (sprint-sheet, person-capacity, dev-performance) now use sprint dates by default

## Impact

- **dev-performance CLI** — Add `--lookback-days` flag, modify `_lookback_hours()` logic
- **config.toml** — Add `sprint_scoped` option to `[dev_performance]` section
- **dbos_scheduling.py** — No changes needed (inherits from config)
- **Backward compatible** — Existing env var overrides still work
