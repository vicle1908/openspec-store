## Why

The memory facade has three layers (context, scratch, long_term) but none support semantic search. Long-term memory is key-value JSONB lookup — you must know the exact key to retrieve information. For RAG patterns, agents need to find relevant past information by semantic similarity, not exact key match. pgvector is the natural choice: we already run Postgres with the `agent_memory` schema, and adding the pgvector extension requires zero new infrastructure.

## What Changes

- New `VectorMemory` backend implementing `MemoryBackend` with pgvector storage
- New `agent_memory.vector_documents` table with `vector(1536)` column and HNSW index
- Pluggable `EmbeddingProvider` abstraction with nhà cung cấp dịch vụ AI `text-embedding-3-small` as default
- `Memory` facade extended with `vector` layer routing
- `store()` accepts optional `embedding` parameter; `search()` accepts query text or embedding with `top_k`

## Capabilities

### New Capabilities
- `vector-memory-search`: Semantic vector storage and similarity search backed by pgvector, with pluggable embedding providers, integrated into the existing Memory facade as a fourth layer

### Modified Capabilities
<!-- Memory facade is extended, not changed — existing layers unaffected -->

## Impact

- **Code:** New `agent_core/memory/vector.py`, modifications to `agent_core/memory/facade.py`, `agent_core/memory/types.py`
- **Tests:** New `tests/memory/test_vector.py`
- **Dependencies:** `pgvector` Postgres extension (one-time), optional `nhà cung cấp dịch vụ AI` SDK for embeddings
- **Database:** One migration for `vector_documents` table + HNSW index
- **Backward compatibility:** Fully backward compatible — existing memory layers unchanged, vector layer is opt-in
