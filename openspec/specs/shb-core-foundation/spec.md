# shb-core-foundation Specification

## Purpose
Provides shared infrastructure, credential management, client factories, and base CLI for the Saigon - Hanoi Bank (SHB) ecosystem.

## Requirements

### Requirement: Unified Environment and Credential Loading

The `shb-core` package SHALL load configuration and credentials from `~/.shb/.env` using `python-dotenv>=1.2.4` and `pydantic>=2.13.5`, protecting secrets with `pydantic.SecretStr`, providing computed configuration fields, defaulting `default_model` to `gemini-3.8-flash-high`, and falling back to process environment variables without accessing or loading `~/.tdt/.env`.

#### Scenario: Dedicated environment file loaded
- **WHEN** an application imports `shb_core` configuration without explicit path overrides
- **THEN** configuration values are resolved from `~/.shb/.env` and process environment variables
- **AND** `settings.default_model` SHALL default to `gemini-3.8-flash-high` when not overridden in the environment

#### Scenario: Dedicated environment file loaded with secret masking
- **WHEN** an application imports `shb_core` configuration without explicit path overrides
- **THEN** configuration values are resolved from `~/.shb/.env` and sensitive fields (such as `model_gateway_key`, `banking_api_token`, and `jira_api_token`) are masked as `SecretStr` instances

#### Scenario: Isolation from other organization credentials
- **WHEN** credentials exist in `~/.tdt/.env` but not in `~/.shb/.env`
- **THEN** `shb_core` configuration loaders SHALL raise a missing credential error and refuse to read `~/.tdt/.env`

### Requirement: Banking and Collaboration Client Factories
The system SHALL provide factory interfaces for authenticated enterprise HTTP services, issue tracking (Jira), and code repositories (GitLab) scoped to SHB endpoints.

#### Scenario: Client factory instantiation
- **WHEN** `JiraClientFactory.from_env()` or `GitlabClientFactory.from_env()` is invoked
- **THEN** client instances are returned configured with SHB-specific base URLs and authentication tokens

### Requirement: Command-Line Interface Entrypoint
The `shb-core` package SHALL expose a Typer-based command-line interface entrypoint named `shb` for configuration diagnostics, credential health checks, and service inspection.

#### Scenario: Command-line health check invocation
- **WHEN** the user executes `shb doctor` or `shb config show`
- **THEN** the CLI verifies `~/.shb/.env` existence and reports connectivity status for configured service endpoints
