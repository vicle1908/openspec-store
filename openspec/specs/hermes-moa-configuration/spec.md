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

The `default` preset SHALL use exactly two enabled references, `shopapikey:fable-5` at `high` and `cockpit:gpt-5.6-luna` at `max`, and SHALL use `shopapikey:fable-5` at `max` as its aggregator, with the validated token, temperature, cadence, privacy, and enablement settings.

#### Scenario: Default preset normalization

- **WHEN** Hermes normalizes the `default` preset
- **THEN** the references SHALL be `shopapikey:fable-5` at `high` and `cockpit:gpt-5.6-luna` at `max`
- **AND** the aggregator SHALL be `shopapikey:fable-5` at `max`
- **AND** `reference_max_tokens` SHALL be `600`
- **AND** `max_tokens` SHALL be `4096`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.4`
- **AND** `fanout` SHALL be `user_turn`

### Requirement: Deep MoA preset

The `deep` preset SHALL provide the maximum-quality configured route with three references, an Advance aggregator, and periodically refreshed advisor context.

#### Scenario: Deep preset normalization

- **WHEN** Hermes normalizes the `deep` preset
- **THEN** the references SHALL be `shopapikey:fable-5` at `xhigh`, `cockpit:gpt-5.6-luna` at `max`, and `giaoduc:Advance` at `high`
- **AND** the aggregator SHALL be `giaoduc:Advance` at `max`
- **AND** `reference_max_tokens` SHALL be `800`
- **AND** `max_tokens` SHALL be `8192`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.3`
- **AND** `fanout` SHALL be `every_n:3`

### Requirement: Fast MoA preset

The `fast` preset SHALL minimize MoA latency while retaining one independent Luna advisor at maximum configured effort and a tool-capable aggregator.

#### Scenario: Fast preset normalization

- **WHEN** Hermes normalizes the `fast` preset
- **THEN** `cockpit:gpt-5.6-luna` SHALL be the enabled reference at `max`
- **AND** `shopapikey:fable-5` SHALL be the aggregator at `high`
- **AND** `reference_max_tokens` SHALL be `300`
- **AND** `max_tokens` SHALL be `4096`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.4`
- **AND** `fanout` SHALL be `user_turn`

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

Hermes SHALL apply `moa.privacy_filter: display` and SHALL preserve the aggregator path when one reference model fails.

#### Scenario: User-visible reference output

- **WHEN** advisor output is shown or persisted as a user-visible MoA trace
- **THEN** emails, formatted phone numbers, and centrally recognized credential shapes SHALL be redacted according to display-mode privacy behavior
- **AND** raw advisor text MAY remain available to the aggregator for answer quality

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

### Requirement: Active cockpit Luna topology

The active Hermes MoA configuration and cockpit provider default SHALL use model `gpt-5.6-luna` rather than `gpt-5.6-sol` in every cockpit-backed MoA slot, and every such cockpit slot SHALL use `reasoning_effort: max`.

#### Scenario: No stale cockpit model remains

- **WHEN** the live MoA configuration and maintained documentation are scanned
- **THEN** `providers.cockpit.model` SHALL be `gpt-5.6-luna`
- **AND** every cockpit-backed MoA reference or aggregator SHALL name `gpt-5.6-luna`
- **AND** every cockpit-backed MoA reference or aggregator SHALL use `reasoning_effort: max`
- **AND** no active configuration, canonical specification, or maintained runbook SHALL name `gpt-5.6-sol` as a MoA slot

#### Scenario: Cockpit Luna inference

- **WHEN** a direct non-streaming inference request is sent to cockpit with model `gpt-5.6-luna`
- **THEN** the provider SHALL return a successful response
- **AND** the verification SHALL not expose credentials or authorization headers
