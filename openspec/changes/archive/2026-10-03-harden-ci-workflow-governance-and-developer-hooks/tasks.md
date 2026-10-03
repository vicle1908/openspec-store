# Tasks: Harden CI Workflow Governance, Concurrency, and Developer Pre-Push Hooks

## 1. Concurrency Management Across Workflows

- [x] 1.1 Add PR-scoped concurrency block with `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}` to `.github/workflows/verify.yml`
- [x] 1.2 Add PR-scoped concurrency block to `.github/workflows/lgtm-e2e.yml`
- [x] 1.3 Add PR-scoped concurrency block to `.github/workflows/deployment-validation.yml`
- [x] 1.4 Add PR-scoped concurrency block to `.github/workflows/gitops-reconcile.yml`
- [x] 1.5 Add PR-scoped concurrency block to `.github/workflows/release-evidence.yml`

## 2. Fast-Fail Preflight & Step Summaries

- [x] 2.1 Reorder preflight checks in `.github/workflows/verify.yml` so lightweight static checks run before heavy service tests
- [x] 2.2 Update `scripts/sync-coverage-docs.py` to stream Markdown coverage summary table into `$GITHUB_STEP_SUMMARY` when running under GitHub Actions
- [x] 2.3 Update `scripts/verify-images.sh` to output verified container image status into `$GITHUB_STEP_SUMMARY` when present
- [x] 2.4 Verify action pinning across all workflows using `tools/actionpin/actionpin.py`

## 3. Developer Pre-Push Hook Automation

- [x] 3.1 Create tracked `.githooks/pre-push` running `make pre-push` with executable permissions
- [x] 3.2 Add `setup-hooks` and `install-hooks` targets to root `Makefile` configuring `git config core.hooksPath .githooks`

## 4. Local Verification & PR Lifecycle

- [x] 4.1 Validate OpenSpec change strictly: `openspec validate harden-ci-workflow-governance-and-developer-hooks --strict --store openspec-store`
- [x] 4.2 Run local pre-push validation (`make pre-push`) and verify 0 errors
- [x] 4.3 Commit and push to feature branch `feat/harden-ci-workflow-governance-and-developer-hooks`
- [x] 4.4 Create PR #45, arm auto-merge, and monitor GitHub Actions workflow runs to completion
- [x] 4.5 Verify PR merges cleanly into `main` (commit `45d1fd8`), sync local `main`, and clean up feature branches
- [x] 4.6 Mark all tasks complete, validate strictly, archive change in `openspec-store`, and push to remote `main`
