# Design — delivery-plan-analysis-cleanup

## Current State

The Delivery Plan Analysis tab has 12 columns:

```
┌─────────────┬──────────────┬─────────────┬─────────────┬──────────────┬─────────────────┬──────────────┬──────────────┬─────────────┬─────────────┬─────────────────┬─────────────┐
│ Jira Link   │ Summary      │ Jira Status │ Jira Progress│ Plan State  │ Development Time│ UAT          │ Beta         │ Target Version│ Target Date │ API Deployment  │ Readiness   │
├─────────────┼──────────────┼─────────────┼─────────────┼──────────────┼─────────────────┼──────────────┼──────────────┼─────────────┼─────────────┼─────────────────┼─────────────┤
│ RMD-4160    │ DLC Visibility│ In Progress│ 64%         │ MATCHED      │ Sprint 18-19    │ Aug 20-26    │ Aug 27-Sep 2 │ 3.3.56      │ Sep 5       │ Not specified   │ 5-line paragraph│
└─────────────┴──────────────┴─────────────┴─────────────┴──────────────┴─────────────────┴──────────────┴──────────────┴─────────────┴─────────────┴─────────────────┴─────────────┘
```

## Issues

1. **Development Time** (2 lines): Multi-line with Sprint 18 + Sprint 19 — keep as-is
2. **Readiness** (5 lines): Long paragraph — condense to single line

## Proposed Changes

### Readiness Column

**Before** (5 lines):
```
Release target: 3.3.56 (05-Sep); 
UAT planned 2026-08-20 to 2026-08-26; 
Beta planned 2026-08-27 to 2026-09-02; 
API deployment: Not specified in Epic Plan; 
Jira completion: 64%; No unresolved Jira blockers
```

**After** (1 line):
```
Release: 3.3.56 (Sep 5) | UAT: Aug 20-26 | Beta: Aug 27-Sep 2 | Jira: 64% | No blockers
```

### Implementation

Modify `_delivery_plan_rows()` in `epic_report/reporters/spreadsheet_reporter.py`:

1. Parse the readiness text to extract key metrics
2. Format as condensed single-line with `|` separators
3. Abbreviate dates (e.g., "2026-08-20" → "Aug 20")

### Code Change

```python
def _condense_readiness(readiness: str) -> str:
    """Condense readiness text to single line with key metrics."""
    if not readiness or readiness == "NO_ANALYSIS":
        return readiness
    
    # Parse semicolon-separated items
    items = [item.strip() for item in readiness.split(";") if item.strip()]
    
    # Condense each item
    condensed = []
    for item in items:
        # Abbreviate dates
        item = re.sub(r"(\d{4})-(\d{2})-(\d{2})", lambda m: f"{_MONTHS[m.group(2)]} {int(m.group(3))}", item)
        # Shorten labels
        item = item.replace("Release target:", "Release:")
        item = item.replace("UAT planned", "UAT:")
        item = item.replace("Beta planned", "Beta:")
        item = item.replace("Jira completion:", "Jira:")
        item = item.replace("No unresolved Jira blockers", "No blockers")
        condensed.append(item.strip())
    
    return " | ".join(condensed)
```

## Testing

1. Run `daily-epic-report` and verify the Delivery Plan Analysis tab shows condensed Readiness
2. Verify Development Time remains multi-line (Sprint 18 + Sprint 19)
3. Check that other columns are unchanged
