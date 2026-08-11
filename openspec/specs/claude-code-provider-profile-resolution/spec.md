# claude-code-provider-profile-resolution Specification

## Purpose
TBD - created by archiving change claude-code-provider-profile-resolution. Update Purpose after archive.
## Requirements
### Requirement: Global settings SHALL provide shopapikey defaults while remaining credential-free

The `~/.claude/settings.json` file SHALL contain the shopapikey model, base URL, resolution aliases, effort level, and capability declarations as global defaults so that bare `claude` invocations and other compatible applications use shopapikey without any launcher or `--settings` flag. The file MUST NOT contain `ANTHROPIC_AUTH_TOKEN` or any secret values.

#### Scenario: settings.json provides shopapikey defaults

- **WHEN** `~/.claude/settings.json` is loaded
- **THEN** it MUST contain a top-level `model` key set to `fable[1m]`
- **AND** its `env` block MUST contain `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`
- **AND** its `env` block MUST contain `ANTHROPIC_MODEL=fable[1m]`
- **AND** its `env` block MUST contain `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]`
- **AND** its `env` block MUST contain `CLAUDE_CODE_EFFORT_LEVEL=xhigh`

#### Scenario: settings.json contains no auth tokens

- **WHEN** `~/.claude/settings.json` is inspected
- **THEN** it MUST NOT contain `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET` in its `env` block

### Requirement: Settings and profiles SHALL use apiKeyHelper for credential retrieval

Both `~/.claude/settings.json` and each profile under `~/.claude/profiles/` SHALL contain an `apiKeyHelper` field pointing to a helper script that writes the provider API key to stdout. The helper script MUST write only the credential to stdout and MUST NOT log or expose it elsewhere.

#### Scenario: settings.json apiKeyHelper provides shopapikey auth

- **WHEN** bare `claude` is invoked without `ANTHROPIC_AUTH_TOKEN` in the environment
- **THEN** the process MUST invoke `apiKeyHelper` from `~/.claude/settings.json`
- **AND** the helper's stdout MUST be used as the bearer token
- **AND** the request MUST reach the provider with valid authentication

#### Scenario: profile apiKeyHelper overrides global

- **WHEN** `claude --settings $HOME/.claude/profiles/giaoduc.json` is invoked
- **THEN** the process MUST invoke `apiKeyHelper` from the giaoduc profile (not the global settings)
- **AND** the giaoduc helper MUST return the giaoduc-specific credential

#### Scenario: helper script failure produces nonzero exit

- **WHEN** an `apiKeyHelper` script fails to produce a credential (missing env var, nonzero exit)
- **THEN** Claude Code MUST NOT launch
- **AND** the exit code MUST be nonzero

### Requirement: Provider profiles SHALL define model, base URL, and effort

Each provider profile JSON under `~/.claude/profiles/` SHALL contain a top-level `model` field and an `env` block with `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`, and `CLAUDE_CODE_EFFORT_LEVEL`.

#### Scenario: giaoduc profile defines Advance[1m] with xhigh

- **WHEN** `~/.claude/profiles/giaoduc.json` is loaded
- **THEN** `model` MUST be `Advance[1m]`
- **AND** `env.ANTHROPIC_BASE_URL` MUST be `https://api.giaoduc.online`
- **AND** `env.ANTHROPIC_MODEL` MUST be `Advance[1m]`
- **AND** `env.CLAUDE_CODE_EFFORT_LEVEL` MUST be `xhigh`

#### Scenario: shopapikey profile defines fable[1m] with xhigh

- **WHEN** `~/.claude/profiles/shopapikey.json` is loaded
- **THEN** `model` MUST be `fable[1m]`
- **AND** `env.ANTHROPIC_BASE_URL` MUST be `https://api.phanmemvip.shop`
- **AND** `env.ANTHROPIC_MODEL` MUST be `fable[1m]`
- **AND** `env.CLAUDE_CODE_EFFORT_LEVEL` MUST be `xhigh`

#### Scenario: cockpit profile defines gpt-5.6-luna[1m] with max

- **WHEN** `~/.claude/profiles/cockpit.json` is loaded
- **THEN** `model` MUST be `gpt-5.6-luna[1m]`
- **AND** `env.ANTHROPIC_BASE_URL` MUST be `http://localhost:8787`
- **AND** `env.ANTHROPIC_MODEL` MUST be `gpt-5.6-luna[1m]`
- **AND** `env.CLAUDE_CODE_EFFORT_LEVEL` MUST be `max`

### Requirement: Launchers SHALL pass `--settings` to Claude Code

Each launcher function in `~/.zshrc` SHALL call `_claude_with_profile` with the corresponding profile path, passing `--settings <profile>` to Claude Code. The launcher MUST NOT use the old `_claude_model_default` helper.

#### Scenario: giaoduc launcher uses --settings with giaoduc.json

- **WHEN** a user invokes `giaoduc()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/giaoduc.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be set from `$HERMES_CUSTOM_GIAODUC_API_KEY`

#### Scenario: shopapikey launcher uses --settings with shopapikey.json

- **WHEN** a user invokes `shopapikey()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/shopapikey.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be set from `$HERMES_CUSTOM_SHOPAPIKEY_API_KEY`

#### Scenario: cockpit launcher uses --settings with cockpit.json

- **WHEN** a user invokes `cockpit()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/cockpit.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be set from `$HERMES_CUSTOM_COCKPIT_API_KEY`

### Requirement: Auth tokens SHALL NOT be persisted in JSON files

Provider API keys MUST be injected through the shell environment at runtime only. Profile JSON files MUST NOT contain `ANTHROPIC_AUTH_TOKEN` or any secret values.

#### Scenario: profiles are credential-free

- **WHEN** any profile under `~/.claude/profiles/` is inspected
- **THEN** it MUST NOT contain `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET` in its `env` block

#### Scenario: profile files are owner-only readable

- **WHEN** any profile under `~/.claude/profiles/` is stat'd
- **THEN** its permissions MUST be `600` (owner read/write only)

### Requirement: Missing token SHALL produce a clear error

When a provider API key environment variable is not set, the launcher MUST exit with a clear error message naming the missing variable and MUST NOT launch Claude Code.

#### Scenario: giaoduc with missing token

- **WHEN** `HERMES_CUSTOM_GIAODUC_API_KEY` is unset and `giaoduc()` is invoked
- **THEN** the function MUST exit with non-zero status
- **AND** stderr MUST contain the name of the missing variable
- **AND** NO Claude process MUST be launched

#### Scenario: shopapikey with missing token

- **WHEN** `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` is unset and `shopapikey()` is invoked
- **THEN** the function MUST exit with non-zero status
- **AND** stderr MUST contain the name of the missing variable

#### Scenario: cockpit with missing token

- **WHEN** `HERMES_CUSTOM_COCKPIT_API_KEY` is unset and `cockpit()` is invoked
- **THEN** the function MUST exit with non-zero status
- **AND** stderr MUST contain the name of the missing variable

### Requirement: claude_reset SHALL clear all provider state

`claude_reset()` MUST unset every provider-specific variable including `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL`, all model aliases, `ANTHROPIC_CUSTOM_MODEL_OPTION*`, `CLAUDE_CODE_EFFORT_LEVEL`, and `CLAUDE_CODE_SUBAGENT_MODEL` before launching Claude Code.

#### Scenario: claude_reset produces clean state

- **WHEN** `claude_reset()` is invoked after any launcher
- **THEN** Claude Code MUST launch with no provider-specific env vars set
- **AND** the process MUST use default model resolution (no profile, no custom model)
