## MODIFIED Requirements

### Requirement: One-million-token custom model contexts

The omp model entries for `shopapikey/Claude-Fable`, `phanmemvip/gpt-5.6-sol`, and `cockpit/gpt-5.6-luna` SHALL declare `contextWindow: 1000000`.

#### Scenario: custom model context metadata

Given `~/.omp/agent/models.yml`
When the three custom model entries are inspected programmatically
Then each SHALL have `contextWindow` equal to `1000000`.

### Requirement: Existing omp routing preserved

The change SHALL preserve all existing provider endpoints, transports, model IDs, non-default role assignments, equivalence mappings, and credential values. The current `default` role SHALL resolve to `phanmemvip/gpt-5.6-sol:max`.

#### Scenario: three explicit providers remain usable

Given the fresh-shell custom provider credentials are loaded
When each explicit selector is run through omp
Then `cockpit/gpt-5.6-luna`, `shopapikey/Claude-Fable`, and `phanmemvip/gpt-5.6-sol` SHALL return `pong` with exit code 0, subject to provider-side rate limits.

#### Scenario: current default uses native Cockpit

*Deprecated heading: retained only for canonical scenario carry-over compatibility; the scenario now verifies the phanmemvip default and does not assert a Cockpit default.*

Given the custom provider credentials are loaded in a fresh login shell
When `omp --no-session --mode json -p "reply only: pong"` is run without `--model`
Then the served provider/model attribution SHALL be `phanmemvip/gpt-5.6-sol`
And no fallback event SHALL occur
And the command SHALL return `pong` with exit code 0.

### Requirement: Cockpit default role

The omp `default` role SHALL resolve to `phanmemvip/gpt-5.6-sol:max`.

#### Scenario: fresh-shell default uses Cockpit

*Deprecated heading: retained only for canonical scenario carry-over compatibility; the scenario now verifies the phanmemvip default and does not assert a Cockpit default.*

Given the custom provider credentials are loaded in a fresh login shell
When `omp --no-session --mode json -p "reply only: pong"` is run without `--model`
Then the served provider/model attribution SHALL be `phanmemvip/gpt-5.6-sol`
And the default thinking level SHALL be `max`
And the command SHALL return `pong` with exit code 0.
