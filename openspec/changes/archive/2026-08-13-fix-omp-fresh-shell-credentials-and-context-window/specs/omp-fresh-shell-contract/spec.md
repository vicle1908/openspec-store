## ADDED Requirements

### Requirement: Fresh-shell custom credentials

A fresh login zsh shell SHALL load the canonical `~/.hermes/.env` file when it
is readable. The shell SHALL expose the three custom provider key variables
without printing their values.

#### Scenario: clean login shell receives custom keys

Given `~/.hermes/.env` exists and is mode 600
When a clean environment starts `/bin/zsh -lic`
Then `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_GIAODUC_API_KEY`, and
`HERMES_CUSTOM_COCKPIT_API_KEY` SHALL be set.

#### Scenario: missing env file does not break shell startup

Given `~/.hermes/.env` does not exist
When a login zsh shell starts
Then the shell SHALL remain syntactically valid and start without an error from
the guarded source block.

### Requirement: One-million-token custom model contexts

The omp model entries for `shopapikey/fable-5`, `giaoduc/Advance`, and
`cockpit/gpt-5.6-luna` SHALL declare `contextWindow: 1000000`.

#### Scenario: custom model context metadata

Given `~/.omp/agent/models.yml`
When the three custom model entries are inspected programmatically
Then each SHALL have `contextWindow` equal to `1000000`.

### Requirement: Native Cockpit default role

The omp `default` role SHALL resolve to `cockpit/gpt-5.6-luna:high`.

#### Scenario: fresh-shell default uses native Cockpit

Given the custom provider credentials are loaded in a clean login shell
When `omp --no-session -p "reply only: pong"` is run without `--model`
Then omp SHALL resolve the default to native Cockpit and return `pong` with
exit code 0.

### Requirement: Existing omp routing preserved

The change SHALL preserve all existing provider endpoints, transports, model
IDs, non-default role assignments, equivalence mappings, and credential values.

#### Scenario: three explicit providers remain usable

Given the corrected fresh-shell environment
When each explicit selector is run through omp
Then `cockpit/gpt-5.6-luna:high`, `shopapikey/fable-5`, and `giaoduc/Advance`
SHALL return `pong` with exit code 0.
