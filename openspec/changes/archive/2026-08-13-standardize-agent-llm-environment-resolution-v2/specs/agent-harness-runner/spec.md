## MODIFIED Requirements

### Requirement: Composed runner configuration

The runner SHALL compose an immutable canonical resolved agent profile with source-preserved harness domain configuration. Model and runtime LLM fields SHALL use the canonical precedence contract. Harness-owned gate, persistence, authority, validation, budget, and retention sections SHALL come only from the selected harness overlay and declared environment keys, never from same-named global sections. The legacy default harness config path SHALL not be read automatically, and explicit config files SHALL use the canonical top-level schema.

#### Scenario: Stage override

- **WHEN** a stage needs different limits or model settings
- **THEN** it SHALL receive an immutable run-scoped copy
- **AND** the parent profile SHALL remain unchanged

#### Scenario: Canonical durable environment

- **WHEN** durable settings are supplied through the canonical environment boundary
- **THEN** registered harness environment keys SHALL populate the declared persistence fields
- **AND** the harness SHALL NOT create a second dotenv loader or accept undeclared aliases

#### Scenario: Harness config resolves from agent-specific YAML

- **GIVEN** the agent-specific harness YAML contains model and runtime values
- **WHEN** runner configuration is loaded
- **THEN** its runtime profile SHALL use the canonically resolved values
- **AND** its model and settings projections SHALL agree

#### Scenario: HARNESS environment variables override agent-specific YAML

- **GIVEN** a registered harness environment value conflicts with agent YAML
- **WHEN** runner configuration is loaded
- **THEN** the environment value SHALL win
- **AND** provenance SHALL identify the registered key name

#### Scenario: Domain sections are source-preserved

- **GIVEN** the harness overlay contains gate, persistence, or authority settings
- **WHEN** runner configuration is loaded
- **THEN** those settings SHALL be read from that overlay
- **AND** same-named global sections SHALL not contribute

#### Scenario: Legacy config path is ignored

- **GIVEN** only the removed legacy harness config path exists
- **WHEN** runner configuration is loaded without an explicit path
- **THEN** it SHALL use agent/global/default sources permitted by the canonical contract
- **AND** it SHALL not read the legacy file

#### Scenario: Explicit legacy wrapper is rejected

- **GIVEN** an explicitly selected config file contains the legacy harness wrapper
- **WHEN** runner configuration is loaded
- **THEN** it SHALL fail with migration guidance to canonical top-level sections

#### Scenario: Explicit config path has canonical parity

- **GIVEN** a caller supplies an explicit `config_path` containing canonical top-level sections
- **WHEN** runner configuration is loaded
- **THEN** it SHALL apply the same precedence, overlay-key policy, path containment, and source-provenance rules as the standard agent path
- **AND** it SHALL not use the removed legacy wrapper or a second YAML loader

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

#### Scenario: Missing agent-specific config falls back to global defaults

- **GIVEN** no agent-specific harness overlay exists
- **WHEN** runner configuration is loaded
- **THEN** global LLM values and typed domain defaults SHALL be used
- **AND** registered environment values SHALL still apply

#### Scenario: Production services propagate the effective model

- **WHEN** production services are constructed from a valid runner configuration
- **THEN** `production_services().model` SHALL equal `config.model`
- **AND** every agent-backed stage SHALL receive the effective model and model behavior from that configuration
- **AND** stage construction SHALL not observe a missing model caused by composition loss

#### Scenario: Domain overlay does not alter the LLM profile

- **GIVEN** an agent overlay contains harness gate, persistence, authority, validation, budget, or retention sections
- **WHEN** runner configuration is composed
- **THEN** those sections SHALL remain source-preserved harness domain data
- **AND** they SHALL not override same-named global LLM or provider fields

#### Scenario: Unsafe or unresolved artifact root

- **WHEN** the configured artifact root is relative, remains an unexpanded variable, escapes the approved root, or traverses a disallowed link
- **THEN** production-service construction SHALL fail before creating a directory or writing an artifact

#### Scenario: Default artifact root with TDT_HOME unset

- **GIVEN** `TDT_HOME` is unset
- **WHEN** the default artifact root is resolved
- **THEN** it SHALL resolve beneath the canonical default TDT root
- **AND** no literal `$TDT_HOME` path component SHALL be created
