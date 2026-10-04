# Design: Synchronize CI/CD Operations Runbook with Modernized Architecture and 4-Tier Matrix DAG

## Overview
This documentation change synchronizes the central developer operational runbook (`docs/runbooks/ci-cd-operations.md`) and documentation index (`docs/README.md`) across `go-microservices` with the modern CI/CD pipeline architecture, 4-tier parallel matrix DAG, and testing infrastructure established in ADR 0009 and PRs #41 through #50.

---

## Detailed Section Updates

### 1. Workflow Catalog & Architecture Updates (`docs/runbooks/ci-cd-operations.md`)
- Update the workflow summary table:
  - `verify`: Document the 4-tier parallel matrix DAG:
    - Tier 1: `preflight` (fast-fail static checks in ~35s)
    - Tier 2: `platform-verify` (shared module runtime verification in ~1m 15s)
    - Tier 3: `service-verify-matrix` (8-service concurrent matrix with `fail-fast: false` in ~2m 10s)
    - Tier 4: `verify-pr` (rollup aggregator preserving required status check context `PR gate (verify-pr)`)
  - `lgtm-e2e`: Document automated headless Newman API integration and E2E saga suite execution after Compose stack convergence.
  - Required status check contexts:
    - `PR gate (verify-pr)`
    - `Deployment validation (report only)`
    - `Gitleaks secret scan`

### 2. Operational Procedures & Network Resolution
- Document the headless Newman CI execution model:
  - Why Newman executed on the GitHub Actions host runner requires loopback addresses (`http://127.0.0.1:<PORT>`) rather than container hostnames (`http://mailpit:8025`).
- Document PostgreSQL connection pool lazy initialization (`MinConns = 0` in unit test environments) to prevent eager socket connect during wiring in test environments where lazy pool lifecycle hooks are asserted.

### 3. Pre-Push Validation Protocol & Developer Automation
- Detail the local developer pre-push gate:
  - `make install-hooks` / `.githooks/pre-push`
  - `make pre-push` executing `git diff --check`, `make validate-agent-guidance`, `python3 scripts/sync-coverage-docs.py --check`, and `make validate-documentation`
  - `make sync-coverage-docs` for deterministic, zero-drift statement coverage markdown table updates.

### 4. Cross-Reference Alignment
- Cross-reference ADR 0009 (`docs/adr/0009-go-1.27-toolchain-and-ci-pipeline-architecture.md`) and Notion architecture guide `3eec4b21-deb4-8186-abc7-d0715d40f7bb` in `docs/runbooks/ci-cd-operations.md` and `docs/README.md`.
