# M2 Platform Access Control

## ADDED Requirements

### Requirement: M2 Platform Detection

The system SHALL identify accounts that belong to the M2 platform based on account metadata.

#### Scenario: M2 account identified
- **WHEN** account has platform identifier "M2" or sub-account type "M2"
- **THEN** system SHALL flag the account as M2 platform

#### Scenario: Non-M2 account identified
- **WHEN** account does not have M2 platform identifier
- **THEN** system SHALL proceed with normal Single Ledger processing

### Requirement: M2 Platform Blocking

M2 platform accounts SHALL be blocked from accessing Single Ledger (Merged UX) functionality until backend migration is complete.

#### Scenario: M2 account attempts Merged UX
- **WHEN** M2 platform account requests CIS flag or attempts to access Merged UX
- **THEN** system SHALL return `{"blocked": true, "reason": "M2_PENDING_MIGRATION"}`

#### Scenario: M2 account shown blocking message
- **WHEN** mobile app detects M2 blocking response
- **THEN** app SHALL display appropriate message indicating feature unavailable

### Requirement: M2 Platform Rollout Coordination

The M2 access control implementation SHALL be coordinated with the backend migration team to ensure phased rollout.

#### Scenario: M2 blocking tied to migration milestone
- **WHEN** backend confirms M2 migration complete
- **THEN** Jira task for removing M2 blocking SHALL be created

### Requirement: M2 Detection Fields

The mobile app SHALL receive M2 platform identification via account metadata or dedicated endpoint.

#### Scenario: M2 flag in account metadata
- **WHEN** account metadata includes `platform: "M2"`
- **THEN** mobile app SHALL use this for access control decisions

#### Scenario: M2 flag missing
- **WHEN** account metadata does not include platform information
- **THEN** mobile app SHALL assume non-M2 platform
