## ADDED Requirements

### Requirement: Read channel messages
The system SHALL retrieve messages from a specified Teams channel and return them as structured JSON, including message body, sender, timestamp, and thread information. The CLI command `teams message list --team <id> --channel <id> --output json` SHALL return a JSON envelope with `success`, `data` (array of messages), and `metadata` fields.

#### Scenario: Retrieve recent messages from a channel
- **WHEN** an agent runs `teams message list --team <team-id> --channel <channel-id> --output json`
- **THEN** the command exits with code 0 and returns a JSON object containing an array of messages in `.data`, each with `body.content`, `from.user.displayName`, and `createdDateTime` fields

#### Scenario: Channel not found
- **WHEN** an agent requests messages from a non-existent channel
- **THEN** the command exits with code 5 (resource not found) and returns `{"success": false, "error": {"code": "RESOURCE_NOT_FOUND"}}`

#### Scenario: Permission denied for channel access
- **WHEN** an agent requests messages from a channel they don't have access to
- **THEN** the command exits with code 4 (permission denied)

### Requirement: Send channel messages
The system SHALL post messages to a specified Teams channel with support for plain text, HTML, and stdin piping. The CLI command `teams message send --team <id> --channel <id> --body <text>` SHALL return structured JSON with the created message ID.

#### Scenario: Send plain text message
- **WHEN** an agent runs `teams message send --team <team-id> --channel <channel-id> --body "Hello"`
- **THEN** the command exits with code 0 and returns JSON with the new message's `id` and `createdDateTime`

#### Scenario: Send message via stdin pipe
- **WHEN** an agent pipes command output: `kubectl get pods | teams message send --team <id> --channel <id> --stdin`
- **THEN** the stdin content is posted as the message body and the command exits with code 0

#### Scenario: Send HTML message with formatting
- **WHEN** an agent runs `teams message send --team <team-id> --channel <channel-id> --body "<h1>Title</h1><p>Content</p>" --content-type html`
- **THEN** the message is posted with HTML formatting rendered in Teams

### Requirement: Reply to messages (threaded)
The system SHALL post replies to specific messages within a channel thread using `teams message reply --team <id> --channel <id> --message <id> --body <text>`.

#### Scenario: Reply to existing message
- **WHEN** an agent runs `teams message reply --team <team-id> --channel <channel-id> --message <msg-id> --body "Thanks!"`
- **THEN** the reply appears in the message thread and the command exits with code 0

#### Scenario: Reply to deleted message
- **WHEN** an agent attempts to reply to a message that no longer exists
- **THEN** the command exits with code 5 (resource not found)

### Requirement: Pin and unpin messages
The system SHALL pin and unpin messages in a channel using `teams message pin` and `teams message unpin` commands.

#### Scenario: Pin a message
- **WHEN** an agent runs `teams message pin --team <team-id> --channel <channel-id> --message <msg-id>`
- **THEN** the message is pinned in the channel and the command exits with code 0

### Requirement: Add and remove reactions
The system SHALL add and remove emoji reactions to messages using `teams message react` and `teams message unreact` commands with supported reaction types (like, heart, laugh, surprised, sad, angry).

#### Scenario: Add like reaction
- **WHEN** an agent runs `teams message react --team <team-id> --channel <channel-id> --message <msg-id> --reaction like`
- **THEN** a like reaction is added to the message and the command exits with code 0

### Requirement: Delete messages
The system SHALL delete messages from a channel using `teams message delete --team <id> --channel <id> --message <id>`.

#### Scenario: Delete own message
- **WHEN** an agent runs `teams message delete --team <team-id> --channel <channel-id> --message <msg-id>`
- **THEN** the message is removed from the channel and the command exits with code 0

### Requirement: Get single message
The system SHALL retrieve a specific message by ID using `teams message get --team <id> --channel <id> --message <id>`.

#### Scenario: Get message by ID
- **WHEN** an agent runs `teams message get --team <team-id> --channel <channel-id> --message <msg-id> --output json`
- **THEN** the command returns the full message object including body, sender, and any replies
