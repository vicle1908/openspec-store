# claude-code-provider-profile-resolution Delta

## MODIFIED Requirements

### Requirement: Global settings SHALL provide shopapikey defaults while remaining credential-free

The `~/.claude/settings.json` file SHALL contain the shopapikey model, base URL, resolution aliases, effort level, and capability declarations as global defaults so that bare `claude` invocations and other compatible applications use shopapikey without any launcher or `--settings` flag. The file MUST NOT contain `ANTHROPIC_AUTH_TOKEN` or any secret values.

#### Scenario: settings.json provides shopapikey defaults

- **WHEN** `~/.claude/settings.json` is loaded
- **THEN** it MUST contain a top-level `model` key set to `fable[1m]`
- **AND** its `env` block MUST contain `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`
- **AND** its `env` block MUST contain `ANTHROPIC_MODEL=fable[1m]`
- **AND** its `env` block MUST contain `ANTHROPIC_DEFAULT_FABLE_MODEL=Claude-Fable[1m]`
- **AND** its `env` block MUST contain `CLAUDE_CODE_EFFORT_LEVEL=xhigh`

#### Scenario: settings.json contains no auth tokens

- **WHEN** `~/.claude/settings.json` is inspected
- **THEN** it MUST NOT contain `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET` in its `env` block

### Requirement: Active provider profiles SHALL define model, base URL, and effort

Each provider profile JSON under `~/.claude/profiles/` SHALL contain a top-level `model` field and an `env` block with `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`, and `CLAUDE_CODE_EFFORT_LEVEL`. The profile set SHALL be exactly `shopapikey.json` and `cockpit.json`; no `giaoduc.json` profile SHALL exist.

#### Scenario: shopapikey profile defines fable[1m] with xhigh

- **WHEN** `~/.claude/profiles/shopapikey.json` is loaded
- **THEN** `model` MUST be `fable[1m]`
- **AND** `env.ANTHROPIC_BASE_URL` MUST be `https://api.phanmemvip.shop`
- **AND** `env.ANTHROPIC_MODEL` MUST be `fable[1m]`
- **AND** `env.CLAUDE_CODE_EFFORT_LEVEL` MUST be `xhigh`

#### Scenario: cockpit profile defines gpt-5.6-luna[1m] with max

- **WHEN** `~/.claude/profiles/cockpit.json` is loaded
- **THEN** `model` MUST be `gpt-5.6-luna[1m]`
- **AND** `env.ANTHROPIC_BASE_URL` MUST be `http://localhost:8788`
- **AND** `env.ANTHROPIC_MODEL` MUST be `gpt-5.6-luna[1m]`
- **AND** `env.CLAUDE_CODE_EFFORT_LEVEL` MUST be `max`

#### Scenario: giaoduc profile removed

- **WHEN** `~/.claude/profiles/` is listed
- **THEN** no `giaoduc.json` file SHALL exist
- **AND** no `giaoduc-key.sh` helper SHALL exist under `~/.claude/helpers/`
