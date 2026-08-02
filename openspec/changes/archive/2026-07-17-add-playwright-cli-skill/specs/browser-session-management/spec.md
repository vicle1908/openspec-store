## ADDED Requirements

### Requirement: Capture storage state from existing Chrome profile
The skill SHALL provide a documented workflow to export browser storage state (cookies, localStorage, sessionStorage) from a Chrome profile to a portable JSON file.

#### Scenario: First-time capture with Chrome closed
- **WHEN** agent runs the capture command with `--user-data-dir` pointing to a Chrome profile and `--save-storage` pointing to a target JSON path while Chrome is not running
- **THEN** Playwright opens the browser with the profile's session, the user verifies the target site loads authenticated, closes the browser, and a storage state JSON is written to the target path

#### Scenario: Capture aborted by profile lock
- **WHEN** agent runs the capture command while Chrome is still running with the target profile
- **THEN** Playwright fails to acquire the profile lock and the skill surfaces a clear "close Chrome first" error

#### Scenario: Capture creates restricted-permission file
- **WHEN** the capture command completes successfully
- **THEN** the storage state file is created with mode `0600` (owner read/write only) under `~/.tdt/playwright/`

### Requirement: Reuse storage state without touching live profile
The skill SHALL allow agents to launch Playwright sessions that reuse a previously captured storage state without requiring Chrome to be closed.

#### Scenario: Reuse with --load-storage on running Chrome
- **WHEN** Chrome is running and agent launches Playwright with `--load-storage=<auth-state.json>`
- **THEN** Playwright opens an isolated browser context with the captured cookies and authenticates to the target site without interfering with the running Chrome instance

#### Scenario: Reuse with programmatic API
- **WHEN** the helper script calls `chromium.launch()` and `browser.newContext({ storageState: '<auth-state.json>' })`
- **THEN** the new context inherits the captured cookies and can request authenticated resources

### Requirement: Per-service storage state files
The skill SHALL support maintaining multiple storage state files keyed by service name to avoid cookie collisions across tenants and services.

#### Scenario: Service-specific filename convention
- **WHEN** agent captures state for SharePoint and separately for GitLab
- **THEN** the files are saved as `~/.tdt/playwright/auth-state.sharepoint.json` and `~/.tdt/playwright/auth-state.gitlab.json` respectively

#### Scenario: Default state file when service not specified
- **WHEN** agent captures state without specifying a service
- **THEN** the file is saved as `~/.tdt/playwright/auth-state.json` and a warning notes per-service files are recommended for production use

### Requirement: Detect expired sessions
The skill SHALL detect when a captured storage state has expired and surface an actionable error.

#### Scenario: Expired session redirects to login
- **WHEN** the helper script navigates to a target URL using a stale storage state and the response redirects to a login page (URL contains `/login`, `/signin`, `/_forms/default.aspx`, or matches Microsoft Online login domains)
- **THEN** the helper exits non-zero and prints "Session expired for <service>. Re-run capture step: <command>"

#### Scenario: Session valid
- **WHEN** the helper navigates and the target page loads authenticated (no login redirect, expected DOM markers present)
- **THEN** the helper proceeds with the requested operation

### Requirement: Storage state security
The skill SHALL enforce baseline security practices for storage state files.

#### Scenario: Storage path is outside legacy cloud
- **WHEN** the skill writes a storage state file
- **THEN** the path is under `~/.tdt/` (outside legacy cloud workspace) to prevent sync corruption and exfiltration

#### Scenario: Storage files are gitignored
- **WHEN** any repo's `.gitignore` is generated or updated as part of skill setup
- **THEN** patterns matching `auth-state*.json`, `playwright/auth-state*`, and `.tdt/` are present

#### Scenario: Storage files never committed
- **WHEN** an agent processes a code change
- **THEN** the agent verifies no `auth-state*.json` files are staged before commit and warns if any are detected

### Requirement: Document session refresh workflow
The skill SHALL document how to refresh an expired storage state without losing other captured sessions.

#### Scenario: Refresh single service state
- **WHEN** agent reports an expired SharePoint session
- **THEN** the documented refresh command rewrites only `auth-state.sharepoint.json` and leaves other service state files untouched

#### Scenario: Storage rotation cadence guidance
- **WHEN** an agent or user reads the skill's session management reference
- **THEN** the document states recommended rotation cadence (capture-on-demand for short-lived tokens, scheduled re-capture every 7 days for long-lived sessions)
