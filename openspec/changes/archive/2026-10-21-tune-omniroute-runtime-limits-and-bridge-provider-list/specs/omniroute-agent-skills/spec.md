# Spec Delta

## ADDED Requirements

### Requirement: Host CLI bridge SHALL query daemon truth for provider inventory

The host CLI bridge (`~/.local/bin/omniroute`) SHALL query the live OmniRoute HTTP daemon on loopback for operational provider listings, routing requests over authenticated HTTP (`/api/providers?limit=5000`) rather than reading from or writing to local ephemeral SQLite state.

#### Scenario: omniroute providers list queries live daemon connections
- **WHEN** `omniroute providers list` is executed on the host
- **THEN** it SHALL request `/api/providers?limit=5000` from the active OmniRoute daemon using the resolved API key
- **AND** it SHALL output the list of active and configured provider connections in table format or JSON format matching upstream's `{ providers: [...] }` schema
- **AND** it SHALL NOT report "No providers configured." when connections exist in the live container database

#### Scenario: Daemon unreachable fails closed
- **WHEN** `omniroute providers list` is executed while the OmniRoute daemon is unreachable or down
- **THEN** it SHALL exit non-zero with an explicit error stating the daemon is unreachable
- **AND** it SHALL NOT fall back to creating or querying an empty local database
