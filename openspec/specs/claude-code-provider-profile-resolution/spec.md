# claude-code-provider-profile-resolution Specification

## Purpose
Define the persistent credential-free defaults surface for Claude Code provider selection: global defaults in `~/.claude/settings.json`, `apiKeyHelper` credential retrieval, and per-provider profile files under `~/.claude/profiles/`. This capability owns the settings/profile files; the `claude-code-provider-routing` capability owns the launcher functions that select a profile via `claude --settings`.

## Requirements

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

### Requirement: Settings and profiles SHALL use apiKeyHelper for credential retrieval

Both `~/.claude/settings.json` and each profile under `~/.claude/profiles/` SHALL contain an `apiKeyHelper` field pointing to a helper script that writes the provider API key to stdout. The helper script MUST write only the credential to stdout and MUST NOT log or expose it elsewhere.

#### Scenario: settings.json apiKeyHelper provides shopapikey auth

- **WHEN** bare `claude` is invoked without `ANTHROPIC_AUTH_TOKEN` in the environment
- **THEN** the process MUST invoke `apiKeyHelper` from `~/.claude/settings.json`
- **AND** the helper's stdout MUST be used as the bearer token
- **AND** the request MUST reach the provider with valid authentication

#### Scenario: profile apiKeyHelper overrides global

- **WHEN** `claude --settings $HOME/.claude/profiles/cockpit.json` is invoked
- **THEN** the process MUST invoke `apiKeyHelper` from the cockpit profile (not the global settings)
- **AND** the cockpit helper MUST return the cockpit-specific credential

#### Scenario: helper script failure produces nonzero exit

- **WHEN** an `apiKeyHelper` script fails to produce a credential (missing env var, nonzero exit)
- **THEN** Claude Code MUST NOT launch
- **AND** the exit code MUST be nonzero

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
- **THEN** it MUST NOT contain literal values for `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_PHANMEMVIP_API_KEY`, or `HERMES_CUSTOM_COCKPIT_API_KEY`

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

### Requirement: Active provider profiles SHALL define model, base URL, and effort

Each provider profile JSON under `~/.claude/profiles/` SHALL contain a top-level `model` field and an `env` block with `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`, and `CLAUDE_CODE_EFFORT_LEVEL`. The profile set SHALL include `shopapikey.json`, `cockpit.json`, and `omniroute-pm.json`; no `giaoduc.json` profile SHALL exist.

#### Scenario: shopapikey profile defines Claude-Fable with xhigh

- **WHEN** `~/.claude/profiles/shopapikey.json` is loaded
- **THEN** `model` MUST be `Claude-Fable`
- **AND** `env.ANTHROPIC_BASE_URL` MUST be `https://api.phanmemvip.shop`
- **AND** `env.ANTHROPIC_MODEL` MUST be `Claude-Fable`
- **AND** `env.ANTHROPIC_DEFAULT_FABLE_MODEL` MUST be `Claude-Fable`
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

### Requirement: Active launchers SHALL pass `--settings` to Claude Code

Each launcher function in `~/.zshrc` SHALL call `_claude_with_profile` with the corresponding profile path, passing `--settings <profile>` to Claude Code. The launcher MUST NOT use the old `_claude_model_default` helper. The launcher MUST defensively unset `ANTHROPIC_AUTH_TOKEN` before exec. The launcher MUST validate credential availability by invoking the profile's `apiKeyHelper` in a child process with stdout and stderr redirected to `/dev/null` (helper preflight). A preflight failure MUST produce a non-zero exit with stderr naming the provider and stating credential unavailability. Claude Code MUST NOT be launched on preflight failure. The Claude Code launcher set SHALL include `shopapikey()`, `cockpit()`, and `omniroute()`; no `giaoduc()` launcher SHALL exist.

#### Scenario: shopapikey launcher uses --settings with shopapikey.json

- **WHEN** a user invokes `shopapikey()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/shopapikey.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be unset in the child process
- **AND** the process MUST invoke `apiKeyHelper` from the shopapikey profile
- **AND** the default model argument MUST be `Claude-Fable`

#### Scenario: cockpit launcher uses --settings with cockpit.json

- **WHEN** a user invokes `cockpit()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/cockpit.json`
- **AND** the default model argument MUST be `gpt-5.6-luna[1m]`

#### Scenario: omniroute launcher uses --settings with omniroute-pm.json

- **WHEN** a user invokes `omniroute()` in a fresh shell
- **THEN** the process MUST receive `--settings $HOME/.claude/profiles/omniroute-pm.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be unset in the child process
- **AND** the default model argument MUST be `pm/Claude-Fable`

#### Scenario: giaoduc launcher removed

- **WHEN** `~/.zshrc` is sourced in a fresh shell
- **THEN** no `giaoduc()` launcher function SHALL be defined

#### Scenario: Helper preflight succeeds silently

- **WHEN** a launcher runs its `apiKeyHelper` preflight and the helper exits zero
- **THEN** the preflight MUST produce no output
- **AND** Claude Code SHALL be launched

#### Scenario: Helper preflight fails with provider error

- **WHEN** a launcher runs its `apiKeyHelper` preflight and the helper exits non-zero
- **THEN** the launcher MUST exit non-zero
- **AND** stderr MUST name the provider and state that the credential is unavailable
- **AND** Claude Code MUST NOT be launched

### Requirement: Missing token for an active launcher SHALL produce a clear error

When a provider's `apiKeyHelper` script cannot retrieve its credential, the launcher MUST exit with a clear error message naming the provider and stating credential unavailability. The launcher MUST NOT expose the helper script's stdout. No Claude process MUST be launched.

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
