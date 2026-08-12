## Purpose

Define a YAML-based provider/model/default configuration schema for TDT Python agent consumers, aligned with the configuration patterns proven by Codex, Grok Build, and Kimi. This is the target architecture that replaces the current `model.primary`/`model.fallback`/`api_key_env` pattern and the separate packaged `environment-key-registry.json`.

**Status: IMPLEMENTED in tdt-core at `21dcd5b`. Consumer projections deferred to successor change `integrate-canonical-cli-projections-v1`.**

## ADDED Requirements

### Requirement: Provider definitions

Each provider in the `providers` section of `~/.tdt/config.yaml` SHALL declare a name, base URL, wire protocol, and credential environment variable reference. Credentials MUST NOT appear as literal values in YAML, JSON, profiles, provenance, or diagnostics.

#### Scenario: Provider definition accepted

- **GIVEN** `~/.tdt/config.yaml` contains `providers.shopapikey` with `*** https://api.phanmemvip.shop/v1`, `protocol: messages`, and `auth_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY`
- **WHEN** the YAML is loaded and validated
- **THEN** the provider definition SHALL be accepted
- **AND** the `auth_env` value SHALL be validated as a valid uppercase environment variable name
- **AND** no credential value SHALL appear in the resolved profile or diagnostics

#### Scenario: auth_env validates as uppercase env name

- **GIVEN** a provider definition contains `auth_env: "lowercase_key"`
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with the provider name and the invalid field
- **AND** the error SHALL not echo the invalid value

#### Scenario: auth_env referenced env var missing at runtime

- **GIVEN** a provider definition contains `auth_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **AND** the referenced environment variable is not set
- **WHEN** a consumer attempts to use that provider
- **THEN** resolution SHALL fail with the provider name and the missing env var name
- **AND** it SHALL NOT fall back to another provider's credential

#### Scenario: Duplicate auth_env across providers

- **GIVEN** two providers reference the same `auth_env` value
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with both provider names and the conflicting key
- **AND** it SHALL NOT silently accept the duplicate

#### Scenario: auth_env value is literal credential rejected

- **GIVEN** a provider definition contains `auth_env: "sk-actual-key-value"`
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL reject the value as a literal credential rather than an env var name

#### Scenario: Provider binding from YAML replaces registry lookup

- **GIVEN** the YAML defines `providers.giaoduc` with `auth_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **WHEN** credential availability is resolved
- **THEN** the provider association SHALL come from the YAML definition
- **AND** the separate `environment-key-registry.json` SHALL NOT override it
- **AND** credential availability SHALL be recorded with the provider from the YAML definition

### Requirement: Model profiles

Each model in the `models` section SHALL declare an alias, provider reference, wire model ID, and optional behavior settings (reasoning effort, context limit). The alias is the user-facing name; the wire model ID is what the provider receives.

#### Scenario: Model profile accepted

- **GIVEN** the YAML contains `models.shopapikey-fable-5` with `provider: shopapikey`, `model: fable-5`
- **WHEN** the YAML is loaded and validated
- **THEN** the model profile SHALL be accepted
- **AND** the provider reference SHALL resolve to a defined provider

#### Scenario: Model references nonexistent provider

- **GIVEN** a model profile contains `provider: nonexistent`
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with the model alias and the undefined provider name

#### Scenario: Per-model reasoning effort

- **GIVEN** a model profile contains `reasoning_effort: max`
- **WHEN** the model is selected
- **THEN** the reasoning effort SHALL be part of the resolved profile
- **AND** it SHALL be distinct from the global default reasoning effort

#### Scenario: Alias semantics in provenance

- **WHEN** a model alias is resolved to a wire model ID
- **THEN** the provenance SHALL record both the alias and the wire model ID
- **AND** the alias SHALL be the user-facing identifier in diagnostics
- **AND** the wire model ID SHALL be the provider-protocol identifier

### Requirement: Default alias selection

The `defaults.model` field SHALL reference a defined model alias. Fallbacks MAY reference additional model aliases. The default selection follows the canonical precedence contract.

#### Scenario: Default alias resolved

- **GIVEN** `defaults.model: shopapikey-fable-5` and `models.shopapikey-fable-5` is defined
- **WHEN** no higher-priority source overrides the default
- **THEN** the effective model SHALL be `shopapikey-fable-5`
- **AND** the resolved profile SHALL contain both the alias and the wire model ID

#### Scenario: Default alias references undefined model

- **GIVEN** `defaults.model: nonexistent-alias`
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with the undefined alias name

#### Scenario: Fallback aliases reference defined models

- **GIVEN** `defaults.fallback: [giaoduc-advance, cockpit-luna]`
- **WHEN** the YAML is loaded and validated
- **THEN** each fallback alias SHALL resolve to a defined model profile
- **AND** validation SHALL fail with all undefined aliases listed

### Requirement: Referential integrity across defaults, models, and providers

Every `defaults.model`, `defaults.fallback`, `models.*.provider`, and `providers.*.auth_env` reference SHALL resolve to a defined entry. Undefined references SHALL fail validation before any profile resolution or model construction.

#### Scenario: Full referential integrity check

- **GIVEN** the YAML defines 3 providers, 4 models, and a default
- **WHEN** the YAML is loaded and validated
- **THEN** every provider reference in models, every model reference in defaults/fallbacks, and every auth_env reference SHALL resolve
- **AND** validation SHALL report all undefined references in one pass

#### Scenario: Migration compatibility with legacy schema

- **GIVEN** the YAML contains both legacy `model.primary`/`model.fallback` fields and new `defaults.model`/`models.*` fields
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with an explicit conflict error
- **AND** it SHALL identify which fields are legacy and which are new
- **AND** it SHALL not silently choose one set over the other

#### Scenario: Legacy-only schema remains supported during migration

- **GIVEN** the YAML contains only legacy `model.primary`/`model.fallback`/`api_key_env` fields
- **WHEN** the YAML is loaded and validated
- **THEN** the legacy schema SHALL be accepted without error
- **AND** provenance SHALL record that the profile used the legacy resolution path
- **AND** the target schema SHALL become authoritative only after an explicit migration gate

### Requirement: Protocol enum

Each provider SHALL declare an explicit wire protocol from a registered set: `messages` (Anthropic Messages API), `responses` (OpenAI Responses API), `openai_chat` (OpenAI Chat Completions API). Silent protocol inference from the base URL or model name SHALL NOT occur.

#### Scenario: Valid protocol accepted

- **GIVEN** a provider definition contains `protocol: messages`
- **WHEN** the YAML is loaded and validated
- **THEN** the protocol SHALL be accepted
- **AND** it SHALL be recorded in the resolved profile for CLI projection

#### Scenario: Invalid protocol rejected

- **GIVEN** a provider definition contains `protocol: unknown_backend`
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with the provider name and the unsupported protocol
- **AND** it SHALL list the supported protocol values

#### Scenario: Missing protocol defaults to error during migration

- **GIVEN** the YAML contains only legacy provider fields without a `protocol` key
- **WHEN** the YAML is loaded under the legacy schema path
- **THEN** the protocol SHALL be inferred from the existing `api_mode` field for backward compatibility
- **AND** provenance SHALL record that the protocol was inferred, not declared

### Requirement: No silent inference of provider capabilities

The resolver SHALL NOT infer provider capabilities (context window, supported features, model family) from the base URL, model name, or protocol. All capability metadata SHALL be explicit in the YAML or derived from the registered environment-key registry during the transition period.

#### Scenario: Capabilities are explicit

- **GIVEN** a provider definition does not declare `context_window`
- **WHEN** the profile is resolved
- **THEN** the context window SHALL be reported as unknown
- **AND** the resolver SHALL NOT infer it from the base URL or model name

#### Scenario: Legacy api_mode inference during migration

- **GIVEN** the YAML contains a legacy `api_mode: anthropic_messages` field
- **WHEN** the profile is resolved under the legacy path
- **THEN** the protocol SHALL be inferred from the legacy field
- **AND** provenance SHALL record that the protocol was inferred
- **AND** after migration, the explicit `protocol` field SHALL take precedence
