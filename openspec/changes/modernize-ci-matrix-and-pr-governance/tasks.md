# Tasks: Modernize CI Matrix Architecture, Single Source of Truth Toolchain, and PR Governance

## 1. Single Source of Truth Toolchain & Caching

- [ ] 1.1 Create root `.go-version` containing `1.27.1` in `go-microservices`
- [ ] 1.2 Update root `Makefile` to derive `GO_VERSION ?= $(shell cat .go-version 2>/dev/null || echo "1.27.1")`
- [ ] 1.3 Update `.github/workflows/{verify.yml,lgtm-e2e.yml,gitops-reconcile.yml,release-evidence.yml}` to use `actions/setup-go` with `go-version-file: '.go-version'` and `cache: true`
- [ ] 1.4 Remove redundant/collision-prone `actions/cache` steps targeting `~/go/pkg/mod` from workflows

## 2. Four-Tier Parallel Verification DAG in `verify.yml`

- [ ] 2.1 Refactor `.github/workflows/verify.yml` to split into 4 tiers:
  - `lint-and-governance`: fast-fail static checks (~1m)
  - `platform-verify`: shared platform tests (~1.5m)
  - `services-verify`: 8-service parallel matrix (`fail-fast: false`, ~2.5m)
  - `verify-pr`: lightweight aggregator anchor preserving exact branch protection check name
- [ ] 2.2 Add `$GITHUB_STEP_SUMMARY` markdown reporting in the `verify-pr` aggregator job
- [ ] 2.3 Verify workflow syntax using actionlint and python actionpin checks

## 3. Local Parity & Guidance Validation

- [ ] 3.1 Verify local root Make targets (`make pre-push`, `make validate-agent-guidance`, `make validate-documentation`, `make -C platform verify`) pass with 0 errors
- [ ] 3.2 Verify git diff hygiene (`git diff --check`)

## 4. OpenSpec Lifecycle & PR Merge

- [ ] 4.1 Validate OpenSpec change strictly: `openspec validate modernize-ci-matrix-and-pr-governance --strict --store openspec-store`
- [ ] 4.2 Commit and push changes to feature branch `feat/modernize-ci-matrix-and-pr-governance`
- [ ] 4.3 Create PR, arm auto-merge, monitor GitHub Actions runs to completion, and merge into `main`
- [ ] 4.4 Archive OpenSpec change in `openspec-store` and push to remote `main`
