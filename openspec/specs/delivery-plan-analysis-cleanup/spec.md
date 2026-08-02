# delivery-plan-analysis-cleanup Specification

## Purpose
TBD - created by archiving change delivery-plan-analysis-cleanup. Update Purpose after archive.
## Requirements
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

