# Proposal: 4-Tier Parallel CI Matrix DAG and Headless Newman E2E Gates

## Why
While PRs #43 through #48 established baseline toolchain single-source-of-truth (`.go-version`), native `actions/setup-go` caching, PR-scoped concurrency, step summary reporting, and tracked pre-push hooks, the primary verification workflow (`.github/workflows/verify.yml`) remains a monolithic sequential bottleneck:
1. **Prolonged Feedback Loops**: A single `ubuntu-latest` runner executes repository preflight, platform verification, and the 8-service unit test and coverage loop serially. Wall-clock execution time ranges from 7m 30s to 8m 30s. If a late-stage service fails, developers wait ~7 minutes before receiving feedback.
2. **Failure Masking & Log Conflation**: Failures in earlier services abort subsequent service checks, preventing developers from seeing complete monorepo health in a single PR run.
3. **Missing Automated E2E Quality Gates**: The comprehensive Postman Collection and Newman runner implemented in PR #41 (`tests/postman/`) runs only ad-hoc locally and is not yet enforced as an automated quality gate in CI.

## What Changes
- **4-Tier Parallel Matrix DAG in `verify.yml`**:
  - Decompose `verify.yml` into a 4-tier DAG:
    1. `preflight`: Fast-fail static checks (module integrity, action pinning, guidance word bounds, coverage documentation parity, doccheck) (~45s).
    2. `platform-verify`: Shared `platform/` module build and unit tests (~1m 15s).
    3. `service-verify-matrix`: Parallel matrix across the 8 microservices (`fail-fast: false`) compiling, testing, and asserting $\ge 80.0\%$ statement coverage (~2m 15s).
    4. `verify-pr`: Lightweight fan-in aggregation rollup job that evaluates all upstream results, emits a unified `$GITHUB_STEP_SUMMARY`, and satisfies the exact required status check context name `PR gate (verify-pr)`.
- **Automated Headless Newman CI Quality Gate in `lgtm-e2e.yml`**:
  - Add an automated step in `.github/workflows/lgtm-e2e.yml` executing `make newman-all` after the Compose stack converges, publishing JUnit XML test reports via `actions/upload-artifact`.
- **Branch Protection Compatibility**:
  - Retain the exact required context `PR gate (verify-pr)` in the fan-in aggregator, maintaining 100% backward compatibility with branch protection and auto-merge.

## Impact
- **Services Affected**: `.github/workflows/verify.yml`, `.github/workflows/lgtm-e2e.yml`, `verification/github-actions-lock.json`.
- **Performance Impact**: Reduces PR turnaround from ~8 minutes down to ~2.5–3.0 minutes (~65% reduction) with complete log isolation per service.
- **Breaking Changes**: None. 100% backward-compatible.
