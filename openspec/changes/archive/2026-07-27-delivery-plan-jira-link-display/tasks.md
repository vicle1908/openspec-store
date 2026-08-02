# Tasks — delivery-plan-jira-link-display

## Implementation

### Phase 1: Code change

- [x] 1. Change `jira_url(epic.key)` to `_link(epic.key)` in `_delivery_plan_rows()` in `epic_report/reporters/spreadsheet_reporter.py`

### Phase 2: Testing and deployment

- [x] 2. Run `epic-report generate RMD-4160 --format spreadsheet` to verify output
- [x] 3. Verify Jira Link column shows ticket number as clickable hyperlink
- [x] 4. Deploy and schedule
