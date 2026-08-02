# person-capacity-daily-total-time

## Why

The Daily Ticket Details column in Person Capacity shows individual ticket times per day, but doesn't show the total time for each day. This makes it harder to quickly assess daily workload.

**Current format:**
```
2026-07-20: PUB-79 (2h 30m), PUB-80 (1h), PUB-82 (5h)
2026-07-21: PUB-79 (8h), PUB-82 (4h)
```

**Enhanced format (Option C):**
```
2026-07-20: 8h 30m | PUB-79 (2h 30m), PUB-80 (1h), PUB-82 (5h)
2026-07-21: 12h | PUB-79 (8h), PUB-82 (4h)
```

## What Changes

1. **Add total time per day** — Calculate and display total hours/minutes at the start of each line
2. **Use pipe separator** — Clear separation between total and individual tickets
3. **Keep existing format** — Individual ticket details remain unchanged

## Impact

- **jira_daily_reports/reports/sprint_report_sheet.py** — Modify `_format_daily_ticket_details()` function
- **No data collection changes** — Keep current worklog fetching logic
- **One function change** — Minimal risk
