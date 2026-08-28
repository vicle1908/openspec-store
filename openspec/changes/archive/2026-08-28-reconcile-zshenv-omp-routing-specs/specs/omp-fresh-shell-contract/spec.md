## MODIFIED Requirements

### Requirement: Fresh-shell custom credentials

A fresh zsh shell SHALL load the managed shared-agent-secrets block from `~/.zshenv`. The shell SHALL expose the five active `HERMES_CUSTOM_*_API_KEY` variables without printing their values. The retired `~/.config/agent-llm/load-hermes-custom-credentials.zsh` MAY remain as a silent compatibility stub but SHALL NOT be required for credential visibility.

#### Scenario: clean login shell receives custom keys

Given `~/.zshenv` contains the managed shared-agent-secrets block
When a clean environment starts `/bin/zsh -lic`
Then `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_PHANMEMVIP_API_KEY`, `HERMES_CUSTOM_COCKPIT_API_KEY`, `HERMES_CUSTOM_ANTIGRAVITY_API_KEY`, and `HERMES_CUSTOM_LOCALHOST_51006_API_KEY` SHALL be set.

#### Scenario: missing env file does not break shell startup

Given the managed shared-agent-secrets block is absent from `~/.zshenv`
When a login zsh shell starts
Then the shell SHALL remain syntactically valid and start without an error from credential loading.

#### Scenario: non-login shell receives custom keys

Given `~/.zshenv` contains the managed shared-agent-secrets block
When a clean environment runs `/bin/zsh -c` (non-login)
Then the five active `HERMES_CUSTOM_*_API_KEY` variables SHALL be set
And unrelated variables such as `DISCORD_BOT_TOKEN` SHALL remain unset.

#### Scenario: loader produces no credential output

Given the retired loader is sourced in any shell context
When stdout and stderr are captured
Then no credential values or `export KEY=value` lines SHALL appear.
Note: interactive zsh `-i` legitimately emits OSC 1337 terminal integration metadata unrelated to credential loading.

