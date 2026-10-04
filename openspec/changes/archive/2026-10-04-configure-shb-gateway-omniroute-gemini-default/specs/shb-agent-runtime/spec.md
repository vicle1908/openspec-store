# Spec Delta

## MODIFIED Requirements

### Requirement: Provider-Agnostic Model Resolution

The `shb-agent-core` runtime SHALL resolve model endpoints dynamically via OpenAI-compatible gateways (OmniRoute `http://127.0.0.1:20128/v1` or direct providers) supporting primary and fallback model chains with automated connection failure failover, defaulting primary model resolution to `gemini-3.8-flash-high`.

#### Scenario: Gateway connection and model invocation
- **WHEN** an agent session is initialized with default settings
- **THEN** the model resolver SHALL construct a model instance configured to query `SHB_MODEL_GATEWAY_URL` using `gemini-3.8-flash-high` as `SHB_DEFAULT_MODEL`

#### Scenario: Fallback model invocation on provider error
- **WHEN** the primary model endpoint returns a connection timeout, rate limit, or 5xx error
- **THEN** the model chain SHALL sequentially fail over to `SHB_FALLBACK_MODEL` without terminating the agent session
