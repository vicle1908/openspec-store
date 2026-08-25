# hermes-display-configuration

## Purpose (updated)

Defines display settings for the Hermes Agent default profile, maximizing operational visibility across all surfaces. Reasoning blocks are shown to provide transparency into model thinking. Full detail is enabled across all platforms. Per-platform overrides allow targeted reduction where needed.

## MODIFIED Requirements

### Requirement: Reasoning-visible display profile

The Hermes display configuration SHALL enable reasoning visibility while using maximum-detail operational settings. Specifically: `show_reasoning` to `true`, `reasoning_full` to `true`, `interim_assistant_messages` to `true`, `show_commentary` to `true`, `turn_summary` to `true`, `spinner_token_flow` to `true`, and `tool_preview_length` to `0` (unlimited).

#### Scenario: Reasoning-enabled display values after mutation

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **THEN** `display.show_reasoning` SHALL be `true`
- **AND** `display.reasoning_full` SHALL be `true`
- **AND** `display.interim_assistant_messages` SHALL be `true`
- **AND** `display.show_commentary` SHALL be `true`
- **AND** `display.turn_summary` SHALL be `true`
- **AND** `display.spinner_token_flow` SHALL be `true`
- **AND** `display.tool_preview_length` SHALL be `0`

#### Scenario: Supported key names

- **WHEN** `hermes config set` is used to set documented display values
- **THEN** all documented setting names SHALL be accepted by the Hermes CLI
- **AND** `hermes config check` SHALL report no errors

#### Scenario: Gateway-only keys recognized at runtime

- **WHEN** `display.tool_progress_grouping` is set to `separate` in raw YAML
- **THEN** the gateway runtime SHALL recognize and apply the value

### Requirement: Operational visibility preservation

The following operational display settings SHALL remain enabled at their current values: `streaming`, `tool_progress`, `tool_progress_grouping`, `show_cost`, `timestamps`, `runtime_footer.enabled`, `background_process_notifications`, `long_running_notifications`, `live_status`, and `busy_ack_detail`.

#### Scenario: Preserved visibility settings

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **THEN** `display.streaming` SHALL be `true`
- **AND** `display.tool_progress` SHALL be `verbose`
- **AND** `display.tool_progress_grouping` SHALL be `separate`
- **AND** `display.show_cost` SHALL be `true`
- **AND** `display.timestamps` SHALL be `true`
- **AND** `display.runtime_footer.enabled` SHALL be `true`
- **AND** `display.runtime_footer.fields` SHALL contain `model`, `context_pct`, `cwd`, and `latency`
- **AND** `display.background_process_notifications` SHALL be `all`
- **AND** `display.long_running_notifications` SHALL be `true`
- **AND** `display.live_status` SHALL be `full`
- **AND** `display.busy_ack_detail` SHALL be `true`

### Requirement: Unsupported key exclusion

The `agent.verbose` key SHALL NOT exist in the `agent` section.

#### Scenario: agent.verbose absent

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **THEN** `agent.verbose` SHALL NOT be present as a key under `agent`

#### Scenario: display.busy_ack_detail absent

- **WHEN** `~/.hermes/config.yaml` is parsed with `yaml.safe_load`
- **AND** `display.busy_ack_detail` is not present as a key under `display`
- **THEN** the built-in default SHALL apply
- **AND** the config SHALL remain valid

#### Scenario: display.busy_ack_detail recognized

- **WHEN** `~/.hermes/config.yaml` contains `display.busy_ack_detail: true`
- **THEN** the raw YAML value SHALL be accepted
- **AND** `hermes config get display.busy_ack_detail` SHALL resolve to `true`
- **AND** `hermes config check` SHALL report no errors
- **AND** a `hermes config set` unknown-key notice is expected behavior, not a config error

### Requirement: Reasoning display is presentation-only

Enabling `show_reasoning` and `reasoning_full` SHALL display visible reasoning/thinking blocks in the output when the provider exposes reasoning content. This SHALL NOT alter the configured `reasoning_effort`, the messages array, tool schemas, reduce provider token usage, or change provider routing. The `reasoning_style` setting (`code`) controls the visual format of reasoning blocks but does not affect model behavior.

#### Scenario: Reasoning display does not change model behavior

- **WHEN** `display.show_reasoning` is `true` and `display.reasoning_full` is `true`
- **THEN** the API request messages array SHALL be identical to the case where both are `false`
- **AND** `agent.reasoning_effort` SHALL remain at its configured value
- **AND** tool schemas SHALL be unchanged
- **AND** provider routing SHALL be unchanged

#### Scenario: Reasoning blocks appear in output

- **WHEN** a model turn completes with reasoning content exposed by the provider
- **THEN** reasoning blocks SHALL be visible in the conversation output
- **AND** the `reasoning_style` format SHALL be applied to rendering

### Requirement: Per-platform reasoning override

The top-level `display.show_reasoning: true` setting SHALL apply to Telegram, CLI, Discord, and other platforms. Per-platform overrides MAY be used to reduce verbosity on specific channels.

#### Scenario: Slack reasoning stays suppressed

- **WHEN** `display.show_reasoning` is `true` and `display.platforms.slack.show_reasoning` is explicitly `false`
- **THEN** reasoning blocks SHALL NOT appear in Slack messages

#### Scenario: Slack reasoning is enabled in full-detail profile

- **WHEN** `display.show_reasoning` is `true` and `display.platforms.slack.show_reasoning` is explicitly `true`
- **THEN** reasoning blocks SHALL appear in Slack messages

#### Scenario: Telegram reasoning is enabled

- **WHEN** `display.show_reasoning` is `true` and a Telegram session is active
- **THEN** reasoning blocks SHALL appear in Telegram responses

### Requirement: Validation and rollback

Before any display configuration mutation, a pre-change backup SHALL be created. The operator SHALL verify the mutation with `hermes config check` and `hermes config get display` after application.

#### Scenario: Pre-change backup exists

- **WHEN** a display configuration change is prepared
- **THEN** a pre-change snapshot SHALL be created
- **AND** the snapshot path SHALL be recorded for rollback

#### Scenario: Post-mutation verification

- **WHEN** the display configuration is mutated
- **THEN** `hermes config check` SHALL pass with no errors
- **AND** `hermes config get display.show_reasoning` SHALL return `true`
- **AND** `hermes config get display.reasoning_full` SHALL return `true`

## ADDED Requirements

### Requirement: Gateway streaming is distinct from CLI streaming

Gateway token streaming and CLI terminal streaming SHALL use separate configuration paths. The top-level `streaming.enabled` SHALL control gateway streaming, while `display.streaming` SHALL control CLI streaming. Per-platform overrides MAY be set under `display.platforms.<platform>.streaming`.

#### Scenario: Gateway and CLI streaming configured independently

- **WHEN** `streaming.enabled` is `true` and `display.streaming` is `true`
- **THEN** both gateway and CLI streaming SHALL be enabled
- **AND** changing one SHALL NOT affect the other

### Requirement: Tool-progress modes and preview length

The `tool_progress` setting SHALL support modes: `off`, `new`, `all`, `verbose`, and `log`. The `log` mode SHALL be gateway-only and exclusive — it suppresses visible progress and writes to `$HERMES_HOME/logs/tool_calls.log`. The `tool_preview_length` setting SHALL interpret `0` as unlimited preview length.

#### Scenario: Preview length unlimited

- **WHEN** `display.tool_preview_length` is `0`
- **THEN** tool call previews SHALL show the full command/path/arguments without truncation

#### Scenario: Log mode is exclusive

- **WHEN** `display.tool_progress` is `log`
- **THEN** tool calls SHALL NOT be visible in the conversation
- **AND** tool calls SHALL be appended to `$HERMES_HOME/logs/tool_calls.log`

#### Scenario: Gateway-only log mode

- **WHEN** `display.tool_progress` is `log` in a CLI session
- **THEN** the log mode SHALL NOT apply (CLI uses `verbose`/`all`/`new`/`off`)

### Requirement: Runtime footer fields

The runtime footer SHALL support exactly four fields: `model`, `context_pct`, `cwd`, and `latency`. Unknown field names SHALL be silently ignored. The `latency` field is opt-in and not in the default field set.

#### Scenario: All four footer fields rendered

- **WHEN** `display.runtime_footer.fields` is `[model, context_pct, cwd, latency]`
- **THEN** the footer SHALL render the model name, context occupancy percentage, working directory, and wall-clock duration
- **AND** unavailable fields SHALL be skipped silently

#### Scenario: Unknown footer field ignored

- **WHEN** an unknown field name appears in `display.runtime_footer.fields`
- **THEN** the unknown field SHALL be silently ignored
- **AND** the footer SHALL render successfully with the remaining valid fields

### Requirement: Deprecated tool_progress_overrides exclusion

The `display.tool_progress_overrides` key SHALL NOT be used. It is deprecated and migrated to `display.platforms` on first load. New configurations SHALL use `display.platforms.<platform>.tool_progress` instead.

#### Scenario: Deprecated key absent

- **WHEN** `~/.hermes/config.yaml` is parsed
- **THEN** `display.tool_progress_overrides` SHALL NOT be present as a key
- **AND** all per-platform tool progress SHALL be configured under `display.platforms`

### Requirement: Explicit platform verbosity and provenance

Telegram, Discord, and Slack SHALL have explicit per-platform overrides that shadow their built-in defaults. Feishu, Matrix, and WhatsApp inherit global `display.*` values; their built-in `_TIER_MEDIUM` defaults (tool_progress: new) are shadowed by the global verbose inheritance. The operator MAY add explicit per-platform overrides for Feishu, Matrix, or WhatsApp if targeted verbosity is desired.

#### Scenario: Explicit overrides for Telegram/Discord/Slack

- **WHEN** `display.platforms.telegram.tool_progress` is `verbose`
- **AND** `display.platforms.discord.tool_progress` is `verbose`
- **AND** `display.platforms.slack.tool_progress` is `verbose`
- **THEN** all three platforms SHALL render verbose progress via their explicit overrides

#### Scenario: Global inheritance for Feishu/Matrix/WhatsApp

- **WHEN** no per-platform `tool_progress` override is set for Feishu, Matrix, or WhatsApp
- **THEN** the global `display.tool_progress: verbose` SHALL apply
- **AND** the built-in platform default (`new`) SHALL be shadowed

### Requirement: reasoning_full is source-recognized

For the validated Hermes Agent v0.20.5 installation, `display.reasoning_full` SHALL be treated as a source-recognized setting and SHALL resolve through `hermes config get display`. This key is absent from the current official documentation.

#### Scenario: reasoning_full resolves correctly

- **WHEN** `display.reasoning_full` is `true` in raw YAML
- **THEN** `hermes config get display.reasoning_full` SHALL return `true`
- **AND** the CLI SHALL apply the value at runtime
