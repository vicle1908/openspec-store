## MODIFIED Requirements

### Requirement: ConsumerConfig composes Settings

A consumer configuration SHALL compose one immutable resolved runtime profile rather than inherit a framework settings class or independently load framework settings. Any compatibility `settings`, `model`, provider, behavior, or runtime projection SHALL be derived from that same profile snapshot and SHALL not expose a second effective value. The canonical compatibility model field is `settings.model.primary`; any legacy shortcut SHALL be a derived alias, never an independent settings value.

#### Scenario: Framework settings accessible via config

- **WHEN** a consumer configuration is constructed
- **THEN** its framework-facing projections SHALL be derived from its resolved runtime profile

#### Scenario: Agent-specific config reflected in Settings

- **GIVEN** the canonical profile resolves an agent-specific model
- **WHEN** a caller reads the consumer's model and settings projections
- **THEN** both SHALL identify the same effective model

#### Scenario: Settings model field and shortcut share provenance

- **WHEN** a caller reads `config.settings.model.primary`, `config.model`, and the generation profile
- **THEN** all SHALL identify the same effective model, fallback order, provider route, behavior settings, and source provenance
- **AND** none SHALL reload configuration or select a different fallback chain

#### Scenario: Consumer cannot expose two model truths

- **WHEN** source configuration would cause a legacy settings object and runtime field to disagree
- **THEN** construction SHALL either reconcile them through the canonical profile or fail
- **AND** the consumer SHALL NOT expose both conflicting values

### Requirement: ConsumerConfig environment variable loading

Consumer-specific process environment SHALL be interpreted by the canonical resolver according to the registered environment-key schema. A consumer SHALL NOT implement a separate environment or dotenv precedence chain for framework model fields.

#### Scenario: Prefixed env vars

- **WHEN** a registered consumer model environment key is set
- **THEN** the resolved profile SHALL apply it at consumer-environment precedence
- **AND** the consumer projection SHALL report that same value and provenance

#### Scenario: Env var overrides agent-specific config

- **GIVEN** a registered consumer environment value conflicts with agent YAML
- **WHEN** consumer configuration is constructed
- **THEN** the environment value SHALL win in the resolved profile and every projection

#### Scenario: Invalid typed environment value

- **WHEN** a registered numeric or enum environment value is invalid
- **THEN** configuration construction SHALL fail before model or write-capable tool construction

### Requirement: ConsumerConfig YAML loading

Repository-local consumer YAML SHALL contain only consumer-owned domain settings. It MUST NOT select an LLM model, fallback chain, provider route, or credential source. Agent-specific LLM configuration SHALL live under `$TDT_HOME/agents/{consumer-name}.yaml`; a repo-local LLM override or legacy consumer wrapper SHALL fail with migration guidance.

#### Scenario: YAML consumer section loaded

- **WHEN** repository YAML contains a supported domain runtime field such as a docs iteration limit
- **THEN** the consumer SHALL apply it according to the domain field's declared precedence
- **AND** unrelated resolved LLM fields SHALL remain unchanged

#### Scenario: Missing YAML file is rejected

- **WHEN** a caller explicitly selects a missing repository configuration file
- **THEN** construction SHALL fail before a consumer is created

#### Scenario: Repo-local model override is rejected

- **WHEN** repository YAML contains a model, fallback, provider, or model-behavior override
- **THEN** construction SHALL fail with the canonical agent-config location
- **AND** the override SHALL not be applied

#### Scenario: Legacy consumer section is rejected

- **WHEN** repository YAML contains the removed legacy consumer wrapper
- **THEN** construction SHALL fail with actionable migration guidance

#### Scenario: Runtime section owns domain fields only

- **GIVEN** repository YAML contains a canonical `runtime:` section
- **WHEN** consumer configuration is constructed
- **THEN** supported domain fields SHALL be applied according to their domain precedence
- **AND** model, fallback, provider, behavior, and credential fields SHALL be rejected rather than applied

### Requirement: ConsumerConfig shortcut properties

Consumer shortcut properties for model, providers, model behavior, observability, secrets metadata, or runtime settings SHALL delegate to the immutable resolved profile or an explicitly documented domain field. They SHALL reflect the effective precedence chain and MUST NOT trigger configuration I/O.

#### Scenario: Shortcut properties delegate to settings

- **WHEN** a caller accesses a consumer model shortcut and the resolved profile
- **THEN** the identifiers SHALL match

#### Scenario: Shortcut access performs no reload

- **WHEN** a shortcut property is accessed after construction
- **THEN** it SHALL return the stored immutable projection
- **AND** it SHALL not reread YAML, dotenv, or process environment
