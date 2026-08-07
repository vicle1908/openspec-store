# agent-step-persistence

## Purpose

Provides step-level persistence for agent runs using ContinuableSnapshot objects, enabling run resumption from tool call boundaries and complementing LangGraph's graph-level checkpointing.
## Requirements
### Requirement: Step persistence via StepPersistence
`AgentRuntime` SHALL accept an explicitly composed upstream `StepPersistence` capability. When no `StepPersistence` is supplied, the runtime MAY compose an in-memory store for ephemeral execution, but it SHALL expose that the store is process-local and SHALL NOT claim restart durability.

#### Scenario: SQLite-backed persistence
- **WHEN** a consumer requires restart-safe agent continuation
- **THEN** it SHALL construct `StepPersistence(store=SqliteStepStore(database=path))` or another supported persistent upstream store and pass it through public capability composition
- **AND** the database path SHALL be resolved beneath the consumer's approved `$TDT_HOME` state root unless explicitly configured otherwise

#### Scenario: In-memory persistence
- **WHEN** no persistent step capability is supplied
- **THEN** the runtime MAY use `StepPersistence(store=InMemoryStepStore())`
- **AND** lifecycle diagnostics SHALL classify continuation as same-process only

#### Scenario: In-memory persistence (testing)
- **WHEN** `step_persistence={"store": "memory"}` is explicitly selected for testing
- **THEN** `StepPersistence(store=InMemoryStepStore())` SHALL be created

#### Scenario: File-backed persistence
- **WHEN** a consumer explicitly selects a supported `FileStepStore` within its approved state root
- **THEN** the runtime SHALL use that supplied store without replacing it
- **AND** path policy SHALL reject storage outside the authorized root

#### Scenario: Persistent agent is reconstructed
- **WHEN** the creating process terminates after a continuable snapshot
- **THEN** a new process SHALL reconstruct the same consumer agent with the same persistent store and agent identity before calling the upstream continuation API
- **AND** no live client, model, or store handle SHALL be serialized as continuation state

#### Scenario: Persistent store is unavailable
- **WHEN** a consumer declares restart-safe continuation but the configured store cannot be opened
- **THEN** construction or lifecycle preflight SHALL fail before model or tool execution
- **AND** the runtime SHALL NOT silently substitute an in-memory store

### Requirement: ContinuableSnapshot

Step persistence SHALL emit `ContinuableSnapshot` objects at safe boundaries (after each complete tool call cycle).

#### Scenario: Snapshot emission
- **WHEN** an agent run completes a tool call cycle
- **THEN** a `ContinuableSnapshot` SHALL be emitted with `run_id`, `step_index`, and `messages`
- **AND** the snapshot SHALL be safe to pass to `Agent.run(message_history=...)` for resume

### Requirement: Run resumption

The system SHALL support resuming an agent run from a `ContinuableSnapshot`.

#### Scenario: Resume from snapshot
- **WHEN** `AgentRuntime.run_resume(snapshot)` is called with a `ContinuableSnapshot`
- **THEN** the agent SHALL continue from the snapshot's `step_index`
- **AND** the message history SHALL be restored from the snapshot

### Requirement: Complementary to LangGraph checkpointing

Step persistence SHALL operate at the agent run level, complementing LangGraph's graph-level checkpointing.

#### Scenario: Both active
- **WHEN** both `StepPersistence` and LangGraph `PostgresSaver` are configured
- **THEN** LangGraph SHALL checkpoint at graph node transitions
- **AND** StepPersistence SHALL checkpoint at agent tool call boundaries
- **AND** both SHALL be independently usable for resume
