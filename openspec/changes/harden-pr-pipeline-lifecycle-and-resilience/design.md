# Design: Harden PR Pipeline Lifecycle and Event Trigger Reliability

## Architecture Overview
This change guarantees deterministic and failure-free execution whenever a Pull Request is opened against `main` in `go-microservices` by:
1. **Explicit Activity Types**: Standardizing `pull_request` triggers to explicitly include `types: [opened, synchronize, reopened]` across `.github/workflows/{verify.yml,lgtm-e2e.yml,deployment-validation.yml,gitleaks.yml,integration.yml}`.
2. **Deep History Checkout**: Ensuring `actions/checkout` specifies `fetch-depth: 0` in all jobs that perform git diffing, retention verification, or secret scanning (`verify.yml`, `gitleaks.yml`).
3. **Preserving Branch Protection Contract**: Ensuring exact job names required by branch protection (`PR gate (verify-pr)`, `Deployment validation (report only)`, `Gitleaks secret scan`) are retained verbatim.
4. **End-to-End Live Verification**: Validating the pipeline by opening a live feature PR, enabling auto-merge, monitoring all workflow checks to green completion, and confirming auto-merge.

---

## Detailed Component Design

### 1. Explicit PR Activity Types
In `.github/workflows/verify.yml`, `lgtm-e2e.yml`, `deployment-validation.yml`, `gitleaks.yml`, `integration.yml`:
```yaml
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
```
This guarantees that GitHub Actions runner scheduling triggers consistently when PRs are opened, new commits are pushed, or closed PRs are reopened.

### 2. Full History Checkout (`fetch-depth: 0`)
In `.github/workflows/verify.yml`:
```yaml
      - name: Checkout
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          submodules: true
          fetch-depth: 0
```
This ensures tools such as `scripts/verify-retention.py` and `git diff` can reliably resolve `origin/main` without git shallow clone depth errors.

### 3. Verification & Live PR Monitoring
- Pre-push validation via `make pre-push` ensures local parity before opening the PR.
- Auto-merge via `gh pr merge --auto --merge` tests the end-to-end vestibule lifecycle.
