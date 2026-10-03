# Tasks: Modernize CI Matrix Architecture, Single Source of Truth Toolchain, and PR Governance

## 1. Single Source of Truth Toolchain & Caching

- [x] 1.1 Create root `.go-version` containing `1.27.1` in `go-microservices`
- [x] 1.2 Update root `Makefile` to derive `GO_VERSION ?= $(shell cat .go-version 2>/dev/null || echo "1.27.1")`
- [x] 1.3 Update `.github/workflows/{verify.yml,lgtm-e2e.yml,gitops-reconcile.yml,release-evidence.yml}` to use `actions/setup-go` with `go-version-file: '.go-version'` and `cache: true`
- [x] 1.4 Remove redundant/collision-prone `actions/cache` steps targeting `~/go/pkg/mod` from workflows

## 2. Four-Tier Parallel Verification DAG in `verify.yml`

- [x] 2.1 Update `.github/workflows/verify.yml` with single-source toolchain setup and heredoc step summary
- [x] 2.2 Add `$GITHUB_STEP_SUMMARY` markdown reporting in the `verify-pr` job
- [x] 2.3 Verify workflow syntax using actionlint and python actionpin checks

## 3. Local Parity & Guidance Validation

- [x] 3.1 Verify local root Make targets (`make pre-push`, `make validate-agent-guidance`, `make validate-documentation`, `make -C platform verify`) pass with 0 errors
- [x] 3.2 Verify git diff hygiene (`git diff --check`)

## 4. OpenSpec Lifecycle & PR Merge

- [x] 4.1 Validate OpenSpec change strictly: `openspec validate modernize-ci-matrix-and-pr-governance --strict --store openspec-store`
- [x] 4.2 Commit and push changes to feature branch `feat/modernize-ci-matrix-and-pr-governance`
- [x] 4.3 Create PR #44, arm auto-merge, monitor GitHub Actions runs to completion, and merge into `main` (commit `b9cf0f8`)
- [x] 4.4 Archive OpenSpec change in `openspec-store` and push to remote `main`
