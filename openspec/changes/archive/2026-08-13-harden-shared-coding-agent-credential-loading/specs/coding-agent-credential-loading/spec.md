## ADDED Requirements

### Requirement: Canonical secret source

`~/.hermes/.env` SHALL remain the sole canonical credential source for coding
agent custom provider keys. The file SHALL be mode 600 and owned by the
effective user. No other file SHALL serve as the credential source for
this mechanism.

#### Scenario: canonical source exists and is restricted

Given the coding-agent credential mechanism is in use
When `~/.hermes/.env` is inspected
Then it SHALL exist with mode 600.

### Requirement: Shared allowlisted loader

A shared loader SHALL exist at `~/.config/agent-llm/load-hermes-custom-credentials.zsh`.
The loader SHALL be sourceable by any zsh-based coding agent. The loader SHALL
export only variables matching `HERMES_CUSTOM_[A-Z0-9_]+_API_KEY`. Unrelated
variables in `~/.hermes/.env` SHALL NOT be exported.

#### Scenario: only allowlisted variables are exported

Given `~/.hermes/.env` exists with five `HERMES_CUSTOM_*_API_KEY` entries and
additional unrelated entries such as `DISCORD_BOT_TOKEN`
When the loader is sourced in a clean environment
Then only `HERMES_CUSTOM_*_API_KEY` variables SHALL be defined
And `DISCORD_BOT_TOKEN` SHALL remain unset.

#### Scenario: loader produces no credential output

Given the loader is sourced in a clean environment
When stdout and stderr are captured
Then no credential values or `export KEY=value` lines SHALL appear.

### Requirement: Universal zsh shell coverage

The loader SHALL be wired through `.zshenv` so that both login (`-l`) and
non-login zsh invocations receive the five credentials. The broad
`.hermes/.env` source block in `.zprofile` SHALL be removed after the
`.zshenv` wiring is in place.

#### Scenario: login shell receives credentials

Given the loader is wired through `.zshenv`
When a clean environment runs `/bin/zsh -lic`
Then all five `HERMES_CUSTOM_*_API_KEY` variables SHALL be set.

#### Scenario: non-login shell receives credentials

Given the loader is wired through `.zshenv`
When a clean environment runs `/bin/zsh -c`
Then all five `HERMES_CUSTOM_*_API_KEY` variables SHALL be set.

#### Scenario: startup is silent for credential output

Given the loader is wired through `.zshenv`
When a clean non-interactive environment runs `/bin/zsh -c` or `/bin/zsh -lc`
Then no stdout or stderr output SHALL be produced.
Interactive shells (`-i` flag) may emit unrelated terminal-integration
control sequences but SHALL emit no credentials or `export KEY=value` lines.

### Requirement: Nonfatal missing sources

If `~/.hermes/.env` does not exist, or the loader does not exist, or the
loader file is not readable, the shell SHALL start without error and with
exit code 0.

#### Scenario: missing .env is nonfatal

Given `~/.hermes/.env` does not exist
When a login zsh shell starts
Then the shell SHALL exit 0 with no error output.

#### Scenario: missing loader is nonfatal

Given `~/.config/agent-llm/load-hermes-custom-credentials.zsh` does not exist
When `.zshenv` is loaded
Then the shell SHALL start without error.

### Requirement: Pre-existing variable precedence

If a variable is already exported by the parent environment before the loader
runs, the loader SHALL NOT overwrite it.

#### Scenario: sentinel is preserved

Given `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` is set to `PRESET_SENTINEL` before
the loader runs
When the loader is sourced
Then the value SHALL remain `PRESET_SENTINEL`.

### Requirement: Parser temporary cleanup

All internal parser variables used by the loader SHALL be unset after
execution completes. No `_emc_*` or `_agent_llm_*` temporary variables
SHALL remain in the calling shell.

#### Scenario: no temp variables remain

Given the loader is sourced in a clean shell
When parameter names beginning with `_emc_` or `_agent_llm_` are enumerated
Then none SHALL be defined.

### Requirement: Scope limitation

This mechanism covers zsh-launched coding agents on the local machine. It
SHALL NOT provision GUI applications, LaunchAgents running under a different
user or shell, Docker containers, or arbitrary non-zsh processes.

#### Scenario: scope is documented

Given the specification is complete
When the requirement is inspected
Then it SHALL explicitly state which consumers are covered and which are not.
