# claude-code-provider-routing (Delta)

## ADDED Requirements

### Requirement: Profile-based launchers SHALL isolate auth to apiKeyHelper only

Each profile-based launcher that passes `--settings` (containing `apiKeyHelper`) MUST ensure the child process has `ANTHROPIC_AUTH_TOKEN` unset or absent. Claude Code 2.1.228+ emits a warning when both `ANTHROPIC_AUTH_TOKEN` and `apiKeyHelper` are present and may fail to authenticate. The launcher MUST NOT export `ANTHROPIC_AUTH_TOKEN` into the child process.

#### Scenario: Profile-based launcher uses apiKeyHelper without ANTHROPIC_AUTH_TOKEN

- **WHEN** a profile-based launcher (`shopapikey`, `giaoduc`, or `cockpit`) is invoked
- **THEN** the child process MUST have `ANTHROPIC_AUTH_TOKEN` unset or absent
- **AND** the child process MUST invoke `apiKeyHelper` from the active profile
- **AND** Claude Code MUST NOT emit the auth mutual-exclusivity warning

#### Scenario: Clean fresh shell produces no auth warning

- **WHEN** a fresh shell is started and any profile launcher is invoked
- **THEN** stderr MUST NOT contain `Both ANTHROPIC_AUTH_TOKEN and apiKeyHelper set`

### Requirement: Helper preflight SHALL validate credential availability without exposing it

Each profile-based launcher MUST validate credential availability before launching Claude Code by invoking the profile's `apiKeyHelper` script in a child process with stdout and stderr redirected to `/dev/null`. A preflight failure MUST produce a non-zero exit with stderr naming the provider and stating credential unavailability. A preflight success MUST produce exit code 0 with no credential content on any output stream.

#### Scenario: Helper preflight succeeds silently

- **WHEN** the helper script produces a credential on stdout
- **THEN** the preflight MUST return exit code 0
- **AND** no credential content MUST appear on the launcher's stdout or stderr

#### Scenario: Helper preflight fails with provider error

- **WHEN** the helper script fails (missing env var, script error, nonzero exit)
- **THEN** the preflight MUST return nonzero exit
- **AND** stderr MUST contain a message naming the provider (not the credential value)
- **AND** Claude Code MUST NOT be launched

### Requirement: Provider credentials SHALL NOT be persisted in shell configuration

Provider API keys MUST NOT be exported, assigned, or otherwise persisted in `~/.zshrc`, `~/.zshenv`, `~/.zprofile`, or any shell initialization file. Credentials MUST only be available through credential files with restrictive permissions (e.g. `~/.hermes/.env` at mode `600`) and loaded at runtime through `apiKeyHelper` scripts.

#### Scenario: Shell config contains no credential values

- **WHEN** `~/.zshrc` is inspected
- **THEN** it MUST NOT contain literal values for `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_GIAODUC_API_KEY`, or `HERMES_CUSTOM_COCKPIT_API_KEY`

### Requirement: reset SHALL clear all provider state

`claude_reset()` MUST unset every provider-specific variable including `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL`, all model aliases, `ANTHROPIC_CUSTOM_MODEL_OPTION*`, `CLAUDE_CODE_EFFORT_LEVEL`, and `CLAUDE_CODE_SUBAGENT_MODEL` before launching Claude Code.

#### Scenario: claude_reset produces clean state

- **WHEN** `claude_reset()` is invoked after any launcher
- **THEN** Claude Code MUST launch with no provider-specific env vars set
- **AND** the process MUST use default model resolution (no profile, no custom model)
