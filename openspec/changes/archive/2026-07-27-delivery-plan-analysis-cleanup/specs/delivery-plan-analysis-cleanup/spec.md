# Capability: delivery-plan-analysis-cleanup

## Purpose

Clean up the presentation of the Delivery Plan Analysis tab in the epic report spreadsheet. Keep exactly 12 columns with proper data presentation. Multiple lines are OK if properly formatted.

## Current State

The code in `epic_report/reporters/spreadsheet_reporter.py` generates 19 columns but only 12 are shown in the sheet:

```
Code columns (19):
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

Sheet columns (12):
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

## ADDED Requirements

### Requirement: Readiness column SHALL be condensed to single line

The Readiness column SHALL display all key metrics in a single, scannable line using `|` separators instead of a multi-line paragraph.

**Current implementation:** The readiness text comes from `analysis.readiness` in `PlanAwareEpicAnalysis` model. It's a free-form string that can be multi-line.

**Proposed change:** Add `_condense_readiness()` function in `spreadsheet_reporter.py` to parse and condense the readiness text.

#### Scenario: Readiness with multiple metrics

- **WHEN** the Readiness value contains release target, UAT dates, Beta dates, API deployment, Jira completion, and blockers
- **THEN** the column SHALL display as: `Release: 3.3.56 (Sep 5) | UAT: Aug 20-26 | Beta: Aug 27-Sep 2 | Jira: 64% | No blockers`
- **AND** SHALL NOT exceed 1 line in height

#### Scenario: Readiness with missing data

- **WHEN** the Readiness value contains "Not specified in Epic Plan"
- **THEN** the column SHALL display: `Not specified in Epic Plan`
- **AND** SHALL NOT show empty segments

### Requirement: Development Time column SHALL remain multi-line

The Development Time column SHALL keep the current multi-line format showing sprint history.

**Current implementation:** `_plan_window(context.development)` returns a date range string. The sheet shows multi-line with Sprint 18 + Sprint 19.

#### Scenario: Multiple sprints in Development Time

- **WHEN** the Development Time contains Sprint 18 and Sprint 19 dates
- **THEN** the column SHALL display both sprints on separate lines
- **AND** SHALL NOT be condensed to a single line

### Requirement: Date abbreviation SHALL use consistent format

Dates in condensed columns SHALL be abbreviated to "Mon DD" format (e.g., "Aug 20" instead of "2026-08-20").

#### Scenario: Full date abbreviation

- **WHEN** the date is "2026-08-20"
- **THEN** the column SHALL display "Aug 20"
- **AND** SHALL NOT display the year when it's clear from context

### Requirement: All other columns SHALL remain unchanged

The following columns SHALL NOT be modified:

- Jira Link
- Summary
- Jira Status
- Jira Progress
- Plan State
- Target Version
- Target Date
- API Deployment

#### Scenario: No changes to other columns

- **WHEN** the Delivery Plan Analysis tab is generated
- **THEN** the columns listed above SHALL display the same data as before
- **AND** SHALL NOT be reordered or renamed
