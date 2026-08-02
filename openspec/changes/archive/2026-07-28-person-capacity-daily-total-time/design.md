# Design — person-capacity-daily-total-time

## Current State

The `_format_daily_ticket_details()` function in `sprint_report_sheet.py` generates:

```
2026-07-20: PUB-79 (2h 30m), PUB-80 (1h), PUB-82 (5h)
2026-07-21: PUB-79 (8h), PUB-82 (4h)
```

## Target State

Add total time at the start of each line:

```
2026-07-20: 8h 30m | PUB-79 (2h 30m), PUB-80 (1h), PUB-82 (5h)
2026-07-21: 12h | PUB-79 (8h), PUB-82 (4h)
```

## Code Change

Modify `_format_daily_ticket_details()` in `sprint_report_sheet.py`:

```python
def _format_daily_ticket_details(site: str, daily_issue_seconds: dict[str, Any]) -> str:
    if not daily_issue_seconds:
        return ""
    parts: list[str] = []
    for day in sorted(daily_issue_seconds):
        issue_seconds = as_dict(daily_issue_seconds.get(day))
        if not issue_seconds:
            continue
        # Calculate total seconds for the day
        total_seconds = sum(int(v) for v in issue_seconds.values())
        # Format individual issues
        issue_parts: list[str] = []
        for issue_key in sorted(issue_seconds):
            seconds = int(issue_seconds.get(issue_key) or 0)
            issue_parts.append(f"{issue_key} ({format_seconds(seconds) if seconds else '0m'})")
        # Prepend total time
        if issue_parts:
            parts.append(f"{day}: {format_seconds(total_seconds)} | {', '.join(issue_parts)}")
    return "\n".join(parts)
```

## Testing

1. Run `sprint-sheet --output sheet` and verify Daily Ticket Details shows total time
2. Verify individual ticket details are still visible
3. Check that empty days are still skipped
