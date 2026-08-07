# consumer-config-composition Specification

## Purpose
Defines the composable configuration pattern for agent-core consumers.

## Requirements

### Requirement: ConsumerConfig composes Settings

`ConsumerConfig` SHALL compose agent-core's `Settings` as a field (not inheritance). This allows consumers to add domain-specific config while inheriting framework config (model, observability, secrets, etc.).

#### Scenario: Framework settings accessible via config
- **WHEN** a consumer creates `DocsSyncConfig()`
- **THEN** `config.settings` SHALL be a fully-loaded `Settings` instance
- **AND** `config.settings.gateway.litellm_url` SHALL reflect `GATEWAY_LITELLM_URL` env var

### Requirement: ConsumerConfig environment variable loading

`ConsumerConfig.from_env()` SHALL load consumer-specific fields from environment variables with an optional prefix.

#### Scenario: Prefixed env vars
- **WHEN** `DocsSyncConfig.from_env(prefix="DOCS_SYNC_")` is called
- **AND** env var `DOCS_SYNC_MODEL=cx/gpt-5.5` is set
- **THEN** `config.model` SHALL be `"cx/gpt-5.5"`

### Requirement: ConsumerConfig YAML loading

`ConsumerConfig.from_yaml()` SHALL load consumer-specific fields from a YAML file's `consumer:` section.

#### Scenario: YAML consumer section loaded
- **WHEN** `DocsSyncConfig.from_yaml("config.yaml")` is called
- **AND** the file contains a `consumer:` section with `model: cx/claude-opus-4.8.5`
- **THEN** `config.model` SHALL be `"cx/claude-opus-4.8.5"`
- **AND** framework settings outside the `consumer:` section SHALL be preserved in `config.settings`

#### Scenario: Missing YAML file is rejected
- **WHEN** `DocsSyncConfig.from_yaml("nonexistent.yaml")` is called
- **THEN** the call SHALL raise a clear error before constructing the config

### Requirement: ConsumerConfig shortcut properties

`ConsumerConfig` SHALL provide shortcut properties for common framework settings (`.gateway`, `.observability`, `.secrets`).

#### Scenario: Shortcut properties delegate to settings
- **WHEN** a consumer accesses `config.gateway`
- **THEN** it SHALL return `config.settings.gateway`
- **AND** the same delegation applies to `.observability` and `.secrets`
