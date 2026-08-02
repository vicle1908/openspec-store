# Options Activation Flow

## ADDED Requirements

### Requirement: Options Activation Toggle

The system SHALL provide a user-controllable toggle to activate or deactivate options trading visibility within the Merged UX.

#### Scenario: User activates options
- **WHEN** user with options-enabled account toggles options activation ON
- **THEN** system SHALL display options positions and transactions in the unified views

#### Scenario: User deactivates options
- **WHEN** user toggles options activation OFF
- **THEN** system SHALL hide options positions and transactions, showing only stocks

### Requirement: Options Activation Persistence

The options activation preference SHALL be persisted per account and retained across sessions.

#### Scenario: Preference persisted
- **WHEN** user changes options activation setting
- **THEN** preference SHALL be saved to backend and synced on next app launch

#### Scenario: Preference loaded on launch
- **WHEN** mobile app loads user account
- **THEN** app SHALL fetch stored options activation preference

### Requirement: Options Activation State

The options activation state SHALL be reflected in the CIS flag response or via a separate account preferences API.

#### Scenario: Options state in CIS response
- **WHEN** CIS flag API is called
- **THEN** response SHALL include `optionsEnabled: boolean` field

### Requirement: Options Activation for Non-Options Accounts

Accounts without options trading privileges SHALL NOT show the options activation toggle.

#### Scenario: Non-options account
- **WHEN** account does not have options trading enabled
- **THEN** mobile app SHALL NOT display options activation toggle

### Requirement: Options Activation Transition

When a user activates options after initially being in stocks-only mode, the app SHALL fetch options data and seamlessly integrate it into existing views.

#### Scenario: First-time options activation
- **WHEN** user activates options for the first time
- **THEN** app SHALL fetch options positions/transactions and update UI without requiring app restart
