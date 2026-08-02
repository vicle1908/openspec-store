## ADDED Requirements

### Requirement: VectorMemory backend
The system SHALL implement `VectorMemory` as a `MemoryBackend` subclass backed by pgvector.

#### Scenario: VectorMemory implements MemoryBackend
- **WHEN** `VectorMemory` is instantiated
- **THEN** it SHALL implement `store()`, `retrieve()`, `list_keys()`, and `search()` methods from `MemoryBackend`

#### Scenario: Store with explicit embedding
- **WHEN** `VectorMemory.store(session, key, value, embedding=vector)` is called
- **THEN** the document SHALL be stored in `agent_memory.vector_documents` with the provided embedding vector

#### Scenario: Store with auto-embedding
- **WHEN** `VectorMemory.store(session, key, value)` is called without an embedding
- **THEN** the embedding SHALL be generated using the configured `EmbeddingProvider`

### Requirement: pgvector table schema
The system SHALL create `agent_memory.vector_documents` with correct pgvector column types.

#### Scenario: Table creation
- **WHEN** the migration runs
- **THEN** `agent_memory.vector_documents` SHALL exist with columns:
  - `id BIGSERIAL PRIMARY KEY`
  - `session_id TEXT NOT NULL`
  - `key TEXT NOT NULL`
  - `content TEXT NOT NULL`
  - `metadata JSONB DEFAULT '{}'`
  - `embedding VECTOR(1536) NOT NULL`
  - `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `UNIQUE(session_id, key)`

#### Scenario: Extension detection
- **WHEN** the migration runs
- **THEN** `CREATE EXTENSION IF NOT EXISTS vector;` SHALL be executed first
- **NOTE:** Requires Postgres superuser for first-time extension install

### Requirement: HNSW index for performance
The system SHALL create an HNSW index on the embedding column for fast approximate nearest neighbor search.

#### Scenario: HNSW index creation
- **WHEN** the migration runs
- **THEN** an HNSW index SHALL be created:
  ```sql
  CREATE INDEX IF NOT EXISTS idx_vector_documents_embedding
      ON agent_memory.vector_documents
      USING hnsw (embedding vector_cosine_ops)
      WITH (m = 16, ef_construction = 64);
  ```
- **NOTE:** `m=16` and `ef_construction=64` are pgvector defaults — good starting point

#### Scenario: Index parameters
- **WHEN** HNSW index is created
- **THEN** `m` (max connections per layer) SHALL default to 16
- **AND** `ef_construction` (candidate list size for build) SHALL default to 64
- **NOTE:** Higher `ef_construction` = better recall but slower build

### Requirement: Similarity search
The system SHALL provide cosine similarity search across stored documents.

#### Scenario: Search by query text
- **WHEN** `VectorMemory.search(session, query_text="how to deploy", top_k=5)` is called
- **THEN** the top 5 most similar documents SHALL be returned ordered by cosine distance ASC (most similar first)

#### Scenario: Search by embedding vector
- **WHEN** `VectorMemory.search(session, query_embedding=[0.1, 0.2, ...], top_k=5)` is called
- **THEN** the top 5 most similar documents SHALL be returned using cosine distance

#### Scenario: Cosine distance operator
- **WHEN** similarity search is performed
- **THEN** the SQL query SHALL use `<=>` operator (pgvector cosine distance):
  ```sql
  SELECT *, embedding <=> $1 AS distance
  FROM agent_memory.vector_documents
  WHERE session_id = $2
  ORDER BY distance ASC
  LIMIT $3
  ```

#### Scenario: Empty results
- **WHEN** `VectorMemory.search(session, query_text="nonexistent topic", top_k=5)` is called and no documents exist for the session
- **THEN** an empty list SHALL be returned

### Requirement: EmbeddingProvider abstraction
The system SHALL define an `EmbeddingProvider` protocol with nhà cung cấp dịch vụ AI as default.

#### Scenario: Default provider
- **WHEN** `VectorMemory` is created without specifying a provider
- **THEN** nhà cung cấp dịch vụ AI `text-embedding-3-small` SHALL be used (1536 dimensions)

#### Scenario: Custom provider
- **WHEN** `VectorMemory(provider=MyCustomProvider())` is created
- **THEN** the custom provider SHALL be used for all embedding operations

#### Scenario: Provider protocol
- **WHEN** a custom `EmbeddingProvider` is implemented
- **THEN** it SHALL implement `async def embed(self, text: str) -> list[float]` method

### Requirement: Memory facade integration
The `Memory` facade SHALL support `layer="vector"` routing to `VectorMemory`.

#### Scenario: Store to vector layer
- **WHEN** `Memory.store(session, key, value, layer="vector")` is called
- **THEN** the value SHALL be stored in the vector backend with auto-generated embedding

#### Scenario: Search via vector layer
- **WHEN** `Memory.search(session, query_text="relevant info", layer="vector")` is called
- **THEN** the vector backend SHALL perform cosine similarity search

#### Scenario: Vector layer not configured
- **WHEN** `Memory` facade is used with `layer="vector"` but `VectorMemory` was not provided to the constructor
- **THEN** a `RuntimeError` SHALL be raised with message "vector memory not configured"

### Requirement: pgvector extension detection
The system SHALL detect whether the pgvector extension is installed and fail fast if not.

#### Scenario: Extension missing
- **WHEN** `VectorMemory` is created but pgvector extension is not installed in Postgres
- **THEN** a `ConfigError` SHALL be raised with message about installing pgvector extension

#### Scenario: Extension present
- **WHEN** `VectorMemory` is created and pgvector extension is installed
- **THEN** initialization SHALL succeed and connection pool SHALL be established

### Requirement: Session-scoped search
Search results SHALL be scoped to the specified session by default.

#### Scenario: Session isolation
- **WHEN** `VectorMemory.search(session="session-A", query_text="info")` is called
- **THEN** only documents with `session_id = "session-A"` SHALL be returned
- **AND** documents from other sessions SHALL NOT appear in results
