## MODIFIED Requirements

### Requirement: Configured Fallback Loading

When the resolved agent profile contains a non-empty fallback list, every agent-core CLI and SDK construction path SHALL build the native fallback chain from the resolved primary followed by the resolved fallback identifiers in order. Construction SHALL NOT re-read configuration or replace an environment-selected primary with an agent-YAML value.

#### Scenario: CLI consumes configured fallback

- **GIVEN** the effective profile selects primary `anthropic:Advance`
- **AND** its fallbacks are `openai-chat:fable-5` then `openai-responses:gpt-5.6-luna`
- **WHEN** a CLI prompt runtime initializes
- **THEN** its model SHALL preserve that exact order

#### Scenario: Environment-selected primary remains selected

- **GIVEN** the effective profile selected a process-environment primary over a different agent-YAML primary
- **WHEN** a CLI or SDK agent is built
- **THEN** the constructed chain SHALL start with the environment-selected primary

### Requirement: Config-driven fallback chain construction

Model-chain construction SHALL consume the primary and fallback identifiers supplied in the resolved agent profile. It SHALL resolve model definitions at construction time but SHALL NOT read TDT YAML, dotenv files, or process environment to discover fallback identifiers or provider routing. It SHALL NOT make a network request merely to construct the chain.

#### Scenario: Config-driven fallback

- **GIVEN** the resolved profile contains primary `provider:model-a` and fallback `provider:model-b`
- **WHEN** model-chain construction runs
- **THEN** it SHALL return a fallback chain containing primary then fallback
- **AND** it SHALL perform no config-source read

#### Scenario: No fallback configured

- **GIVEN** the resolved profile has no fallback identifiers
- **WHEN** model-chain construction runs
- **THEN** it SHALL return only the resolved primary model

#### Scenario: Explicit Model instance bypasses fallback

- **GIVEN** a caller supplies an already constructed Model instance
- **WHEN** model-chain construction runs
- **THEN** the instance SHALL be returned unchanged
- **AND** no config or credential source SHALL be consulted

## ADDED Requirements

### Requirement: Model layer is configuration-input only

The model layer MUST be configuration-input only for model selection and provider routing. All public model constructors, CLI helpers, SDK builders, and base-agent paths SHALL accept resolved inputs or an explicit model and SHALL NOT own YAML, dotenv, or environment precedence.

#### Scenario: Static source conformance

- **WHEN** the model construction modules are audited
- **THEN** they SHALL contain no YAML reader, dotenv reader, TDT config-path read, or independent model-environment lookup

#### Scenario: All construction entry points agree

- **WHEN** CLI, SDK, and base-agent entry points receive the same resolved profile
- **THEN** they SHALL select the same primary, fallbacks, provider route, and model behavior settings

### Requirement: Effective model diagnostics match execution

Agent-core diagnostics SHALL report the effective model chain and non-secret provider route that the next construction call will use from the same resolved profile snapshot.

#### Scenario: Diagnostic and constructed chain agree

- **WHEN** the effective-config diagnostic and model construction are run from one profile
- **THEN** their model identifiers and order SHALL match

#### Scenario: Missing provider credential metadata

- **WHEN** a selected provider lacks its required registered environment key
- **THEN** diagnostics and construction SHALL fail with the same provider and environment-key name
- **AND** neither output SHALL reveal credential values

### Requirement: Caller-owned fallback and identifier validation

The caller that resolves an agent profile SHALL own the primary and fallback
identifiers passed to model construction. A model factory or fallback helper SHALL
not reinterpret a native CLI alias as a direct model, read TDT configuration to fill
missing fallback values, or replace a caller-selected identifier with a localized
alias. Direct identifiers SHALL be registered canonical `provider:model` values.

#### Scenario: Caller-owned fallback is preserved

- **GIVEN** a caller passes a resolved primary and ordered fallback identifiers
- **WHEN** the fallback chain is constructed
- **THEN** construction SHALL use exactly those identifiers in that order
- **AND** it SHALL perform no YAML, dotenv, or process-environment lookup for fallback discovery

#### Scenario: Unregistered live identifier is rejected

- **GIVEN** a direct-model input is a localized, display-only, or otherwise unregistered alias
- **WHEN** a CLI or SDK model chain is prepared
- **THEN** preparation SHALL fail before provider invocation
- **AND** model construction or a zero-exit wrapper SHALL not count as live acceptance
