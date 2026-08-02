# gateway Specification

## Purpose

LLM gateway routing for Bifrost and LiteLLM providers, plus USD cost ceiling enforcement via BudgetTracker. The gateway provides a pydantic-ai `Model` instance via `get_model()` — all LLM calls flow through pydantic-ai natively.

## Requirements

### Requirement: GW-3: LLMGateway Interface Minimized

`LLMGateway.get_model()` SHALL return a `pydantic_ai.models.Model` instance configured for the gateway's provider.

`LLMGateway.is_available()` SHALL return a boolean indicating gateway health. This method is part of the public API surface used by external consumers (type-annotated by `agent-docs-sync`).

`LLMGateway.close()` SHALL perform cleanup of gateway resources.

`LLMGateway.complete()`, `LLMGateway.stream()`, and associated types `LLMResponse`, `LLMDelta` SHALL NOT exist on the interface. These raw HTTP methods have zero callers — pydantic-ai provides full replacements: `Agent.run()` for completions, `Agent.run_stream()` for streaming, `RunUsage` for usage tracking, `InstrumentedModel` for OTel.

`BudgetTracker` SHALL provide USD cost ceiling enforcement that pydantic-ai's `UsageLimits` does not cover. pydantic-ai tracks tokens/requests; BudgetTracker tracks dollars.

#### Scenario: Gateway interface compatibility

- **GIVEN** `LLMGateway` is used by `agent_base/agent.py` and type-annotated by `agent-docs-sync`
- **WHEN** `gateway.get_model()` is called
- **THEN** it SHALL return a `pydantic_ai.models.Model` configured for the gateway's provider

#### Scenario: Legacy methods not present

- **GIVEN** `LLMGateway` ABC is defined in `llm_gateway/types.py`
- **WHEN** a developer inspects the interface
- **THEN** `complete()` and `stream()` SHALL NOT be defined as abstract methods
- **AND** `LLMResponse` and `LLMDelta` types SHALL NOT exist in `llm_gateway/types.py`

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
- **AND** `BudgetTracker` SHALL be preserved for future hooks integration
