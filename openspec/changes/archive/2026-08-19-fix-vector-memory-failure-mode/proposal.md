# Proposal: Fix Vector Memory Silent Failure Mode

## Why

The `Memory.recall()` method in `agent_core/memory/facade.py:162` catches all exceptions from vector search and silently discards them:

```python
try:
    vector_results = await self.vector.search(session, query, top_k=top_k)
    for vr in vector_results:
        results.append(...)
except Exception:
    pass  # Vector search is best-effort
```

This means:
1. If the pgvector extension is missing, connection fails, or the embedding provider errors — recall silently returns fewer results with no indication of degradation
2. Consumers have no way to know vector memory is unavailable
3. The existing `vector-memory-search` spec requires proper error handling but the facade doesn't honor it
4. The `VectorMemory` backend (244 lines, fully implemented with pgvector cosine similarity, metadata filtering, distance threshold) is never exercised in production because failures are swallowed

## What Changes

1. **Replace silent catch** with structured degradation: log a warning with the error type and message, set a `vector_available` flag, return empty list from vector layer
2. **Expose degradation status** via `Memory.vector_degraded: bool` property so consumers can detect degraded recall
3. **Add vector availability check** in `Memory.__init__` to verify the backend is reachable at construction time
4. **Update `vector-memory-search` spec** to require explicit error classification (connection error vs query error vs missing extension) and degradation reporting

## Scope

- `agent_core/memory/facade.py` — fix the silent catch
- `agent_core/memory/vector.py` — no changes needed (already correct)
- `openspec/specs/vector-memory-search/spec.md` — add error classification requirement

## Out of Scope

- Semantic/embedding-based skill matching (separate P4 change)
- Memory consolidation across layers (separate P5 change)
- New embedding providers
