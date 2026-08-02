# Gateway Specification

## Purpose

Define the migration of `BifrostGateway` and `LiteLLMGateway` from raw httpx implementations to pydantic-ai model backends.

## ADDED Requirements

### Requirement: GW-1: BifrostGateway Uses OpenAIModel

`BifrostGateway` SHALL use `pydantic_ai.models.openai.OpenAIModel` internally, configured with the Bifrost `base_url` and `api_key`.

`BifrostGateway` SHALL delegate LLM calls to `_ai/models.py` factory functions.

#### Scenario: Bifrost model is OpenAIModel-backed

- **GIVEN** `BifrostGateway(base_url="https://bifrost.example.com", api_key="test")` is instantiated
- **WHEN** the gateway is used to complete a request
- **THEN** the underlying model is `OpenAIModel` pointing to Bifrost

### Requirement: GW-2: LiteLLMGateway Uses LiteLLMModel

`LiteLLMGateway` SHALL use `pydantic_ai.models.litellm.LiteLLMModel` internally.

`LiteLLMGateway` SHALL delegate LLM calls to `_ai/models.py` factory functions.

#### Scenario: LiteLLM model is LiteLLMModel-backed

- **GIVEN** `LiteLLMGateway(base_url="https://litellm.example.com")` is instantiated
- **WHEN** the gateway is used to complete a request
- **THEN** the underlying model is `LiteLLMModel`

### Requirement: GW-3: LLMGateway Interface Unchanged

`LLMGateway.complete()`, `LLMGateway.stream()`, `LLMGateway.is_available()`, `LLMGateway.close()` signatures SHALL be unchanged.

`BudgetTracker` SHALL be unchanged and continue to track cost against `budget_id` independently.

#### Scenario: Gateway interface compatibility

- **GIVEN** `LLMGateway` is used by existing consumer code
- **WHEN** `gateway.complete(messages, model="gpt-4o")` is called
- **THEN** the method signature matches the pre-migration interface
