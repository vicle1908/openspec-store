## ADDED Requirements

### Requirement: Download authenticated files via Playwright CLI
The skill SHALL provide a documented workflow to download files from authenticated web services (SharePoint, corporate portals, internal wikis) using Playwright with an existing Chrome profile's session cookies.

#### Scenario: Download SharePoint .docx with valid session
- **WHEN** agent invokes the download helper with a SharePoint document URL and a valid storage state file
- **THEN** the system downloads the .docx file to `~/.tdt/playwright/downloads/` and exits with code 0

#### Scenario: Download fails due to expired session
- **WHEN** agent invokes the download helper and the target redirects to a login page (URL contains `/login`, `/_forms/`, or `login.microsoftonline.com`)
- **THEN** the system exits with a non-zero code and prints: "Session expired for <service>. Re-run capture: npx playwright open --channel=chrome --user-data-dir=<profile-path> --save-storage=<state-path> <url>"

#### Scenario: Download with direct user-data-dir mode
- **WHEN** Chrome is not running and agent invokes `npx playwright open --channel=chrome --user-data-dir="$HOME/Library/Application Support/Google/Chrome/Profile 5" --save-storage=~/.tdt/playwright/auth-state.sharepoint.json <url>`
- **THEN** the browser opens with the profile's existing cookies and the agent can navigate to authenticated resources

### Requirement: SharePoint URL transformation for direct download
The skill SHALL automatically transform SharePoint Word Online viewer URLs into direct download URLs.

#### Scenario: Transform viewer URL to download URL
- **WHEN** the target URL matches SharePoint Doc.aspx pattern with `action=default` or no action parameter
- **THEN** the helper replaces `action=default` with `action=download` (or appends `&action=download`) before navigating

#### Scenario: URL already has action=download
- **WHEN** the target URL already contains `action=download`
- **THEN** the helper uses the URL as-is without modification

#### Scenario: Non-SharePoint URL passes through unchanged
- **WHEN** the target URL does not match SharePoint Doc.aspx pattern
- **THEN** the helper navigates to the URL without transformation

### Requirement: Profile discovery by email
The skill SHALL document how to identify the correct Chrome profile directory given a user email address.

#### Scenario: Find profile by email on macOS
- **WHEN** agent runs profile discovery searching `~/Library/Application Support/Google/Chrome/Profile */Preferences` for a matching email
- **THEN** the correct `Profile N` directory is identified (e.g., Profile 5 for `lekhanhvinh.phillip.com.sg@gmail.com`)

#### Scenario: No matching profile found
- **WHEN** agent searches all Chrome profiles and no email matches
- **THEN** the skill outputs an error message listing available profiles and their associated emails

### Requirement: Support multiple file types
The skill SHALL handle downloads of common document types without special configuration.

#### Scenario: Download PDF from authenticated portal
- **WHEN** agent requests a PDF URL via the download helper with valid storage state
- **THEN** the PDF is saved to the downloads directory with correct MIME type and extension

#### Scenario: Download triggers browser-rendered view instead of file
- **WHEN** the target URL renders the document in-browser (e.g., Word Online viewer) instead of triggering a download
- **THEN** the helper applies URL transformation (SharePoint) or locates the download button/link within the viewer to obtain the raw file

### Requirement: Output path control
The skill SHALL allow the caller to specify a custom output path for downloaded files.

#### Scenario: Custom output path specified
- **WHEN** agent provides `--out /path/to/custom/filename.docx`
- **THEN** the file is saved at the specified path, creating parent directories if needed

#### Scenario: No output path specified
- **WHEN** agent omits the `--out` flag
- **THEN** the file is saved to `~/.tdt/playwright/downloads/` with the filename from the HTTP response Content-Disposition header or URL basename

### Requirement: Chrome profile lock safety
The skill SHALL prevent concurrent access to a Chrome profile that is in use by a running Chrome instance.

#### Scenario: Chrome is running when user-data-dir mode requested
- **WHEN** agent attempts `--user-data-dir` mode and detects Chrome process running (via `pgrep -x "Google Chrome"`)
- **THEN** the skill aborts with error: "Chrome is running. Either close Chrome or use --load-storage mode instead." and suggests the `--load-storage` alternative command

#### Scenario: Chrome is not running
- **WHEN** agent checks for Chrome process and finds none
- **THEN** the skill proceeds with `--user-data-dir` mode normally

### Requirement: Use system Chrome via --channel=chrome
The skill SHALL default to using the system-installed Google Chrome binary instead of bundled Chromium.

#### Scenario: System Chrome available
- **WHEN** `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` exists
- **THEN** all Playwright commands include `--channel=chrome` flag by default

#### Scenario: System Chrome not available
- **WHEN** system Chrome is not found at the expected path
- **THEN** the skill falls back to bundled Chromium and instructs user to run `npx playwright install chromium`
