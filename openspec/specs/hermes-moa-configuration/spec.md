# hermes-moa-configuration Specification

## Purpose
Define the validated local Hermes Mixture of Agents model topology, provider-level context ownership, independent failover, operational documentation, and evidence required to keep configuration, behavior, and recovery aligned.
## Requirements
### Requirement: MoA default route

The Hermes default profile SHALL select the Mixture of Agents virtual provider with `model.provider: moa` and `model.default: default`, and the `moa.default_preset` SHALL be `default`.

#### Scenario: Fresh default-profile session

- **WHEN** Hermes starts a fresh session without a session-scoped model override
- **THEN** the runtime SHALL resolve provider `moa` and preset `default`
- **AND** the MoA facade SHALL own the main agent call path

#### Scenario: Config-level active preset is empty

- **WHEN** `moa.active_preset` is empty or absent while `model.provider` is `moa` and `model.default` is `default`
- **THEN** the empty active-preset marker SHALL NOT be interpreted as disabling the selected MoA default route
- **AND** operator documentation SHALL distinguish `moa.active_preset` from primary model selection

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

### Requirement: Context-window ownership

The one-million-token context declaration SHALL be owned by provider and model configuration, and MoA reference or aggregator slots SHALL NOT duplicate `context_length`.

#### Scenario: Provider context validation

- **WHEN** configuration validation inspects `cockpit`, `shopapikey`, and `giaoduc`
- **THEN** each provider SHALL declare `context_length: 1000000`
- **AND** each MoA-used model SHALL resolve a one-million-token context declaration from its provider/model configuration

#### Scenario: MoA slot validation

- **WHEN** configuration validation traverses every reference and aggregator slot
- **THEN** no slot SHALL contain a `context_length` field

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

### Requirement: Fallback independence

The fallback chain SHALL contain routes that are distinct from the selected primary `moa:default` deployment and SHALL preserve the configured direct-provider order.

#### Scenario: Primary MoA failure

- **WHEN** `moa:default` fails after its retry policy
- **THEN** Hermes SHALL attempt `shopapikey:fable-5`, then `giaoduc:Advance`, then `cockpit:gpt-5.6-luna`, subject to local availability and failure-scope skip rules

#### Scenario: Duplicate primary candidate

- **WHEN** a fallback entry resolves to the same provider, model, and effective virtual deployment as the failed `moa:default` primary
- **THEN** the configuration SHALL exclude that redundant entry
- **AND** validation SHALL confirm the chain begins with an independent direct provider

### Requirement: Operational documentation and evidence

The maintained runbook SHALL document architecture, preset intent, selection, inspection, health checks, cost/latency, privacy, partial failures, context ownership, rollback, and sanitized validation evidence.

#### Scenario: Operator validates MoA

- **WHEN** an operator follows the runbook
- **THEN** they SHALL be able to verify YAML shape, normalized configuration, all three direct providers, and a fresh MoA tool-call continuation without exposing credentials

#### Scenario: Real tool-call smoke test

- **WHEN** a fresh `moa:default` session is instructed to use a harmless terminal tool
- **THEN** retained transcript or runtime metadata SHALL show the MoA aggregator requested the tool
- **AND** the session SHALL continue after the tool result to produce the final answer

#### Scenario: Rollback

- **WHEN** the reconciled configuration must be rolled back
- **THEN** the operator SHALL restore only a local sanitized backup or the explicitly removed fields/entry
- **AND** SHALL rerun config and MoA validation before declaring recovery complete

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

### Requirement: Default-2 MoA role-switch preset

The Hermes MoA configuration SHALL provide an enabled `default-2` preset that switches the shopapikey and giaoduc roles relative to the existing `default` preset while retaining the cockpit Sol advisor and the established default-route tuning. The `default-2` preset SHALL use `shopapikey:fable-5` as an enabled reference at `high`, `cockpit:gpt-5.6-sol` as an enabled reference at `high`, and `giaoduc:Advance` as its aggregator at `xhigh`.

#### Scenario: Default-2 preset normalization

- **WHEN** Hermes normalizes the `default-2` preset
- **THEN** the references SHALL be `shopapikey:fable-5` at `high` and `cockpit:gpt-5.6-sol` at `high`
- **AND** the aggregator SHALL be `giaoduc:Advance` at `xhigh`
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
- **AND** the direct fallback order SHALL remain `shopapikey:fable-5`, `giaoduc:Advance`, then `cockpit:gpt-5.6-luna`

#### Scenario: Default-2 selection

- **WHEN** a fresh Hermes session selects `/model default-2 --provider moa`
- **THEN** Hermes SHALL resolve the MoA provider and `default-2` preset
- **AND** the `giaoduc:Advance` aggregator SHALL own the user-visible response and tool-call continuation

#### Scenario: Default-2 aggregator continuation

- **WHEN** a fresh `moa:default-2` session is instructed to run a harmless terminal command
- **THEN** retained transcript or runtime metadata SHALL show the `giaoduc:Advance` aggregator requested the terminal tool
- **AND** the session SHALL continue after the tool result to produce the final answer

#### Scenario: Default-2 rollback

- **WHEN** the `default-2` preset is removed or the pre-change backup is restored
- **THEN** the existing `default`, `deep`, and `fast` presets SHALL remain available with their prior values
- **AND** the primary route SHALL remain `moa:default`
- **AND** structural and runtime MoA validation SHALL pass after rollback
