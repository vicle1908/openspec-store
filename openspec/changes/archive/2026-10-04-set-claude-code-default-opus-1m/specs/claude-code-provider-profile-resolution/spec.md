# Spec Delta

## MODIFIED Requirements

### Requirement: Global settings SHALL provide shopapikey defaults while remaining credential-free

The `~/.claude/settings.json` file SHALL contain the Claude model, base URL, resolution aliases, effort level, and capability declarations as global defaults so that bare `claude` invocations and other compatible applications use the phanmemvip provider without any launcher or `--settings` flag. The selected model SHALL be `Claude-Fable[1m]` (the Claude model with the 1M context-window selector). The `[1m]` suffix SHALL be applied to the Claude Code default selector; Claude Code strips it before transmission, so it is a selector-side stance and MUST NOT be interpreted as proof of provider-side 1M capacity. The file MUST NOT contain `ANTHROPIC_AUTH_TOKEN` or any secret values.

#### Scenario: settings.json provides shopapikey defaults

- **WHEN** `~/.claude/settings.json` is loaded
- **THEN** it MUST contain a top-level `model` key set to `Claude-Fable[1m]`
- **AND** its `env` block MUST contain `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`
- **AND** its `env` block MUST contain `ANTHROPIC_MODEL=Claude-Fable[1m]`
- **AND** its `env` block MUST contain `ANTHROPIC_DEFAULT_FABLE_MODEL=Claude-Fable[1m]`
- **AND** its `env` block MUST contain `CLAUDE_CODE_EFFORT_LEVEL=xhigh`
- **AND** the default model selector MUST carry the `[1m]` suffix

#### Scenario: settings.json contains no auth tokens

- **WHEN** `~/.claude/settings.json` is inspected
- **THEN** it MUST NOT contain `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET` in its `env` block
