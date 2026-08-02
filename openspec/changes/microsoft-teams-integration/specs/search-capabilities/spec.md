## ADDED Requirements

### Requirement: Search messages across Teams
The system SHALL perform full-text search across all accessible Teams messages using `teams search messages --query <text>` and return ranked results with message content, sender, channel, and timestamp. Results SHALL be filterable by team, channel, date range, and sender.

#### Scenario: Search messages by keyword
- **WHEN** an agent runs `teams search messages --query "deploy" --output json`
- **THEN** the command exits with code 0 and returns a JSON array of matching messages with `body.content`, `from.user.displayName`, `channelIdentity`, and `createdDateTime` fields

#### Scenario: Search messages with team filter
- **WHEN** an agent runs `teams search messages --query "release" --team <team-id> --output json`
- **THEN** the command returns only messages from the specified team matching the query

#### Scenario: Search with no results
- **WHEN** an agent searches for a term that matches no messages
- **THEN** the command exits with code 0 and returns `{"success": true, "data": []}` (empty array, not an error)

### Requirement: Search users
The system SHALL search for users across the tenant by name or email using `teams search users --query <text>` and return structured results with user IDs, display names, and email addresses.

#### Scenario: Search users by partial name
- **WHEN** an agent runs `teams search users --query "john" --output json`
- **THEN** the command returns all users whose display name or email contains "john" (case-insensitive)

#### Scenario: Search users by email
- **WHEN** an agent runs `teams search users --query "john@example.com" --output json`
- **THEN** the command returns the exact user match if found, or an empty array if not

### Requirement: Search teams
The system SHALL search for teams by name using `teams search teams --query <text>` and return matching team objects with IDs, display names, and descriptions.

#### Scenario: Search teams by name
- **WHEN** an agent runs `teams search teams --query "engineering" --output json`
- **THEN** the command returns all teams whose display name contains "engineering" (case-insensitive)

### Requirement: Message content extraction from search
The system SHALL extract clean, searchable text content from search results, stripping HTML tags and normalizing formatting for downstream processing.

#### Scenario: Extract plain text from HTML message
- **WHEN** a search result contains HTML-formatted message body
- **THEN** the `--output json` response includes both raw `body.content` (HTML) and a `body.contentText` field (plain text)
