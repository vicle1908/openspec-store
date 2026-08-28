## Why

The first reconciliation archive corrected most credential requirements but left stale Purpose text and migration-era loader semantics. This follow-up makes the canonical specifications internally consistent with the managed `.zshenv` implementation.

## What Changes

- Update Purpose text for `coding-agent-credential-loading` and `omp-fresh-shell-contract`.
- Replace `Shared allowlisted loader` with `Retired loader status`.
- Replace `Nonfatal missing sources` with `Managed zshenv missing source is nonfatal`.
- Replace `Pre-existing variable precedence` with `Managed zshenv assignment precedence`.
- Preserve accurate scenarios for managed-block absence and retired-loader absence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `coding-agent-credential-loading`
- `omp-fresh-shell-contract`

## Non-Goals

- Do not change credentials, shell files, OMP config, provider declarations, or routing.
