## Context

The archived `standardize-zshenv-shared-secrets` change established `~/.zshenv` as the active shared credential source and retired the old loader. Canonical credential specifications still describe the pre-migration `.hermes/.env` flow.

## Goals / Non-Goals

**Goals:**

- Make canonical credential specifications describe the archived `.zshenv` implementation.
- Define value-blind `zsh -c` and `zsh -lc` verification.
- Preserve the existing credential value and loading mechanism.
- Leave OMP routing drift explicitly deferred until direct provider acceptance is unblocked.

**Non-Goals:**

- Provider-side credential rotation or live inference.
- Changes to `~/.omp/agent/config.yml`.
- Changes to provider declarations, roles, fallback chains, or consumer CLIs.

## Decisions

1. The managed shared-agent-secrets block in `~/.zshenv` is authoritative for active `HERMES_CUSTOM_*_API_KEY` exports.
2. `~/.hermes/.env` remains service-private and must not contain duplicate shared-tier provider keys.
3. The old loader remains compatibility-only and is not required for shell visibility.
4. Fresh-shell checks report only presence, length, or a non-reversible digest; no credential value is emitted.
5. Existing OMP processes must be restarted after environment changes because they retain their startup environment snapshot.
6. Canonical specs are updated through this OpenSpec delta and later synchronized with the OpenSpec sync workflow during an explicit apply request.

## Risks / Trade-offs

- The existing provider key remains security-sensitive until provider-side rotation; live Phanmemvip testing is blocked.
- Canonical routing still has a separate known drift and requires a later, independently approved change.
- Historical artifacts may retain `.hermes/.env` references for audit; only active normative requirements are corrected here.
