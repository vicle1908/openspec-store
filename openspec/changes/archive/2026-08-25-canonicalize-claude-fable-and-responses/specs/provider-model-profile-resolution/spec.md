# provider-model-profile-resolution Delta

## MODIFIED Requirements

### Requirement: Model profiles

Each model in the `models` section SHALL declare an alias, provider reference, wire model ID, and optional behavior settings (reasoning effort, context limit). The alias is the user-facing name; the wire model ID is what the provider receives.

#### Scenario: Model profile accepted

- **GIVEN** the YAML contains `models.shopapikey-claude-fable` with `provider: shopapikey`, `model: Claude-Fable`
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

- **GIVEN** `defaults.model: shopapikey-claude-fable` and `models.shopapikey-claude-fable` is defined
- **WHEN** no higher-priority source overrides the default
- **THEN** the effective model SHALL be `shopapikey-claude-fable`
- **AND** the resolved profile SHALL contain both the alias and the wire model ID

#### Scenario: Default alias references undefined model

- **GIVEN** `defaults.model: nonexistent-alias`
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with the undefined alias name

#### Scenario: Fallback aliases reference defined models

- **GIVEN** `defaults.fallback: [phanmemvip-sol, cockpit-luna]`
- **WHEN** the YAML is loaded and validated
- **THEN** each fallback alias SHALL resolve to a defined model profile
- **AND** validation SHALL fail with all undefined aliases listed
