## MODIFIED Requirements

### Requirement: Composed runner configuration

The runner SHALL consume harness domain configuration containing an immutable core runtime profile. Configuration SHALL be resolved through `load_agent_config("agent-harness")`, with `HARNESS_*` environment variables retaining precedence over agent-specific YAML, and the legacy `$TDT_HOME/harness/config.yaml` path no longer being authoritative.

#### Scenario: Stage override

- **WHEN** a stage needs different limits or model settings
- **THEN** it SHALL receive an immutable profile copy and run-scoped inputs
- **AND** the parent harness configuration SHALL remain unchanged

#### Scenario: Canonical durable environment

- **WHEN** durable settings are supplied through `$TDT_HOME/.env` or the process environment
- **THEN** `HarnessConfig.load()` SHALL delegate dotenv loading to `tdt_core.env.load_tdt_env()`
- **AND** `HARNESS_DURABLE` SHALL populate `persistence.durable`
- **AND** `TDT_POSTGRES_URL` SHALL populate `persistence.postgres_url`
- **AND** the harness SHALL NOT create a second settings loader or require `HARNESS_PERSISTENCE_DURABLE`

#### Scenario: Harness config resolves from agent-specific YAML

- **GIVEN** `~/.tdt/agents/agent-harness.yaml` exists with model, max_iterations, and timeout_seconds
- **WHEN** `HarnessConfig.load()` is called
- **THEN** configuration SHALL be resolved from `~/.tdt/agents/agent-harness.yaml` via `load_agent_config("agent-harness")`
- **AND** the loaded values SHALL be used for runtime settings

#### Scenario: HARNESS environment variables override agent-specific YAML

- **GIVEN** `~/.tdt/agents/agent-harness.yaml` specifies `durable: false`
- **AND** `HARNESS_DURABLE=true` is set in the environment
- **WHEN** `HarnessConfig.load()` is called
- **THEN** `config.persistence.durable` SHALL be `true`
- **AND** the environment variable SHALL take precedence

#### Scenario: Legacy config path is ignored

- **GIVEN** only `$TDT_HOME/harness/config.yaml` exists (no `~/.tdt/agents/agent-harness.yaml`)
- **WHEN** `HarnessConfig.load()` is called
- **THEN** configuration SHALL fall back to global TDT defaults and code defaults
- **AND** the legacy path SHALL NOT be read

#### Scenario: Missing agent-specific config falls back to global defaults

- **GIVEN** neither `~/.tdt/agents/agent-harness.yaml` nor `$TDT_HOME/harness/config.yaml` exists
- **WHEN** `HarnessConfig.load()` is called
- **THEN** code defaults SHALL be used without error
- **AND** `HARNESS_*` environment variables SHALL still be applied
