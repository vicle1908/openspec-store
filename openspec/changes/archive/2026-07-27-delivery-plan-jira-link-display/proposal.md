# delivery-plan-jira-link-display

## Why

The Jira Link column in the Delivery Plan Analysis tab currently shows the full URL (e.g., `https://psplit.atlassian.net/browse/RMD-4160`). The user wants it to show only the ticket number (e.g., `RMD-4160`) for cleaner display.

## What Changes

1. **Change Jira Link display** — Show ticket number only instead of full URL
2. **Update spec** — Align with new display format
3. **Deploy and verify** — Run epic-report and verify output

## Impact

- **epic_report/reporters/spreadsheet_reporter.py** — Change `jira_url(epic.key)` to `epic.key` in `_delivery_plan_rows()`
- **No data collection changes** — Keep current crawling logic
- **One-line change** — Minimal risk
