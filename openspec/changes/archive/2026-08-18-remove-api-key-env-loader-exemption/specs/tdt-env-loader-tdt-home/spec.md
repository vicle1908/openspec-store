## MODIFIED Requirements

### Requirement: Typed configuration uses secret references

The provider SHALL accept secret-shaped configuration only when it uses the supported full-scalar environment-reference grammar after environment loading; literal secret values are rejected. Retired credential-field names (such as `api_key_env`) SHALL receive no backward-compatibility exemption in the configuration loader's secret policy; they SHALL be classified as secret-shaped so that literal values are rejected and only full-scalar `${ENV}` references pass the loader, exactly as for any other secret-shaped key. The canonical credential field is `auth_env`, and the canonical schema parser SHALL reject the retired field name itself regardless of value form.

#### Scenario: Full-scalar reference resolves

- **GIVEN** a secret-shaped setting contains exactly `${UPPER_SNAKE_CASE_NAME}`
- **AND** the named environment value is available
- **WHEN** typed configuration is loaded
- **THEN** the setting resolves without emitting the secret value in diagnostics

#### Scenario: Literal or composite secret is rejected

- **GIVEN** a secret-shaped setting contains a literal, a collection, or a composite string containing a reference
- **WHEN** typed configuration is loaded
- **THEN** validation fails with the logical key and source but not the value

#### Scenario: Retired api_key_env field with a literal value is rejected by the loader

- **GIVEN** a configuration mapping contains `providers.<id>.api_key_env` with a bare environment-variable name or any other literal value
- **WHEN** the configuration loader applies its secret policy
- **THEN** the loader SHALL reject the mapping with a secret-shaped-key error identifying the `api_key_env` path
- **AND** the loader SHALL NOT carry a backward-compatibility exemption for the retired field

#### Scenario: Retired api_key_env field is rejected by the canonical schema regardless of value form

- **GIVEN** a configuration mapping contains `providers.<id>.api_key_env` with any value, including a full-scalar `${ENV}` reference that passes the loader's secret policy
- **WHEN** the canonical schema parser validates the provider definition
- **THEN** the parser SHALL reject the mapping because `api_key_env` is not a declared provider field
- **AND** the retired field SHALL NOT reach profile resolution in any value form

#### Scenario: Canonical auth_env field passes the loader

- **GIVEN** a configuration mapping contains `providers.<id>.auth_env` with a bare environment-variable name
- **WHEN** the configuration loader applies its secret policy
- **THEN** the loader SHALL accept the mapping without a secret-shaped-key error

#### Scenario: Conflicting scheduler sources are visible

- **GIVEN** the same logical scheduler setting appears in competing supported sources
- **WHEN** governed configuration is loaded
- **THEN** equal normalized values are reported as a deterministic compatibility condition and conflicting values fail closed

#### Scenario: Missing reference is redacted

- **GIVEN** a referenced environment name is unavailable
- **WHEN** governed configuration is loaded
- **THEN** the error identifies the missing logical setting and reference name without revealing any credential value

### Requirement: Environment-key registry

The system SHALL publish a machine-readable registry for LLM and consumer environment keys. Each entry SHALL define the logical field, owner, type, precedence class, secret classification, supported consumers, and compatibility status. Duplicate logical ownership or incompatible aliases SHALL fail validation.

#### Scenario: Registered key drives resolution

- **WHEN** a registered environment key is present
- **THEN** the resolver SHALL coerce and apply it according to its declared type and precedence

#### Scenario: Alias deprecation is visible

- **WHEN** a supported legacy alias is used
- **THEN** diagnostics SHALL identify its deprecated status and canonical replacement
- **AND** both aliases SHALL not produce ambiguous effective values

#### Scenario: Conflicting aliases

- **WHEN** canonical and legacy keys for one field are both set to different values
- **THEN** resolution SHALL fail with the key names and logical field
- **AND** it SHALL not reveal protected values

#### Scenario: Provider credential registered and bound

- **GIVEN** the registry contains a credential entry with `secret: true` and `provider: "giaoduc"`
- **WHEN** a canonical provider declares `auth_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **THEN** the resolved route SHALL record credential availability bound to the `giaoduc` provider
- **AND** credential availability SHALL be recorded without the secret value

#### Scenario: Unregistered credential key is rejected

- **WHEN** the registry's `credential_entry()` validation is asked for a key not present in the registry
- **THEN** it SHALL raise `ProfileResolutionError` identifying that the key is not registered
- **AND** the error SHALL NOT reveal credential values

#### Scenario: Credential availability reflects the environment, not registry membership

- **GIVEN** a canonical provider declares an `auth_env` value
- **WHEN** `resolve_agent_profile()` resolves that provider
- **THEN** the resolved route SHALL record `available` as true only when the named environment variable is present
- **AND** the registry SHALL serve as credential metadata (secret classification and provider binding), not as a resolution-time gate on `auth_env`
- **AND** no credential value SHALL be recorded or revealed

#### Scenario: Credential key assigned to wrong provider is rejected

- **GIVEN** the registry binds `ANTHROPIC_API_KEY` to provider `anthropic`
- **WHEN** a canonical provider for `openai-chat` declares `auth_env: ANTHROPIC_API_KEY`
- **THEN** the resolver SHALL reject the cross-provider assignment
- **AND** it SHALL not silently accept the mismatched credential binding
