## REMOVED Requirements

### Requirement: VectorMemory backend
**Reason**: `VectorMemory` is not imported by the `Memory` facade or any production code. The module was implemented but never integrated into the agent runtime. Removing it eliminates ~200 lines of dead code.
**Migration**: If vector search is needed in the future, re-implement against the current `MemoryBackend` protocol in `memory/types.py`.

### Requirement: pgvector table schema
**Reason**: Dependent on `VectorMemory` which is being removed.
**Migration**: N/A — schema was never applied to production database.

### Requirement: HNSW index for performance
**Reason**: Dependent on `VectorMemory` which is being removed.
**Migration**: N/A — index was never created in production.

### Requirement: Similarity search
**Reason**: Dependent on `VectorMemory` which is being removed.
**Migration**: N/A — search was never used in production.

### Requirement: EmbeddingProvider abstraction
**Reason**: Dependent on `VectorMemory` which is being removed.
**Migration**: N/A — provider was never instantiated in production.

### Requirement: Memory facade integration
**Reason**: The `Memory` facade never routed to `VectorMemory` — the `layer="vector"` path was never wired.
**Migration**: N/A — facade integration was never completed.

### Requirement: pgvector extension detection
**Reason**: Dependent on `VectorMemory` which is being removed.
**Migration**: N/A — detection was never triggered in production.

### Requirement: Session-scoped search
**Reason**: Dependent on `VectorMemory` which is being removed.
**Migration**: N/A — session-scoped search was never used in production.
