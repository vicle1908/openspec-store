## Purpose

Provides semantic similarity search for agent memory using pgvector, enabling recall of contextually relevant past observations.

## Requirements

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
- AND the memory facade SHALL expose vector_degraded=True

#### Scenario: Embedding provider error
- WHEN the embedding provider fails during vector search
- THEN the error SHALL be logged with the provider's error type
- AND recall SHALL return empty vector results
- AND the memory facade SHALL expose vector_degraded=True

#### Scenario: No vector backend configured
- WHEN vector is None in Memory constructor
- THEN recall SHALL skip the vector layer silently
- AND vector_degraded SHALL be False
