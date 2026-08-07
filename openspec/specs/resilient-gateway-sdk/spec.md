## Purpose

REPLACED by pydantic-ai native `FallbackModel`. The `ResilientGateway` class, which wrapped `LLMGateway` with circuit-breaking and optional fallback, has been removed.

## Migration Summary

| Removed | Replacement |
|---|---|
| `ResilientGateway` | `pydantic_ai.models.fallback.FallbackModel` |
| `CircuitBreaker` per provider | `FallbackModel` transparent failover |
| `FallbackChain` | `FallbackModel(primary, *fallbacks)` |

## Requirements

### Requirement: ResilientGateway removed

`ResilientGateway` SHALL NOT be importable from agent-core SDK or `agent_core.llm_gateway`.

#### Scenario: Import fails

- **WHEN** `from agent_core.sdk import ResilientGateway` is attempted
- **THEN** an `ImportError` SHALL be raised

#### Scenario: FallbackModel used instead

- **WHEN** model failover is needed
- **THEN** `FallbackModel(primary_model, *fallback_models, fallback_on=FALLBACK_EXCEPTIONS)` SHALL be used
