## ADDED Requirements

### Requirement: Explicit spreadsheet health contract

The spreadsheet reporter SHALL use documented blocked-percentage and root-blocker boundaries for each health tier. Boundary values, labels, and colors MUST be covered by automated tests and MUST remain consistent between summary and detail outputs.

#### Scenario: Health boundary is evaluated

- **WHEN** blocked percentage or root-blocker count is exactly at a configured tier boundary
- **THEN** the report assigns the documented tier, label, and color
- **AND** the same inputs produce the same tier in every managed tab

### Requirement: Truthful capacity utilization

A metric labeled Effective Utilization SHALL be calculated only when authoritative logged effort, planned estimate, and blocked-time inputs are available. When required inputs are absent, the report MUST display an explicit unavailable state and MUST NOT label an item-count proxy as time utilization.

#### Scenario: Time inputs are unavailable

- **WHEN** a person lacks logged effort, planned estimate, or blocked-time data
- **THEN** Effective Utilization is rendered as unavailable
- **AND** any item-flow proxy is separately named and explained

#### Scenario: Time inputs are available

- **WHEN** authoritative logged effort, planned estimate, and blocked-time values are present
- **THEN** Effective Utilization is calculated from those values using a bounded documented formula

### Requirement: Optional role-aware capacity grouping

The capacity output SHALL group people by role when a normalized role value is available and SHALL retain an ungrouped fallback when it is not. Missing role data MUST NOT drop a person from capacity output.

#### Scenario: Mixed role availability

- **WHEN** some people have normalized roles and others do not
- **THEN** role summaries include known roles and an explicit ungrouped category
- **AND** every person remains represented exactly once

### Requirement: Managed blocking filters

Managed blocking tables SHALL include a supported filter mechanism for issue key, status, assignee, blocker state, and impact tier. Failure to create a required managed filter MUST be surfaced as a managed-output failure.

#### Scenario: Blocking tab is synchronized

- **WHEN** the Blocking Dependencies tab is created or updated
- **THEN** its managed data range has filters for the documented exploration fields
- **AND** stakeholder-owned tabs remain unchanged
