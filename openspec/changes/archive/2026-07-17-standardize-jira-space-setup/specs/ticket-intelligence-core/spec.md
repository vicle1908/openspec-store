## MODIFIED Requirements

### Requirement: Be reusable across ecosystem consumers
The system SHALL allow at least `jira-epic-report`, `jira-daily-reports`, `webhook-receiver`, and Jira space setup workflows to consume the same analysis contract without duplicating the core signal extraction logic.

#### Scenario: Shared analysis runs from snapshot input
- **WHEN** a consumer or test provides a Jira snapshot input to the analysis layer
- **THEN** the system SHALL produce the same canonical bundle without requiring live Jira API access during bundle construction

#### Scenario: A consumer adapts the bundle
- **WHEN** a consumer needs a report, reminder, webhook decision, or setup evidence review
- **THEN** it SHALL adapt the shared ticket intelligence bundle instead of re-implementing the same core signals locally

#### Scenario: Consumer behavior stays local
- **WHEN** a consumer renders or acts on the bundle
- **THEN** presentation, prioritization thresholds, escalation ladders, and actioning logic SHALL remain in that consumer while the analysis contract stays shared

#### Scenario: Setup workflows reuse canonical filter metadata
- **WHEN** Jira space setup or alignment work captures canonical filter IDs, names, sharing state, spreadsheet metadata, or JQL intended for downstream automation
- **THEN** `ticket-intelligence-core` consumers SHALL be allowed to treat that metadata as supported upstream input for filter-driven analysis and onboarding flows
- **AND** consumers SHALL NOT require rediscovery of the same filter identity when the setup evidence already provides it
