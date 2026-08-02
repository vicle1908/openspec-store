# Proposal: Refresh Documentation and Sync Specs

## Why

Recent implementation work (security-contract, local-readiness, reporting-reconcile, ecosystem evaluation) has left documentation stale:

1. **Missing files referenced in index**: `platform/docs/temporal.md` and `platform/docs/health.md` are listed in `platform/docs/README.md` but don't exist
2. **deploy/README.md outdated**: No mention of production-contract/local-fast compose overlays, security contract, container hardening, or runtime-contract
3. **docs/runbooks/README.md incomplete**: 4 runbooks not indexed (service-runtime-security-contract, knowledge-graphs, temporal-nexus-shipping, temporal-clean-slate)
4. **platform/docs/architecture.md stale**: No mention of security packages (pgroles, pgownership, pgconn)
5. **platform/docs/README.md stale**: References missing files, doesn't list new docs
6. **Service READMEs**: Most services lack consistent documentation

## What Changes

Create/update documentation to match current implementation:

- Create `platform/docs/temporal.md` — Temporal TLS, Nexus, workflow security
- Create `platform/docs/health.md` — health probe contracts
- Update `deploy/README.md` — add security contract, compose profiles, container hardening
- Update `docs/runbooks/README.md` — index all runbooks
- Update `platform/docs/architecture.md` — add security packages section
- Update `platform/docs/README.md` — fix table, add new docs

## Capabilities

- `platform-documentation` — Platform module documentation accuracy
- `deployment-documentation` — Deployment layer documentation completeness
- `operational-runbooks` — Runbook index completeness

## Non-Goals

- Service-level documentation (each service owns its own docs)
- API documentation (generated from code)
- Tutorial/getting-started guides (separate concern)

## Compatibility

Documentation-only changes. No code, no tests, no deployment impact.

## Rollback

Git revert. No operational risk.
