# hermes-moa-configuration Delta

## MODIFIED Requirements

### Requirement: Default MoA preset

The `default` preset SHALL use exactly two enabled references, `phanmemvip:gpt-5.6-sol` at `high` and `cockpit:gpt-5.6-sol` at `high`, and SHALL use `shopapikey:fable-5` at `xhigh` as its aggregator, with the validated token, temperature, cadence, and enablement settings.

#### Scenario: Default preset normalization

- **WHEN** Hermes normalizes the `default` preset
- **THEN** the references SHALL be `phanmemvip:gpt-5.6-sol` at `high` and `cockpit:gpt-5.6-sol` at `high`
- **AND** the aggregator SHALL be `shopapikey:fable-5` at `xhigh`
- **AND** `reference_max_tokens` SHALL be `1000`
- **AND** `max_tokens` SHALL be `8192`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.4`
- **AND** `fanout` SHALL be `every_n:3`
- **AND** `degraded_reference_policy` SHALL be `loud`
- **AND** the preset SHALL be `enabled: true`

### Requirement: Deep MoA preset

The `deep` preset SHALL provide a three-reference route with periodic advisor refresh, a phanmemvip aggregator, and three distinct provider perspectives.

#### Scenario: Deep preset normalization

- **WHEN** Hermes normalizes the `deep` preset
- **THEN** the references SHALL be `shopapikey:fable-5` at `high`, `cockpit:gpt-5.6-sol` at `high`, and `phanmemvip:gpt-5.6-sol` at `high`
- **AND** the aggregator SHALL be `phanmemvip:gpt-5.6-sol` at `max`
- **AND** `reference_max_tokens` SHALL be `800`
- **AND** `max_tokens` SHALL be `8192`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.3`
- **AND** `fanout` SHALL be `per_iteration`
- **AND** `degraded_reference_policy` SHALL be `loud`
- **AND** the preset SHALL be `enabled: true`

### Requirement: Context-window ownership

The one-million-token context declaration SHALL be owned by provider and model configuration, and MoA reference or aggregator slots SHALL NOT duplicate `context_length`.

#### Scenario: Provider context validation

- **WHEN** configuration validation inspects `cockpit`, `shopapikey`, and `phanmemvip`
- **THEN** each provider SHALL declare `context_length: 1000000`
- **AND** each MoA-used model SHALL resolve a one-million-token context declaration from its provider/model configuration

#### Scenario: MoA slot validation

- **WHEN** configuration validation traverses every reference and aggregator slot
- **THEN** no slot SHALL contain a `context_length` field

### Requirement: Fallback independence

The fallback chain SHALL contain routes that are distinct from the selected primary `moa:default` deployment and SHALL preserve the configured direct-provider order.

#### Scenario: Primary MoA failure

- **WHEN** `moa:default` fails after its retry policy
- **THEN** Hermes SHALL attempt `shopapikey:fable-5`, then `phanmemvip:gpt-5.6-sol`, then `cockpit:gpt-5.6-luna`, subject to local availability and failure-scope skip rules

#### Scenario: Duplicate primary candidate

- **WHEN** a fallback entry resolves to the same provider, model, and effective virtual deployment as the failed `moa:default` primary
- **THEN** the configuration SHALL exclude that redundant entry
- **AND** validation SHALL confirm the chain begins with an independent direct provider

### Requirement: Specialist MoA topology and independent cockpit routes

The MoA configuration SHALL use `cockpit:gpt-5.6-sol` as the cockpit-backed reference in every preset. No active MoA reference or aggregator SHALL use `cockpit:gpt-5.6-luna`. The direct cockpit provider default and direct fallback entry SHALL use `cockpit:gpt-5.6-luna`. The cockpit provider default model (`providers.cockpit.model`) SHALL be `gpt-5.6-luna` and is independent of the MoA preset slot models. The direct-provider default and the MoA slot selection are orthogonal configuration surfaces; the cockpit model name appearing in `providers.cockpit.model` does not constrain which model names appear in MoA presets, and vice versa.

#### Scenario: MoA presets use Sol as reference

- **WHEN** any MoA preset reference list is inspected
- **THEN** every cockpit-backed MoA reference SHALL name `gpt-5.6-sol` at `high`
- **AND** no MoA reference or aggregator slot SHALL name `gpt-5.6-luna`
- **AND** the default aggregator SHALL be `shopapikey:fable-5`
- **AND** the deep aggregator SHALL be `phanmemvip:gpt-5.6-sol`
- **AND** the fast aggregator SHALL be `shopapikey:fable-5`

#### Scenario: Cockpit provider default uses Luna

- **WHEN** the direct cockpit provider configuration is inspected
- **THEN** `providers.cockpit.model` SHALL be `gpt-5.6-luna`
- **AND** the direct fallback chain SHALL use `cockpit:gpt-5.6-luna` at `max`

#### Scenario: Cockpit Sol inference

- **WHEN** a direct non-streaming inference request is sent to cockpit with model `gpt-5.6-sol`
- **THEN** the provider SHALL return a successful response
- **AND** the verification SHALL not expose credentials or authorization headers

#### Scenario: Cockpit Luna inference

- **WHEN** a direct non-streaming inference request is sent to cockpit with model `gpt-5.6-luna`
- **THEN** the provider SHALL return a successful response
- **AND** the verification SHALL not expose credentials or authorization headers

### Requirement: Default-2 MoA role-switch preset

The Hermes MoA configuration SHALL provide an enabled `default-2` preset that switches the shopapikey and phanmemvip roles relative to the existing `default` preset while retaining the cockpit Sol advisor and the established default-route tuning. The `default-2` preset SHALL use `shopapikey:fable-5` as an enabled reference at `high`, `cockpit:gpt-5.6-sol` as an enabled reference at `high`, and `phanmemvip:gpt-5.6-sol` as its aggregator at `xhigh`.

#### Scenario: Default-2 preset normalization

- **WHEN** Hermes normalizes the `default-2` preset
- **THEN** the references SHALL be `shopapikey:fable-5` at `high` and `cockpit:gpt-5.6-sol` at `high`
- **AND** the aggregator SHALL be `phanmemvip:gpt-5.6-sol` at `xhigh`
- **AND** `reference_max_tokens` SHALL be `1000`
- **AND** `max_tokens` SHALL be `8192`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.4`
- **AND** `fanout` SHALL be `every_n:3`
- **AND** `degraded_reference_policy` SHALL be `loud`
- **AND** the preset SHALL be `enabled: true`

#### Scenario: Default-2 is additive

- **WHEN** the `default-2` preset is added
- **THEN** `model.provider` SHALL remain `moa`
- **AND** `model.default` SHALL remain `default`
- **AND** the existing `default`, `deep`, and `fast` presets SHALL retain their prior normalized values
- **AND** the direct fallback order SHALL remain `shopapikey:fable-5`, `phanmemvip:gpt-5.6-sol`, then `cockpit:gpt-5.6-luna`

#### Scenario: Default-2 selection

- **WHEN** a fresh Hermes session selects `/model default-2 --provider moa`
- **THEN** Hermes SHALL resolve the MoA provider and `default-2` preset
- **AND** the `phanmemvip:gpt-5.6-sol` aggregator SHALL own the user-visible response and tool-call continuation

#### Scenario: Default-2 aggregator continuation

- **WHEN** a fresh `moa:default-2` session is instructed to run a harmless terminal command
- **THEN** retained transcript or runtime metadata SHALL show the `phanmemvip:gpt-5.6-sol` aggregator requested the terminal tool
- **AND** the session SHALL continue after the tool result to produce the final answer

#### Scenario: Default-2 rollback

- **WHEN** the `default-2` preset is removed or the pre-change backup is restored
- **THEN** the existing `default`, `deep`, and `fast` presets SHALL remain available with their prior values
- **AND** the primary route SHALL remain `moa:default`
- **AND** structural and runtime MoA validation SHALL pass after rollback

### Requirement: Hermes provider configuration is a separate runtime surface

Hermes provider configuration (`providers.<name>.model`, `providers.<name>.context_length`, and MoA preset slot references) SHALL be governed by this capability and the Hermes runtime, not by the canonical TDT provider schema. The canonical TDT provider schema (transport, protocol, auth_env, cli_provider, base_url, and model-level context_window) SHALL NOT be treated as the authority for Hermes provider fields. Context-window ownership at the Hermes provider level (`providers.<name>.context_length`) is intentional and distinct from the canonical model-level `context_window` behavior field. The two schemas MAY reference the same underlying providers (shopapikey, phanmemvip, cockpit) without one being a projection of the other.

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
