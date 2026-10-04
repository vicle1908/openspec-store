# Proposal: Synchronize CI/CD Operations Runbook with Modernized Architecture and 4-Tier Matrix DAG

## Why
Over PRs #43 through #50, the `go-microservices` CI/CD pipeline underwent a structural architectural transformation:
1. Toolchain Single Source of Truth (`.go-version` at Go `1.27.1`) dynamically imported by the root `Makefile` and native `actions/setup-go@v5` module caching.
2. Automated coverage documentation synchronization via `scripts/sync-coverage-docs.py` and `make sync-coverage-docs` (0.0% drift).
3. Pinned GitHub Actions supply chain governance (`verification/github-actions-lock.json` via `tools/actionpin`).
4. Container image manifest inspection resilience with exponential backoff retries (`scripts/verify-images.sh`).
5. PR-scoped concurrency with safe preemption rules across all PR workflows.
6. Formalization of Architecture Decision Record 0009 (`docs/adr/0009-go-1.27-toolchain-and-ci-pipeline-architecture.md`).
7. 4-tier parallel matrix DAG decomposition in `verify.yml` (`preflight` -> `platform-verify` -> 8-way `service-verify-matrix` with `fail-fast: false` -> rollup aggregator anchor `PR gate (verify-pr)`).
8. Automated headless Newman API integration and E2E saga testing in CI (`lgtm-e2e.yml`) using mapped loopback endpoints (`http://127.0.0.1:<PORT>`).

However, developer operational runbooks—most notably `docs/runbooks/ci-cd-operations.md`—still contain legacy descriptions, lacking documentation of the 4-tier parallel DAG topology, Newman host loopback network resolution, and the database pool lazy-wiring requirement (`MinConns = 0`).

## What Changes
- Update `docs/runbooks/ci-cd-operations.md` to:
  - Document the 4-tier parallel matrix DAG in `verify.yml` and its component tiers.
  - Document the automated headless Newman execution in `lgtm-e2e.yml` and its loopback networking model (`127.0.0.1:<PORT>`).
  - Document the unit testing `pgxpool` lazy connection initialization requirement (`MinConns = 0`).
  - Formalize the local developer pre-push gate (`make pre-push`, `.githooks/pre-push`, `make install-hooks`).
  - Cross-reference ADR 0009 and Notion architecture guide `3eec4b21-deb4-8186-abc7-d0715d40f7bb`.
- Update `docs/README.md` runbook references where appropriate.

## Impact
- **Services Affected**: Documentation only (`docs/runbooks/ci-cd-operations.md`, `docs/README.md`).
- **Breaking Changes**: None. Zero code or schema changes.
