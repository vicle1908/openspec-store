## Purpose

REPLACED by pydantic-ai native `FallbackModel` and `Agent.run(retries=N)`. The custom resilience primitives (`CircuitBreaker`, `FallbackChain`, `retry_with_jitter`, `DegradationManager`) have been removed.

## Migration Summary

| Removed | Replacement |
|---|---|
| `CircuitBreaker` + `CircuitBreakerRegistry` | `FallbackModel` failover |
| `FallbackChain` + `FallbackEntry` | `FallbackModel(primary, *fallbacks)` |
| `retry_with_jitter` | `Agent.run(retries=N)` |
| `CircuitBreakerOpenError` | `FallbackModel` transparent failover |
| `FallbackChainError` | `FallbackModel` transparent failover |
| `DegradationManager` | Removed (no replacement needed) |

## Requirements

### Requirement: Resilience layer fully removed

The `resilience/` package SHALL be deleted from agent-core. All resilience behavior is now handled by pydantic-ai native patterns.

#### Scenario: No resilience imports remain

- **WHEN** `grep -r "from agent_core.resilience" src/` is run
- **THEN** zero hits SHALL be returned

#### Scenario: FallbackModel used instead

- **WHEN** model fallback is needed
- **THEN** `FallbackModel(primary, *fallbacks, fallback_on=...)` SHALL be used
- **AND** fallback SHALL only trigger on specified exception types
