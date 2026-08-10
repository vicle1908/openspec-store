## MODIFIED Requirements

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
