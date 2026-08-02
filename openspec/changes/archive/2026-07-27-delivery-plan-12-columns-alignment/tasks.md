# Tasks — delivery-plan-12-columns-alignment

## Implementation

### Phase 1: Code alignment

- [x] 1. Update `_DELIVERY_PLAN_HEADERS` in `epic_report/reporters/spreadsheet_reporter.py` to exactly 12 target columns
- [x] 2. Update `_delivery_plan_rows()` to only output 12 columns
- [x] 3. Remove extra columns: Jira Key, Development Sprint Overlaps, Target Precision, Alignment Signals, Diagnostics, Source As Of, Source Timezone
- [x] 4. Rename "Development Window" to "Development Time" in headers

### Phase 2: Spec alignment

- [x] 5. Update delivery-plan-analysis-cleanup spec to match 12-column target
- [x] 6. Update design doc with implementation details

### Phase 3: Testing and deployment

- [x] 7. Run `epic-report generate RMD-4160 --format spreadsheet` to verify output
- [x] 8. Verify Delivery Plan Analysis tab has exactly 12 columns
- [x] 9. Verify all data is correctly formatted
- [x] 10. Deploy and schedule
