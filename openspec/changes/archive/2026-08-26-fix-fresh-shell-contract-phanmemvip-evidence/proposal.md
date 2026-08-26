## Why

The archived `update-fresh-shell-contract-phanmemvip` change was archived without implementation evidence (0/3 tasks) and left two default-role scenario headings falsely referring to native Cockpit even though their bodies and the live default resolve to `phanmemvip/gpt-5.6-sol:max`.

## What Changes

- Run the three original `zsh -lc` verification probes and record their raw evidence.
- Retain the two contradictory Cockpit scenario headings for validator carry-over compliance while adding explicit deprecation notes and updating their bodies to describe the phanmemvip default.
- Mark all three verification tasks complete only after their real commands produce the expected results.
- **Non-goals:** No changes to the credential loader, `.zshenv` wiring, credential values, or any provider configuration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `omp-fresh-shell-contract`: Correct the canonical default-role scenario semantics and attach real verification evidence for the phanmemvip fresh-shell contract.

## Impact

- Ownership boundary: OpenSpec planning and canonical contract content in `openspec-store` only.
- Runtime impact: read-only shell and OMP verification probes; no runtime configuration mutation.
- No API, dependency, credential-loader, shell-wiring, or provider-config changes.
