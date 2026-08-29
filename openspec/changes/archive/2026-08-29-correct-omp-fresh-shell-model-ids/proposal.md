## Why

The canonical `omp-fresh-shell-contract` contains stale provider model identifiers that do not match the inspected OMP catalog. This correction restores the exact registered IDs without changing runtime configuration.

## What Changes

- Replace every stale Phanmemvip and Cockpit model reference in the affected `omp-fresh-shell-contract` requirements with the exact registered catalog IDs:
  - `phanmemvip/gpt-5.6-sol`
  - `cockpit/gpt-5.6-luna`
- Preserve all existing requirement and scenario names.
- Preserve the canonical `:max` default-role assertions.
- Explicitly document the current runtime default-level difference (`:xhigh` live versus `:max` canonical) as deferred drift; this change does not edit runtime routing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `omp-fresh-shell-contract`

## Non-Goals

- Do not modify `~/.omp/agent/config.yml` or `~/.omp/agent/models.yml`.
- Do not change provider credentials, transports, roles, or fallback chains.
- Do not run live Phanmemvip inference while the retained exposed key remains security-blocked.
- Do not resolve the runtime default-level drift; track that as a separate routing change.
