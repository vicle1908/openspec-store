## REMOVED Requirements

### Requirement: Native Cockpit default role

The omp `default` role SHALL resolve to `cockpit/gpt-5.6-luna:high`.

#### Scenario: fresh-shell default uses native Cockpit

Given the custom provider credentials are loaded in a clean login shell
When `omp --no-session -p "reply only: pong"` is run without `--model`
Then omp SHALL resolve the default to native Cockpit and return `pong` with
exit code 0.

## ADDED Requirements

### Requirement: Giaoduc default role

The omp `default` role SHALL resolve to `giaoduc/Advance`.

#### Scenario: fresh-shell default uses Giaoduc

Given the custom provider credentials are loaded in a clean login shell
When `omp --no-session -p "reply only: pong"` is run without `--model`
Then omp SHALL resolve the default to Giaoduc Advance and return `pong` with
exit code 0.
