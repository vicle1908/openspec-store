# Proposal: Modernize CI Matrix Architecture, Single Source of Truth Toolchain, and PR Governance

## Why
While PR #43 established baseline network resiliency (`scripts/verify-images.sh` retries/dedup) and automated coverage table synchronization (`make sync-coverage-docs`), the primary GitHub Actions verification pipeline (`.github/workflows/verify.yml`) remains a monolithic sequential execution loop:
1. **Monolithic Sequential Feedback Bottleneck**: All verification steps (linting, action pinning, guidance, doccheck, platform tests, and tests for all 8 microservices) run sequentially in a single job (`verify-pr`) taking 19 to 23 minutes. If Service 7 fails, developers wait nearly 20 minutes before receiving feedback, and zero signal is obtained for Service 8.
2. **Triplicate Go Toolchain Declaration**: Go versions are independently declared in `go.mod` files, the root `Makefile` (`GO_VERSION := 1.27.1`), and four GitHub Actions workflow YAML files (`verify.yml`, `lgtm-e2e.yml`, `gitops-reconcile.yml`, `release-evidence.yml`). Upgrades require manual edits across all files, risking toolchain drift.
3. **Redundant Module Caching**: Separate `actions/cache` steps risk file permission collisions when bootstrap tools write into `~/go/pkg/mod` with read-only permissions (`0555`).

## What Changes
- **Single Source of Truth Toolchain (`.go-version`)**:
  - Add root `.go-version` specifying `1.27.1`.
  - Migrate all workflow files (`verify.yml`, `lgtm-e2e.yml`, `gitops-reconcile.yml`, `release-evidence.yml`) to use `actions/setup-go@v5` with `go-version-file: '.go-version'` and native `cache: true` on `**/go.sum`.
  - Remove separate `actions/cache` steps that conflict with read-only module directories.
- **Matrix Parallelism with Aggregator Anchor (`verify-pr`)**:
  - Decompose monolithic `verify.yml` into a 4-tier parallel DAG:
    1. `preflight`: Module integrity, Action pinning, Actionlint, Agent guidance, Documentation currency (~1m).
    2. `platform-verify`: Shared `platform/` module build, vet, and unit tests (~1.5m).
    3. `services-verify`: Parallel matrix over the 8 microservices (`fail-fast: false`) compiling, testing, and asserting $\ge 80.0\%$ statement coverage (~2.5m).
    4. `verify-pr`: Lightweight aggregator anchor (`needs: [preflight, platform-verify, services-verify]`, `if: always()`) that evaluates upstream job conclusions and satisfies GitHub branch protection.
- **Live Markdown Step Summary (`$GITHUB_STEP_SUMMARY`)**:
  - Add live Markdown reporting to the PR run summary, detailing per-service coverage percentages, test counts, and execution status.

## Impact
- **Services Affected**: All 8 microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), shared `platform/` module, and CI workflows.
- **Performance Impact**: Reduces PR feedback loop from ~23 minutes down to ~3.5 minutes.
- **Branch Protection**: 100% backward-compatible. The required status check name `PR gate (verify-pr)` remains identical.
