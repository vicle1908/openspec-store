## Purpose

REPLACED by pydantic-ai native retry patterns. The custom tool-level resilience (`@resilient_tool` decorator, per-tool `CircuitBreakerRegistry`) has been removed.

## Migration Summary

| Removed | Replacement |
|---|---|
| `@resilient_tool` decorator | Native retry via `Agent.run(retries=N)` |
| Per-tool `CircuitBreakerRegistry` | `FallbackModel` for model-level failover |
| `resilient_tool` config in `ToolMetadata` | Removed |

## Requirements

### Requirement: Tool resilience removed

The `@resilient_tool` decorator and per-tool circuit breaker registry SHALL be deleted from agent-core.

#### Scenario: No tool resilience imports

- **WHEN** `grep -r "resilient_tool" src/` is run
- **THEN** zero hits SHALL be returned
