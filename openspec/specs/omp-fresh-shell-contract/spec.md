# omp-fresh-shell-contract Specification

## Purpose
Ensures fresh zsh shells receive active shared-tier provider credentials from the managed `.zshenv` shared-agent-secrets block and verifies that OMP custom-model metadata remains consistent.

## Requirements

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

### Requirement: One-million-token custom model contexts

The omp model entries for `shopapikey/Claude-Fable`, `phanmemvip/codex`, and `cockpit/codex` SHALL declare `contextWindow: 1000000`.

#### Scenario: custom model context metadata

Given `~/.omp/agent/models.yml`
When the three custom model entries are inspected programmatically
Then each SHALL have `contextWindow` equal to `1000000`.

### Requirement: Existing omp routing preserved

The change SHALL preserve all existing provider endpoints, transports, model IDs, non-default role assignments, equivalence mappings, and credential values. The current `default` role SHALL resolve to `phanmemvip/codex:max`.

#### Scenario: three explicit providers remain usable

Given the fresh-shell custom provider credentials are loaded
When each explicit selector is run through omp
Then `cockpit/codex`, `shopapikey/Claude-Fable`, and `phanmemvip/codex` SHALL return `pong` with exit code 0, subject to provider-side rate limits.

#### Scenario: current default uses native Cockpit

*Deprecated heading: retained only for canonical scenario carry-over compatibility; the scenario now verifies the phanmemvip default and does not assert a Cockpit default.*

Given the custom provider credentials are loaded in a fresh login shell
When `omp --no-session --mode json -p "reply only: pong"` is run without `--model`
Then the served provider/model attribution SHALL be `phanmemvip/codex`
And no fallback event SHALL occur
And the command SHALL return `pong` with exit code 0.

### Requirement: Cockpit default role

The omp `default` role SHALL resolve to `phanmemvip/codex:max`.

#### Scenario: fresh-shell default uses Cockpit

*Deprecated heading: retained only for canonical scenario carry-over compatibility; the scenario now verifies the phanmemvip default and does not assert a Cockpit default.*

Given the custom provider credentials are loaded in a fresh login shell
When `omp --no-session --mode json -p "reply only: pong"` is run without `--model`
Then the served provider/model attribution SHALL be `phanmemvip/codex`
And the default thinking level SHALL be `max`
And the command SHALL return `pong` with exit code 0.
