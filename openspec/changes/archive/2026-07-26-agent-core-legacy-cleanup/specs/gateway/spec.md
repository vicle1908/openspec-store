## MODIFIED Requirements

### Requirement: GW-3: LLMGateway Interface Minimized

`LLMGateway.get_model()` SHALL return a `pydantic_ai.models.Model` instance configured for the gateway's provider.

`LLMGateway.is_available()` SHALL return a boolean indicating gateway health. This method is part of the public API surface used by external consumers (type-annotated by `agent-docs-sync`).

`LLMGateway.close()` SHALL perform cleanup of gateway resources.

`LLMGateway.complete()`, `LLMGateway.stream()`, and associated types `LLMResponse`, `LLMDelta` SHALL be removed from the interface. These raw HTTP methods have zero callers across all 40+ repos — pydantic-ai provides full replacements: `Agent.run()` for completions, `Agent.run_stream()` for streaming, `RunUsage` for usage tracking, `InstrumentedModel` for OTel.

`BudgetTracker` SHALL be rewired from the dead HTTP path into pydantic-ai's hooks system. It fills a unique gap — pydantic-ai's `UsageLimits` tracks token/request counts but has NO USD cost ceiling enforcement. BudgetTracker's `set_budget()`/`check_and_record()` with thread-safe atomicity provides cross-agent USD budget enforcement.

#### Scenario: Gateway interface compatibility

- **GIVEN** `LLMGateway` is used by `agent_base/agent.py` and type-annotated by `agent-docs-sync`
- **WHEN** `gateway.get_model()` is called
- **THEN** it SHALL return a `pydantic_ai.models.Model` configured for the gateway's provider

#### Scenario: Legacy methods removed

- **GIVEN** `LLMGateway` ABC is defined in `llm_gateway/types.py`
- **WHEN** a developer inspects the interface
- **THEN** `complete()` and `stream()` SHALL NOT be defined as abstract methods
- **AND** `LLMResponse` and `LLMDelta` types SHALL NOT exist in `llm_gateway/types.py`

#### Scenario: BudgetTracker rewired

- **GIVEN** `BudgetTracker` provides USD cost ceiling enforcement
- **WHEN** the rewire is applied
- **THEN** `BudgetTracker` SHALL be accessible via pydantic-ai's `before_model_request` / `after_model_request` hooks
- **AND** `set_budget(budget_id, budget_usd)` SHALL continue to register per-run ceilings
- **AND** `check_and_record(budget_id, cost_usd)` SHALL be called from the hooks path instead of the dead HTTP path
- **AND** `GatewayError(code="budget_exceeded")` SHALL be raised when budget is exceeded

#### Scenario: RunUsage propagated

- **WHEN** `AgentRuntime._to_result()` converts pydantic-ai's `AgentRunResult`
- **THEN** `RunUsage` (token counts, request counts, cache hits) SHALL be propagated to `AgentResult`
- **AND** `AgentResult` SHALL have a `usage` field containing the `RunUsage` data

#### Scenario: Implementations updated

- **GIVEN** `BifrostGateway` and `LiteLLMGateway` implement `LLMGateway`
- **WHEN** the cleanup is applied
- **THEN** neither implementation SHALL contain `complete()` or `stream()` methods
- **AND** the `httpx.AsyncClient` SHALL be removed from gateway implementations
- **AND** `_parse_response()` and `_parse_delta()` helper functions SHALL be removed
- **AND** `BudgetTracker` SHALL be preserved and rewired

#### Scenario: httpx dependency check

- **WHEN** gateway raw methods are removed
- **THEN** `httpx` SHALL be checked for usage in `tool_registry/builtins/http_request.py` and `memory/embedding.py`
- **AND** if `httpx` is still imported anywhere in `src/`, the package dependency SHALL be kept in `pyproject.toml`
- **AND** if `httpx` is unused, it SHALL be removed from `pyproject.toml` and `uv lock` SHALL be run

## REMOVED Requirements

### Requirement: GW-1: BifrostGateway Uses OpenAIModel
**Reason**: Requirement is preserved but the scenario references `gateway.complete()` which is being removed. The core behavior (BifrostGateway uses OpenAIModel via `get_model()`) is unchanged.
**Migration**: Use `gateway.get_model()` instead of `gateway.complete()`.

### Requirement: GW-2: LiteLLMGateway Uses LiteLLMModel
**Reason**: Same as GW-1 — the scenario references the legacy interface.
**Migration**: Use `gateway.get_model()` instead of `gateway.complete()`.
