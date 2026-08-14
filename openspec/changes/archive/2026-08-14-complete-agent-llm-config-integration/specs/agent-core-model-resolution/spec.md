## MODIFIED Requirements

### Requirement: Model layer is configuration-input only

The model layer MUST be configuration-input only for model selection and provider routing. Every public model constructor, CLI helper, SDK builder, and base-agent path SHALL receive either an already constructed model instance or a model identifier together with one caller-resolved immutable profile or compatibility snapshot. These construction paths SHALL NOT own YAML, dotenv, environment, credential, provider, or fallback precedence. If a caller supplies a model identifier or omits an already constructed model without supplying the resolved snapshot needed for selection, construction MUST fail before configuration discovery, provider or credential lookup, fallback construction, or model instantiation. A caller-supplied model instance MUST remain authoritative and bypass configuration, environment, provider-credential, and fallback discovery entirely, including when another supplied input contains conflicting model-selection fields.

#### Scenario: Static source conformance

- **WHEN** the model construction modules are audited
- **THEN** they SHALL contain no YAML reader, dotenv reader, TDT config-path read, or independent model-environment lookup

#### Scenario: All construction entry points agree

- **WHEN** CLI, SDK, and base-agent entry points receive the same resolved snapshot
- **THEN** they SHALL select the same primary, fallbacks, provider route, and model behavior settings
- **AND** none of those entry points SHALL resolve a second configuration snapshot

#### Scenario: Caller-resolved snapshot is reused

- **GIVEN** a caller has already resolved an agent profile or compatibility projection
- **WHEN** it constructs an agent through a public entry point using a model identifier
- **THEN** the primary, fallback order, provider route, behavior, provenance, and source fingerprints SHALL come from that supplied snapshot
- **AND** nested construction SHALL NOT reload, replace, or mutate any of those values

#### Scenario: Model identifier without caller snapshot fails before discovery

- **GIVEN** a caller supplies a model identifier or omits an already constructed model
- **AND** the caller does not supply a resolved profile or compatibility snapshot
- **WHEN** a public CLI, SDK, or base-agent construction entry point is invoked
- **THEN** construction SHALL fail with an actionable missing-snapshot diagnostic
- **AND** no TDT configuration, YAML, dotenv, model environment, provider credential, or fallback source SHALL be read
- **AND** no provider model or fallback chain SHALL be constructed

#### Scenario: Explicit Model performs zero source reads

- **GIVEN** a caller supplies an already constructed model instance
- **WHEN** any public agent-construction entry point builds the agent
- **THEN** the same model instance SHALL be used unchanged
- **AND** no TDT configuration, YAML, dotenv, model environment, provider credential, or fallback source SHALL be read

#### Scenario: Explicit Model remains authoritative over conflicting selection

- **GIVEN** a caller supplies an already constructed model instance
- **AND** another already supplied input names a different primary, fallback chain, provider route, or credential reference
- **WHEN** a public agent-construction entry point builds the agent
- **THEN** the constructed model instance SHALL remain the selected model by object identity
- **AND** the conflicting selection fields SHALL NOT replace, rebuild, wrap, or add a fallback around that instance
- **AND** no credential lookup for the conflicting provider SHALL occur

#### Scenario: Concurrent constructions keep snapshots isolated

- **GIVEN** two callers supply different resolved snapshots to simultaneous construction operations
- **WHEN** the operations construct their agents
- **THEN** each agent SHALL use only its own snapshot's primary, fallback order, provider route, behavior, provenance, and source fingerprints
- **AND** neither construction SHALL mutate, cache over, or substitute values from the other snapshot
