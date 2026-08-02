## Purpose

This specification defines requirements for Agent Core Memory Lifecycle.

## Requirements

### Requirement: Harness MemoryStore adapter

TDT memory backends SHALL implement or adapt to the public Harness `MemoryStore` interface, and the official Harness `Memory` capability SHALL own memory tools and prompt injection limits.

#### Scenario: Existing TDT backend

- **WHEN** a consumer selects the TDT in-memory, file, SQLite, or Postgres-backed memory implementation
- **THEN** a public adapter SHALL expose it as a Harness memory store
- **AND** existing namespace/tenant/session isolation SHALL be preserved

#### Scenario: Generic upstream store

- **WHEN** TDT-specific tenancy or search behavior is not required
- **THEN** the integration SHALL use the public Harness `InMemoryStore`, `FileStore`, `SqliteMemoryStore`, or `PostgresMemoryStore` whose semantics match the use case
- **AND** it SHALL not create a parallel generic store

#### Scenario: Memory injection

- **WHEN** memory is injected into an agent run
- **THEN** official maximum-token, maximum-line, result-count, and result-size limits SHALL apply

#### Scenario: Memory tools

- **WHEN** memory tools are enabled
- **THEN** they SHALL come from the official Memory capability
- **AND** `agent-core` SHALL not construct a parallel private capability class

### Requirement: State ownership matrix

The integration documentation SHALL define which persistence layer owns each kind of state.

#### Scenario: Agent memory

- **WHEN** durable semantic or working memory is required
- **THEN** the Harness Memory capability backed by TDT storage SHALL own it

#### Scenario: Agent step continuation

- **WHEN** an agent run needs step-level continuation or forking
- **THEN** Harness `StepPersistence` and `InMemoryStepStore`, `FileStepStore`, or `SqliteStepStore` SHALL own it
- **AND** continuation SHALL use the public module-level `pydantic_ai_harness.step_persistence.continue_run(store, run_id=...)` contract

#### Scenario: Workflow checkpoint

- **WHEN** a LangGraph workflow needs node-state recovery
- **THEN** the LangGraph checkpointer SHALL own it

#### Scenario: Scheduled durable execution

- **WHEN** a scheduled workflow requires DBOS recovery
- **THEN** DBOS SHALL own scheduler-level durability
