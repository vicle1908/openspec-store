## Why

The archived `standardize-zshenv-shared-secrets` migration made `~/.zshenv` the canonical source for shared provider credentials, but canonical credential specifications still describe the retired `~/.hermes/.env`/loader flow. The live OMP routing also drifted from the canonical default-role contract, so the specifications and operational configuration no longer describe one consistent system.

## What Changes

- Update credential-loading requirements to make the managed `~/.zshenv` shared-agent-secrets block authoritative for `HERMES_CUSTOM_*_API_KEY` values.
- Retain `~/.hermes/.env` for service-private variables only; prohibit duplicate shared-tier provider keys there and in `~/.zshrc`/`.zprofile`.
- Document the retired loader as a compatibility stub that is not the active source of credentials.
- Add value-blind fresh-shell verification requirements for `zsh -c` and `zsh -lc`, plus restart guidance for already-running OMP processes.
- Preserve the existing credential value; provider-side key rotation and live inference remain security-gated.
- Defer OMP routing drift correction because direct Phanmemvip acceptance is currently blocked.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `coding-agent-credential-loading`: replace the retired `.hermes/.env` loader contract with the archived `.zshenv` shared-tier contract.
- `omp-fresh-shell-contract`: align shell-source assumptions and OMP verification with the `.zshenv` migration.

## Non-Goals

- Rotate or replace any provider credential.
- Print, copy, or otherwise disclose credential values.
- Re-enable the retired loader or duplicate provider keys into `.hermes/.env`, `.zshrc`, or `.zprofile`.
- Perform live Phanmemvip inference while the archived security evidence blocks testing.
- Modify unrelated provider roles, consumer CLIs, or service-private credentials.

## Ownership Boundaries

- The OpenSpec store owns canonical credential requirements and this correction's planning artifacts.
- The local user configuration owns `~/.zshenv`; implementation must be applied separately with explicit scope and value-blind verification.
- Provider-side credential rotation remains outside this environment and outside this change.
