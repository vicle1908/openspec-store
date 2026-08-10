## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Default MoA preset

The `default` preset SHALL use exactly two enabled references, `shopapikey:fable-5` at `high` and `cockpit:gpt-5.6-luna` at `max`, and SHALL use `cockpit:gpt-5.6-luna` at `max` as its aggregator, with the validated token, temperature, cadence, privacy, and enablement settings.

#### Scenario: Default preset normalization

- **WHEN** Hermes normalizes the `default` preset
- **THEN** the references SHALL be `shopapikey:fable-5` at `high` and `cockpit:gpt-5.6-luna` at `max`
- **AND** the aggregator SHALL be `cockpit:gpt-5.6-luna` at `max`
- **AND** `reference_max_tokens` SHALL be `600`
- **AND** `max_tokens` SHALL be `4096`
- **AND** reference and aggregator temperatures SHALL be `0.6` and `0.4`
- **AND** `fanout` SHALL be `user_turn`

### Requirement: Deep MoA preset

The `deep` preset SHALL provide the maximum-quality configured route with three references, a Luna aggregator, and periodically refreshed advisor context.

#### Scenario: Deep preset normalization

- **WHEN** Hermes normalizes the `deep` preset
- **THEN** the references SHALL be `shopapikey:fable-5` at `xhigh`, `cockpit:gpt-5.6-luna` at `max`, and `giaoduc:Advance` at `high`
- **AND** the aggregator SHALL be `cockpit:gpt-5.6-luna` at `max`
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
