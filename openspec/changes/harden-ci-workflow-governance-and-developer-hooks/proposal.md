# Proposal: Harden CI Workflow Governance, Concurrency, and Developer Pre-Push Hooks

## Why
While PR #43 and PR #44 established baseline network retry resilience, automated coverage table synchronization, Go toolchain single-source-of-truth (`.go-version`), and step summaries, several operational and governance gaps remain in the PR and CI/CD pipelines:
1. **Unscoped Concurrency Thrashing**: Workflow concurrency currently lacks PR-scoped cancellation. Rapid successive pushes queue redundant builds that waste runner capacity and risk cancelling post-merge runs on `main` if configured with unconditional cancellation.
2. **Missing In-Line CI Visibility**: Test results, statement coverage metrics, and container image verification status are buried inside raw logs rather than surfaced directly in GitHub Actions step summaries (`$GITHUB_STEP_SUMMARY`).
3. **Manual Pre-Push Execution**: Developers must remember to run `make pre-push` manually before pushing. Without an automated git hook installer, preventable lint or doccheck failures still reach remote PRs.
4. **Supply Chain Pinning**: External actions must be kept fully pinned to immutable commit SHAs with semantic version tags as tracked in `verification/github-actions-lock.json` and validated by `tools/actionpin/actionpin.py`.

## What Changes
- **PR-Scoped Workflow Concurrency**: Standardize concurrency across all PR workflows (`verify.yml`, `lgtm-e2e.yml`, `deployment-validation.yml`, `gitops-reconcile.yml`, `release-evidence.yml`) using `group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}` with `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`.
- **Fast-Fail Preflight Gate Structuring in `verify.yml`**: Organize lightweight governance and static checks (`validate-agent-guidance`, `sync-coverage-docs.py --check`, `make validate-documentation`, actionpinning) at the start of the job before long service test loops.
- **Rich Step Summaries (`$GITHUB_STEP_SUMMARY`)**: Update `scripts/sync-coverage-docs.py` and `scripts/verify-images.sh` to emit structured Markdown tables to GitHub Actions summaries when `$GITHUB_STEP_SUMMARY` is present.
- **Automated Git Pre-Push Hook Installer (`make install-hooks`)**: Provide a tracked `.githooks/pre-push` running `make pre-push` and a `make install-hooks` target that configures `git config core.hooksPath .githooks`.

## Impact
- **Services Affected**: All CI workflows (`.github/workflows/`), root `Makefile`, `scripts/`, and `.githooks/`.
- **Breaking Changes**: None. The required status check name `PR gate (verify-pr)` remains identical.
