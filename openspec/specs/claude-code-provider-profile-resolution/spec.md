# claude-code-provider-profile-resolution Specification

## Purpose
Define the persistent credential-free defaults surface for Claude Code provider selection: global defaults in `~/.claude/settings.json`, `apiKeyHelper` credential retrieval, and per-provider profile files under `~/.claude/profiles/`. This capability owns the settings/profile files; the `claude-code-provider-routing` capability owns the launcher functions that select a profile via `claude --settings`.

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

Each launcher function in `~/.zshrc` SHALL call `_claude_with_profile` with the corresponding profile path, passing `--settings <profile>` to Claude Code. The launcher MUST NOT use the old `_claude_model_default` helper. The launcher MUST defensively unset `ANTHROPIC_AUTH_TOKEN` before exec. The launcher MUST validate credential availability by invoking the profile's `apiKeyHelper` in a child process with stdout and stderr redirected to `/dev/null` (helper preflight). A preflight failure MUST produce a non-zero exit with stderr naming the provider and stating credential unavailability. Claude Code MUST NOT be launched on preflight failure.

#### Scenario: giaoduc launcher uses --settings with giaoduc.json

- **WHEN** a user invokes `giaoduc()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/giaoduc.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be unset in the child process
- **AND** the process MUST invoke `apiKeyHelper` from the giaoduc profile

#### Scenario: shopapikey launcher uses --settings with shopapikey.json

- **WHEN** a user invokes `shopapikey()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/shopapikey.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be unset in the child process
- **AND** the process MUST invoke `apiKeyHelper` from the shopapikey profile

#### Scenario: cockpit launcher uses --settings with cockpit.json

- **WHEN** a user invokes `cockpit()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/cockpit.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be unset in the child process
- **AND** the process MUST invoke `apiKeyHelper` from the cockpit profile

#### Scenario: Helper preflight succeeds silently

- **WHEN** the helper script produces a credential on stdout
- **THEN** the preflight MUST return exit code 0
- **AND** no credential content MUST appear on the launcher's stdout or stderr

#### Scenario: Helper preflight fails with provider error

- **WHEN** the helper script fails (missing env var, script error, nonzero exit)
- **THEN** the preflight MUST return nonzero exit
- **AND** stderr MUST contain a message naming the provider (not the credential value)
- **AND** Claude Code MUST NOT be launched

### Requirement: Auth tokens SHALL NOT be persisted in JSON files

Provider API keys MUST be injected through `apiKeyHelper` scripts at runtime. Profile JSON files and `settings.json` MUST NOT contain `ANTHROPIC_AUTH_TOKEN` or any secret values. Provider API keys MUST NOT be exported, assigned, or otherwise persisted in `~/.zshrc`, `~/.zshenv`, `~/.zprofile`, or any shell initialization file.

#### Scenario: profiles are credential-free

- **WHEN** any profile under `~/.claude/profiles/` is inspected
- **THEN** it MUST NOT contain `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET` in its `env` block

#### Scenario: profile files are owner-only readable

- **WHEN** any profile under `~/.claude/profiles/` is stat'd
- **THEN** its permissions MUST be `600` (owner read/write only)

#### Scenario: Shell config contains no credential values

- **WHEN** `~/.zshrc` is inspected
- **THEN** it MUST NOT contain literal values for `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_GIAODUC_API_KEY`, or `HERMES_CUSTOM_COCKPIT_API_KEY`

### Requirement: Missing token SHALL produce a clear error

When a provider's `apiKeyHelper` script cannot retrieve its credential, the launcher MUST exit with a clear error message naming the provider and stating credential unavailability. The launcher MUST NOT expose the helper script's stdout. No Claude process MUST be launched.

#### Scenario: giaoduc with missing token

- **WHEN** the giaoduc helper cannot retrieve its credential and `giaoduc()` is invoked
- **THEN** the function MUST exit with non-zero status
- **AND** stderr MUST name the provider and state credential unavailability
- **AND** NO Claude process MUST be launched

#### Scenario: shopapikey with missing token

- **WHEN** the shopapikey helper cannot retrieve its credential and `shopapikey()` is invoked
- **THEN** the function MUST exit with non-zero status
- **AND** stderr MUST name the provider and state credential unavailability
- **AND** NO Claude process MUST be launched

#### Scenario: cockpit with missing token

- **WHEN** the cockpit helper cannot retrieve its credential and `cockpit()` is invoked
- **THEN** the function MUST exit with non-zero status
- **AND** stderr MUST name the provider and state credential unavailability
- **AND** NO Claude process MUST be launched

### Requirement: claude_reset SHALL clear all provider state

`claude_reset()` MUST unset every provider-specific variable including `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL`, all model aliases, `ANTHROPIC_CUSTOM_MODEL_OPTION*`, `CLAUDE_CODE_EFFORT_LEVEL`, and `CLAUDE_CODE_SUBAGENT_MODEL` before launching Claude Code.

#### Scenario: claude_reset produces clean state

- **WHEN** `claude_reset()` is invoked after any launcher
- **THEN** Claude Code MUST launch with no provider-specific env vars set
- **AND** the process MUST use default model resolution (no profile, no custom model)

### Requirement: Profile resolution and launcher routing own distinct surfaces

This capability SHALL own the persistent credential-free defaults surface: `~/.claude/settings.json` global defaults, `apiKeyHelper` credential retrieval, and per-provider profile files under `~/.claude/profiles/`. The `claude-code-provider-routing` capability SHALL own the per-provider launcher functions that select a profile via `claude --settings <profile>` and pass a default model via `--model`. Model-selection precedence SHALL be: an explicit `--model` CLI flag, then the `--settings` profile file selected by the launcher, then the global `~/.claude/settings.json`. Neither capability SHALL claim authority over the other's surface.

#### Scenario: Global settings provide credential-free defaults

- **WHEN** `~/.claude/settings.json` is loaded for a bare invocation
- **THEN** it SHALL provide the default provider model, base URL, and effort without containing any credential values

#### Scenario: apiKeyHelper is the sole credential boundary

- **WHEN** Claude Code requires a bearer token
- **THEN** it SHALL obtain it by invoking the configured `apiKeyHelper`
- **AND** no credential value SHALL appear in settings files or profile files

#### Scenario: Launcher-selected profile overrides global settings

- **GIVEN** a provider launcher invokes `claude --settings <profile.json>`
- **WHEN** Claude Code starts from that launcher
- **THEN** the selected profile SHALL win for that session over the global settings file
