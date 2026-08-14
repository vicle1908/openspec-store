# hermes-display-configuration Specification

## Purpose
TBD - created by archiving change align-hermes-balanced-display-profile. Update Purpose after archive.

## Requirements

### Requirement: Balanced low-noise display profile

The Hermes display configuration SHALL set six supported display settings to their balanced low-noise values: `show_reasoning` to `false`, `interim_assistant_messages` to `false`, `busy_steer_ack_enabled` to `false`, `turn_summary` to `false`, `tool_preview_length` to `60`, and `platforms.slack.show_reasoning` to `false`.

#### Scenario: Balanced display values after mutation

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **THEN** `display.show_reasoning` SHALL be `false`
- **AND** `display.interim_assistant_messages` SHALL be `false`
- **AND** `display.busy_steer_ack_enabled` SHALL be `false`
- **AND** `display.turn_summary` SHALL be `false`
- **AND** `display.tool_preview_length` SHALL be `60`
- **AND** `display.platforms.slack.show_reasoning` SHALL be `false`

#### Scenario: Supported key names

- **WHEN** `hermes config set` is used to set display values
- **THEN** all six setting names SHALL be recognized by the Hermes CLI without warnings
- **AND** `hermes config check` SHALL report no errors

### Requirement: Operational visibility preservation

The following operational display settings SHALL remain enabled at their current values: `streaming`, `tool_progress`, `show_cost`, `timestamps`, `runtime_footer.enabled`, `background_process_notifications`, and `long_running_notifications`.

#### Scenario: Preserved visibility settings

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **THEN** `display.streaming` SHALL be `true`
- **AND** `display.tool_progress` SHALL be `all`
- **AND** `display.show_cost` SHALL be `true`
- **AND** `display.timestamps` SHALL be `true`
- **AND** `display.runtime_footer.enabled` SHALL be `true`
- **AND** `display.background_process_notifications` SHALL be `all`
- **AND** `display.long_running_notifications` SHALL be `true`

### Requirement: Unsupported key exclusion

The `agent.verbose` key SHALL NOT exist in the `agent` section. The `display.busy_ack_detail` key SHALL NOT exist in the `display` section.

#### Scenario: agent.verbose absent

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **THEN** `agent.verbose` SHALL NOT be present as a key under `agent`

#### Scenario: display.busy_ack_detail absent

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **THEN** `display.busy_ack_detail` SHALL NOT be present as a key under `display`

### Requirement: Display-only suppression

Disabling `show_reasoning` SHALL suppress visible reasoning/thinking blocks only. It SHALL NOT lower the configured model `reasoning_effort`, reduce provider token usage, or change the model's actual reasoning depth.

#### Scenario: Reasoning suppression is presentation-only

- **WHEN** `display.show_reasoning` is `false`
- **THEN** `agent.reasoning_effort` SHALL remain at its configured value (`xhigh`)
- **AND** `agent.reasoning_overrides` SHALL remain unchanged

### Requirement: Per-platform consistency

When the top-level `display.show_reasoning` is `false`, the `display.platforms.slack.show_reasoning` override SHALL also be `false`.

#### Scenario: Slack reasoning aligned with top-level

- **WHEN** `display.show_reasoning` is `false` and `display.platforms.slack.show_reasoning` is inspected
- **THEN** the Slack override SHALL be `false`

### Requirement: Validation and rollback

A rollback backup SHALL exist under `~/.hermes/backups/` and its SHA-256 SHALL match. Rollback restores this backup atomically and verifies with `hermes config check` and `hermes config get display`.

#### Scenario: Backup integrity

- **WHEN** the pre-change backup file is inspected
- **THEN** its path SHALL contain `config-before-balanced-display`
- **AND** its SHA-256 SHALL match `758e26008eb94f05682f932fa36074b0a571899b337aee63f05e5859fc76d28c`

#### Scenario: Rollback path

- **WHEN** the operator restores the backup and runs `hermes config check`
- **THEN** the check SHALL pass with no errors
- **AND** `hermes config get display` SHALL show the restored values
