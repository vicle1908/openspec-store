# consumer-config-composition Specification

## Purpose
Defines the composable configuration pattern for agent-core consumers, extended to support per-agent TDT config overrides via `~/.tdt/agents/{consumer-name}.yaml`.

## Requirements

### Requirement: ConsumerConfig composes Settings

`ConsumerConfig` SHALL compose agent-core's `Settings` as a field (not inheritance). This allows consumers to add domain-specific config while inheriting framework config (model, observability, secrets, etc.). The `Settings` instance SHALL reflect the merged global + agent-specific configuration from `~/.tdt/agents/{consumer-name}.yaml`.

#### Scenario: Framework settings accessible via config
- **WHEN** a consumer creates `DocsSyncConfig()`
- **THEN** `config.settings` SHALL be a fully-loaded `Settings` instance
- **AND** `config.settings.model.base_url` SHALL reflect the `MODEL_BASE_URL` env var

#### Scenario: Agent-specific config reflected in Settings
- **WHEN** `~/.tdt/agents/agent-docs-sync.yaml` contains `model: { primary: "openai-chat:fable-5" }`
- **AND** a consumer creates `DocsSyncConfig()`
- **THEN** `config.settings.model.primary` SHALL be `"openai-chat:fable-5"`

### Requirement: ConsumerConfig environment variable loading

`ConsumerConfig.from_env()` SHALL load consumer-specific fields from environment variables with an optional prefix. Environment variables SHALL override both agent-specific and global config values.

#### Scenario: Prefixed env vars
- **WHEN** `DocsSyncConfig.from_env(prefix="DOCS_SYNC_")` is called
- **AND** env var `DOCS_SYNC_MODEL=cx/gpt-5.5` is set
- **THEN** `config.model` SHALL be `"cx/gpt-5.5"`

#### Scenario: Env var overrides agent-specific config
- **WHEN** `DOCS_SYNC_MODEL=openai-chat:fable-5` is set
- **AND** `~/.tdt/agents/agent-docs-sync.yaml` contains `model: { primary: "anthropic:Advance" }`
- **THEN** `config.model` SHALL be `"openai-chat:fable-5"`

### Requirement: ConsumerConfig YAML loading

`ConsumerConfig.from_yaml()` SHALL load consumer-specific fields from a YAML file's `runtime:` section. This supersedes the previous `consumer:` section convention. Local runtime fields SHALL override agent-specific TDT config, which overrides global TDT config.

**BREAKING**: The `consumer:` section key from the previous spec version is replaced by `runtime:`.

#### Scenario: YAML consumer section loaded
- **WHEN** `DocsSyncConfig.from_yaml("config.yaml")` is called
- **AND** the file contains a `runtime:` section with `max_iterations: 15`
- **THEN** `config.runtime.max_iterations` SHALL be `15`
- **AND** framework settings outside the `runtime:` section SHALL be preserved in `config.settings`

#### Scenario: Missing YAML file is rejected
- **WHEN** `DocsSyncConfig.from_yaml("nonexistent.yaml")` is called
- **THEN** the system SHALL raise a `ConfigMigrationError` before constructing the config

#### Scenario: Repo-local model override is rejected
- **WHEN** `DocsSyncConfig.from_yaml("config.yaml")` is called
- **AND** the file contains `runtime: { model: "openai-chat:fable-5" }`
- **THEN** the system SHALL raise a `ConfigMigrationError` with message containing "model" and the agent config path `~/.tdt/agents/`
- **AND** the override SHALL NOT be applied

#### Scenario: Legacy consumer section is rejected
- **WHEN** `DocsSyncConfig.from_yaml("config.yaml")` is called
- **AND** the file contains a `consumer:` section
- **THEN** the system SHALL raise a `ConfigMigrationError` indicating the `consumer:` section is no longer supported
- **AND** directing the user to use the `runtime:` section and `~/.tdt/agents/` for model config

### Requirement: ConsumerConfig shortcut properties

`ConsumerConfig` SHALL provide shortcut properties for common framework settings (`.model`, `.observability`, `.secrets`). These properties SHALL reflect the fully resolved configuration chain.

#### Scenario: Shortcut properties delegate to settings
- **WHEN** a consumer accesses `config.model`
- **THEN** it SHALL return the resolved model from the full config chain (env > agent-specific > global > default)
