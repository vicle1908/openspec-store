# Design — delivery-plan-jira-link-display

## Current State

The Jira Link column shows the full URL as text:

```
Jira Link: https://psplit.atlassian.net/browse/RMD-4160
```

## Target State

The Jira Link column should show the ticket number as a clickable hyperlink:

```
Jira Link: RMD-4160 (clickable → https://psplit.atlassian.net/browse/RMD-4160)
```

## Code Change

In `_delivery_plan_rows()`, change:

```python
# Before
jira_url(epic.key),

# After
 HYPERLINK(jira_url(epic.key), epic.key)
```

Use the `_hyperlink()` helper function that already exists in the codebase.

This is a one-line change in `epic_report/reporters/spreadsheet_reporter.py`.
