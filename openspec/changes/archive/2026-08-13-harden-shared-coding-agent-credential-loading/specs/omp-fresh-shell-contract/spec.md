## MODIFIED Requirements

### Requirement: Fresh-shell custom credentials

A fresh zsh shell SHALL source the shared allowlisted loader at
`~/.config/agent-llm/load-hermes-custom-credentials.zsh` when it is
readable. The shell SHALL expose the five `HERMES_CUSTOM_*_API_KEY`
variables without printing their values. The shared loader SHALL NOT
export unrelated Hermes variables. The loader SHALL produce no
stdout or stderr when sourced.

#### Scenario: clean login shell receives custom keys

Given `~/.hermes/.env` exists and is mode 600
And the shared loader exists at `~/.config/agent-llm/load-hermes-custom-credentials.zsh`
When a clean environment starts `/bin/zsh -lic`
Then `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_GIAODUC_API_KEY`,
`HERMES_CUSTOM_COCKPIT_API_KEY`, `HERMES_CUSTOM_ANTIGRAVITY_API_KEY`, and
`HERMES_CUSTOM_LOCALHOST_51006_API_KEY` SHALL be set.

#### Scenario: missing env file does not break shell startup

Given `~/.hermes/.env` does not exist
When a login zsh shell starts
Then the shell SHALL remain syntactically valid and start without an error
from the guarded loader block.

#### Scenario: non-login shell receives custom keys

Given the shared loader exists and `~/.hermes/.env` is readable
When a clean environment runs `/bin/zsh -c` (non-login)
Then the five `HERMES_CUSTOM_*_API_KEY` variables SHALL be set
And unrelated variables such as `DISCORD_BOT_TOKEN` SHALL remain unset.

#### Scenario: loader produces no credential output

Given the loader is sourced in any shell context
When stdout and stderr are captured
Then no credential values or `export KEY=value` lines SHALL appear.
Note: interactive zsh `-i` legitimately emits OSC 1337 terminal
integration metadata unrelated to credential loading.
