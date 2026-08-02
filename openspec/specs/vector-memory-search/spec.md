# vector-memory-search Specification

## Purpose

Vector-backed semantic search for agent memory. Provides `VectorMemory` backend with pgvector cosine similarity, metadata filtering, and distance threshold support. Part of the `agent_core.memory` module (EXPERIMENTAL — not wired into agent lifecycle).

## Requirements

### Requirement: VectorMemory backend
The system SHALL implement `VectorMemory` as a `MemoryBackend` subclass backed by pgvector.

#### Scenario: VectorMemory implements MemoryBackend
- **WHEN** `VectorMemory` is instantiated
- **THEN** it SHALL implement `store()`, `retrieve()`, `list_keys()`, `delete()`, `count()`, and `search()` methods from `MemoryBackend`

### Requirement: Similarity search with filtering
`VectorMemory.search()` SHALL support metadata filtering and distance threshold.

#### Scenario: Filtered search
- **WHEN** `search(session, query_text="info", metadata_filter={"source": "jira"})` is called
- **THEN** only documents matching the metadata filter SHALL be returned

#### Scenario: Distance threshold
- **WHEN** `search(session, query_text="info", threshold=0.8)` is called
- **THEN** only documents with cosine similarity >= 0.8 SHALL be returned

#### Scenario: Empty results
- **WHEN** `search(session, query_text="nonexistent", top_k=5)` is called and no documents exist
- **THEN** an empty list SHALL be returned

### Requirement: EmbeddingProvider abstraction
The system SHALL define an `EmbeddingProvider` protocol with LRU caching.

#### Scenario: Cache hit
- **WHEN** `embed(text)` is called with text that was previously embedded
- **THEN** the cached result SHALL be returned without an API call

#### Scenario: Provider protocol
- **WHEN** a custom `EmbeddingProvider` is implemented
- **THEN** it SHALL implement `async def embed(self, text: str) -> list[float]` method
