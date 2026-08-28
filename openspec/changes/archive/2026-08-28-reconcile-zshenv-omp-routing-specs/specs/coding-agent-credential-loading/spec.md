## MODIFIED Requirements

### Requirement: Canonical secret source

The managed shared-agent-secrets block in `~/.zshenv` SHALL be the sole canonical source for active shared-tier `HERMES_CUSTOM_*_API_KEY` values. `~/.hermes/.env` SHALL remain mode 600 for service-private variables but SHALL NOT contain duplicate shared-tier provider keys. No other file SHALL serve as the credential source for this mechanism.

#### Scenario: canonical source exists and is restricted

Given the coding-agent credential mechanism is in use
When `~/.zshenv` is inspected
Then it SHALL exist with mode 600 and contain the managed shared-agent-secrets block
And `~/.hermes/.env` SHALL contain no active `HERMES_CUSTOM_*_API_KEY` entries.

### Requirement: Shared allowlisted loader

The retired `~/.config/agent-llm/load-hermes-custom-credentials.zsh` SHALL NOT be the active credential source. It MAY remain as a compatibility stub, while active shared-tier provider keys SHALL be exported by the managed `~/.zshenv` block. Unrelated variables SHALL NOT be exported by the shared credential mechanism.

#### Scenario: only allowlisted variables are exported

Given `~/.zshenv` contains the managed shared-agent-secrets block
When a clean zsh shell starts
Then only the declared shared-tier variables are exported by that block
And service-private variables such as `DISCORD_BOT_TOKEN` remain outside the shared tier.

#### Scenario: loader produces no credential output

Given the retired loader is sourced in a clean environment
When stdout and stderr are captured
Then no credential values or `export KEY=value` lines SHALL appear.

### Requirement: Universal zsh shell coverage

The managed shared-agent-secrets block SHALL be wired through `.zshenv` so that both login (`-l`) and non-login zsh invocations receive the shared provider credentials. The broad `.hermes/.env` source block in `.zprofile` SHALL remain absent, and `.zshrc` SHALL NOT override the managed exports.

#### Scenario: login shell receives credentials

Given the managed shared-agent-secrets block is present in `.zshenv`
When a clean environment runs `/bin/zsh -lic`
Then all five active `HERMES_CUSTOM_*_API_KEY` variables SHALL be set.

#### Scenario: non-login shell receives credentials

Given the managed shared-agent-secrets block is present in `.zshenv`
When a clean environment runs `/bin/zsh -c`
Then all five active `HERMES_CUSTOM_*_API_KEY` variables SHALL be set.

#### Scenario: startup is silent for credential output

Given the managed shared-agent-secrets block is present in `.zshenv`
When a clean non-interactive environment runs `/bin/zsh -c` or `/bin/zsh -lc`
Then no stdout or stderr output SHALL be produced by credential loading.
Interactive shells (`-i` flag) may emit unrelated terminal-integration control sequences but SHALL emit no credentials or `export KEY=value` lines.

### Requirement: Nonfatal missing sources

If `~/.zshenv` or its managed shared-agent-secrets block is absent, the shell SHALL start without error and with exit code 0. The retired loader MAY also be absent or unreadable without breaking shell startup.

#### Scenario: missing .env is nonfatal

Given the managed shared-agent-secrets block is absent from `~/.zshenv`
When a login zsh shell starts
Then the shell SHALL exit 0 with no error output from credential loading.

#### Scenario: missing loader is nonfatal

Given `~/.config/agent-llm/load-hermes-custom-credentials.zsh` does not exist
When `.zshenv` is loaded
Then the shell SHALL start without error.

### Requirement: Pre-existing variable precedence

The unconditional managed shared-agent-secrets exports in `~/.zshenv` SHALL take precedence over conflicting inherited values.

#### Scenario: sentinel is preserved

Given `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` is set to `PRESET_SENTINEL` before zsh startup
When `.zshenv` is loaded
Then the resulting value SHALL be the managed `.zshenv` value
And the value SHALL be verified only by presence, length, or digest without printing it.

### Requirement: Parser temporary cleanup

Any internal parser variables used by compatibility credential loading SHALL be unset after execution completes. No `_emc_*` or `_agent_llm_*` temporary variables SHALL remain in the calling shell.

#### Scenario: no temp variables remain

Given the retired loader is sourced in a clean shell
When parameter names beginning with `_emc_` or `_agent_llm_` are enumerated
Then none SHALL be defined.

### Requirement: Scope limitation

This mechanism covers zsh-launched coding agents on the local machine. It SHALL NOT provision GUI applications, LaunchAgents running under a different user or shell, Docker containers, or arbitrary non-zsh processes; those consumers require an explicit zsh wrapper or native environment bridge.

#### Scenario: scope is documented

Given the specification is complete
When the requirement is inspected
Then it SHALL explicitly state which consumers are covered and which are not.
