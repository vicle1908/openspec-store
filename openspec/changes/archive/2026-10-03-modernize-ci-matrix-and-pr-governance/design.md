# Design: Modernize CI Matrix Architecture, Single Source of Truth Toolchain, and PR Governance

## Architecture Overview
This change modernizes the primary GitHub Actions verification pipeline (`.github/workflows/verify.yml`) and related workflows in `go-microservices` by:
1. Establishing `.go-version` as the single source of truth for the Go toolchain across all workflows and root `Makefile`.
2. Migrating to `actions/setup-go@v5` native caching with `go-version-file: '.go-version'` and `cache: true`, eliminating external `actions/cache` steps that cause tar permission collisions on read-only module directories.
3. Decomposing the monolithic 23-minute sequential `verify-pr` job into a 4-tier parallel DAG with matrix fan-out across the 8 microservices, while preserving the exact required status check name `PR gate (verify-pr)` via a lightweight aggregator job.
4. Adding live `$GITHUB_STEP_SUMMARY` Markdown reporting on coverage and test execution.

---

## Detailed Component Design

### 1. Single Source of Truth Toolchain (`.go-version`)
- Create root `.go-version` containing `1.27.1`.
- In `.github/workflows/{verify.yml,lgtm-e2e.yml,gitops-reconcile.yml,release-evidence.yml}`, update the `actions/setup-go` step:
  ```yaml
  - name: Install Go
    uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
    with:
      go-version-file: '.go-version'
      cache: true
      cache-dependency-path: '**/go.sum'
  ```
- Remove redundant `actions/cache` steps targeting `~/go/pkg/mod`.
- Update root `Makefile` to dynamically read `GO_VERSION ?= $(shell cat .go-version 2>/dev/null || echo "1.27.1")`.

### 2. Four-Tier Parallel Verification DAG
Instead of running sequentially in one 23-minute job, decompose `verify.yml` into four coordinated jobs:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  Four-Tier Verification DAG                            │
├─────────────────────┬──────────────────────────┬───────────────────────────────────────┤
│    Tier 1: Lint     │   Tier 2: Platform       │         Tier 3: Services              │
│ (actionpin, guide,  │ (shared contracts &      │    (parallel matrix of 8 services)    │
│  doccheck, modules) │  runtime packages)       │ [catalog, customer, inventory, ...]   │
│     (~1.0 min)      │     (~1.5 min)           │           (~2.5 min)                  │
└──────────┬──────────┴────────────┬─────────────┴───────────────────┬───────────────────┘
           │                       │                                 │
           └───────────────────────┼─────────────────────────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │      Tier 4: verify-pr       │
                    │   (Lightweight Aggregator)   │
                    │ - Evaluates all upstream     │
                    │ - Preserves Branch Gate Name │
                    │ - Generates Step Summary     │
                    └──────────────────────────────┘
```

#### Tier 1: `lint-and-governance`
Runs fast-fail static checks:
- Verify Go module integrity (`scripts/verify-go-modules.sh`)
- Validate pinned GitHub Actions (`tools/actionpin/actionpin.py`)
- Actionlint on workflow files
- Agent guidance validation (`make validate-agent-guidance`)
- Coverage documentation parity (`python3 scripts/sync-coverage-docs.py --check`)
- Documentation currency validation (`make validate-documentation`)

#### Tier 2: `platform-verify`
Compiles and tests the shared module:
- `make -C platform verify`

#### Tier 3: `services-verify` (Matrix Fan-Out)
Runs in parallel with `fail-fast: false` across the 8 microservices:
```yaml
strategy:
  fail-fast: false
  matrix:
    service:
      - catalog-service
      - customer-service
      - inventory-service
      - notification-service
      - order-service
      - payment-service
      - reporting-service
      - shipping-service
```
Each matrix instance:
- Lints with `gofmt -l`, `go vet`, and `golangci-lint` (using per-service `.golangci.yml`)
- Executes test suite with race detector (`go test -race ./...`)
- Enforces statement coverage $\ge 80.0\%$ (`./scripts/check-coverage.sh ${{ matrix.service }} 80`)

#### Tier 4: `verify-pr` (Aggregator Anchor)
- Depends on `[lint-and-governance, platform-verify, services-verify]`.
- Runs with `if: always()`.
- Checks the conclusion of each upstream job: if any failed or was cancelled, exits 1.
- Satisfies the exact GitHub branch protection context `PR gate (verify-pr)`.
- Writes a live summary table to `$GITHUB_STEP_SUMMARY`.

---

## Verification & Risk Mitigation
- **Branch Protection Compatibility**: The final aggregator job is named `PR gate (verify-pr)`, exactly matching the current GitHub branch protection required status check.
- **Local Parity**: Developers continue to run `make verify-pr` locally, which executes all gates sequentially or per-service via `make -C services/<service> verify-pr`.
- **Pre-Push Guarantee**: `make pre-push` guarantees all Tier 1 checks pass before push.
