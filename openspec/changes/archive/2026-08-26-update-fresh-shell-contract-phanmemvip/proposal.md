## Why

The canonical fresh-shell contract still references giaoduc credentials and Cockpit-default routing, although the phanmemvip migration and external default-role rebinding have superseded both. This change aligns the contract with the current verified OMP routing and credential state through the required OpenSpec delta workflow.

## What Changes

- Replace `HERMES_CUSTOM_GIAODUC_API_KEY` references with `HERMES_CUSTOM_PHANMEMVIP_API_KEY`.
- Replace `cockpit/gpt-5.6-luna:max` default-role assertions with `phanmemvip/gpt-5.6-sol:max`.
- Update affected scenario bodies to match the current verified state while retaining canonical scenario headings required for delta compatibility.
- Preserve the loader mechanism and existing provider inventory outside the superseded credential and default-role assertions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `omp-fresh-shell-contract`: Align fresh-shell credential and default-routing requirements with the phanmemvip migration.

## Impact

The affected ownership boundary is the canonical `omp-fresh-shell-contract` specification and its assertions about the workstation OMP environment. There are no loader implementation changes, `.zshenv` wiring changes, OmniRoute changes, API changes, or dependency changes.

## Non-goals

- Changing the shared credential loader mechanism or `.zshenv` wiring.
- Changing OmniRoute configuration or behavior.
- Modifying unrelated OMP model roles, providers, endpoints, or transports.
