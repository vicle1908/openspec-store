# shb-core-foundation Specification Delta

## MODIFIED Requirements

### Requirement: Unified Environment and Credential Loading
The `shb-core` package SHALL load configuration and credentials from `~/.shb/.env` using `python-dotenv>=1.2.4` and `pydantic>=2.13.5`, protecting secrets with `pydantic.SecretStr`, providing computed configuration fields, and falling back to process environment variables without accessing or loading `~/.tdt/.env`.

#### Scenario: Dedicated environment file loaded
- **WHEN** an application imports `shb_core` configuration without explicit path overrides
- **THEN** configuration values are resolved from `~/.shb/.env` and process environment variables

#### Scenario: Dedicated environment file loaded with secret masking
- **WHEN** an application imports `shb_core` configuration without explicit path overrides
- **THEN** configuration values are resolved from `~/.shb/.env` and sensitive fields (such as `model_gateway_key`, `banking_api_token`, and `jira_api_token`) are masked as `SecretStr` instances

#### Scenario: Isolation from other organization credentials
- **WHEN** credentials exist in `~/.tdt/.env` but not in `~/.shb/.env`
- **THEN** `shb_core` configuration loaders SHALL raise a missing credential error and refuse to read `~/.tdt/.env`
