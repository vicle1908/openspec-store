## ADDED Requirements

### Requirement: Hermes provider configuration is a separate runtime surface

Hermes provider configuration (`providers.<name>.model`, `providers.<name>.context_length`, and MoA preset slot references) SHALL be governed by this capability and the Hermes runtime, not by the canonical TDT provider schema. The canonical TDT provider schema (transport, protocol, auth_env, cli_provider, base_url, and model-level context_window) SHALL NOT be treated as the authority for Hermes provider fields. Context-window ownership at the Hermes provider level (`providers.<name>.context_length`) is intentional and distinct from the canonical model-level `context_window` behavior field. The two schemas MAY reference the same underlying providers (shopapikey, giaoduc, cockpit) without one being a projection of the other.

#### Scenario: Hermes provider fields are not canonical TDT fields

- **WHEN** Hermes configuration declares `providers.cockpit.model` or `providers.cockpit.context_length`
- **THEN** those fields SHALL be interpreted under the Hermes runtime schema
- **AND** they SHALL NOT be validated against or rejected by the canonical TDT provider schema

#### Scenario: Shared providers do not imply shared schema

- **GIVEN** both Hermes and the canonical TDT configuration reference the cockpit provider
- **WHEN** either configuration is validated
- **THEN** each SHALL be validated under its own runtime schema
- **AND** agreement on the provider name SHALL NOT require agreement on field structure

#### Scenario: Context-window ownership remains provider-level for Hermes

- **WHEN** Hermes validation inspects a provider used by MoA
- **THEN** the one-million-token context declaration SHALL be owned by `providers.<name>.context_length`
- **AND** MoA reference and aggregator slots SHALL NOT duplicate that declaration
