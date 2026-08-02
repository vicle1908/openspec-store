# CIS Flag API Contract

## ADDED Requirements

### Requirement: CIS Flag Endpoint

The system SHALL provide a REST API endpoint to retrieve the CIS flag status for a given account. The CIS flag determines whether the account should receive the Legacy UX or Merged UX.

#### Scenario: Retrieve CIS flag for eligible account
- **WHEN** mobile app requests CIS flag for an account eligible for Merged UX
- **THEN** system SHALL return `{"cisFlag": true, "uxMode": "MERGED"}`

#### Scenario: Retrieve CIS flag for legacy account
- **WHEN** mobile app requests CIS flag for an account not yet migrated
- **THEN** system SHALL return `{"cisFlag": false, "uxMode": "LEGACY"}`

#### Scenario: CIS flag unavailable for account
- **WHEN** mobile app requests CIS flag for a non-existent account
- **THEN** system SHALL return HTTP 404 with error code `ACCOUNT_NOT_FOUND`

### Requirement: CIS Flag Response Schema

The CIS flag API response SHALL include the following fields:
- `cisFlag` (boolean): Whether the account is enabled for Merged UX
- `uxMode` (string): Either "MERGED" or "LEGACY"
- `accountId` (string): The account identifier
- `effectiveDate` (ISO 8601 datetime): When the flag takes effect

#### Scenario: Complete CIS flag response
- **WHEN** backend returns CIS flag data
- **THEN** response SHALL include all required fields and conform to schema version 1.0

### Requirement: CIS Flag Caching

The mobile app SHALL cache CIS flag responses locally with a maximum TTL of 5 minutes.

#### Scenario: Cache expiration
- **WHEN** cached CIS flag exceeds 5 minutes
- **THEN** mobile app SHALL refresh from API before rendering UI

### Requirement: CIS Flag Error Handling

The mobile app SHALL gracefully handle CIS flag API failures by falling back to Legacy UX.

#### Scenario: API timeout
- **WHEN** CIS flag API times out (>3 seconds)
- **THEN** mobile app SHALL default to Legacy UX and log the error

#### Scenario: API returns 5xx error
- **WHEN** CIS flag API returns server error
- **THEN** mobile app SHALL default to Legacy UX and retry with exponential backoff

### Requirement: CIS Flag Blocking

No UI feature tasks SHALL be marked complete until the CIS flag API contract is agreed upon with backend team.

#### Scenario: API contract review
- **WHEN** CIS flag spec is finalized
- **THEN** backend team SHALL sign off on the API contract before implementation proceeds
