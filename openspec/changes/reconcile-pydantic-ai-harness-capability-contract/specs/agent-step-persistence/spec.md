## ADDED Requirements

### Requirement: Shared history capabilities use caller-owned persistence

When a caller composes step persistence and conversation history search for one agent, both capabilities SHALL use the same caller-owned snapshot source and SHALL preserve its agent/run identity.

#### Scenario: Shared store is supplied

- **WHEN** a caller supplies one snapshot store to step persistence and conversation search
- **THEN** searches SHALL observe snapshots written by the runtime
- **AND** compaction-dropped turns SHALL remain searchable through retained snapshots

#### Scenario: Shared store is unavailable

- **WHEN** shared history is requested but the declared store cannot be opened or resolved
- **THEN** construction SHALL fail before model or tool execution
- **AND** the runtime SHALL not substitute a fresh disconnected in-memory store

#### Scenario: Search is not requested

- **WHEN** a caller composes step persistence without conversation search
- **THEN** step continuation SHALL retain its existing persistence semantics
- **AND** no search index or search tool SHALL be created implicitly
