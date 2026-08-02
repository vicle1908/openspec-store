## ADDED Requirements

### Requirement: Service account authentication
The system SHALL authenticate to Google Sheets API using service account credentials from a JSON key file.

#### Scenario: Successful authentication with explicit path
- **WHEN** GOOGLE_SERVICE_ACCOUNT_PATH environment variable is set to a valid service account JSON file
- **THEN** system loads credentials from that file and authenticates successfully

#### Scenario: Fallback to standard Google path
- **WHEN** GOOGLE_SERVICE_ACCOUNT_PATH is not set but GOOGLE_APPLICATION_CREDENTIALS is set
- **THEN** system loads credentials from GOOGLE_APPLICATION_CREDENTIALS path

#### Scenario: Default path fallback
- **WHEN** neither GOOGLE_SERVICE_ACCOUNT_PATH nor GOOGLE_APPLICATION_CREDENTIALS is set
- **THEN** system attempts to load credentials from ~/.tdt/google-service-account.json

#### Scenario: Missing service account file
- **WHEN** all fallback paths are exhausted and no service account file exists
- **THEN** system raises FileNotFoundError with clear error message indicating checked paths

### Requirement: Credential caching
The system SHALL cache loaded credentials at module level to avoid repeated file reads and API calls.

#### Scenario: First credential load
- **WHEN** credentials are requested for the first time
- **THEN** system loads from file, caches in memory, and returns credentials

#### Scenario: Subsequent credential requests
- **WHEN** credentials are requested again with same service account path
- **THEN** system returns cached credentials without reading file again

#### Scenario: Different service account paths
- **WHEN** credentials are requested with a different service account path
- **THEN** system loads and caches credentials separately for each unique path

### Requirement: Token refresh
The system SHALL automatically refresh expired access tokens before making API calls.

#### Scenario: Token still valid
- **WHEN** cached credentials have a token that expires more than 60 seconds in the future
- **THEN** system returns cached credentials without refresh

#### Scenario: Token expiring soon
- **WHEN** cached credentials have a token expiring within 60 seconds
- **THEN** system refreshes the token before returning credentials

#### Scenario: Token already expired
- **WHEN** cached credentials have an expired token
- **THEN** system refreshes the token before returning credentials

#### Scenario: Token refresh failure
- **WHEN** token refresh fails (network error, revoked credentials)
- **THEN** system clears cache and attempts to reload credentials from file

### Requirement: Environment loading integration
The system SHALL integrate with tdt_core.env.load_tdt_env() when available to load ~/.tdt/.env before resolving paths.

#### Scenario: tdt_core available
- **WHEN** tdt_core package is installed and load_tdt_env() is available
- **THEN** system calls load_tdt_env() before checking environment variables

#### Scenario: tdt_core not available
- **WHEN** tdt_core package is not installed
- **THEN** system proceeds with environment variable resolution using current environment

### Requirement: API scopes configuration
The system SHALL request appropriate Google API scopes for Sheets and Drive access.

#### Scenario: Default scopes
- **WHEN** credentials are loaded without custom scope specification
- **THEN** system requests scopes: https://www.googleapis.com/auth/spreadsheets and https://www.googleapis.com/auth/drive

#### Scenario: Sheets-only usage
- **WHEN** user only needs Sheets API access
- **THEN** system supports loading credentials with spreadsheets scope only

### Requirement: Thread safety
The system SHALL ensure credential caching and token refresh are thread-safe for concurrent access.

#### Scenario: Concurrent authentication requests
- **WHEN** multiple threads request credentials simultaneously
- **THEN** system ensures only one thread loads credentials and others wait for cached result

#### Scenario: Concurrent token refresh
- **WHEN** multiple threads detect expired token simultaneously
- **THEN** system ensures only one thread refreshes token and others use refreshed result
