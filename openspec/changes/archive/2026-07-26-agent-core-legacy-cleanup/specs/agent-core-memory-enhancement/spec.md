## ADDED Requirements

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
