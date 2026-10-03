# Spec Delta

## MODIFIED Requirements

### Requirement: Global settings SHALL provide shopapikey defaults while remaining credential-free

The `~/.claude/settings.json` file SHALL contain the phanmemvip-provider model, base URL, resolution aliases, effort level, and capability declarations as global defaults so that bare `claude` invocations and other compatible applications use the phanmemvip provider without any launcher or `--settings` flag. The selected model SHALL be `codex-x` (the phanmemvip codex-x channel), and the `[1m]` context-window suffix SHALL NOT be applied to `codex-x` because its 1M provider-side capacity is not established. The file MUST NOT contain `ANTHROPIC_AUTH_TOKEN` or any secret values.

#### Scenario: settings.json provides shopapikey defaults

- **WHEN** `~/.claude/settings.json` is loaded
- **THEN** it MUST contain a top-level `model` key set to `codex-x`
- **AND** its `env` block MUST contain `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`
- **AND** its `env` block MUST contain `ANTHROPIC_MODEL=codex-x`
- **AND** its `env` block MUST contain `ANTHROPIC_DEFAULT_FABLE_MODEL=codex-x`
- **AND** its `env` block MUST contain `CLAUDE_CODE_EFFORT_LEVEL=xhigh`
- **AND** no model selector in the file SHALL carry the `[1m]` suffix

#### Scenario: settings.json contains no auth tokens

- **WHEN** `~/.claude/settings.json` is inspected
- **THEN** it MUST NOT contain `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET` in its `env` block
