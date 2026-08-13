## MODIFIED Requirements

### Requirement: ConsumerConfig Extension

The harness and other agent-core consumers SHALL compose an immutable canonical runtime profile as a field and SHALL NOT subclass a framework configuration class for domain configuration. Consumer-owned fields SHALL remain in the consumer model, while framework LLM fields SHALL be projected from the composed profile.

#### Scenario: HarnessConfig definition

- **WHEN** harness configuration is defined
- **THEN** it SHALL own a resolved runtime-profile field alongside harness domain fields
- **AND** it SHALL not inherit framework settings fields

#### Scenario: Config loading

- **WHEN** a registered harness environment key is set
- **THEN** the canonical resolver SHALL apply it to the effective profile or declared domain field
- **AND** the harness SHALL not run a separate framework environment loader

#### Scenario: Framework settings access

- **WHEN** harness code needs the effective model or model behavior
- **THEN** it SHALL read the composed resolved profile
- **AND** any compatibility settings projection SHALL identify the same values

#### Scenario: Canonical settings projection

- **WHEN** harness code reads the effective model through configuration
- **THEN** `config.settings.model.primary`, the model shortcut, and the resolved profile SHALL identify the same value and provenance
- **AND** the stale `config.settings.agent.default_model` path SHALL not be an independent source or trigger a reload

### Requirement: Model Configuration

The harness SHALL use the public agent-core SDK to construct models from its canonical resolved profile. It SHALL NOT import private model modules, reread configuration sources, or select a different model after profile resolution.

#### Scenario: Model from config

- **WHEN** an agent-backed harness stage is initialized
- **THEN** the stage SHALL receive the effective model, fallback order, provider route, and behavior from the composed profile through the public SDK

#### Scenario: Model fallback

- **WHEN** the resolved profile declares fallbacks
- **THEN** the public SDK SHALL construct the fallback chain in declared order
- **AND** the harness SHALL not maintain a separate fallback list

#### Scenario: Caller-owned model chain

- **WHEN** the public SDK constructs a model from a resolved profile
- **THEN** the primary, fallback order, provider route, and behavior settings SHALL come from that profile
- **AND** the harness SHALL not read TDT files, dotenv, or process environment to replace them

#### Scenario: Production model is missing

- **WHEN** an agent-backed production stage has no effective model after configuration composition
- **THEN** stage construction SHALL fail closed with a configuration error before provider invocation
