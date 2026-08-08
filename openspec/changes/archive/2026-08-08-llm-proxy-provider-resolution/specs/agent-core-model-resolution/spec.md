# agent-core-model-resolution (Delta)

## ADDED Requirements

### Requirement: Model Resolution from Config

**WHEN** `create_model(model_id)` is called
**AND** no explicit `base_url`/`api_key` kwargs provided
**THEN** the system SHALL resolve proxy configuration in this order:
1. `MODEL_BASE_URL` + `MODEL_API_KEY` env vars
2. `~/.tdt/config.yaml` model.base_url + env var from model.api_key_env
3. native provider environment variables handled by pydantic-ai

#### Scenario: Config-based resolution
- **GIVEN** `~/.tdt/config.yaml` has `model.primary: anthropic:Advance`
- **AND** `model.base_url: https://api.giaoduc.online/v1`
- **AND** `model.api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **AND** `HERMES_CUSTOM_GIAODUC_API_KEY=pmv_...` is set in environment
- **WHEN** `create_model("openai-chat:Advance")` is called
- **THEN** the model SHALL be created using the proxy endpoint via OpenAI Chat Completions API

#### Scenario: Anthropic Messages API
- **GIVEN** `~/.tdt/config.yaml` has `model.primary: anthropic:Advance`
- **AND** `model.base_url: https://api.giaoduc.online/v1`
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

### Requirement: Dual API Support

**WHEN** a provider supports both OpenAI and Anthropic API formats
**THEN** the system SHALL route to the correct endpoint based on model kind prefix:
- `openai-chat:*` → `/v1/chat/completions` (OpenAI format)
- `anthropic:*` → `/v1/messages` (Anthropic format)

#### Scenario: OpenAI Chat Completions
- **GIVEN** provider supports `/v1/chat/completions`
- **WHEN** `create_model("openai-chat:Advance")` is called
- **THEN** requests SHALL use OpenAI Chat Completions format

#### Scenario: Anthropic Messages
- **GIVEN** provider supports `/v1/messages`
- **WHEN** `create_model("anthropic:Advance")` is called
- **THEN** requests SHALL use Anthropic Messages format

### Requirement: Config Schema

**WHEN** `~/.tdt/config.yaml` is loaded
**THEN** the model section SHALL support:
- `primary`: Default model identifier (the active value is "anthropic:Advance")
- `base_url`: Proxy endpoint URL
- `api_key_env`: Environment variable name containing the API key
- `fallback`: List of fallback model identifiers
- `timeout_seconds`: Request timeout

#### Scenario: TDT model configuration
- **GIVEN** the active TDT config contains `model.primary`, `model.base_url`, and `model.api_key_env`
- **WHEN** the settings and model factory are initialized
- **THEN** the model endpoint and API key SHALL be resolved from those configured values

### Requirement: Verified Provider (giaoduc)

**WHEN** using the giaoduc provider (`https://api.giaoduc.online/v1`)
**THEN** the following features SHALL be supported:

| API Format | Endpoint | Model Kind | Features |
|------------|----------|------------|----------|
| OpenAI Chat Completions | `/v1/chat/completions` | `openai-chat:Advance` | Streaming, tool calling, reasoning |
| Anthropic Messages | `/v1/messages` | `anthropic:Advance` | Thinking blocks, tool use, system prompts |
| OpenAI Responses | `/v1/responses` | `openai-responses:Advance` | Not supported by active provider |

#### Scenario: giaoduc Anthropic verification
- **GIVEN** the active provider is giaoduc and the model is `anthropic:Advance`
- **WHEN** the agent runs a real prompt
- **THEN** the provider SHALL return an Anthropic Messages response successfully
