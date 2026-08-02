## ADDED Requirements

### Requirement: ConsumerConfig composes Settings

`ConsumerConfig` SHALL compose agent-core's `Settings` as a field (not inheritance). This allows consumers to add domain-specific config while inheriting framework config (gateway, observability, secrets, etc.).

#### Scenario: Framework settings accessible via config
- **WHEN** a consumer creates `DocsSyncConfig()`
- **THEN** `config.settings` SHALL be a fully-loaded `Settings` instance
- **AND** `config.settings.gateway.litellm_url` SHALL reflect `GATEWAY_LITELLM_URL` env var
- **AND** `config.settings.secrets.litellm_api_key` SHALL reflect the `.env` file value
- **AND** `config.settings.observability.otel_endpoint` SHALL reflect `OTEL_ENDPOINT` env var

#### Scenario: Consumer-specific fields independent of Settings
- **WHEN** a consumer defines `allowed_doc_roots: list[str] = ["docs/"]` in its config subclass
- **THEN** `config.allowed_doc_roots` SHALL be accessible alongside `config.settings`
- **AND** consumer fields SHALL NOT conflict with framework Settings field names

### Requirement: ConsumerConfig environment variable loading

`ConsumerConfig.from_env()` SHALL load consumer-specific fields from environment variables with an optional prefix.

#### Scenario: Prefixed env vars
- **WHEN** `DocsSyncConfig.from_env(prefix="DOCS_SYNC_")` is called
- **AND** env var `DOCS_SYNC_MODEL=cx/gpt-5.5` is set
- **THEN** `config.model` SHALL be `"cx/gpt-5.5"`

#### Scenario: No-prefix env vars
- **WHEN** `DocsSyncConfig.from_env()` is called (no prefix)
- **AND** env var `MODEL=gpt-4o` is set
- **THEN** `config.model` SHALL be `"gpt-4o"`

### Requirement: ConsumerConfig YAML loading

`ConsumerConfig.from_yaml()` SHALL load consumer-specific fields from a YAML file's `consumer:` section.

#### Scenario: YAML with consumer section
- **WHEN** `config.yaml` contains:
  ```yaml
  consumer:
    model: cx/gpt-5.5
    max_iterations: 20
  ```
- **AND** `DocsSyncConfig.from_yaml(path)` is called
- **THEN** `config.model` SHALL be `"cx/gpt-5.5"`
- **AND** `config.max_iterations` SHALL be `20`

#### Scenario: YAML without consumer section
- **WHEN** `config.yaml` does not contain a `consumer:` section
- **THEN** defaults SHALL be used
- **AND** no error SHALL be raised

### Requirement: ConsumerConfig shortcut properties

`ConsumerConfig` SHALL provide shortcut properties for common framework settings.

#### Scenario: Gateway shortcut
- **WHEN** `config.gateway` is accessed
- **THEN** it SHALL return `config.settings.gateway`

#### Scenario: Observability shortcut
- **WHEN** `config.observability` is accessed
- **THEN** it SHALL return `config.settings.observability`
