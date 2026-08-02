## ADDED Requirements

### Requirement: Spreadsheet URL parsing
The system SHALL parse Google Sheets URLs to extract spreadsheet ID and optional GID (sheet ID).

#### Scenario: Standard edit URL
- **WHEN** user provides URL 'https://docs.google.com/spreadsheets/d/ABC123/edit'
- **THEN** system returns spreadsheet_id='ABC123', gid=None

#### Scenario: URL with GID in fragment
- **WHEN** user provides URL 'https://docs.google.com/spreadsheets/d/ABC123/edit#gid=456'
- **THEN** system returns spreadsheet_id='ABC123', gid=456

#### Scenario: URL with GID in query parameter
- **WHEN** user provides URL 'https://docs.google.com/spreadsheets/d/ABC123/edit?gid=456'
- **THEN** system returns spreadsheet_id='ABC123', gid=456

#### Scenario: URL with GID in both locations
- **WHEN** user provides URL with GID in query and fragment
- **THEN** system returns the GID from fragment (takes precedence)

#### Scenario: Invalid URL format
- **WHEN** user provides URL that doesn't match Google Sheets pattern
- **THEN** system returns spreadsheet_id=None, gid=None

#### Scenario: Spreadsheet ID format validation
- **WHEN** extracted spreadsheet ID contains only alphanumeric, hyphen, underscore
- **THEN** system accepts ID as valid

### Requirement: GID to sheet name resolution
The system SHALL resolve numeric GID to human-readable sheet name via Sheets API.

#### Scenario: Successful GID resolution
- **WHEN** user calls resolve_gid(spreadsheet_id, gid=123)
- **THEN** system queries spreadsheet metadata and returns matching sheet title

#### Scenario: GID not found
- **WHEN** user provides GID that doesn't exist in spreadsheet
- **THEN** system returns None

#### Scenario: Multiple sheets with metadata lookup
- **WHEN** spreadsheet contains 20 sheets
- **THEN** system retrieves all sheet properties in single API call and finds match

#### Scenario: Default sheet (GID 0)
- **WHEN** user resolves gid=0
- **THEN** system returns name of first sheet in spreadsheet

#### Scenario: API error during resolution
- **WHEN** spreadsheet metadata fetch fails (permission denied, not found)
- **THEN** system raises appropriate exception with spreadsheet ID in message

### Requirement: Sheet name to GID resolution
The system SHALL resolve human-readable sheet name to numeric GID via Sheets API.

#### Scenario: Successful name resolution
- **WHEN** user calls resolve_sheet_name(spreadsheet_id, sheet_name='Person Capacity')
- **THEN** system queries spreadsheet metadata and returns matching GID

#### Scenario: Sheet name not found
- **WHEN** user provides sheet name that doesn't exist
- **THEN** system returns None

#### Scenario: Case-sensitive matching
- **WHEN** user searches for sheet name with different case
- **THEN** system performs case-sensitive match (Sheet1 ≠ sheet1)

### Requirement: Spreadsheet ID validation
The system SHALL validate spreadsheet ID format before making API calls.

#### Scenario: Valid spreadsheet ID
- **WHEN** user provides ID matching pattern [a-zA-Z0-9_-]+
- **THEN** system validates ID as acceptable

#### Scenario: Invalid characters in ID
- **WHEN** user provides ID with spaces or special characters
- **THEN** system raises ValueError with format requirements

#### Scenario: Empty spreadsheet ID
- **WHEN** user provides empty string or None as spreadsheet_id
- **THEN** system raises ValueError indicating ID is required

### Requirement: A1 notation validation
The system SHALL validate A1 notation range format.

#### Scenario: Valid single cell
- **WHEN** user provides range 'A1'
- **THEN** system validates as acceptable

#### Scenario: Valid range
- **WHEN** user provides range 'Sheet1!A1:D10'
- **THEN** system validates as acceptable

#### Scenario: Valid entire sheet
- **WHEN** user provides range 'Sheet1'
- **THEN** system validates as acceptable

#### Scenario: Invalid range format
- **WHEN** user provides malformed range 'Sheet1!A1-D10' (hyphen instead of colon)
- **THEN** system raises ValueError with correct format example

#### Scenario: Column-only range
- **WHEN** user provides range 'A:Z'
- **THEN** system validates as acceptable (entire columns)

#### Scenario: Row-only range
- **WHEN** user provides range '1:10'
- **THEN** system validates as acceptable (entire rows)

### Requirement: URL construction
The system SHALL construct valid Google Sheets URLs from spreadsheet ID and optional GID.

#### Scenario: Construct URL without GID
- **WHEN** user calls construct_url(spreadsheet_id='ABC123')
- **THEN** system returns 'https://docs.google.com/spreadsheets/d/ABC123/edit'

#### Scenario: Construct URL with GID
- **WHEN** user calls construct_url(spreadsheet_id='ABC123', gid=456)
- **THEN** system returns 'https://docs.google.com/spreadsheets/d/ABC123/edit#gid=456'

#### Scenario: Construct URL with sheet name
- **WHEN** user calls construct_url with sheet_name parameter
- **THEN** system resolves sheet name to GID first, then constructs URL

### Requirement: Utility function caching
The system SHALL cache metadata lookups to minimize API calls.

#### Scenario: First GID resolution
- **WHEN** user resolves GID for a spreadsheet for first time
- **THEN** system fetches metadata via API and caches sheet list

#### Scenario: Subsequent GID resolution for same spreadsheet
- **WHEN** user resolves different GID for same spreadsheet_id
- **THEN** system uses cached metadata without additional API call

#### Scenario: Cache invalidation
- **WHEN** cache entry is older than 5 minutes
- **THEN** system refetches metadata on next resolution

#### Scenario: Explicit cache clear
- **WHEN** user calls clear_metadata_cache()
- **THEN** system removes all cached spreadsheet metadata
