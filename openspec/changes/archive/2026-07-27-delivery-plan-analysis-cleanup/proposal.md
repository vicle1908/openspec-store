# delivery-plan-analysis-cleanup

## Why

The Delivery Plan Analysis tab in the epic report spreadsheet has presentation issues that make the data hard to read:

1. **Development Time** column has multi-line text (Sprint 18 + Sprint 19 dates)
2. **Readiness** column is a 5-line paragraph with multiple metrics
3. Data is not organized for quick scanning

The goal is to clean up the data presentation while keeping the same 12 columns.

## What Changes

### Readiness Column Cleanup

**Current** (5 lines):
```
Release target: 3.3.56 (05-Sep); 
UAT planned 2026-08-20 to 2026-08-26; 
Beta planned 2026-08-27 to 2026-09-02; 
API deployment: Not specified in Epic Plan; 
Jira completion: 64%; No unresolved Jira blockers
```

**Proposed** (1 line):
```
Release: 3.3.56 (Sep 5) | UAT: Aug 20-26 | Beta: Aug 27-Sep 2 | Jira: 64% | No blockers
```

### Development Time Column

Keep as-is (multi-line with Sprint 18 + Sprint 19 dates). The multi-line format is actually useful for showing sprint history.

## Impact

- **epic_report/reporters/spreadsheet_reporter.py** — Modify `_delivery_plan_rows()` to condense Readiness column
- **No data collection changes** — Keep current crawling logic and scheduling
- **Backward compatible** — Same columns, cleaner presentation
