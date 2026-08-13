## MODIFIED Requirements

### Requirement: TDTSettings loads from YAML with env var override

Typed TDT settings SHALL load global configuration from the effective TDT root after canonical environment initialization. Registered process environment SHALL override YAML values according to the environment-key registry. Agent-specific LLM resolution SHALL compose typed global values with the agent overlay through the canonical agent-profile resolver rather than creating a second typed settings truth.

#### Scenario: YAML config loaded

- **GIVEN** global TDT YAML contains a valid non-secret setting
- **WHEN** typed settings are loaded
- **THEN** the setting SHALL be present in the typed result

#### Scenario: Env var overrides YAML

- **GIVEN** YAML and a registered environment key define the same logical field
- **WHEN** typed settings are loaded
- **THEN** the environment value SHALL win

#### Scenario: Agent profile and typed global value agree

- **GIVEN** no agent override or higher-priority model source is present
- **WHEN** typed global settings and an agent profile are loaded
- **THEN** equivalent global model fields SHALL agree

#### Scenario: Missing YAML file

- **GIVEN** no global config file exists under the effective root
- **WHEN** typed settings are loaded
- **THEN** registered environment values and typed defaults SHALL remain available

### Requirement: Secret fields use SecretStr

Typed fields that temporarily hold credential material MUST use protected secret types, and serializable resolved profiles MUST retain only secret availability and environment-key metadata. Literal secret values MUST NOT appear in YAML, caches, logs, diagnostics, exceptions, or provenance.

#### Scenario: Secret field masked in output

- **GIVEN** the canonical environment boundary provides a credential
- **WHEN** a typed credential field is inspected or serialized
- **THEN** the value SHALL be masked

#### Scenario: Secret field not in YAML

- **GIVEN** YAML contains a literal value in a secret-shaped field
- **WHEN** typed configuration is loaded
- **THEN** validation SHALL fail without echoing the value

#### Scenario: Resolved profile is serialized

- **WHEN** an effective agent profile is emitted for diagnostics
- **THEN** it SHALL contain the registered environment-key name and availability only
- **AND** it SHALL not contain a secret value or protected type serialization

## ADDED Requirements

### Requirement: Typed settings and agent profiles share one snapshot

Typed global settings and an agent profile SHALL use the same effective root,
environment-key registry, precedence order, source identities, and redacted secret
policy. A typed settings projection MAY expose non-LLM domain fields, but it SHALL not
form a second effective model or provider truth.

#### Scenario: Typed and profile model projections agree

- **GIVEN** a global model value, agent overlay, and registered environment value are available
- **WHEN** typed settings and the agent profile are loaded for one consumer
- **THEN** their effective model, fallback, behavior, provider metadata, and provenance SHALL agree
- **AND** downstream consumers SHALL use the profile snapshot rather than reloading typed settings

#### Scenario: Invalid higher-priority source fails closed

- **GIVEN** a higher-priority environment or YAML value is malformed, secret-invalid, or an unregistered direct-model alias
- **WHEN** typed settings or the agent profile is loaded
- **THEN** loading SHALL fail with redacted source information
- **AND** it SHALL not fall through to defaults or another credential
