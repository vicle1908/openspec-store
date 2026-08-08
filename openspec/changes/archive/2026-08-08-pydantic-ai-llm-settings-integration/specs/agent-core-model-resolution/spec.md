## ADDED Requirements

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
