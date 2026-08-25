# claude-code-provider-routing Delta

## REMOVED Requirements

### Requirement: Provider launchers SHALL use the documented model alias, `[1m]` suffix, and effort contract

**Reason**: The giaoduc launcher is retired along with the provider. The
requirement is rebuilt below for the remaining shopapikey and cockpit
launchers; the giaoduc alias/effort scenario is intentionally dropped.

**Migration**: The rebuilt requirement is re-added in this same delta under
ADDED Requirements. No phanmemvip Claude launcher is introduced in this
change; shopapikey/Claude-Fable remains the Anthropic-side Claude route until
a later change adds one.

## ADDED Requirements

### Requirement: Active provider launchers SHALL use the documented model alias, `[1m]` suffix, and effort contract

Each provider launcher MUST use lowercase `[1m]` on its model selector to request the 1 million token context window, declare the capability needed for its requested effort, and set `CLAUDE_CODE_EFFORT_LEVEL` in its subshell. The shopapikey launcher MUST use the built-in `fable` alias pinned with `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]`; cockpit MUST use a custom model option with `[1m]` for `gpt-5.6-luna[1m]`. The Claude Code launcher set SHALL be exactly shopapikey and cockpit; no giaoduc launcher SHALL exist.

Claude Code MUST strip the `[1m]` suffix before transmitting the model ID to the provider. The wire model ID MUST be the bare base name without the `[1m]` suffix. Selector acceptance by Claude Code MUST NOT be interpreted as proof of provider-side 1M context window capacity.

#### Scenario: Shopapikey resolves the Fable alias with 1M context

- **WHEN** `shopapikey` launches Claude Code with `ANTHROPIC_MODEL=fable[1m]` and `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]`
- **THEN** Claude Code MUST send `model=fable-5` (suffix stripped) and `output_config.effort=xhigh`

#### Scenario: Cockpit selects its custom model with 1M context

- **WHEN** `cockpit` launches Claude Code with `ANTHROPIC_MODEL=gpt-5.6-luna[1m]` and `ANTHROPIC_CUSTOM_MODEL_OPTION=gpt-5.6-luna[1m]`
- **THEN** Claude Code MUST send `model=gpt-5.6-luna` (suffix stripped) and `output_config.effort=max`

#### Scenario: Giaoduc launcher removed

- **WHEN** `~/.zshrc` is sourced in a fresh shell
- **THEN** no `giaoduc` launcher function SHALL be defined
- **AND** no `cline_giaoduc` launcher function SHALL be defined
- **AND** the Anthropic-side Claude route SHALL remain shopapikey only until a phanmemvip launcher is introduced by a later change

## MODIFIED Requirements

### Requirement: Provider acceptance SHALL be evidence-gated

The change MUST NOT be archived as complete until all remaining launchers (shopapikey, cockpit) have fresh live smoke evidence, the cockpit outbound body independently proves the requested effort field, the wire model excludes the `[1m]` suffix, and every migrated consumer selector for `phanmemvip/gpt-5.6-sol` returns a successful response in its own CLI.

#### Scenario: A provider is rate limited

- **WHEN** a provider returns an account or capacity error
- **THEN** its acceptance gate MUST remain pending and the error MUST be recorded as an external blocker rather than a pass

#### Scenario: `[1m]` selector acceptance does not prove provider 1M capacity

- **WHEN** Claude Code accepts a `[1m]` selector and strips it before transmission
- **THEN** the provider-side 1M context window capacity MUST be verified separately before claiming 1M support
