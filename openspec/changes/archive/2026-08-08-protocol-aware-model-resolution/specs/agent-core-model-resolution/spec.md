# agent-core-model-resolution (Delta)

## MODIFIED Requirements

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

### Requirement: Dual API Support

**WHEN** a provider supports both OpenAI and Anthropic API formats
**THEN** the system SHALL route to the correct endpoint based on model kind prefix:
- `anthropic:*` → `/v1/messages` (Anthropic format)
- `openai-chat:*` → `/v1/chat/completions` (OpenAI format)
- `openai-responses:*` → `/v1/responses` (OpenAI format)
- `google:*`, `fable-5:*`, `groq:*`, etc. → `/v1/chat/completions` (OpenAI-compatible proxy)

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

#### Scenario: Google via OpenAI-compatible proxy
- **GIVEN** provider exposes Google models via OpenAI-compatible API
- **WHEN** `create_model("google:gemini-2.0-flash")` is called
- **THEN** requests SHALL use OpenAI Chat Completions format via the proxy

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
