# delivery-plan-12-columns-alignment

## Why

The Delivery Plan Analysis tab currently has 19 columns but only 12 are needed. The extra columns create visual clutter and make the tab harder to read.

The 12 target columns are:
1. Jira Link
2. Summary
3. Jira Status
4. Jira Progress
5. Plan State
6. Development Time
7. UAT
8. Beta
9. Target Version
10. Target Date
11. API Deployment
12. Readiness

## What Changes

1. **Reduce columns from 19 to 12** — Remove extra columns that are not needed
2. **Fix column naming** — "Development Window" → "Development Time" to match target
3. **Update spec** — Align with actual implementation
4. **Deploy and verify** — Run epic-report and verify output matches target

## Impact

- **epic_report/reporters/spreadsheet_reporter.py** — Update `_DELIVERY_PLAN_HEADERS` and `_delivery_plan_rows()`
- **Specs** — Update delivery-plan-analysis-cleanup spec
- **No data collection changes** — Keep current crawling logic
