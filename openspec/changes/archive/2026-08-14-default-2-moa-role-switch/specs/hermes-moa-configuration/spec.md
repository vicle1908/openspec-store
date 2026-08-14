# Spec delta for hermes-moa-configuration

This delta is applied to
`openspec/specs/hermes-moa-configuration/spec.md`
when the `default-2-moa-role-switch` change is archived.

## ADDED Requirements

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
