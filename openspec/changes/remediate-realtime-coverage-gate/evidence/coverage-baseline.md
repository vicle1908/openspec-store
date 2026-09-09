# Realtime Frontend Coverage Baseline (final14 canonical run)

Change: `remediate-realtime-coverage-gate`
Canonical command (from `realtime/frontend`): `npm run test:ci -- --reporter=dot --maxWorkers=1`
Evidence source: `/tmp/realtime-test-ci-final14.log`, coverage table lines 23311–23416.

## Test results (separate dimension from coverage)

- Test Files: **78 passed | 5 skipped (83)**
- Tests: **580 passed | 43 skipped (623)**
- Duration: 102.23s
- Test gate: **green** (zero test failures, zero unhandled errors)

## Coverage summary (v8 provider)

Global (`All files`):

| Metric | Measured | Configured threshold |
|---|---|---|
| Statements | 39.95% (1636/4095) | 75% |
| Branches | 34.09% (1018/2986) | 75% |
| Functions | 34.90% (400/1146) | 75% |
| Lines | 41.32% (1575/3811) | 75% |

Threshold errors emitted at exit (log lines 23413–23416):

```
ERROR: Coverage for lines (22.83%) does not meet "src/components/Analytics/**/*" threshold (85%)
ERROR: Coverage for functions (17.42%) does not meet "src/components/Analytics/**/*" threshold (85%)
ERROR: Coverage for statements (21.96%) does not meet "src/components/Analytics/**/*" threshold (85%)
ERROR: Coverage for branches (26.19%) does not meet "src/components/Analytics/**/*" threshold (85%)
```

Only the `src/components/Analytics/**/*` threshold errors are emitted; global thresholds are also unmet (41.32% lines vs 75%) but the run surfaced the Analytics errors. Canonical command exit is **nonzero due to coverage enforcement only** — all tests passed.

## Per-file Analytics coverage (src/components/Analytics)

Columns: % Stmts | % Branch | % Funcs | % Lines (log lines 23321–23336)

| Component (src/components/Analytics/…) | % Stmts | % Branch | % Funcs | % Lines |
|---|---|---|---|---|
| **Directory total** | **21.96** | **26.19** | **17.42** | **22.83** |
| AnalyticsFilters.tsx | 1.72 | 0 | 0 | 1.81 |
| BarChart.tsx | 54.05 | 60 | 54.54 | 55.07 |
| Pagination.tsx | 2.85 | 0 | 0 | 3.03 |
| DateRangePicker.tsx | 29.7 | 14.49 | 16 | 32.58 |
| DrillDownPanel.tsx | 1.03 | 0 | 0 | 1.12 |
| ExportManager.tsx | 11.32 | 15.53 | 5.26 | 12.16 |
| FunnelChart.tsx | 55.17 | 52 | 80 | 56.6 |
| GaugeChart.tsx | 1.04 | 0 | 0 | 1.06 |
| Heatmap.tsx | 1.08 | 0 | 0 | 1.14 |
| MetricCard.tsx | 52 | 69.09 | 44.44 | 56.81 |
| PieChart.tsx | 59.57 | 61.53 | 57.14 | 60.86 |
| RealtimeControls.tsx | 60 | 52.5 | 47.36 | 60.29 |
| ScatterPlot.tsx | 0.64 | 0 | 0 | 0.7 |
| TimeSeriesChart.tsx | 36.61 | 51.25 | 36.36 | 37.87 |
| ChartSkeleton.tsx | 68.75 | 84.61 | 62.5 | 68.75 |

All 15 `src/components/Analytics/*.tsx` files from the run table are listed. Uncovered-line ranges are recorded in the log (e.g. AnalyticsFilters 59–301, GaugeChart 51–345, Heatmap 48–356, ScatterPlot 65–478).

### Substantially uncovered components (≈0–12% lines)

ScatterPlot (0.7), GaugeChart (1.06), Heatmap (1.14), DrillDownPanel (1.12), AnalyticsFilters (1.81), Pagination (3.03), ExportManager (12.16) — seven components.

## Threshold provenance

Repository: `realtime/frontend`. File history for `vitest.config.ts` (`git log --oneline -- vitest.config.ts`):

- `71b99ca3` chore(frontend): align test configuration and mocks to Vitest
- `d15e4939` test(frontend): align Vitest mocks and global setup
- `95e031de` feat(frontend): track web application source, tests, and configuration

Verification via `git show <commit>:frontend/vitest.config.ts` threshold blocks:

- **`95e031de feat(frontend): track web application source, tests, and configuration`** — initial tracking commit; `vitest.config.ts` added whole (150 insertions) with the threshold block already present: global `branches/functions/lines/statements: 75`, `src/components/Analytics/**/*: 85` on all four metrics, property-based override `0`.
- **`71b99ca3 chore(frontend): align test configuration and mocks to Vitest`** — migration commit; threshold block byte-identical to `95e031de` (unchanged by the migration).
- Working-tree block at HEAD (`21c790e7`) is identical to both commits.

Conclusion: the 75/85 thresholds predate the Vitest migration (entered at initial tracking commit `95e031de`) and were untouched by migration commit `71b99ca3`; the migration-config commit did not modify the threshold block.
