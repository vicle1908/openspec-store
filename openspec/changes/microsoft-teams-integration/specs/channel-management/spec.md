## ADDED Requirements

### Requirement: List teams and channels
The system SHALL retrieve all teams the authenticated app has access to and list channels within a specific team. The CLI commands `teams team list --output json` and `teams channel list <team-id> --output json` SHALL return structured JSON arrays.

#### Scenario: List all accessible teams
- **WHEN** an agent runs `teams team list --output json`
- **THEN** the command exits with code 0 and returns a JSON array of team objects with `id` and `displayName` fields

#### Scenario: List channels in a team
- **WHEN** an agent runs `teams channel list <team-id> --output json`
- **THEN** the command exits with code 0 and returns a JSON array of channel objects with `id`, `displayName`, and `description` fields

### Requirement: Create channels
The system SHALL create standard and private channels within a team using `teams channel create <team-id> --name <name> [--description <desc>] [--type private]`.

#### Scenario: Create a standard channel
- **WHEN** an agent runs `teams channel create <team-id> --name "sprint-15" --description "Sprint 15 tracking"`
- **THEN** the channel is created, the command exits with code 0, and returns JSON with the new channel's `id`

#### Scenario: Create a private channel
- **WHEN** an agent runs `teams channel create <team-id> --name "leads-only" --type private`
- **THEN** a private channel is created and the command exits with code 0

### Requirement: Delete channels
The system SHALL delete channels from a team using `teams channel delete <team-id> <channel-id>`.

#### Scenario: Delete an existing channel
- **WHEN** an agent runs `teams channel delete <team-id> <channel-id>`
- **THEN** the channel is removed and the command exits with code 0

### Requirement: Manage channel membership
The system SHALL list and add members to a channel using `teams channel members list` and `teams channel members add <team-id> <channel-id> --user-id <id>`.

#### Scenario: List channel members
- **WHEN** an agent runs `teams channel members list <team-id> <channel-id> --output json`
- **THEN** the command returns a JSON array of member objects with `id` and `displayName` fields

#### Scenario: Add a member to a channel
- **WHEN** an agent runs `teams channel members add <team-id> <channel-id> --user-id <user-id>`
- **THEN** the user is added to the channel and the command exits with code 0

### Requirement: Manage team lifecycle
The system SHALL create, delete, clone, and archive teams using `teams team create`, `teams team delete`, `teams team clone`, and `teams team archive` commands.

#### Scenario: Create a new team
- **WHEN** an agent runs `teams team create --name "Engineering"`
- **THEN** the team is created and the command returns JSON with the new team's `id`

#### Scenario: Clone an existing team
- **WHEN** an agent runs `teams team clone <team-id> --name "Engineering Copy" --parts channels,members`
- **THEN** a new team is created with cloned channels and members, and the command exits with code 0
