## ADDED Requirements

### Requirement: Search users
The system SHALL search for users by name or email using `teams search users --query <text> --output json` and return structured results matching the query against display names and email addresses.

#### Scenario: Find user by display name
- **WHEN** an agent runs `teams search users --query "vinh" --output json`
- **THEN** the command exits with code 0 and returns a JSON array of user objects with `id`, `displayName`, and `mail` fields for all matching users

#### Scenario: No users found
- **WHEN** an agent searches for a non-existent user
- **THEN** the command exits with code 0 and returns `{"data": []}` (empty array, not an error)

### Requirement: Get user presence
The system SHALL retrieve the presence status (available, busy, do-not-disturb, away, offline) of the authenticated user or a specific user using `teams presence get [--user-id <id>] --output json`.

#### Scenario: Get own presence
- **WHEN** an agent runs `teams presence get --output json`
- **THEN** the command returns JSON with `availability` and `activity` fields for the authenticated service principal

#### Scenario: Get another user's presence
- **WHEN** an agent runs `teams presence get --user-id <user-id> --output json`
- **THEN** the command returns JSON with the target user's presence information including `availability`, `activity`, and `lastSeenDateTime`

### Requirement: Set availability
The system SHALL set the authenticated user's availability status using `teams presence set --availability <status> --activity <activity>`.

#### Scenario: Set presence to available
- **WHEN** an agent runs `teams presence set --availability Available --activity Available`
- **THEN** the user's presence is updated and the command exits with code 0

### Requirement: Set status message
The system SHALL set a custom status message with optional expiry using `teams presence status --message <text> [--expiry <datetime>]`.

#### Scenario: Set status message with expiry
- **WHEN** an agent runs `teams presence status --message "In deep focus" --expiry "2026-05-18T18:00:00Z"`
- **THEN** the status message is set, expires at the specified time, and the command exits with code 0

### Requirement: Mention users in messages
The system SHALL mention users in channel messages using HTML `<at>` tags combined with the `--mentions` flag. The mentions array SHALL specify the mention ID, display text, and target user ID.

#### Scenario: Mention a user in a channel message
- **WHEN** an agent runs `teams message send --team <team-id> --channel <channel-id> --body '<at id="0">John Doe</at> please review' --content-type html --mentions '[{"id": 0, "mentionText": "John Doe", "userId": "<user-id>"}]'`
- **THEN** the message is posted with an active @mention that notifies the target user, and the command exits with code 0

#### Scenario: Mention user not in team
- **WHEN** an agent attempts to mention a user who is not a member of the target team
- **THEN** the command exits with code 4 (permission denied) or the mention is silently ignored
