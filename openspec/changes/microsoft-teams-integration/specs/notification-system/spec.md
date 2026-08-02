## ADDED Requirements

### Requirement: Notify individual users
The system SHALL send targeted notifications to specific users using `teams notify send --user-id <id> --topic <text> --activity-type <type> --preview <text>`. Supported activity types SHALL include `taskCreated`, `deploymentComplete`, `statusUpdate`, and custom strings.

#### Scenario: Send task notification to user
- **WHEN** an agent runs `teams notify send --user-id <user-id> --topic "New Assignment" --activity-type taskCreated --preview "You have a new Jira task"`
- **THEN** the user receives a Teams notification with the specified topic, activity type, and preview text, and the command exits with code 0

#### Scenario: Notify user not found
- **WHEN** an agent attempts to notify a non-existent user ID
- **THEN** the command exits with code 5 (resource not found)

### Requirement: Notify teams
The system SHALL send notifications to all members of a team using `teams notify send-to-team --team-id <id> --topic <text> --activity-type <type> --preview <text>`.

#### Scenario: Send deployment notification to team
- **WHEN** an agent runs `teams notify send-to-team --team-id <team-id> --topic "Deploy" --activity-type deploymentComplete --preview "v2.3.1 deployed"`
- **THEN** all team members receive the notification and the command exits with code 0

### Requirement: Notify chat participants
The system SHALL send notifications to all participants in a chat using `teams notify send-to-chat --chat-id <id> --topic <text> --activity-type <type> --preview <text>`.

#### Scenario: Send status update to chat
- **WHEN** an agent runs `teams notify send-to-chat --chat-id <chat-id> --topic "Update" --activity-type statusUpdate --preview "Status changed"`
- **THEN** all chat participants receive the notification and the command exits with code 0

### Requirement: Fan-out notifications
The system SHALL support broadcasting a single notification to all channels in a team by piping channel list output into the notify command.

#### Scenario: Fan-out to all channels
- **WHEN** an agent runs `teams channel list <team-id> --output json | jq -r '.data[].id' | xargs -I{} teams notify send-to-team --team-id <team-id> --topic "Broadcast" --activity-type statusUpdate --preview "All channels"`
- **THEN** every channel in the team receives the notification
