# Spec delta for hermes-moa-configuration

This delta is applied to
`openspec/specs/hermes-moa-configuration/spec.md`
when the `reconcile-hermes-moa-specialist-topology` change is archived.

## MODIFIED Requirements

### Requirement: Default MoA preset

The `default` preset SHALL use exactly two enabled references, `giaoduc:Advance` at `high` and `cockpit:gpt-5.6-sol` at `high`, and SHALL use `shopapikey:fable-5` at `xhigh` as its aggregator, with the validated token, temperature, cadence, and enablement settings.

#### Scenario: Default preset normalization

- **WHEN** Hermes normalizes the `default` preset
- **THEN** the references SHALL be `giaoduc:Advance` at `high` and `cockpit:gpt-5.6-sol` at `high`
- **AND** the aggregator SHALL be `shopapikey:fable-5` at `xhigh`
- **AND** `reference_max_tokens` SHALL be `1000`
- **AND** `max_tokens` SHALL be `8192`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.4`
- **AND** `fanout` SHALL be `every_n:3`
- **AND** `degraded_reference_policy` SHALL be `loud`
- **AND** the preset SHALL be `enabled: true`

### Requirement: Deep MoA preset

The `deep` preset SHALL provide a three-reference route with periodic advisor refresh, a giaoduc aggregator, and three distinct provider perspectives.

#### Scenario: Deep preset normalization

- **WHEN** Hermes normalizes the `deep` preset
- **THEN** the references SHALL be `shopapikey:fable-5` at `high`, `cockpit:gpt-5.6-sol` at `high`, and `giaoduc:Advance` at `high`
- **AND** the aggregator SHALL be `giaoduc:Advance` at `max`
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
- **AND** `shopapikey:fable-5` SHALL be the aggregator at `high`
- **AND** `reference_max_tokens` SHALL be `300`
- **AND** `max_tokens` SHALL be `4096`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.4`
- **AND** `fanout` SHALL be `user_turn`
- **AND** `degraded_reference_policy` SHALL be `loud`
- **AND** the preset SHALL be `enabled: true`

### Requirement: Advisor privacy and failure isolation

Hermes SHALL preserve the aggregator path when one reference model fails. The `moa.privacy_filter` value SHALL be the literal empty string. The degraded-reference policy for every preset SHALL be `loud`. A failed advisor SHALL NOT abort aggregation when another advisor and the aggregator remain available.

#### Scenario: Privacy filter literal value

- **WHEN** configuration validation inspects `moa.privacy_filter`
- **THEN** the value SHALL be the literal empty string

#### Scenario: User-visible reference output

- **WHEN** advisor output is shown or persisted as a user-visible MoA trace
- **THEN** maintained documentation SHALL NOT claim that `display`-mode privacy filtering is configured
- **AND** any redaction guarantee SHALL require separate runtime verification

#### Scenario: One advisor fails

- **WHEN** one reference provider fails while at least one remaining reference and the aggregator remain available
- **THEN** Hermes SHALL report or retain the degraded-reference result
- **AND** SHALL continue to the aggregator rather than aborting the entire turn solely because of that advisor failure

## ADDED Requirements

### Requirement: Specialist MoA topology and independent cockpit routes

The MoA configuration SHALL use `cockpit:gpt-5.6-sol` as the cockpit-backed reference in every preset. No active MoA reference or aggregator SHALL use `cockpit:gpt-5.6-luna`. The direct cockpit provider default and direct fallback entry SHALL use `cockpit:gpt-5.6-luna`. The cockpit provider default model (`providers.cockpit.model`) SHALL be `gpt-5.6-luna` and is independent of the MoA preset slot models. The direct-provider default and the MoA slot selection are orthogonal configuration surfaces; the cockpit model name appearing in `providers.cockpit.model` does not constrain which model names appear in MoA presets, and vice versa.

#### Scenario: MoA presets use Sol as reference

- **WHEN** any MoA preset reference list is inspected
- **THEN** every cockpit-backed MoA reference SHALL name `gpt-5.6-sol` at `high`
- **AND** no MoA reference or aggregator slot SHALL name `gpt-5.6-luna`
- **AND** the default aggregator SHALL be `shopapikey:fable-5`
- **AND** the deep aggregator SHALL be `giaoduc:Advance`
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

### Requirement: MoA root normalization

The `moa` configuration root SHALL contain exactly `default_preset`, `privacy_filter`, and `presets`. No legacy flat-level operational fields (`reference_models`, `aggregator`, `reference_temperature`, `aggregator_temperature`, `degraded_reference_policy`, `max_tokens`, `reference_max_tokens`, `fanout`, `enabled`) SHALL exist directly under `moa`. Preset tuning (temperatures, token limits, fanout cadence, degraded-reference policy, enablement) SHALL be owned exclusively by each preset entry under `moa.presets`.

#### Scenario: Root key validation

- **WHEN** configuration validation inspects the `moa` root
- **THEN** the only permitted top-level keys SHALL be `default_preset`, `privacy_filter`, and `presets`
- **AND** no legacy flat-level operational field SHALL be present

#### Scenario: Preset owns all tuning

- **WHEN** a preset is inspected for its operational parameters
- **THEN** each preset SHALL contain its own `reference_temperature`, `aggregator_temperature`, `degraded_reference_policy`, `max_tokens`, `reference_max_tokens`, `fanout`, and `enabled` fields
- **AND** these values SHALL NOT be inherited from or shadowed by root-level `moa.*` fields

## REMOVED Requirements

### Requirement: Active cockpit Luna topology

**Reason:** The requirement described a topology where every cockpit-backed MoA slot used `gpt-5.6-luna` at `reasoning_effort: max`. That topology has been superseded by the current specialist design where cockpit MoA references use `gpt-5.6-sol` at `high` and the cockpit provider default uses `gpt-5.6-luna` for direct routes. The replacement contract is the `Specialist MoA topology and independent cockpit routes` requirement plus the exact preset topology defined by the modified default, deep, and fast requirements.

**Migration:** Replace the former Luna-in-every-cockpit-slot contract with the exact preset topology defined by the modified default, deep, and fast requirements. Cockpit-backed MoA references use `gpt-5.6-sol` at `high`; the direct cockpit provider default and fallback entry remain `gpt-5.6-luna`.
