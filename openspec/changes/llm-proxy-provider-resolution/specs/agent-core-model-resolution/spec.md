# agent-core-model-resolution (Delta)

## MODIFIED Requirements

### Requirement: Model Resolution from Config

**WHEN** `create_model(model_id)` is called
**AND** no explicit `base_url`/`api_key` kwargs provided
**THEN** the system SHALL resolve proxy configuration in this order:
1. `MODEL_BASE_URL` + `MODEL_API_KEY` env vars
2. `~/.tdt/config.yaml` model.base_url + env var from model.api_key_env
3. `OMNIROUTE_URL` + `OMNIROUTE_API_KEY` env vars

#### Scenario: Config-based resolution
- **GIVEN** `~/.tdt/config.yaml` has `model.base_url: https://api.example.com/v1`
- **AND** `model.api_key_env: MY_API_KEY`
- **AND** `MY_API_KEY=secret123` is set in environment
- **WHEN** `create_model("openai-chat:gpt-4o")` is called
- **THEN** the model SHALL be created using the proxy endpoint

#### Scenario: Explicit kwargs override config
- **GIVEN** `create_model("openai-chat:gpt-4o", base_url="https://other.com/v1", api_key="key")`
- **WHEN** the model is created
- **THEN** the explicit kwargs SHALL be used instead of config

### Requirement: Config Schema

**WHEN** `~/.tdt/config.yaml` is loaded
**THEN** the model section SHALL support:
- `primary`: Default model identifier (e.g. "openai-chat:fable-5")
- `base_url`: Proxy endpoint URL
- `api_key_env`: Environment variable name containing the API key
- `fallback`: List of fallback model identifiers
- `timeout_seconds`: Request timeout
