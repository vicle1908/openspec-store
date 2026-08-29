## MODIFIED Requirements

### Requirement: Active provider launchers SHALL use the documented model alias, `[1m]` suffix, and effort contract

Each provider launcher MUST use lowercase `[1m]` on its model selector to request the 1 million token context window, declare the capability needed for its requested effort, and set `CLAUDE_CODE_EFFORT_LEVEL` in its subshell. The shopapikey launcher MUST use the canonical `Claude-Fable[1m]` selector pinned with `ANTHROPIC_DEFAULT_FABLE_MODEL=Claude-Fable[1m]`; cockpit MUST use a custom model option with `[1m]` for `gpt-5.6-luna[1m]`. The Claude Code launcher set SHALL be exactly shopapikey and cockpit; no giaoduc launcher SHALL exist.

Claude Code MUST strip the `[1m]` suffix before transmitting the model ID to the provider. The wire model ID MUST be the bare base name without the `[1m]` suffix. Selector acceptance by Claude Code MUST NOT be interpreted as proof of provider-side 1M context window capacity.

#### Scenario: Shopapikey resolves the Fable alias with 1M context

- **WHEN** `shopapikey` launches Claude Code with `ANTHROPIC_MODEL=Claude-Fable[1m]` and `ANTHROPIC_DEFAULT_FABLE_MODEL=Claude-Fable[1m]`
- **THEN** Claude Code MUST send `model=Claude-Fable` (suffix stripped) and `output_config.effort=xhigh`

#### Scenario: Cockpit selects its custom model with 1M context

- **WHEN** `cockpit` launches Claude Code with `ANTHROPIC_MODEL=gpt-5.6-luna[1m]` and `ANTHROPIC_CUSTOM_MODEL_OPTION=gpt-5.6-luna[1m]`
- **THEN** Claude Code MUST send `model=gpt-5.6-luna` (suffix stripped) and `output_config.effort=max`

#### Scenario: Giaoduc launcher removed

- **WHEN** `~/.zshrc` is sourced in a fresh shell
- **THEN** no `giaoduc` launcher function SHALL be defined
- **AND** no `cline_giaoduc` launcher function SHALL be defined
- **AND** the Anthropic-side Claude route SHALL remain shopapikey only until a phanmemvip launcher is introduced by a later change
