## ADDED Requirements

### Requirement: Shared history capabilities use caller-owned persistence

When a caller composes step persistence and conversation history search for one agent, both capabilities SHALL use the same caller-owned snapshot source and SHALL preserve its agent/run identity. Shared-store search SHALL default to `scope="conversation"` and use the stable conversation identity supplied by the public runtime; it SHALL not expose another conversation's history.

#### Scenario: Shared store is supplied

- **WHEN** a caller supplies one snapshot store to step persistence and conversation search
- **THEN** searches SHALL observe snapshots written by the runtime
- **AND** acceptance SHALL prove both capabilities were constructed from the exact same caller-owned store object without private upstream attribute access
- **AND** compaction-dropped turns SHALL remain searchable through retained snapshots

#### Scenario: Shared store isolates conversations

- **WHEN** two agents or runs with different stable conversation identities write to the same snapshot store
- **THEN** each conversation-scoped search SHALL return only matching conversation history
- **AND** a search with no stable conversation identity SHALL return no corpus rather than falling back to all runs

#### Scenario: Shared store is unavailable

- **WHEN** shared history is requested but the declared store cannot be opened or resolved
- **THEN** construction SHALL fail before model or tool execution
- **AND** the runtime SHALL not substitute a fresh disconnected in-memory store

#### Scenario: Search is not requested

- **WHEN** a caller composes step persistence without conversation search
- **THEN** step continuation SHALL retain its existing persistence semantics
- **AND** no search index or search tool SHALL be created implicitly

#### Scenario: Snapshot retention prunes history

- **WHEN** the caller configures a bounded retention policy that prunes an older snapshot
- **THEN** conversation search SHALL continue to use the same store and its remaining snapshots
- **AND** the runtime and documentation SHALL not claim that a pruned turn remains searchable
