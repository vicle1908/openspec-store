## ADDED Requirements

### Requirement: Memory facade SHALL accept optional VectorMemory backend
The `Memory.__init__()` SHALL accept an optional `vector: VectorMemory | None = None` parameter (default: `None`). The `MemoryLayer` literal SHALL be extended to include `"vector"`. When provided, `Memory.store()` SHALL support `layer="vector"`, `Memory.recall()` SHALL include vector search results, and `Memory.close()` SHALL close the vector backend.

**Verified API:**
```python
# Current signature (memory/facade.py:28-35):
class Memory:
    def __init__(self, *, context: ContextMemory, scratch: ScratchMemory,
                 long_term: PostgresMemory | None = None,
                 feedback: FeedbackStore | None = None) -> None:

# Target signature:
class Memory:
    def __init__(self, *, context: ContextMemory, scratch: ScratchMemory,
                 long_term: PostgresMemory | None = None,
                 vector: VectorMemory | None = None,
                 feedback: FeedbackStore | None = None) -> None:
```

**VectorMemory.search() signature (memory/vector.py:167-177):**
```python
async def search(self, session: str, query: str = "", *,
                 query_text: str | None = None,
                 query_embedding: list[float] | None = None,
                 top_k: int = 5,
                 metadata_filter: dict[str, Any] | None = None,
                 threshold: float | None = None) -> list[dict[str, Any]]
```

#### Scenario: VectorMemory included in store and recall
- **WHEN** Memory is constructed with `vector=some_vector_memory` and `store()` is called with `layer="vector"`
- **THEN** the value SHALL be stored via `vector.store(session, key, value)`
- **AND** `recall()` SHALL include vector search results with `layer: "vector"`

#### Scenario: VectorMemory not provided
- **WHEN** Memory is constructed without a vector parameter
- **THEN** `store(layer="vector")` SHALL raise `ValueError("Unknown memory layer: vector")`
- **AND** `recall()` SHALL function normally using only context, scratch, and long_term

#### Scenario: MemoryLayer type extended
- **WHEN** `MemoryLayer` is imported from `agent_core.memory.types`
- **THEN** it SHALL be `Literal["context", "scratch", "long_term", "vector"]`

### Requirement: create_consumer_memory SHALL support vector option
`create_consumer_memory()` SHALL accept `enable_vector: bool = False` and `vector_dsn: str | None = None` parameters. When enabled, it SHALL create a `VectorMemory` instance with an embedding provider and add it to the Memory facade.

**Verified current signature (sdk/memory.py:13-20):**
```python
async def create_consumer_memory(
    consumer_name: str, *,
    enable_postgres: bool = False,
    postgres_dsn: str | None = None,
    context_max_messages: int = 50,
    scratch_dir: str | None = None,
) -> Memory:
```

**VectorMemory.create() signature (memory/vector.py:30-38):**
```python
@classmethod
async def create(cls, dsn: str, embedding_provider: Any, *,
                 min_size: int = 1, max_size: int = 5) -> VectorMemory
```

#### Scenario: Vector enabled with valid DSN
- **WHEN** `create_consumer_memory(name, enable_vector=True, vector_dsn="postgresql://...")` is called
- **THEN** a VectorMemory SHALL be created via `VectorMemory.create(dsn, embedding_provider)` and added to the Memory instance
- **AND** the embedding_provider SHALL be resolved from settings or a default provider

#### Scenario: Vector enabled without DSN
- **WHEN** `enable_vector=True` but `vector_dsn` is empty and no default DSN is available
- **THEN** vector creation SHALL be skipped with a warning log (consistent with PostgresMemory pattern)

#### Scenario: Vector creation fails
- **WHEN** `VectorMemory.create()` raises an exception (e.g., pgvector not installed)
- **THEN** the exception SHALL be caught, a warning logged, and Memory returned without vector (graceful degradation)

### Requirement: Syntax error SHALL be fixed
`sdk/memory.py:63` SHALL use `except (TimeoutError, Exception):` instead of `except TimeoutError, Exception:`.

**Verified bug location:** `sdk/memory.py:63` — `except TimeoutError, Exception:` is invalid Python 3 syntax.

#### Scenario: Non-timeout exception during long-term memory creation
- **WHEN** `PostgresMemory.create(dsn)` raises a non-timeout exception (e.g., connection refused)
- **THEN** the exception SHALL be caught by `except (TimeoutError, Exception):` and a warning logged
- **AND** `long_term` SHALL remain `None` (graceful degradation)
