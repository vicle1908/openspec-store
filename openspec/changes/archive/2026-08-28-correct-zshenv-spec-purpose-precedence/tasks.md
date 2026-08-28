## 1. Specification correction

- [x] 1.1 Edit the main `coding-agent-credential-loading` Purpose text to state that the managed `.zshenv` shared-agent-secrets block is authoritative; verify it no longer says the loader reads canonical `~/.hermes/.env`.
- [x] 1.2 Edit the main `omp-fresh-shell-contract` Purpose text to state that active credentials come from the managed `.zshenv` block; verify it no longer presents the retired loader as active.
- [x] 1.3 Replace `Shared allowlisted loader` with `Retired loader status`, preserving a no-credential-output scenario.
- [x] 1.4 Replace `Nonfatal missing sources` with `Managed zshenv missing source is nonfatal`, covering both managed-block absence and retired-loader absence.
- [x] 1.5 Replace `Pre-existing variable precedence` with `Managed zshenv assignment precedence`, verifying unconditional overwrite value-blind.

## 2. Validation and delivery

- [x] 2.1 Run strict validation and inspect the resulting canonical specs for internal consistency.
- [x] 2.2 Review and commit only the two OpenSpec changes; do not modify credential values or OMP runtime configuration.
