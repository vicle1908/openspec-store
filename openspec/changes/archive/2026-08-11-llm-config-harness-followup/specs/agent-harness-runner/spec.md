## MODIFIED Requirements

### Requirement: Composed runner configuration

The runner SHALL consume harness domain configuration containing an immutable core runtime profile. Model and runtime settings SHALL be resolved through `load_agent_config("agent-harness")` for the merged LLM configuration. Harness domain sections (`gate`, `persistence`, `authority`, `validation`, `budget`, `retention`) SHALL be resolved through `load_agent_overlay("agent-harness")`, which preserves source provenance by reading the agent YAML file directly without merging with the global config. Domain keys validated by `allowed_overlay_keys` in `load_agent_config()` SHALL be accepted without error but SHALL NOT appear in the merged LLM result — `load_agent_overlay()` is the sole source for harness domain sections. `HARNESS_*` environment variables SHALL retain precedence over agent-specific YAML values. The legacy `$TDT_HOME/harness/config.yaml` path SHALL NOT be read automatically.

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

#### Scenario: Domain sections sourced from agent overlay only

- **GIVEN** `~/.tdt/agents/agent-harness.yaml` contains `gate: {approvers: ["alice"]}`
- **AND** `~/.tdt/config.yaml` does NOT contain a `gate` key
- **WHEN** `HarnessConfig.load()` is called
- **THEN** `config.gate.approvers` SHALL be `["alice"]`
- **AND** the value SHALL have been read by `load_agent_overlay("agent-harness")`

#### Scenario: Global config does not supply domain sections

- **GIVEN** `~/.tdt/config.yaml` contains `gate: {approvers: ["bob"]}`
- **AND** `~/.tdt/agents/agent-harness.yaml` does NOT contain a `gate` key
- **WHEN** `HarnessConfig.load()` is called
- **THEN** `config.gate.approvers` SHALL use the `HarnessConfig` field default (empty list)
- **AND** the value `"bob"` SHALL NOT appear in the configuration

#### Scenario: Explicit config_path overrides agent overlay path

- **GIVEN** an explicit `config_path` is provided to `HarnessConfig.load()`
- **WHEN** `HarnessConfig.load(config_path=path)` is called
- **THEN** both `load_agent_config()` and `load_agent_overlay()` SHALL use the explicit path as the agent overlay source
- **AND** the standard `~/.tdt/agents/agent-harness.yaml` SHALL NOT be read

#### Scenario: Legacy harness wrapper rejected

- **GIVEN** an explicit config file contains a `harness:` top-level wrapper section
- **WHEN** `HarnessConfig.load(config_path=path)` is called
- **THEN** a `ConfigMigrationError` SHALL be raised directing the operator to use top-level sections
