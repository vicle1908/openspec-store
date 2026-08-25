# hermes-moa-configuration Delta

## MODIFIED Requirements

### Requirement: Default MoA preset

The `default` preset SHALL use exactly two enabled references, `phanmemvip:gpt-5.6-sol` at `high` and `cockpit:gpt-5.6-sol` at `high`, and SHALL use `shopapikey:Claude-Fable` at `xhigh` as its aggregator, with the validated token, temperature, cadence, and enablement settings.

#### Scenario: Default preset normalization

- **WHEN** Hermes normalizes the `default` preset
- **THEN** the references SHALL be `phanmemvip:gpt-5.6-sol` at `high` and `cockpit:gpt-5.6-sol` at `high`
- **AND** the aggregator SHALL be `shopapikey:Claude-Fable` at `xhigh`
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
- **THEN** the references SHALL be `shopapikey:Claude-Fable` at `high`, `cockpit:gpt-5.6-sol` at `high`, and `phanmemvip:gpt-5.6-sol` at `high`
- **AND** the aggregator SHALL be `phanmemvip:gpt-5.6-sol` at `max`
- **AND** `reference_max_tokens` SHALL be `800`
- **AND** `max_tokens` SHALL be `8192`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.3`
- **AND** `fanout` SHALL be `per_iteration`
- **AND** `degraded_reference_policy` SHALL be `loud`
- **AND** the preset SHALL be `enabled: true`

### Requirement: Fast MoA preset

The `fast` preset SHALL minimize MoA latency while retaining one independent reasoning advisor at high configured effort and a tool-capable aggregator.

#### Scenario: Fast preset normalization

- **WHEN** Hermes normalizes the `fast` preset
- **THEN** `cockpit:gpt-5.6-sol` SHALL be the enabled reference at `high`
- **AND** `shopapikey:Claude-Fable` SHALL be the aggregator at `high`
- **AND** `reference_max_tokens` SHALL be `300`
- **AND** `max_tokens` SHALL be `4096`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.4`
- **AND** `fanout` SHALL be `user_turn`
- **AND** `degraded_reference_policy` SHALL be `loud`
- **AND** the preset SHALL be `enabled: true`

### Requirement: Fallback independence

The fallback chain SHALL contain routes that are distinct from the selected primary `moa:default` deployment and SHALL preserve the configured direct-provider order.

#### Scenario: Primary MoA failure

- **WHEN** `moa:default` fails after its retry policy
- **THEN** Hermes SHALL attempt `shopapikey:Claude-Fable`, then `phanmemvip:gpt-5.6-sol`, then `cockpit:gpt-5.6-luna`, subject to local availability and failure-scope skip rules

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
- **AND** the default aggregator SHALL be `shopapikey:Claude-Fable`
- **AND** the deep aggregator SHALL be `phanmemvip:gpt-5.6-sol`
- **AND** the fast aggregator SHALL be `shopapikey:Claude-Fable`

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

The Hermes MoA configuration SHALL provide an enabled `default-2` preset that switches the shopapikey and phanmemvip roles relative to the existing `default` preset while retaining the cockpit Sol advisor and the established default-route tuning. The `default-2` preset SHALL use `shopapikey:Claude-Fable` as an enabled reference at `high`, `cockpit:gpt-5.6-sol` as an enabled reference at `high`, and `phanmemvip:gpt-5.6-sol` as its aggregator at `xhigh`.

#### Scenario: Default-2 preset normalization

- **WHEN** Hermes normalizes the `default-2` preset
- **THEN** the references SHALL be `shopapikey:Claude-Fable` at `high` and `cockpit:gpt-5.6-sol` at `high`
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
- **AND** the direct fallback order SHALL remain `shopapikey:Claude-Fable`, `phanmemvip:gpt-5.6-sol`, then `cockpit:gpt-5.6-luna`

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
