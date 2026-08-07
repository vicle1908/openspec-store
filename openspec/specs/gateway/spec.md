# gateway Specification

## Purpose

REPLACED by native pydantic-ai model resolution. The custom `LLMGateway` abstraction (`llm_gateway/`), `BifrostGateway`, `LiteLLMGateway`, `ResilientGateway`, `CircuitBreaker`, `FallbackChain`, `BudgetTracker`, and `retry_with_jitter` have been entirely removed. All LLM model resolution now uses pydantic-ai's `infer_model()` and `FallbackModel` directly.

## Migration Summary

| Removed | Replacement |
|---|---|
| `LLMGateway` ABC | `pydantic_ai.models.Model` (via `infer_model()`) |
| `BifrostGateway` | `infer_model("openai-chat:model_name")` |
| `LiteLLMGateway` | `infer_model("openai-chat:model_name")` |
| `ResilientGateway` | `pydantic_ai.models.fallback.FallbackModel` |
| `CircuitBreaker` + `Registry` | `FallbackModel` failover |
| `FallbackChain` | `FallbackModel(primary, *fallbacks)` |
| `BudgetTracker` | `pydantic_ai.UsageLimits` (token-based) |
| `retry_with_jitter` | `Agent.run(retries=N)` |
| `resilient_tool` decorator | Native retry |
| `GatewaySettings` | `ModelSettings` (pydantic-settings) |
| `GatewayError` | `ModelAPIError`, `UsageLimitExceeded`, `ConnectionError` |

## Requirements

### Requirement: Gateway layer fully removed

The `llm_gateway/` package, `resilience/` package, and all gateway-related SDK exports SHALL be deleted from agent-core.

#### Scenario: No gateway imports remain

- **WHEN** `grep -r "from agent_core.llm_gateway" src/` is run
- **THEN** zero hits SHALL be returned

#### Scenario: No resilience imports remain

- **WHEN** `grep -r "from agent_core.resilience" src/` is run
- **THEN** zero hits SHALL be returned

#### Scenario: SDK exports updated

- **WHEN** a consumer inspects `agent_core.sdk.__all__`
- **THEN** `LLMGateway`, `BifrostGateway`, `LiteLLMGateway`, `ResilientGateway`, `CircuitBreaker`, `CircuitBreakerRegistry`, `CircuitBreakerOpenError`, `FallbackChain`, `FallbackEntry`, `FallbackChainError`, `retry_with_jitter`, `resilient_tool` SHALL NOT be present

### Requirement: Native model resolution

Model creation SHALL use `infer_model()` from pydantic-ai with provider:model format.

#### Scenario: Model creation

- **WHEN** `create_model("openai-chat:gpt-4o")` is called
- **THEN** it SHALL return a `pydantic_ai.models.Model` instance via `infer_model()`

#### Scenario: Fallback model

- **WHEN** `create_fallback_model(primary_id, *fallback_ids)` is called
- **THEN** it SHALL return a `FallbackModel` wrapping the primary and fallback models
- **AND** fallback SHALL only trigger on transient errors (ConnectionError, ModelAPIError), NOT on auth/config errors

### Requirement: ModelSettings replaces GatewaySettings

`ModelSettings` SHALL replace `GatewaySettings` with fields: `primary`, `base_url`, `api_key` (SecretStr), `fallback`, `timeout_seconds`.

#### Scenario: Config loading

- **WHEN** `load_settings()` is called
- **THEN** `settings.model.primary` SHALL contain the primary model ID
- **AND** `settings.model.api_key` SHALL be resolved from `MODEL_API_KEY` or `OMNIROUTE_API_KEY` env var, NOT from yaml

### Requirement: RunUsage propagated

- **WHEN** `AgentRuntime._to_result()` converts pydantic-ai's `AgentRunResult`
- **THEN** `RunUsage` (token counts, request counts, cache hits) SHALL be propagated to `AgentResult`
- **AND** `AgentResult` SHALL have a `usage` field containing the `RunUsage` data
