## ADDED Requirements

### Requirement: Sprint Health Status Display in Sheet
The Sprint Report worksheet SHALL display the computed sprint health status (HEALTHY/AT RISK/CRITICAL) in the Sprint Summary section.

#### Scenario: Sprint sheet rows include health status
- **WHEN** `build_sheet_rows()` generates the Sprint Report sheet output
- **THEN** it SHALL include a "Sprint Health" row in the Sprint Summary section with the computed health status from `result.summary["health"]`
- **AND** the row SHALL display both emoji indicator and text status (e.g., "🟢 HEALTHY", "🟡 AT RISK", "🔴 CRITICAL")

#### Scenario: Health status matches computed value
- **WHEN** the sprint has no blocked tickets and code review count ≤ 8
- **THEN** the sheet SHALL display "🟢 HEALTHY"
- **WHEN** the sprint has any blocked tickets OR code review count > 8
- **THEN** the sheet SHALL display "🟡 AT RISK"
- **WHEN** the sprint has more than 3 blocked tickets OR code review count > 12
- **THEN** the sheet SHALL display "🔴 CRITICAL"

### Requirement: Health Attribution Clarity
The skill documentation SHALL accurately describe where health thresholds apply.

#### Scenario: SKILL.md describes health correctly
- **WHEN** users read the jira-daily-reports skill documentation
- **THEN** health threshold documentation SHALL state that health applies to the Sprint Report's sprint-wide metrics
- **AND** it SHALL clarify that health is computed from blocked and code review status counts
- **AND** it SHALL distinguish from the standalone `sprint-health` report

### Requirement: Person Capacity Sort Behavior Documentation
The skill documentation SHALL describe the conditional sort behavior when planning data availability changes.

#### Scenario: Sort order changes based on planning availability
- **WHEN** planning data is available in the workbook
- **THEN** person rows SHALL be ordered by mapping sheet member order
- **WHEN** planning data is NOT available
- **THEN** person rows SHALL be sorted by logged total (desc), then worked tickets (desc), then person name (asc)
- **AND** this behavior SHALL be documented in the skill so users understand ordering may vary between runs
