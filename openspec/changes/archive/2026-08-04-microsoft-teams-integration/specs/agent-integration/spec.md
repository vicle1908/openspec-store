## ADDED Requirements

### Requirement: Delegated authentication via device code flow
The system SHALL authenticate using Azure AD device code flow for development and testing. The CLI command `teams auth login --device-code --client-id <id> --tenant-id <id>` SHALL display a URL and code for the user to complete authentication in a browser on any device. Tokens SHALL be cached in the OS keyring for subsequent commands within the same session.

#### Scenario: Device code authentication
- **WHEN** an agent runs `teams auth login --device-code --client-id <client-id> --tenant-id <tenant-id>`
- **THEN** the CLI displays a URL (https://login.microsoft.com/device) and an 8-character code, and upon successful browser-based sign-in, caches the token for subsequent commands

#### Scenario: Device code expires before sign-in
- **WHEN** the user does not complete sign-in within 15 minutes (device code expiry)
- **THEN** the CLI returns exit code 3 (authentication error) and provides a fresh code on the next attempt

#### Scenario: User cancels device code sign-in
- **WHEN** the user cancels the browser-based sign-in flow
- **THEN** the CLI returns exit code 3 (authentication error) with a descriptive message

### Requirement: Application authentication via client credentials flow
The system SHALL authenticate using Azure AD client credentials flow for production and CI/CD without any browser interaction. The CLI command `teams auth login --client-credentials` SHALL use `TEAMS_CLI_CLIENT_ID`, `TEAMS_CLI_CLIENT_SECRET`, and `TEAMS_CLI_TENANT_ID` environment variables (or `--client-id`, `--client-secret`, `--tenant-id` flags) to obtain an access token. This flow requires admin consent for Application permissions in Azure AD. Tokens SHALL be cached in the OS keyring for subsequent commands.

#### Scenario: Authenticate with environment variables
- **WHEN** environment variables are set and admin consent has been granted, and the agent runs `teams auth login --client-credentials`
- **THEN** the command exits with code 0, caches the token, and subsequent commands succeed without re-authentication

#### Scenario: Missing credentials
- **WHEN** required environment variables are not set and no flags are provided
- **THEN** the command exits with code 10 (configuration error) and displays which variables are missing

#### Scenario: Admin consent not granted
- **WHEN** the application has Application permissions but admin consent is pending
- **THEN** the command exits with code 3 (authentication error) with a message indicating admin consent is required

### Requirement: Pre-obtained token bypass
The system SHALL accept a pre-obtained access token via `TEAMS_CLI_ACCESS_TOKEN` environment variable or `teams auth token` command output, bypassing the login flow entirely for the current session.

#### Scenario: Use pre-obtained token
- **WHEN** `TEAMS_CLI_ACCESS_TOKEN` is set to a valid JWT
- **THEN** any Teams command succeeds without running `teams auth login`

### Requirement: Profile management
The system SHALL support multiple authentication profiles (e.g., prod, staging, dev) via `--profile <name>` flag, with each profile storing separate credentials in the config file at `~/.config/teams-cli/config.toml` (Linux) or `~/Library/Application Support/teams-cli/config.toml` (macOS).

#### Scenario: Switch between profiles
- **WHEN** an agent runs `teams --profile prod team list` then `teams --profile staging team list`
- **THEN** each command uses the correct profile's credentials and returns the appropriate team list

#### Scenario: Profile not found
- **WHEN** an agent uses `--profile unknown` and the profile does not exist in config
- **THEN** the command exits with code 10 (configuration error)

### Requirement: Credential resolution order
The system SHALL resolve credentials in this priority order: CLI flags > environment variables > config file profiles. The first source that provides all required values SHALL be used.

#### Scenario: CLI flags override environment
- **WHEN** both `--client-id` flag and `TEAMS_CLI_CLIENT_ID` env var are set with different values
- **THEN** the CLI flag value is used

### Requirement: Token caching and refresh
The system SHALL cache access tokens in the OS keyring and automatically refresh them before expiry. The cached token SHALL be reused across commands without re-authentication until it expires or the user runs `teams auth logout`.

#### Scenario: Token reuse across commands
- **WHEN** an agent authenticates once then runs multiple Teams commands
- **THEN** all commands succeed without re-authentication until the token expires

#### Scenario: Token expired and refresh fails
- **WHEN** the cached refresh token has expired
- **THEN** the command exits with code 3 (authentication error) and the agent must re-authenticate
