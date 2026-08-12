# claude-code-provider-profile-resolution (Delta)

## ADDED Requirements

### Requirement: Profile-based launchers SHALL NOT export ANTHROPIC_AUTH_TOKEN

Each launcher function in `~/.zshrc` that passes `--settings <profile>` with `apiKeyHelper` MUST NOT export `ANTHROPIC_AUTH_TOKEN` into the child process environment. The launcher MUST defensively unset `ANTHROPIC_AUTH_TOKEN` before exec to prevent inherited values from reaching Claude Code.

#### Scenario: giaoduc launcher unsets ANTHROPIC_AUTH_TOKEN

- **WHEN** a user invokes `giaoduc()` in a fresh shell
- **THEN** the child process MUST receive `--settings $HOME/.claude/profiles/giaoduc.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be unset in the child process
- **AND** the process MUST invoke `apiKeyHelper` from the giaoduc profile

#### Scenario: shopapikey launcher unsets ANTHROPIC_AUTH_TOKEN

- **WHEN** a user invokes `shopapikey()` in a fresh shell
- **THEN** the child process MUST receive `--settings $HOME/.claude/profiles/shopapikey.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be unset in the child process
- **AND** the process MUST invoke `apiKeyHelper` from the shopapikey profile

#### Scenario: cockpit launcher unsets ANTHROPIC_AUTH_TOKEN

- **WHEN** a user invokes `cockpit()` in a fresh shell
- **THEN** the child process MUST receive `--settings $HOME/.claude/profiles/cockpit.json`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST be unset in the child process
- **AND** the process MUST invoke `apiKeyHelper` from the cockpit profile

### Requirement: Launchers SHALL validate credential availability via helper preflight

Each launcher MUST invoke the profile's `apiKeyHelper` script in a child process with stdout and stderr redirected to `/dev/null` as a preflight check before launching Claude Code. A successful preflight produces exit code 0. A failed preflight produces nonzero exit with stderr naming the provider and stating credential unavailability. Claude Code MUST NOT be launched on preflight failure.

#### Scenario: Helper preflight succeeds silently

- **WHEN** the helper script produces a credential on stdout
- **THEN** the preflight MUST return exit code 0
- **AND** no credential content MUST appear on the launcher's stdout or stderr

#### Scenario: Helper preflight fails with provider error

- **WHEN** the helper script fails (missing env var, script error, nonzero exit)
- **THEN** the preflight MUST return nonzero exit
- **AND** stderr MUST contain a message naming the provider (not the credential value)
- **AND** Claude Code MUST NOT be launched

### Requirement: Provider credentials SHALL NOT be persisted in shell configuration files

Provider API keys MUST NOT be exported, assigned, or otherwise persisted in `~/.zshrc`, `~/.zshenv`, `~/.zprofile`, or any shell initialization file. Credentials MUST only be available through credential files with restrictive permissions (mode `600`) loaded at runtime through `apiKeyHelper` scripts.

#### Scenario: Shell config contains no credential values

- **WHEN** `~/.zshrc` is inspected
- **THEN** it MUST NOT contain literal values for `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_GIAODUC_API_KEY`, or `HERMES_CUSTOM_COCKPIT_API_KEY`
