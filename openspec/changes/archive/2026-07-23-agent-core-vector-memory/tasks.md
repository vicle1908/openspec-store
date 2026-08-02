## 1. Infrastructure

- [x] 1.1 Create migration: `CREATE EXTENSION IF NOT EXISTS vector;`
- [x] 1.2 Create migration: `agent_memory.vector_documents` table with columns (id, session_id, key, content, metadata JSONB, embedding vector(1536), created_at, updated_at)
- [x] 1.3 Create migration: HNSW index on `embedding` column with cosine distance
- [x] 1.4 Verify migration runs on existing Postgres instance

## 2. Embedding Provider

- [x] 2.1 Define `EmbeddingProvider` protocol in `agent_core/memory/embedding.py`
- [x] 2.2 Implement nhà cung cấp dịch vụ AI `text-embedding-3-small` provider in `agent_core/memory/embedding.py`
- [x] 2.3 Implement LiteLLM fallback provider for proxy-based embedding
- [x] 2.4 Add `EMBEDDING_PROVIDER` and `EMBEDDING_MODEL` settings to config

## 3. VectorMemory Backend

- [x] 3.1 Create `agent_core/memory/vector.py` with `VectorMemory` class implementing `MemoryBackend`
- [x] 3.2 Implement `store()` with optional embedding parameter and auto-embedding fallback
- [x] 3.3 Implement `search()` with query text or embedding, `top_k` parameter, and cosine similarity
- [x] 3.4 Implement `list_keys()` for session-scoped key listing
- [x] 3.5 Add pgvector extension detection with clear error message

## 4. Facade Integration

- [x] 4.1 Add `"vector"` to `MemoryLayer` literal type in `types.py`
- [x] 4.2 Extend `Memory` facade constructor to accept `vector: VectorMemory | None`
- [x] 4.3 Add routing for `layer="vector"` in `store()`, `retrieve()`, `list_keys()`
- [x] 4.4 Add `search()` method to `Memory` facade for vector queries

## 5. Tests

- [x] 5.1 Create `tests/memory/test_vector.py`
- [x] 5.2 Test `VectorMemory.store()` with auto-embedding
- [x] 5.3 Test `VectorMemory.search()` returns results ordered by similarity
- [x] 5.4 Test `VectorMemory.search()` returns empty for no matches
- [x] 5.5 Test `Memory` facade routing to vector layer
- [x] 5.6 Test pgvector extension detection error
- [x] 5.7 Test with mock embedding provider (no API calls in tests)
- [x] 5.8 Run `pytest tests/memory/ -x`

## 6. Validation

- [x] 6.1 Run `mypy agent_core/memory/ --strict`
- [x] 6.2 Run `ruff check agent_core/memory/ && ruff format agent_core/memory/`
- [x] 6.3 Run full test suite `pytest tests/ -x`
