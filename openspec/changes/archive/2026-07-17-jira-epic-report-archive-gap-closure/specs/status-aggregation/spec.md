## ADDED Requirements

### Requirement: Consistent completion status semantics

Report and dashboard completion calculations SHALL use one authoritative status-weight mapping or an explicit normalization layer for dashboard-only Jira statuses. The same normalized status MUST NOT produce contradictory completion percentages across output formats.

#### Scenario: Dashboard-only status is aggregated

- **WHEN** a collected item has a supported workflow status not present in the core display categories
- **THEN** the status is normalized to a documented completion weight
- **AND** report and dashboard calculations produce the same weighted contribution
