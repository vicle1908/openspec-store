# Tasks: Harden PR Pipeline Lifecycle and Event Trigger Reliability

## 1. Workflow Trigger & Checkout Standardization

- [ ] 1.1 Update `pull_request` triggers in `.github/workflows/verify.yml` with explicit `types: [opened, synchronize, reopened]`
- [ ] 1.2 Update `pull_request` triggers in `.github/workflows/lgtm-e2e.yml` with explicit `types: [opened, synchronize, reopened]`
- [ ] 1.3 Update `pull_request` triggers in `.github/workflows/deployment-validation.yml` with explicit `types: [opened, synchronize, reopened]`
- [ ] 1.4 Update `pull_request` triggers in `.github/workflows/gitleaks.yml` with explicit `types: [opened, synchronize, reopened]`
- [ ] 1.5 Update `pull_request` triggers in `.github/workflows/integration.yml` with explicit `types: [opened, synchronize, reopened]`

## 2. Supply Chain & Action Pinning Verification

- [ ] 2.1 Verify action pinning across all workflows using `python3 tools/actionpin/actionpin.py --root . --lock verification/github-actions-lock.json`
- [ ] 2.2 Verify actionlint passes cleanly on all modified workflow files

## 3. Local Parity & Pre-Push Gate

- [ ] 3.1 Verify local pre-push validation (`make pre-push`) passes with 0 errors
- [ ] 3.2 Verify clean git status and zero uncommitted/untracked artifacts

## 4. Live PR Verification & Archival Lifecycle

- [ ] 4.1 Validate OpenSpec change strictly: `openspec validate harden-pr-pipeline-lifecycle-and-resilience --strict --store openspec-store`
- [ ] 4.2 Create feature branch `feat/harden-pr-pipeline-lifecycle-and-resilience` and commit adjustments
- [ ] 4.3 Push branch and open Pull Request #46 with `gh pr create`
- [ ] 4.4 Enable auto-merge and monitor GitHub Actions workflow runs to completion
- [ ] 4.5 Verify all required checks (`PR gate (verify-pr)`, `Deployment validation (report only)`, `Gitleaks secret scan`) pass green on open and PR merges
- [ ] 4.6 Sync local `main`, archive OpenSpec change in `openspec-store`, and push to remote `main`
