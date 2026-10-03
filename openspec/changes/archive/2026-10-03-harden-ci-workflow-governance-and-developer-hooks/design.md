# Design: Harden CI Workflow Governance, Concurrency, and Developer Pre-Push Hooks

## Architecture Overview
This change hardens the CI/CD pipelines across `go-microservices` by:
1. **Intelligent Workflow Concurrency**: Standardizing concurrency groups across all workflows with PR-scoped preemption (`cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`), canceling superseded PR builds immediately upon new pushes while safeguarding `main` runs.
2. **Fast-Fail Preflight Gate Partitioning**: Structuring fast governance checks (`tools/agentguide`, `scripts/sync-coverage-docs.py --check`, `make validate-documentation`, actionpinning) at the start of `PR gate (verify-pr)` in `.github/workflows/verify.yml` before running the heavy multi-service test suites, reducing developer feedback cycle for lint/doc regressions to < 45 seconds.
3. **Step Summary Streaming**: Augmenting `scripts/sync-coverage-docs.py` and `scripts/verify-images.sh` to output structured Markdown status tables to `$GITHUB_STEP_SUMMARY` when running under GitHub Actions.
4. **Automated Git Pre-Push Hook Provisioning**: Providing a tracked `.githooks/pre-push` running `make pre-push` and Makefile targets `setup-hooks` / `install-hooks` to configure `git config core.hooksPath .githooks`.

---

## Detailed Component Design

### 1. Workflow Concurrency Specification
Across `.github/workflows/{verify.yml,lgtm-e2e.yml,deployment-validation.yml,gitops-reconcile.yml,release-evidence.yml}`:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```
- **PR Updates**: `github.event.pull_request.number || github.ref` groups runs per pull request. When a developer pushes a new commit to an active PR, any running job for the preceding commit is terminated immediately, freeing up runner capacity.
- **`main` Protection**: For pushes to `main`, `cancel-in-progress` evaluates to `false`. Post-merge deployments, evidence captures, and GitOps reconciliations are never cancelled.

### 2. Fast-Fail Preflight & Required Status Check Contract
The required status check context in GitHub branch protection is strictly:
`PR gate (verify-pr)`
To preserve 100% compatibility with branch protection and auto-merge:
- The job in `verify.yml` retains `name: PR gate (verify-pr)`.
- Preflight steps are ordered first:
  1. `actions/checkout`
  2. `actions/setup-go@v5` (Go 1.27.1 SSOT via `.go-version` with dual-tier module and build caching)
  3. Action pinning verification (`tools/actionpin/actionpin.py`)
  4. Agent guidance word-count bounds (`make validate-agent-guidance`)
  5. Coverage documentation table synchronization (`python3 scripts/sync-coverage-docs.py --check`)
  6. Documentation currency verification (`make validate-documentation`)
  7. Container image manifest verification (`./scripts/verify-images.sh`)
  8. Service verification loop across 8 microservices
  9. PR gate summary table generation (`$GITHUB_STEP_SUMMARY`)

### 3. Step Summary Markdown Generation
- `scripts/sync-coverage-docs.py`: If `GITHUB_STEP_SUMMARY` is present in the environment, append the Markdown table of service statement coverage metrics directly to the summary file.
- `scripts/verify-images.sh`: If `GITHUB_STEP_SUMMARY` is present in the environment, append the list of verified image tags and platforms.

### 4. Git Hooks Configuration
- Track `.githooks/pre-push` with executable permissions.
- In root `Makefile`:
  ```makefile
  .PHONY: setup-hooks install-hooks
  setup-hooks install-hooks: ## Configure git to use repository pre-push hooks (.githooks/)
  	@git config core.hooksPath .githooks
  	@chmod +x .githooks/*
  	@echo "Local git hooks configured to .githooks/"
  ```
