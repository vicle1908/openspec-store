# claude-code-provider-profile-resolution (Delta)

## MODIFIED Requirements

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
