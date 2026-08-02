# delivery-plan-12-columns-alignment Specification

## Purpose
TBD - created by archiving change delivery-plan-12-columns-alignment. Update Purpose after archive.
## Requirements
### Requirement: Delivery Plan Analysis SHALL have exactly 12 columns

The Delivery Plan Analysis tab SHALL display exactly 12 columns with the specified names.

#### Scenario: Column count verification

- **WHEN** the Delivery Plan Analysis tab is generated
- **THEN** the tab SHALL have exactly 12 columns
- **AND** SHALL NOT have more or fewer columns

### Requirement: Column names SHALL match target specification

The 12 columns SHALL be named exactly as specified:

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

#### Scenario: Column names match target

- **WHEN** the Delivery Plan Analysis tab is generated
- **THEN** the column names SHALL match the target specification exactly
- **AND** SHALL NOT have extra or missing columns

### Requirement: Development Time column SHALL use correct name

The column previously named "Development Window" SHALL be renamed to "Development Time" to match the target specification.

#### Scenario: Column name updated

- **WHEN** the Delivery Plan Analysis tab is generated
- **THEN** the column SHALL be named "Development Time"
- **AND** SHALL NOT be named "Development Window"

### Requirement: Readiness column SHALL be condensed to single line

The Readiness column SHALL display all key metrics in a single, scannable line using `|` separators.

#### Scenario: Readiness condensed

- **WHEN** the Readiness value contains multiple metrics
- **THEN** the column SHALL display as single line with `|` separators
- **AND** SHALL NOT exceed 1 line in height

### Requirement: Development Time column SHALL remain multi-line

The Development Time column SHALL keep the current multi-line format showing sprint history.

#### Scenario: Multiple sprints

- **WHEN** the Development Time contains multiple sprints
- **THEN** the column SHALL display all sprints on separate lines
- **AND** SHALL NOT be condensed to a single line

