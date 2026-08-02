## ADDED Requirements

### Requirement: Optional collection edge verification

The collector and downstream dashboard path SHALL have automated tests for an epic with no subtasks, no bugs, no sprint assignments, and no collected work items. These states MUST complete or exit through the documented empty-result behavior without an unhandled exception or division by zero.

#### Scenario: Optional Jira collections are empty

- **WHEN** fixture-backed collection returns no subtasks, bugs, or sprint assignments
- **THEN** collection returns normalized empty values
- **AND** dashboard rendering handles the result without an arithmetic error

#### Scenario: No work items are collected

- **WHEN** the dashboard command receives an epic scope with no collected work items
- **THEN** it returns the documented non-success empty-result response
- **AND** it does not write a misleading successful dashboard
