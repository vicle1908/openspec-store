## Context

The memory facade has three layers: `ContextMemory` (in-process), `ScratchMemory` (filesystem), and `PostgresMemory` (JSONB key-value). None support semantic search — you must know the exact key to retrieve information. For RAG patterns, agents need to find relevant past information by semantic similarity. The Postgres instance already runs with the `agent_memory` schema, making pgvector the natural choice.

## Goals / Non-Goals

**Goals:**
- `VectorMemory` backend implementing `MemoryBackend` with pgvector storage
- Pluggable `EmbeddingProvider` abstraction (nhà cung cấp dịch vụ AI default, LiteLLM fallback)
- Integration into `Memory` facade as fourth layer (`layer="vector"`)
- Cosine similarity search with configurable `top_k`
- Session-scoped search with metadata filtering

**Non-Goals:**
- Document chunking/ingestion pipeline (consumers handle this)
- Hybrid search (vector + keyword) — future enhancement
- Real-time embedding updates (batch ingest is sufficient)
- Multiple embedding dimensions (1536 fixed for v1)

## Decisions

### Decision 1: pgvector over Chroma

**Choice:** pgvector (Postgres extension)

**Rationale:**
- Already run Postgres with `agent_memory` schema — zero new infrastructure
- pgvector extension is `CREATE EXTENSION IF NOT EXISTS vector;` — one command
- SQL WHERE clauses for session-scoped filtering
- HNSW index for fast approximate nearest neighbor search
- Cosine distance via `<=>` operator

**Verified pgvector syntax:**
```sql
-- Extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Table
CREATE TABLE agent_memory.vector_documents (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(session_id, key)
);

-- HNSW index (cosine distance)
CREATE INDEX idx_vector_documents_embedding
    ON agent_memory.vector_documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Search query
SELECT *, embedding <=> $1 AS distance
FROM agent_memory.vector_documents
WHERE session_id = $2
ORDER BY distance ASC
LIMIT $3;
```

**Alternatives considered:**
- Chroma: Separate server process, new dependency, no SQL filtering. Rejected.
- Pinecone/Weaviate: External SaaS, cost, vendor lock-in. Rejected.

### Decision 2: Pluggable EmbeddingProvider

**Choice:** Abstract `EmbeddingProvider` protocol with nhà cung cấp dịch vụ AI default

**Rationale:**
- nhà cung cấp dịch vụ AI `text-embedding-3-small` is cost-effective and widely available (1536 dimensions)
- LiteLLM proxy can route to any provider (nhà cung cấp dịch vụ AI, Google, local models)
- Protocol allows swapping without code changes
- Consumers can use local models for offline/airgapped environments

**Protocol:**
```python
from typing import Protocol

class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...
```

### Decision 3: Separate table, not JSONB column

**Choice:** Dedicated `vector_documents` table with typed columns

**Rationale:**
- pgvector requires a `vector` column type — can't be inside JSONB
- Typed columns enable efficient indexing and filtering
- HNSW index on the vector column for fast search
- Separate from `long_term` JSONB to avoid schema conflicts
- UNIQUE(session_id, key) constraint prevents duplicates

## Risks / Trade-offs

**[Risk] Embedding API latency** → Each `search()` call requires embedding the query text. Mitigation: Cache embeddings for repeated queries, use fast models (text-embedding-3-small is ~50ms).

**[Risk] pgvector not installed** → Some Postgres instances may not have pgvector. Mitigation: Feature detection — `VectorMemory` raises clear error if extension missing, other layers unaffected.

**[Risk] Index build time** → HNSW index can be slow for large datasets. Mitigation: Create index CONCURRENTLY, monitor build time. HNSW can be created without data (unlike IVFFlat).

**[Risk] Dimension mismatch** → Embedding provider must output 1536 dimensions to match `VECTOR(1536)`. Mitigation: Validate dimension on store, clear error message.

## Migration Plan

1. `CREATE EXTENSION IF NOT EXISTS vector;` (one-time, requires Postgres superuser)
2. Create migration for `agent_memory.vector_documents` table
3. Create HNSW index on `embedding` column with `vector_cosine_ops`
4. Implement `VectorMemory` backend in `agent_core/memory/vector.py`
5. Add `EmbeddingProvider` protocol and nhà cung cấp dịch vụ AI implementation
6. Extend `Memory` facade with `vector` layer routing
7. Add `vector` to `MemoryLayer` literal type
8. Add tests in `tests/memory/test_vector.py`

## Open Questions

- Should we support multiple embedding dimensions (384, 768, 1536) or fix at 1536? (Recommend: 1536 for v1, configurable later)
- Should embedding generation be async or sync? (Recommend: async to match memory facade)
