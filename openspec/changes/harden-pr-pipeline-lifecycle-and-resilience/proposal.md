# Proposal: Harden PR Pipeline Lifecycle and Event Trigger Reliability

## Why
While PR #44 and PR #45 established toolchain single-source-of-truth (`.go-version`), native `actions/setup-go` caching, PR-scoped concurrency, and step summary reporting, the pipeline lifecycle requires explicit event trigger typing and working tree cleanliness guardrails to guarantee that every new pull request opened against `main` runs deterministically to green completion without race conditions or manual retries:
1. **Ambiguous Default PR Triggers**: Several workflows rely on implicit default pull request activity types. Explicitly declaring `types: [opened, synchronize, reopened]` ensures predictable dispatching across `verify.yml`, `lgtm-e2e.yml`, `deployment-validation.yml`, and `gitleaks.yml`.
2. **Git Checkout History Consistency**: Workflows evaluating git history, diffs, or secrets (e.g. `gitleaks.yml` and `verify.yml`) must explicitly specify `fetch-depth: 0` to prevent shallow clone ambiguity against synthetic PR merge refs (`refs/pull/<PR>/merge`).
3. **Pre-Push Validation Gate Enforceability**: Ensure that the pre-push hook `.githooks/pre-push` guarantees complete local parity before any branch is pushed to origin.

## What Changes
- **Explicit PR Activity Types**: Explicitly define `types: [opened, synchronize, reopened]` on all PR-triggered workflows (`verify.yml`, `lgtm-e2e.yml`, `deployment-validation.yml`, `gitleaks.yml`).
- **Full History Retrieval on PR Checkouts**: Ensure `actions/checkout` specifies `fetch-depth: 0` across diff-evaluating and secret-scanning jobs.
- **Strict Required Status Check Compatibility**: Preserve exact status check contexts required by branch protection (`PR gate (verify-pr)`, `Deployment validation (report only)`, `Gitleaks secret scan`).
- **Live PR Open Verification**: Open a feature PR against `main`, arm auto-merge, and monitor all runs until full green success.

## Impact
- **Services Affected**: All workflows in `.github/workflows/`, root `Makefile`, `.githooks/`.
- **Breaking Changes**: None. 100% backward-compatible.
