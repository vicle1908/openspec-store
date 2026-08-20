# hermes-display-configuration Specification

## Purpose

Defines display settings for the Hermes Agent default profile, balancing operational visibility with output clarity. Reasoning blocks are shown to provide transparency into model thinking. Per-platform overrides keep shared channels (Slack) clean while enabling full reasoning on Telegram and CLI.

## Requirements

### Requirement: Reasoning-visible display profile

The Hermes display configuration SHALL enable reasoning visibility while retaining the existing low-noise operational settings. Specifically: `show_reasoning` to `true`, `reasoning_full` to `true`, `reasoning_style` to `code`, `interim_assistant_messages` to `false`, `busy_steer_ack_enabled` to `false`, `turn_summary` to `false`, and `tool_preview_length` to `60`.

#### Scenario: Reasoning-enabled display values after mutation

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **THEN** `display.show_reasoning` SHALL be `true`
- **AND** `display.reasoning_full` SHALL be `true`
- **AND** `display.reasoning_style` SHALL be `code`
- **AND** `display.interim_assistant_messages` SHALL be `false`
- **AND** `display.busy_steer_ack_enabled` SHALL be `false`
- **AND** `display.turn_summary` SHALL be `false`
- **AND** `display.tool_preview_length` SHALL be `60`

#### Scenario: Supported key names

- **WHEN** `hermes config set` is used to set display values
- **THEN** all setting names SHALL be recognized by the Hermes CLI without warnings
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

### Requirement: Reasoning display is presentation-only

Enabling `show_reasoning` and `reasoning_full` SHALL display visible reasoning/thinking blocks in the output. This SHALL NOT lower the configured model `reasoning_effort`, reduce provider token usage, or change the model's actual reasoning depth. The `reasoning_style` setting (`code`) controls the visual format of reasoning blocks but does not affect model behavior.

#### Scenario: Reasoning display does not change model behavior

- **WHEN** `display.show_reasoning` is `true` and `display.reasoning_full` is `true`
- **THEN** `agent.reasoning_effort` SHALL remain at its configured value (`xhigh`)
- **AND** `agent.reasoning_overrides` SHALL remain unchanged
- **AND** the model SHALL produce identical output regardless of display settings

#### Scenario: Reasoning blocks appear in output

- **WHEN** a model turn completes with reasoning content
- **THEN** reasoning blocks SHALL be visible in the conversation output
- **AND** the `reasoning_style` format SHALL be applied to rendering

### Requirement: Per-platform reasoning override

The top-level `display.show_reasoning: true` setting SHALL apply to Telegram, CLI, Discord, and other platforms. The `display.platforms.slack.show_reasoning` override SHALL remain `false` because shared Slack channels are too noisy for reasoning blocks.

#### Scenario: Slack reasoning stays suppressed

- **WHEN** `display.show_reasoning` is `true` and `display.platforms.slack.show_reasoning` is inspected
- **THEN** the Slack override SHALL be `false`
- **AND** reasoning blocks SHALL NOT appear in Slack messages

#### Scenario: Telegram reasoning is enabled

- **WHEN** `display.show_reasoning` is `true` and a Telegram session is active
- **THEN** reasoning blocks SHALL appear in Telegram responses

### Requirement: Validation and rollback

Before any display configuration mutation, a pre-change backup SHALL be created. The operator SHALL verify the mutation with `hermes config check` and `hermes config get display` after application.

#### Scenario: Pre-change backup exists

- **WHEN** a display configuration change is prepared
- **THEN** a pre-change snapshot SHALL be created via `hermes backup --quick`
- **AND** the snapshot ID SHALL be recorded for rollback

#### Scenario: Post-mutation verification

- **WHEN** the display configuration is mutated
- **THEN** `hermes config check` SHALL pass with no errors
- **AND** `hermes config get display.show_reasoning` SHALL return `true`
- **AND** `hermes config get display.reasoning_full` SHALL return `true`
