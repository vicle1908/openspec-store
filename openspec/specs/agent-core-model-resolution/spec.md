# agent-core-model-resolution Specification

## Purpose

Define configuration-driven model and proxy resolution for agent-core, including the active giaoduc Anthropic Messages setup and the OpenAI-compatible alternative.
## Requirements
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

### Requirement: Dual API Support

**WHEN** a provider supports both OpenAI and Anthropic API formats
**THEN** the system SHALL route to the correct endpoint based on the model kind prefix:
- `anthropic:*` → `/v1/messages` (Anthropic format)
- `openai-chat:*` → `/v1/chat/completions` (OpenAI format)
- `openai-responses:*` → `/v1/responses` (OpenAI format)

The `api_mode` field selects the provider class (`AnthropicProvider` vs `OpenAIProvider`), not the endpoint.

#### Scenario: OpenAI Chat Completions
- **GIVEN** provider supports `/v1/chat/completions`
- **WHEN** `create_model("openai-chat:Advance")` is called
- **THEN** requests SHALL use OpenAI Chat Completions format

#### Scenario: Anthropic Messages
- **GIVEN** provider supports `/v1/messages`
- **WHEN** `create_model("anthropic:Advance")` is called
- **THEN** requests SHALL use Anthropic Messages format

#### Scenario: OpenAI Responses
- **GIVEN** provider supports `/v1/responses`
- **WHEN** `create_model("openai-responses:gpt-5")` is called
- **THEN** requests SHALL use OpenAI Responses format

### Requirement: Config Schema

**WHEN** `~/.tdt/config.yaml` is loaded
**THEN** the model section SHALL support:
- `primary`: Default model identifier (the active value is "anthropic:Advance")
- `base_url`: Proxy endpoint URL
- `api_key_env`: Environment variable name containing the API key
- `fallback`: List of fallback model identifiers
- `timeout_seconds`: Request timeout

**AND** the providers section SHALL support:
- `base_url`: Proxy endpoint URL (per provider)
- `api_key_env`: Environment variable name (per provider)
- `api_mode`: Provider class mode (`anthropic_messages`, `codex_responses`, or empty)
- `model_names`: Optional exact model-name list checked before prefix routing

#### Scenario: TDT model configuration
- **GIVEN** the active TDT config contains `model.primary`, `model.base_url`, and `model.api_key_env`
- **WHEN** the settings and model factory are initialized
- **THEN** the model endpoint and API key SHALL be resolved from those configured values

#### Scenario: Multi-provider with api_mode
- **GIVEN** the active TDT config has `providers.giaoduc.api_mode: anthropic_messages`
- **AND** `providers.shopapikey.api_mode: codex_responses`
- **WHEN** `create_model("anthropic:Advance")` is called
- **THEN** the giaoduc provider SHALL be used with AnthropicProvider
- **WHEN** `create_model("openai-responses:fable-5")` is called
- **THEN** the shopapikey provider SHALL be used with OpenAIProvider

#### Scenario: Exact provider model names
- **GIVEN** `providers.cockpit.model_names` contains `gpt-5.6-sol`
- **WHEN** `create_model("openai-responses:gpt-5.6-sol")` is called
- **THEN** the cockpit provider SHALL be selected before the prefix default

### Requirement: Configured Fallback Loading

**WHEN** the loaded model settings contain a non-empty `fallback` list
**AND** the agent-core CLI creates a runtime model
**THEN** the runtime SHALL use the native `FallbackModel` factory with the primary model followed by configured fallback models.

#### Scenario: CLI consumes configured fallback
- **GIVEN** `model.primary` is `anthropic:Advance`
- **AND** `model.fallback` contains `openai-chat:fable-5`
- **WHEN** the CLI prompt runtime initializes
- **THEN** its model SHALL be a fallback chain in the configured order.

### Requirement: Verified Provider (giaoduc)

**WHEN** using the giaoduc provider (`https://api.giaoduc.online`)
**THEN** the following features SHALL be supported:

| API Format | Endpoint | Model Kind | api_mode | Features |
|------------|----------|------------|----------|----------|
| OpenAI Chat Completions | `/v1/chat/completions` | `openai-chat:Advance` | (default) | Streaming, tool calling, reasoning |
| Anthropic Messages | `/v1/messages` | `anthropic:Advance` | `anthropic_messages` | Thinking blocks, tool use, system prompts |
| OpenAI Responses | `/v1/responses` | `openai-responses:Advance` | `codex_responses` | Not supported by active provider |

#### Scenario: giaoduc Anthropic verification
- **GIVEN** the active provider is giaoduc and the model is `anthropic:Advance`
- **WHEN** the agent runs a real prompt
- **THEN** the provider SHALL return an Anthropic Messages response successfully

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

### Requirement: Configurable Thinking Effort

**WHEN** `model.thinking` is set in `~/.tdt/config.yaml` or `MODEL_THINKING` env var
**THEN** the system SHALL inject a `pydantic_ai.capabilities.Thinking` capability into the agent
**AND** the effort level SHALL be one of: `true`, `false`, `'minimal'`, `'low'`, `'medium'`, `'high'`, `'xhigh'`
**AND** the Thinking capability SHALL translate the effort level to the active provider's native format automatically.

#### Scenario: Config-driven thinking for Anthropic
- **GIVEN** `model.thinking: "high"` in config.yaml
- **AND** the active model is `anthropic:Advance`
- **WHEN** `build_agent()` is called
- **THEN** the agent SHALL have a Thinking capability with effort `'high'`
- **AND** the capability SHALL translate to Anthropic's adaptive thinking format

#### Scenario: Config-driven thinking for OpenAI
- **GIVEN** `model.thinking: "medium"` in config.yaml
- **AND** the active model is `openai-chat:fable-5`
- **WHEN** `build_agent()` is called
- **THEN** the agent SHALL have a Thinking capability with effort `'medium'`
- **AND** the capability SHALL translate to OpenAI's `reasoning_effort: 'medium'`

#### Scenario: Env var override
- **GIVEN** `model.thinking: "low"` in config.yaml
- **AND** `MODEL_THINKING=high` in environment
- **WHEN** settings are loaded
- **THEN** the thinking level SHALL be `'high'` (env var takes precedence)

#### Scenario: Thinking disabled
- **GIVEN** `model.thinking: false` or `MODEL_THINKING=false`
- **WHEN** the agent is built
- **THEN** no Thinking capability SHALL be injected
- **AND** the model SHALL use its default behavior (may include thinking for reasoning models)

#### Scenario: Thinking override per-call
- **GIVEN** a `build_agent()` call with `thinking="high"` parameter
- **AND** config has `thinking: "low"`
- **WHEN** the agent is built
- **THEN** the per-call `thinking` parameter SHALL take precedence

### Requirement: Model Behavior Defaults

**WHEN** `model.temperature`, `model.max_tokens`, or `model.service_tier` are set in config or env vars
**THEN** the system SHALL include these as default model_settings in every agent run
**AND** per-call `model_settings` parameter SHALL override config defaults.

#### Scenario: Temperature from config
- **GIVEN** `model.temperature: 0.7` in config.yaml
- **WHEN** the agent runs
- **THEN** the request SHALL include `temperature: 0.7` in model settings

#### Scenario: Max tokens from config
- **GIVEN** `model.max_tokens: 4096` in config.yaml
- **AND** `MODEL_MAX_TOKENS=8192` in environment
- **WHEN** settings are loaded
- **THEN** the effective max_tokens SHALL be `8192`

#### Scenario: Service tier selection
- **GIVEN** `model.service_tier: "flex"` in config.yaml
- **WHEN** the agent runs
- **THEN** the request SHALL use the flex service tier

#### Scenario: Per-call override
- **GIVEN** config has `temperature: 0.7`
- **AND** a run call passes `model_settings={'temperature': 0.2}`
- **WHEN** the agent runs
- **THEN** the run SHALL use `temperature: 0.2` (override wins)

### Requirement: Provider-Specific Settings Escape Hatch

**WHEN** `model.extra_model_settings` is set in config
**THEN** the system SHALL merge those key-value pairs into the model_settings dict
**AND** they SHALL take precedence over the unified fields.

#### Scenario: Anthropic thinking config
- **GIVEN** `model.extra_model_settings: {anthropic_thinking: {type: 'enabled', budget_tokens: 8192}}`
- **WHEN** the agent runs with an Anthropic model
- **THEN** the request SHALL include the native Anthropic thinking config

#### Scenario: OpenAI reasoning summary
- **GIVEN** `model.extra_model_settings: {openai_reasoning_summary: 'detailed'}`
- **WHEN** the agent runs with an OpenAI Responses model
- **THEN** the request SHALL include `openai_reasoning_summary: 'detailed'`

### Requirement: Thinking Field Migration

**WHEN** `AgentConfig.thinking` is referenced in consumer code
**THEN** the system SHALL NOT have a `thinking` field on `AgentConfig`
**AND** consumers SHALL use the `Thinking` capability or `model_settings` dict instead.

#### Scenario: Dead field removed
- **GIVEN** `AgentConfig` is defined in `_ai/config.py`
- **WHEN** the codebase is searched for `AgentConfig.thinking`
- **THEN** zero references SHALL be found outside of test assertions for removal

### Requirement: extra_model_settings Security Validation

**WHEN** `model.extra_model_settings` is set in config
**THEN** the system SHALL reject keys `extra_headers` and `extra_body` (header/body injection risk)
**AND** SHALL reject keys matching sensitive patterns (`api_key`, `secret`, `token`, `password`, `authorization`)
**AND** SHALL NOT serialize `extra_model_settings` in `model_dump()` output

#### Scenario: Blocked dangerous keys
- **GIVEN** config has `extra_model_settings: {extra_headers: {Authorization: "Bearer x"}}`
- **WHEN** settings are loaded
- **THEN** a `ValueError` SHALL be raised with the blocked key name

#### Scenario: Sensitive key rejection
- **GIVEN** config has `extra_model_settings: {api_key: "sk-123"}`
- **WHEN** settings are loaded
- **THEN** a `ValueError` SHALL be raised listing the sensitive key

#### Scenario: Serialization exclusion
- **GIVEN** `extra_model_settings` contains `{anthropic_thinking: {type: 'adaptive'}}`
- **WHEN** `model_dump()` is called on ModelSettings
- **THEN** the output SHALL NOT contain `extra_model_settings`

### Requirement: Model Settings Range Validation

**WHEN** `model.temperature` or `model.max_tokens` are set
**THEN** the system SHALL validate `temperature` is between 0.0 and 2.0
**AND** SHALL validate `max_tokens` is between 1 and 1,000,000
**AND** SHALL raise `ValueError` for out-of-range values

#### Scenario: Temperature in range
- **GIVEN** `model.temperature: 0.7`
- **WHEN** settings are loaded
- **THEN** no error SHALL be raised

#### Scenario: Temperature out of range
- **GIVEN** `model.temperature: 5.0`
- **WHEN** settings are loaded
- **THEN** a `ValueError` SHALL be raised

