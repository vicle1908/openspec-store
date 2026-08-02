# fix-rca-fix-status-detection Specification

## Purpose
TBD - created by archiving change fix-rca-fix-status-detection. Update Purpose after archive.
## Requirements
### Requirement: RCA Detection Test Coverage

The RCA classification system SHALL have comprehensive test coverage across all 9 RCA categories, with regression tests for greedy pattern matching, empty content handling, and confidence score caps.

#### Scenario: All 9 RCA categories are correctly classified

- **WHEN** `detect_rca` is called with representative inputs from each category
- **THEN** it SHALL return the correct category name for all 9 categories: Crash/ANR, Wrong Data, Silent Exit, UI Layout, Performance, Auth, Network, Feature Not Working, General Polish
- **AND** empty content SHALL return `None`
- **AND** greedy patterns SHALL NOT match false positives

