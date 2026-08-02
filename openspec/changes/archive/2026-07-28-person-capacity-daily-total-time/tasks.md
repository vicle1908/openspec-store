# Tasks — person-capacity-daily-total-time

## Implementation

### Phase 1: Code change

- [x] 1. Modify `_format_daily_ticket_details()` in `jira_daily_reports/reports/sprint_report_sheet.py` to calculate and display total time per day at the start of each line

### Phase 2: Testing and deployment

- [x] 2. Run `sprint-sheet --output sheet` to write to actual Google Sheet
- [x] 3. Read Person Capacity tab from sheet to verify Daily Ticket Details shows total time format: `YYYY-MM-DD: Hh Mm | TICKET (Hh Mm)`
- [x] 4. Verify individual ticket details are still visible after total time
- [x] 5. Verify empty days are still skipped
- [x] 6. Verify total time calculation matches sum of individual ticket times
- [x] 7. Deploy and schedule
