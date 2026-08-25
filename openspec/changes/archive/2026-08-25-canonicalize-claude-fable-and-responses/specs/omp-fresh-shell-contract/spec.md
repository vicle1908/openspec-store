# omp-fresh-shell-contract Delta

## MODIFIED Requirements

### Requirement: One-million-token custom model contexts

The omp model entries for `shopapikey/Claude-Fable`, `phanmemvip/gpt-5.6-sol`, and
`cockpit/gpt-5.6-luna` SHALL declare `contextWindow: 1000000`.

#### Scenario: custom model context metadata

Given `~/.omp/agent/models.yml`
When the three custom model entries are inspected programmatically
Then each SHALL have `contextWindow` equal to `1000000`.

### Requirement: Existing omp routing preserved

The change SHALL preserve all existing provider endpoints, transports, model
IDs, non-default role assignments, equivalence mappings, and credential values.
The current `default` role SHALL resolve to `cockpit/gpt-5.6-luna:max`.

#### Scenario: three explicit providers remain usable

Given the corrected fresh-shell environment
When each explicit selector is run through omp
Then `cockpit/gpt-5.6-luna`, `shopapikey/Claude-Fable`, and `phanmemvip/gpt-5.6-sol`
SHALL return `pong` with exit code 0, subject to provider-side rate limits.

#### Scenario: current default uses native Cockpit

Given the custom provider credentials are loaded in a clean login shell
When `omp --no-session -p "reply only: pong"` is run without `--model`
Then omp SHALL resolve the default to `cockpit/gpt-5.6-luna:max` and return
`pong` with exit code 0
