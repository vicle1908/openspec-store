# agent-core-model-resolution (Delta)

## ADDED Requirements

### Requirement: CLI Consumer Model Behavior Alignment

The agent-core CLI SHALL apply the same config-driven model behavior contract as
SDK consumers. It SHALL pass configured sampling, token, service-tier, and
provider-specific settings through `BaseAgent.run(model_settings=...)`, and SHALL
represent `model.thinking` using the public Thinking capability.

#### Scenario: CLI applies unified model settings

- **GIVEN** `~/.tdt/config.yaml` contains `model.temperature: 0.7`, `model.max_tokens: 4096`, and `model.service_tier: flex`
- **WHEN** a CLI review, propose, explore, or REPL prompt runs
- **THEN** the CLI SHALL pass those values as default model settings to `BaseAgent.run()`

#### Scenario: CLI flattens provider-specific settings

- **GIVEN** `model.extra_model_settings` contains `openai_reasoning_summary: detailed`
- **WHEN** a CLI prompt runs
- **THEN** the CLI SHALL pass `openai_reasoning_summary: detailed` as a top-level model setting
- **AND** SHALL NOT pass an `extra_model_settings` wrapper key

#### Scenario: CLI injects configured thinking

- **GIVEN** `model.thinking: high`
- **WHEN** a CLI prompt runtime initializes
- **THEN** the CLI SHALL add a Thinking capability with effort `high`
- **AND** SHALL NOT pass `thinking` as a raw model-settings key

#### Scenario: CLI uses pydantic-ai defaults when behavior settings are absent

- **GIVEN** no sampling, token, service-tier, provider-specific, or thinking settings are configured
- **WHEN** a CLI prompt runs
- **THEN** the CLI SHALL pass no config-derived model settings
- **AND** SHALL add no Thinking capability

### Requirement: Canonical Model YAML Section

The settings loader SHALL use `model:` as the only YAML section for model
configuration and SHALL NOT fall back to the removed legacy `gateway:` section.

#### Scenario: Legacy gateway section is ignored

- **GIVEN** a configuration file contains a `gateway:` section but no `model:` section
- **WHEN** `load_settings()` is called
- **THEN** model settings SHALL use canonical defaults and environment overrides
- **AND** SHALL NOT read values from `gateway:`

#### Scenario: Canonical model section is loaded

- **GIVEN** a configuration file contains `model.primary: openai-chat:fable-5`
- **WHEN** `load_settings()` is called
- **THEN** `settings.model.primary` SHALL equal `openai-chat:fable-5`

### Requirement: CLI Fallback Behavior Settings

When the CLI creates a native `FallbackModel`, it SHALL construct the primary and
fallback models in configured positional order and SHALL apply behavior settings
at the enclosing agent-run boundary so the settings govern whichever model is
selected.

#### Scenario: Fallback chain uses configured agent-run settings

- **GIVEN** `model.primary: anthropic:Advance`
- **AND** `model.fallback: [openai-chat:fable-5]`
- **AND** `model.temperature: 0.7`
- **WHEN** the CLI prompt runtime initializes
- **THEN** the native fallback chain SHALL preserve the configured model order
- **AND** the CLI SHALL pass `temperature: 0.7` to `BaseAgent.run()`
