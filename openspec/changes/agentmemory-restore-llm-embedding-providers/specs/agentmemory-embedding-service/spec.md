# Spec Delta

## Purpose

Availability and supervision of the local embedding backend that agentmemory
uses to index memories for vector-backed semantic recall.

## ADDED Requirements

### Requirement: Local embedding service SHALL be running for vector indexing

The runtime SHALL provide a reachable embedding endpoint at
`OPENAI_EMBEDDING_BASE_URL=http://localhost:11434/v1` serving the configured
`OPENAI_EMBEDDING_MODEL` (`nomic-embed-text`) at the configured
`OPENAI_EMBEDDING_DIMENSIONS` (768).

#### Scenario: Embedding endpoint answers

- WHEN the agentmemory server writes a memory or observation to the vector index
- THEN the embedding endpoint SHALL answer a POST to
  `http://localhost:11434/v1/embeddings`
- AND the returned vector length SHALL equal the configured dimensions (768)
- AND the vector write SHALL succeed without an
  `vector-index add: embed failed — skipping` entry

#### Scenario: Embedding service unavailable

- WHEN the embedding endpoint is unreachable at the time of a vector write
- THEN the memory SHALL still be persisted without its vector
- AND a single `embed failed` warning SHALL be emitted for that item
- AND the failure SHALL NOT block observation capture or memory persistence

### Requirement: Embedding service SHALL start at login and restart on failure

The embedding backend SHALL be supervised by a login-starting, keep-alive service
so that it is available without an operator starting it manually.

#### Scenario: Service starts at login

- WHEN the user logs in
- THEN the embedding service SHALL be started automatically by its supervisor
- AND the endpoint at `127.0.0.1:11434` SHALL become reachable without manual
  intervention

#### Scenario: Service restarts after crashes

- WHEN the embedding service process exits unexpectedly
- THEN the supervisor SHALL restart it automatically
- AND the service SHALL re-serve the configured embedding model after restart

#### Scenario: Models persist across restarts

- WHEN the embedding service restarts
- THEN the configured embedding model SHALL remain available without re-download
- AND its on-disk model store SHALL be preserved

### Requirement: Embedding capability SHALL be verifiable end to end

Operators SHALL be able to confirm working vector indexing through observable
signals, not configuration presence alone.

#### Scenario: Successful vector indexing is observable

- WHEN a memory is written while the embedding service is reachable
- THEN the server logs SHALL show the memory saved
- AND no embedding-skip warning SHALL appear for that write
- AND semantic recall over the stored content SHALL return the stored item for a
  matching query

#### Scenario: Configured-but-unreachable is distinguished from working

- WHEN the embedding provider is configured but the endpoint is unreachable
- THEN capability reporting SHALL NOT present the embedding backend as fully
  healthy on configuration alone
- AND the distinction SHALL be observable in server logs and service status
