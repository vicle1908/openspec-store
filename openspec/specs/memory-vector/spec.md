## Purpose

Defines vector memory integration with pgvector, semantic similarity search, embedding providers, error classification, and automatic cross-layer consolidation (promotion, demotion, deduplication) for the agent memory system.

## Requirements

### Requirement: Memory facade SHALL accept optional VectorMemory backend

The `Memory.__init__()` SHALL accept an optional `vector: VectorMemory | None = None` parameter (default: `None`). The `MemoryLayer` literal SHALL be extended to include `"vector"`. When provided, `Memory.store()` SHALL support `layer="vector"`, `Memory.recall()` SHALL include vector search results, and `Memory.close()` SHALL close the vector backend.

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

#### Scenario: Non-timeout exception during long-term memory creation

- **WHEN** `PostgresMemory.create(dsn)` raises a non-timeout exception (e.g., connection refused)
- **THEN** the exception SHALL be caught by `except (TimeoutError, Exception):` and a warning logged
- **AND** `long_term` SHALL remain `None` (graceful degradation)

### Requirement: Vector search error classification

Vector search failures SHALL be classified and logged, never silently discarded.

#### Scenario: Connection error

- **WHEN** the vector backend is unreachable
- **THEN** the error SHALL be logged with error_type="ConnectionError"
- **AND** recall SHALL return empty vector results
- **AND** the memory facade SHALL expose vector_degraded=True

#### Scenario: Missing extension

- **WHEN** pgvector extension is not installed
- **THEN** the error SHALL be logged with error_type="ConfigError"
- **AND** recall SHALL return empty vector results
- **AND** the memory facade SHALL expose vector_degraded=True

#### Scenario: Embedding provider error

- **WHEN** the embedding provider fails during vector search
- **THEN** the error SHALL be logged with the provider's error type
- **AND** recall SHALL return empty vector results
- **AND** the memory facade SHALL expose vector_degraded=True

#### Scenario: No vector backend configured

- **WHEN** vector is None in Memory constructor
- **THEN** recall SHALL skip the vector layer silently
- **AND** vector_degraded SHALL be False

### Requirement: Consolidation trigger

The memory system SHALL support automatic consolidation triggered by recall count threshold or explicit invocation.

#### Scenario: Recall-count trigger

- **WHEN** the number of recall operations since last consolidation exceeds the configured threshold
- **THEN** the consolidation engine SHALL execute promotion, demotion, and merge passes
- **AND** metrics SHALL be returned to the caller

#### Scenario: Explicit trigger

- **WHEN** a consumer calls `memory.consolidate()`
- **THEN** the consolidation engine SHALL execute all passes immediately
- **AND** metrics SHALL be returned

#### Scenario: No trigger when disabled

- **WHEN** consolidation is not configured (default)
- **THEN** no consolidation SHALL execute automatically
- **AND** `memory.consolidate()` SHALL be a no-op returning zero metrics

### Requirement: Scratch-to-long-term promotion

Frequently-accessed scratch entries SHALL be promoted to long_term storage.

#### Scenario: Promotion threshold met

- **WHEN** a scratch entry has `access_count` greater than the promotion threshold
- **AND** the entry does not already exist in long_term
- **THEN** the entry SHALL be copied to long_term with the default long_term TTL
- **AND** the scratch entry SHALL remain unchanged

#### Scenario: Promotion skipped when already in long_term

- **WHEN** a scratch entry exists in long_term with the same key
- **THEN** the scratch entry SHALL NOT be promoted
- **AND** the long_term entry SHALL be left unchanged

### Requirement: Long-term demotion and expiry

Stale long_term entries SHALL be cleaned up based on TTL and access patterns.

#### Scenario: Expired entry with zero accesses

- **WHEN** a long_term entry has `expires_at` in the past
- **AND** its `access_count` is zero
- **THEN** the entry SHALL be deleted

#### Scenario: Expired entry with prior accesses

- **WHEN** a long_term entry has `expires_at` in the past
- **AND** its `access_count` is greater than zero
- **THEN** the entry SHALL be deleted
- **AND** a metrics entry SHALL record it as expired (not demoted)

### Requirement: Duplicate key conflict resolution

When the same key exists across multiple sessions, the most recently written value SHALL win.

#### Scenario: Cross-session duplicate

- **WHEN** `store("session-a", "key", value_a)` and `store("session-b", "key", value_b)` exist
- **AND** `updated_at` for session-b is more recent
- **THEN** consolidation SHALL retain session-b's entry
- **AND** session-a's entry SHALL be deleted
- **AND** metrics SHALL record one merge

### Requirement: Consolidation metrics

Consolidation SHALL return structured metrics about its operations.

#### Scenario: Metrics returned

- **WHEN** consolidation completes
- **THEN** it SHALL return a dict with keys: `promoted`, `demoted`, `merged`, `expired`
- **AND** each value SHALL be a non-negative integer
