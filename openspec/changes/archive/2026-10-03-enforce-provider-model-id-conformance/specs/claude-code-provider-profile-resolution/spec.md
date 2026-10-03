## MODIFIED Requirements

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
