## MODIFIED Requirements

### Requirement: Active provider launchers SHALL use the documented model alias, `[1m]` suffix, and effort contract

Each provider launcher MUST declare the capability needed for its requested effort and set `CLAUDE_CODE_EFFORT_LEVEL` in its subshell. The shopapikey launcher MUST use the canonical `Claude-Fable` selector pinned with `ANTHROPIC_DEFAULT_FABLE_MODEL=Claude-Fable`, with `env.ANTHROPIC_DEFAULT_OPUS_MODEL` carrying `opus`; cockpit MUST use a custom model option with `[1m]` for `gpt-5.6-luna[1m]`. The Claude Code launcher set SHALL include shopapikey, cockpit, and omniroute; no giaoduc launcher SHALL exist.

The `[1m]` context-window suffix SHALL be applied only where the provider is reached through Claude Code's own model picker, and SHALL NOT be appended to a phanmemvip model alias that the client catalog does not describe. Claude Code MUST strip any `[1m]` suffix before transmitting the model ID to the provider. The wire model ID MUST be the bare base name without the `[1m]` suffix. Selector acceptance by Claude Code MUST NOT be interpreted as proof of provider-side 1M context window capacity.

#### Scenario: Shopapikey resolves the Fable alias with 1M context

- **WHEN** `shopapikey` launches Claude Code with `ANTHROPIC_MODEL=Claude-Fable` and `ANTHROPIC_DEFAULT_FABLE_MODEL=Claude-Fable`
- **THEN** Claude Code MUST send `model=Claude-Fable` and `output_config.effort=xhigh`

#### Scenario: Shopapikey resolves the Fable alias without a suffix

- **WHEN** `shopapikey` launches Claude Code with `ANTHROPIC_MODEL=Claude-Fable` and `ANTHROPIC_DEFAULT_FABLE_MODEL=Claude-Fable`
- **THEN** Claude Code MUST send `model=Claude-Fable` and `output_config.effort=xhigh`

#### Scenario: The OPUS-named alias stays independently selectable

- **WHEN** `shopapikey` launches Claude Code
- **THEN** `env.ANTHROPIC_DEFAULT_OPUS_MODEL` MUST be `opus`
- **AND** requesting the opus alias MUST NOT resolve to the same identifier as the fable alias

#### Scenario: Cockpit selects its custom model with 1M context

- **WHEN** `cockpit` launches Claude Code with `ANTHROPIC_MODEL=gpt-5.6-luna[1m]` and `ANTHROPIC_CUSTOM_MODEL_OPTION=gpt-5.6-luna[1m]`
- **THEN** Claude Code MUST send `model=gpt-5.6-luna` (suffix stripped) and `output_config.effort=max`

#### Scenario: Giaoduc launcher removed

- **WHEN** `~/.zshrc` is sourced in a fresh shell
- **THEN** no `giaoduc` launcher function SHALL be defined

#### Scenario: Omniroute launcher is a covered provider surface

- **WHEN** `~/.zshrc` is sourced in a fresh shell
- **THEN** the `omniroute` launcher function SHALL be defined
- **AND** it MUST select `pm/Claude-Fable` without a `[1m]` suffix
