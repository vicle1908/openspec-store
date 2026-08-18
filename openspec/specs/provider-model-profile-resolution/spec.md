# provider-model-profile-resolution Specification

## Purpose
Define a YAML-based provider/model/default configuration schema for TDT Python agent consumers, aligned with the configuration patterns proven by Codex, Grok Build, and Kimi. This is the target architecture that replaces the legacy `model.primary`/`model.fallback`/`api_key_env` YAML pattern with the canonical `providers`/`models`/`defaults` schema and the `auth_env` credential field. The packaged `environment-key-registry.json` is NOT replaced by this schema; it persists as the credential-metadata authority (secret classification and provider binding), while `auth_env` replaces only the retired `api_key_env` YAML field.

**Status: IMPLEMENTED in tdt-core current main (`75cd519`). Consumer projections were completed and corrected through successor/corrective changes: ai-harness-skills `02d0410`, ai-review `f1b6e0f`.**

## Requirements

### Requirement: Canonical transport-specific provider definitions

Every provider MUST declare its transport type (endpoint or native) and the corresponding configuration fields. Endpoint providers MUST include `base_url`. Native providers MUST include `cli_provider` and MUST NOT include `base_url`.

#### Scenario: Endpoint provider has base_url

- **WHEN** a provider is declared with `transport: endpoint`
- **THEN** it MUST include a valid `base_url` field
- **AND** it MUST NOT include a `cli_provider` field

#### Scenario: Native provider has cli_provider

- **WHEN** a provider is declared with `transport: native`
- **THEN** it MUST include a `cli_provider` field
- **AND** it MUST NOT include a `base_url` field

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

### Requirement: Canonical catalog referential integrity

Every model alias referenced in `defaults.model`, `defaults.fallback`, or `defaults.cli_models` MUST resolve to a declared model. Every provider referenced by a model MUST be declared in `providers`. Referential integrity violations MUST fail before profile resolution.

#### Scenario: Undefined model alias fails

- **WHEN** a model alias in `defaults.model` or `defaults.fallback` is not declared in `models`
- **THEN** configuration validation SHALL fail with the undefined alias identified

#### Scenario: Undefined provider fails

- **WHEN** a model references a provider not declared in `providers`
- **THEN** configuration validation SHALL fail with the undefined provider identified

### Requirement: Explicit typed provider protocol

Every provider MUST declare its protocol. The closed protocol vocabulary is `messages` (Anthropic Messages), `openai_chat` (OpenAI Chat Completions), and `responses` (OpenAI Responses). The protocol determines the API format used for model requests. Inference or defaulting of protocol type SHALL NOT occur.

#### Scenario: Protocol is explicitly declared

- **WHEN** a provider is configured
- **THEN** it MUST include an explicit `protocol` field
- **AND** the protocol MUST be one of `messages`, `openai_chat`, or `responses`

#### Scenario: OpenAI Chat protocol is accepted

- **GIVEN** a provider declared with `protocol: openai_chat`
- **WHEN** the YAML is loaded and validated
- **THEN** the provider SHALL be accepted
- **AND** the protocol SHALL map to the OpenAI Chat Completions wire format

#### Scenario: Unknown protocol is rejected

- **GIVEN** a provider declared with a protocol value outside the closed vocabulary
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with the unsupported protocol value identified

### Requirement: Explicit provider capability authority

Provider capabilities (model support, context length, tool support) MUST be explicitly declared or discovered through the provider's API. Silent inference or assumption of capabilities SHALL NOT occur. Unknown capabilities MUST fail closed.

#### Scenario: Capability is explicitly declared

- **WHEN** a provider is configured
- **THEN** its capabilities MUST be either declared in configuration or discovered via API probing
- **AND** undetermined capabilities SHALL NOT be assumed

### Requirement: Provider-bound credential access

Every public boundary that resolves or reveals protected provider credential material MUST require an explicit, non-empty canonical provider identity. Before reading an environment value, resolution SHALL identify exactly one credential metadata entry for the supplied typed or raw reference and SHALL verify that the selected metadata, any provider carried by the reference, and the requested provider all have the same non-empty provider binding. Missing, duplicate, ambiguous, unbound, or mismatched relationships MUST fail closed. A raw key-name reference SHALL NOT bypass provider binding. The credential-binding identity SHALL be the canonical provider ID, not a CLI adapter identity, protocol, model name, endpoint, or another provider's available credential. Protected material SHALL remain process-local and non-serializable and SHALL NOT appear in profiles, diagnostics, provenance, reports, exceptions, or retained evidence.

#### Scenario: Matching provider accesses protected credential

- **GIVEN** exactly one validated credential reference is bound to canonical provider `giaoduc`
- **WHEN** resolution and reveal are requested with canonical provider identity `giaoduc`
- **THEN** the process-local credential SHALL be available to that provider boundary
- **AND** no serializable profile, diagnostic, provenance record, report, exception, or retained evidence SHALL contain the value

#### Scenario: Public credential boundary requires provider identity

- **GIVEN** a protected provider credential reference or protected credential is available
- **WHEN** public resolution or reveal is invoked without a provider argument or with an empty provider identity
- **THEN** access SHALL fail at the public security boundary before environment lookup or value return
- **AND** the error SHALL identify the missing provider context without exposing protected material

#### Scenario: Raw key reference is bound before environment lookup

- **GIVEN** a raw environment-key name identifies exactly one credential metadata entry bound to canonical provider `giaoduc`
- **WHEN** protected resolution is requested with canonical provider identity `giaoduc`
- **THEN** the resolver SHALL validate the unique provider binding before reading the environment value
- **AND** any returned protected credential SHALL remain bound to `giaoduc`
- **AND** later reveal SHALL still require the matching canonical provider identity

#### Scenario: Credential provider binding is missing or ambiguous

- **GIVEN** a typed or raw credential reference identifies no provider-bound metadata entry or more than one candidate metadata entry
- **WHEN** protected access is requested
- **THEN** access SHALL fail before any environment value is read
- **AND** an available environment variable SHALL NOT make an unbound or ambiguous reference acceptable
- **AND** no protected credential SHALL be constructed or returned

#### Scenario: Typed reference and requested provider disagree

- **GIVEN** a typed credential reference carries provider `anthropic`
- **WHEN** its matched metadata or requested canonical provider identity is `openai-chat`
- **THEN** resolution SHALL fail with a redacted provider-mismatch diagnostic before environment lookup
- **AND** no protected credential SHALL be constructed or substituted

#### Scenario: Cross-provider credential access is rejected

- **GIVEN** a protected credential is bound to canonical provider `anthropic`
- **WHEN** reveal is requested for canonical provider `openai-chat`
- **THEN** access SHALL fail with a redacted provider-mismatch diagnostic
- **AND** the `anthropic` credential SHALL NOT be returned, copied, or substituted

#### Scenario: Another provider credential is available

- **GIVEN** the selected provider's credential is unavailable and another provider's credential is available
- **WHEN** the selected provider attempts protected access
- **THEN** access SHALL fail for the selected provider
- **AND** the other provider's credential SHALL NOT be used as a fallback
