## Purpose

Defines the memory API facade, backend adapter contract, lifecycle management, and integration points that allow agent-core consumers to use memory tools, injection, and state ownership consistently.

## Requirements

### Requirement: Widened MemoryBackend ABC

The `MemoryBackend` ABC SHALL support CRUD operations and search beyond simple key-value.

#### Scenario: Delete operation

- **WHEN** `backend.delete(session, key)` is called
- **THEN** the entry SHALL be removed from the backend
- **AND** a subsequent `retrieve(session, key)` SHALL return `None`

#### Scenario: Count operation

- **WHEN** `backend.count(session)` is called
- **THEN** it SHALL return the number of entries for that session as an integer

#### Scenario: Search operation

- **WHEN** `backend.search(session, query)` is called
- **THEN** it SHALL return entries matching the query (implementation-specific: exact match for KV, semantic for vector)

### Requirement: Unified recall on Memory facade

The `Memory` facade SHALL expose a unified `recall()` method that searches across layers.

#### Scenario: Cross-layer recall

- **WHEN** `memory.recall(session, query, top_k=5)` is called
- **THEN** it SHALL search context, scratch, long_term, and vector layers
- **AND** results SHALL be ranked by relevance across layers
- **AND** the caller SHALL NOT need to specify which layer to search

### Requirement: ContextMemory role-based API

`ContextMemory` SHALL accept `role` and `content` directly instead of abusing the `key` parameter.

#### Scenario: Direct role/content storage

- **WHEN** `context.store(session, role="user", content="hello")` is called
- **THEN** the message SHALL be stored with the correct role
- **AND** `get_context_for_llm()` SHALL return it in OpenAI format

### Requirement: PostgresMemory bug fix

The `PostgresMemory.cleanup_expired()` method SHALL read `cur.rowcount` inside the connection context.

#### Scenario: Rowcount fix

- **WHEN** `cleanup_expired()` is called
- **THEN** `cur.rowcount` SHALL be read inside the `async with conn.cursor() as cur:` block
- **AND** the return value SHALL correctly reflect the number of deleted rows

### Requirement: EmbeddingProvider URL fix

The OpenAI embedding provider SHALL use the correct API URL.

#### Scenario: Correct URL

- **WHEN** `OpenAIEmbeddingProvider` is instantiated
- **THEN** the base URL SHALL be `https://api.openai.com/v1/embeddings` (lowercase "openai")

### Requirement: Embedding caching

Embedding providers SHALL cache results to avoid redundant API calls.

#### Scenario: Cache hit

- **WHEN** `embed(text)` is called with text that was previously embedded
- **THEN** the cached result SHALL be returned without an API call

#### Scenario: Cache miss

- **WHEN** `embed(text)` is called with new text
- **THEN** the embedding SHALL be computed via API and cached for future calls

### Requirement: VectorMemory metadata filtering

`VectorMemory.search()` SHALL support optional metadata filtering.

#### Scenario: Filtered search

- **WHEN** `search(session, query_text="info", filter={"source": "jira"})` is called
- **THEN** only documents matching the metadata filter SHALL be returned

#### Scenario: Distance threshold

- **WHEN** `search(session, query_text="info", threshold=0.8)` is called
- **THEN** only documents with cosine similarity >= 0.8 SHALL be returned

### Requirement: EXPERIMENTAL annotation

The memory module SHALL be annotated as experimental pending agent lifecycle wiring.

#### Scenario: Module docstring

- **WHEN** a developer reads `agent_core/memory/__init__.py`
- **THEN** the docstring SHALL state that the module is enhanced but not yet wired into the agent lifecycle
- **AND** it SHALL reference the `_ai/capability.py` integration point for future wiring

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
- **THEN** Harness StepPersistence and InMemoryStepStore, FileStepStore, or SqliteStepStore SHALL own it
- **AND** continuation SHALL use the public module-level `pydantic_ai_harness.step_persistence.continue_run(store, run_id=...)` contract

#### Scenario: Workflow checkpoint

- **WHEN** a LangGraph workflow needs node-state recovery
- **THEN** the LangGraph checkpointer SHALL own it

#### Scenario: Scheduled durable execution

- **WHEN** a scheduled workflow requires DBOS recovery
- **THEN** DBOS SHALL own scheduler-level durability
