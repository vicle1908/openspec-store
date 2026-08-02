# Design — delivery-plan-12-columns-alignment

## Current State

The Delivery Plan Analysis tab has 19 columns:

```
1. Jira Key
2. Jira Link
3. Summary
4. Jira Status
5. Jira Progress
6. Plan State
7. Development Window
8. Development Sprint Overlaps
9. Target Version
10. Target Date
11. Target Precision
12. API Deployment
13. UAT
14. Beta
15. Readiness
16. Alignment Signals
17. Diagnostics
18. Source As Of
19. Source Timezone
```

## Target State

The tab should have exactly 12 columns:

```
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
```

## Changes Required

### 1. Update Headers

Replace `_DELIVERY_PLAN_HEADERS` with 12 target columns.

### 2. Update Data Generation

Modify `_delivery_plan_rows()` to only output 12 columns:
- Remove: Jira Key, Development Sprint Overlaps, Target Precision, Alignment Signals, Diagnostics, Source As Of, Source Timezone
- Rename: Development Window → Development Time

### 3. Update Spec

Align the spec with the actual implementation.

## Code Changes

```python
_DELIVERY_PLAN_HEADERS = [
    "Jira Link",
    "Summary",
    "Jira Status",
    "Jira Progress",
    "Plan State",
    "Development Time",
    "UAT",
    "Beta",
    "Target Version",
    "Target Date",
    "API Deployment",
    "Readiness",
]
```

## Testing

1. Run `epic-report generate RMD-4160 --format spreadsheet`
2. Verify Delivery Plan Analysis tab has exactly 12 columns
3. Verify all data is correctly formatted
