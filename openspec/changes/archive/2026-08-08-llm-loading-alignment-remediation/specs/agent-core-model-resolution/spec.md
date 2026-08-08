# Delta: Agent-Core Model Resolution

## MODIFIED Requirements

### Requirement: Model Resolution from Config

**WHEN** `create_model(model_id)` is called
**AND** no explicit `base_url`/`api_key` kwargs provided
**THEN** the system SHALL resolve proxy configuration in this order:
1. `MODEL_BASE_URL` + `MODEL_API_KEY` env vars
2. Exact provider `model_names` entries in `~/.tdt/config.yaml` providers map
3. `~/.tdt/config.yaml` providers map using the model-kind prefix and `api_mode`
4. `~/.tdt/config.yaml` model.base_url + env var from model.api_key_env
5. native provider environment variables handled by pydantic-ai

#### Scenario: Config-based resolution
- **GIVEN** `~/.tdt/config.yaml` has `model.primary: anthropic:Advance`
- **AND** `model.base_url: https://api.giaoduc.online`
- **AND** `model.api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **AND** `HERMES_CUSTOM_GIAODUC_API_KEY=pmv_...` is set in environment
- **WHEN** `create_model("openai-chat:Advance")` is called
- **THEN** the model SHALL be created using the proxy endpoint via OpenAI Chat Completions API

#### Scenario: Anthropic Messages API
- **GIVEN** `~/.tdt/config.yaml` has `model.primary: anthropic:Advance`
- **AND** `model.base_url: https://api.giaoduc.online`
- **AND** `model.api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **WHEN** `create_model("anthropic:Advance")` is called
- **THEN** the model SHALL be created using the proxy endpoint via Anthropic Messages API

#### Scenario: Provider-specific factory
- **GIVEN** the configured model identifier starts with `anthropic:`
- **WHEN** the model is resolved through the configured proxy
- **THEN** the system SHALL use `AnthropicProvider`
- **AND** SHALL remove one trailing `/v1` from the configured base URL before constructing it

#### Scenario: Explicit kwargs override config
- **GIVEN** `create_model("openai-chat:Advance", base_url="https://other.com/v1", api_key="key")`
- **WHEN** the model is created
- **THEN** the explicit kwargs SHALL be used instead of config

#### Scenario: Protocol routing via model kind prefix
- **GIVEN** the model identifier is `anthropic:Advance`
- **WHEN** the model is resolved through the configured proxy
- **THEN** the system SHALL use `AnthropicProvider` and route to `/v1/messages`

#### Scenario: OpenAI Chat via model kind prefix
- **GIVEN** the model identifier is `openai-chat:fable-5`
- **WHEN** the model is resolved through the configured proxy
- **THEN** the system SHALL use `OpenAIProvider` and route to `/v1/chat/completions`

#### Scenario: No explicit protocol field needed
- **GIVEN** the model kind prefix determines the protocol
- **WHEN** the config is loaded
- **THEN** the system SHALL NOT require an explicit `protocol` field
- **AND** the model kind prefix SHALL be the single source of truth for protocol selection

#### Scenario: api_mode selects provider class only
- **GIVEN** the provider config has `api_mode: anthropic_messages`
- **WHEN** the model is resolved through the configured proxy
- **THEN** the system SHALL use `AnthropicProvider` for `anthropic:*` prefixes
- **AND** SHALL use `OpenAIProvider` for `openai-chat:*` and `openai-responses:*` prefixes
- **AND** the model kind prefix SHALL remain authoritative for endpoint selection

#### Scenario: api_mode/prefix mismatch produces incompatible pairing
- **GIVEN** `api_mode: anthropic_messages` and model identifier `openai-chat:demo`
- **WHEN** the model is constructed
- **THEN** the system SHALL raise an actionable configuration error
- **AND** SHALL NOT construct an OpenAI model backed by an Anthropic provider

#### Scenario: Cockpit model-name routing
- **GIVEN** a provider config contains `model_names: [gpt-5.6-sol]`
- **AND** the model identifier is `openai-responses:gpt-5.6-sol`
- **WHEN** the model is resolved
- **THEN** the cockpit provider configuration SHALL be selected
- **AND** the `openai-responses:` prefix SHALL remain authoritative for the Responses endpoint

#### Scenario: Ambiguous model name is not a provider prefix
- **GIVEN** the model identifier is `openai-chat:fable-5`
- **WHEN** the provider is resolved
- **THEN** the `openai-chat` prefix SHALL select the configured OpenAI provider
- **AND** `fable-5` SHALL be treated only as the model name, not as a provider prefix

## ADDED Requirements

### Requirement: Configured Fallback Loading

**WHEN** the loaded model settings contain a non-empty `fallback` list
**AND** the agent-core CLI creates a runtime model
**THEN** the runtime SHALL use the native `FallbackModel` factory with the primary model followed by configured fallback models.

#### Scenario: CLI consumes configured fallback
- **GIVEN** `model.primary` is `anthropic:Advance`
- **AND** `model.fallback` contains `openai-chat:fable-5`
- **WHEN** the CLI prompt runtime initializes
- **THEN** its model SHALL be a fallback chain in the configured order.

### Requirement: API Mode Compatibility

**WHEN** a configured provider has an `api_mode`
**THEN** the system SHALL select the corresponding compatible pydantic-ai provider class
**AND** SHALL reject an incompatible model-kind prefix before constructing the model.

#### Scenario: Compatible Anthropic mode
- **GIVEN** `api_mode: anthropic_messages`
- **AND** the model identifier starts with `anthropic:`
- **WHEN** the model is constructed
- **THEN** `AnthropicProvider` SHALL be used.

#### Scenario: Incompatible mode is rejected
- **GIVEN** `api_mode: anthropic_messages`
- **AND** the model identifier starts with `openai-chat:`
- **WHEN** the model is constructed
- **THEN** the system SHALL raise an actionable configuration error
- **AND** SHALL NOT construct an OpenAI model backed by an Anthropic provider.
