## ADDED Requirements

### Requirement: Step persistence via StepPersistence

When `AgentConfig.step_persistence` is set, `AgentRuntime` SHALL create a `StepPersistence` capability.

#### Scenario: SQLite-backed persistence
- **WHEN** `step_persistence={"database": "~/.tdt/agent_steps.db"}`
- **THEN** `StepPersistence(store=SqliteStepStore(database=path))` SHALL be created

#### Scenario: In-memory persistence (testing)
- **WHEN** `step_persistence={"store": "memory"}`
- **THEN** `StepPersistence(store=InMemoryStepStore())` SHALL be created

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
