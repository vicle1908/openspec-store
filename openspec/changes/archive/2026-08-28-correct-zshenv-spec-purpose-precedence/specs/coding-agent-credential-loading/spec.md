## REMOVED Requirements

### Requirement: Shared allowlisted loader

A shared loader SHALL exist at `~/.config/agent-llm/load-hermes-custom-credentials.zsh` and export only variables matching `HERMES_CUSTOM_[A-Z0-9_]+_API_KEY` from `~/.hermes/.env`.

#### Scenario: only allowlisted variables are exported

Given `~/.hermes/.env` exists with provider entries
When the loader is sourced
Then only `HERMES_CUSTOM_*_API_KEY` variables SHALL be defined.

### Requirement: Nonfatal missing sources

If `~/.hermes/.env` does not exist, or the loader does not exist, or the loader file is not readable, the shell SHALL start without error and with exit code 0.

#### Scenario: missing .env is nonfatal

Given `~/.hermes/.env` does not exist
When a login zsh shell starts
Then the shell SHALL exit 0 with no error output.

#### Scenario: missing loader is nonfatal

Given `~/.config/agent-llm/load-hermes-custom-credentials.zsh` does not exist
When `.zshenv` is loaded
Then the shell SHALL start without error.

### Requirement: Pre-existing variable precedence

If a shared-tier variable is already exported by the parent environment before the loader runs, the loader SHALL NOT overwrite it.

#### Scenario: sentinel is preserved

Given `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` is set to `PRESET_SENTINEL` before the loader runs
When the loader is sourced
Then the value SHALL remain `PRESET_SENTINEL`.

## ADDED Requirements

### Requirement: Retired loader status

The retired loader MAY remain as a silent compatibility stub, but it SHALL NOT be the active credential source. Active provider keys SHALL come from the managed `.zshenv` shared-agent-secrets block.

#### Scenario: loader is not authoritative

Given the retired loader is sourced
When credential visibility is checked
Then active provider keys SHALL be attributed to the managed `.zshenv` block and no credential values SHALL be printed.

### Requirement: Managed zshenv missing source is nonfatal

If the managed shared-agent-secrets block is absent from `~/.zshenv`, or the retired loader is absent or unreadable, the shell SHALL start without error and with exit code 0.

#### Scenario: missing managed block is nonfatal

Given the managed shared-agent-secrets block is absent from `~/.zshenv`
When a login zsh shell starts
Then the shell SHALL exit 0 with no error output from credential loading.

#### Scenario: missing retired loader is nonfatal

Given `~/.config/agent-llm/load-hermes-custom-credentials.zsh` does not exist
When `.zshenv` is loaded
Then the shell SHALL start without error.

### Requirement: Managed zshenv assignment precedence

The unconditional managed shared-agent-secrets exports in `~/.zshenv` SHALL overwrite conflicting inherited values.

#### Scenario: managed value overwrites parent sentinel

Given `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` is set to `PRESET_SENTINEL` before zsh startup
When `.zshenv` is loaded
Then the resulting value SHALL be the managed `.zshenv` value
And verification SHALL use only presence, length, or digest without printing it.
