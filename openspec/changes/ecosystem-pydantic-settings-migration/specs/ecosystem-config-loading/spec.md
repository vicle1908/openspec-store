# Delta Spec: ecosystem-config-loading (ADDED)

## Purpose

Define the unified YAML-based config loading capability using pydantic-settings.

## ADDED Requirements

### Requirement: TDTSettings loads from YAML with env var override

The system SHALL provide a `TDTSettings` root model using `pydantic-settings` `BaseSettings` with `YamlConfigSettingsSource`. Config SHALL be loaded from `$TDT_HOME/config.yaml` with environment variables overriding YAML values.

#### Scenario: YAML config loaded

- **GIVEN** `~/.tdt/config.yaml` contains `sprint.current_sprint: 19`
- **WHEN** `TDTSettings.load()` is called
- **THEN** `settings.sprint["current_sprint"]` SHALL be `19`

#### Scenario: Env var overrides YAML

- **GIVEN** `~/.tdt/config.yaml` contains `sprint.current_sprint: 19`
- **AND** environment variable `SPRINT__CURRENT_SPRINT=20` is set
- **WHEN** `TDTSettings.load()` is called
- **THEN** `settings.sprint["current_sprint"]` SHALL be `20`

#### Scenario: Missing YAML file

- **GIVEN** `~/.tdt/config.yaml` does not exist
- **WHEN** `TDTSettings.load()` is called
- **THEN** it SHALL return default settings without error

### Requirement: Secret fields use SecretStr

Config fields that hold secrets SHALL use `pydantic.SecretStr` type. Secret values SHALL NOT appear in YAML, logs, or error messages.

#### Scenario: Secret field masked in output

- **GIVEN** `~/.tdt/.env` contains `ATLASSIAN_ACCESS_TOKEN=secret123`
- **WHEN** `JiraConfig.from_env()` is called
- **THEN** `config.token` SHALL be a `SecretStr` instance

#### Scenario: Secret field not in YAML

- **GIVEN** `~/.tdt/config.yaml` contains `jira.token: secret123`
- **WHEN** `TDTSettings.load()` is called
- **THEN** it SHALL raise a validation error (secrets must be in `.env`)

### Requirement: Config validation at load time

Pydantic models SHALL validate config values at load time. Invalid values SHALL raise clear error messages.

#### Scenario: Invalid port number

- **GIVEN** `~/.tdt/config.yaml` contains `webhook_receiver.port: -1`
- **WHEN** `TDTSettings.load()` is called
- **THEN** it SHALL raise a `ValidationError` with message about port being less than minimum

### Requirement: Backward-compatible env injection

`load_sprint_config()` SHALL remain available as a deprecated shim. It SHALL inject config values into `os.environ` for backward compatibility during transition.

#### Scenario: Deprecated function warns

- **WHEN** `load_sprint_config()` is called
- **THEN** it SHALL emit a `DeprecationWarning`
- **AND** it SHALL set `SPREADSHEET_ID` in `os.environ`
