# Tasks — delivery-plan-analysis-cleanup

## Implementation

### Phase 1: Readiness column cleanup

- [x] 1. Add `_condense_readiness()` function to `epic_report/reporters/spreadsheet_reporter.py` that condenses the 5-line readiness paragraph to a single line with `|` separators
- [x] 2. Update `_delivery_plan_rows()` to call `_condense_readiness()` on the readiness value before appending to row
- [x] 3. Add date abbreviation helper `_abbreviate_date()` to format dates as "Mon DD" instead of "YYYY-MM-DD"

### Phase 2: Testing

- [x] 4. Run `daily-epic-report` and verify the Delivery Plan Analysis tab shows condensed Readiness
- [x] 5. Verify Development Time remains multi-line (Sprint 18 + Sprint 19)
- [x] 6. Verify other columns are unchanged
- [x] 7. Run unit tests for `_condense_readiness()` function

### Phase 3: Documentation

- [x] 8. Update design doc with implementation details
- [x] 9. Update OpenSpec spec with final requirements
