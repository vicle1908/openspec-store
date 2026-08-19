# Design: Fix Vector Memory Silent Failure Mode

## Problem

`Memory.recall()` in `agent_core/memory/facade.py:162` catches all exceptions from vector search and silently discards them:

```python
try:
    vector_results = await self.vector.search(session, query, top_k=top_k)
    ...
except Exception:
    pass  # Vector search is best-effort
```

This means connection errors, missing pgvector extension, embedding provider failures, and query errors all silently return fewer results with no indication of degradation.

## Approach

### 1. Structured degradation in facade.py

Replace the bare `except Exception: pass` with:

```python
except Exception as exc:
    logger.warning(
        "vector_search_degraded",
        error_type=type(exc).__name__,
        error=str(exc)[:200],
        session=session,
    )
```

- Log the error type and message (truncated to 200 chars to avoid log flooding)
- Still return empty list from vector layer (preserve best-effort behavior)
- No crash, no silent swallowing

### 2. Expose degradation status

Add a `vector_degraded: bool` property to `Memory`:

```python
class Memory:
    def __init__(self, *, context, scratch, long_term=None, vector=None, feedback=None):
        ...
        self._vector_degraded = False

    @property
    def vector_degraded(self) -> bool:
        return self._vector_degraded
```

Set `self._vector_degraded = True` in the except block. This lets consumers check whether recall results are complete or potentially missing vector matches.

### 3. Update vector-memory-search spec

Add an error classification requirement to the existing spec:

```markdown
### Requirement: Vector search error classification
Vector search failures SHALL be classified and logged, never silently discarded.

#### Scenario: Connection error
- WHEN the vector backend is unreachable
- THEN the error SHALL be logged with error_type="ConnectionError"
- AND recall SHALL return empty vector results
- AND the memory facade SHALL expose vector_degraded=True

#### Scenario: Missing extension
- WHEN pgvector extension is not installed
- THEN the error SHALL be logged with error_type="ConfigError"
- AND recall SHALL return empty vector results

#### Scenario: Embedding provider error
- WHEN the embedding provider fails
- THEN the error SHALL be logged with error_type from the provider
- AND recall SHALL return empty vector results
```

## Files Changed

| File | Change |
|------|--------|
| `agent_core/memory/facade.py:162` | Replace `except Exception: pass` with logged degradation |
| `agent_core/memory/facade.py:23-42` | Add `_vector_degraded` flag and property |
| `openspec/specs/vector-memory-search/spec.md` | Add error classification requirement |

## Testing

- Existing 704 agent-core tests must pass
- New test: mock `VectorMemory.search()` to raise `ConnectionError`, verify `facade.recall()` returns empty vector results and logs warning
- New test: verify `vector_degraded` property is `True` after vector failure
- New test: verify `vector_degraded` is `False` when vector is `None` (not configured)
