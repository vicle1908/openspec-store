# provider-model-profile-resolution Delta Specification

## ADDED Requirements

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

### Requirement: Canonical catalog referential integrity

Every model alias referenced in `defaults.model`, `defaults.fallback`, or `defaults.cli_models` MUST resolve to a declared model. Every provider referenced by a model MUST be declared in `providers`. Referential integrity violations MUST fail before profile resolution.

#### Scenario: Undefined model alias fails

- **WHEN** a model alias in `defaults.model` or `defaults.fallback` is not declared in `models`
- **THEN** configuration validation SHALL fail with the undefined alias identified

### Requirement: Explicit typed provider protocol

Every provider MUST declare its protocol (`messages` or `responses`). The protocol determines the API format used for model requests. Inference or defaulting of protocol type SHALL NOT occur.

#### Scenario: Protocol is explicitly declared

- **WHEN** a provider is configured
- **THEN** it MUST include an explicit `protocol` field
- **AND** the protocol MUST be one of the declared types

### Requirement: Explicit provider capability authority

Provider capabilities (model support, context length, tool support) MUST be explicitly declared or discovered through the provider's API. Silent inference or assumption of capabilities SHALL NOT occur.

#### Scenario: Capability is explicitly declared

- **WHEN** a provider is configured
- **THEN** its capabilities MUST be either declared in configuration or discovered via API probing
- **AND** undetermined capabilities SHALL NOT be assumed

## REMOVED Requirements

### Requirement: Provider definitions

**Reason:** Replaced by canonical transport-specific provider definitions that enforce transport-specific field requirements.

### Requirement: Referential integrity across defaults, models, and providers

**Reason:** Replaced by canonical catalog referential integrity with clearer failure semantics.

### Requirement: Protocol enum

**Reason:** Replaced by explicit typed provider protocol with inference prohibition.

### Requirement: No silent inference of provider capabilities

**Reason:** Replaced by explicit provider capability authority with discovery requirements.
