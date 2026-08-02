# Capability: delivery-plan-jira-link-display

## Purpose

Display the ticket number as a clickable hyperlink in the Jira Link column of the Delivery Plan Analysis tab.

## ADDED Requirements

### Requirement: Jira Link column SHALL display ticket number as hyperlink

The Jira Link column SHALL display the ticket number (e.g., "RMD-4160") as a clickable hyperlink to the actual ticket URL.

#### Scenario: Ticket number hyperlink display

- **WHEN** the Delivery Plan Analysis tab is generated
- **THEN** the Jira Link column SHALL display the ticket number (e.g., "RMD-4160")
- **AND** SHALL be a clickable hyperlink to the ticket URL (e.g., "https://psplit.atlassian.net/browse/RMD-4160")
- **AND** SHALL NOT display the full URL as text
