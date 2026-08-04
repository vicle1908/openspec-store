## Why

Security audit reveals 3 critical gaps against 2025/2026 best practices:

1. **Actions use mutable tags** (`@v7`) not SHA-pinned — supply chain attack vector.
   The tj-actions/reviewdog incident (March 2025, CVE-2025-30066) demonstrated
   that tag-based references can be hijacked. GitHub's Aug 2025 policy now supports
   blocking unpinned actions org-wide.

2. **No OpenSSF Scorecard** — no continuous visibility into supply-chain security
   posture. Critical checks (Pinned-Dependencies, Token-Permissions, Branch-Protection)
   should be automated.

3. **No secret scanning** — gitleaks or equivalent not in CI. Accidentally committed
   secrets may not be caught before push.

## What Changes

- Pin all GitHub Actions to full commit SHAs with version comments
- Add OpenSSF Scorecard workflow (weekly + push to main)
- Add gitleaks secret scanning to CI
- Add `go mod verify` step for dependency integrity
- Shorten artifact retention to 30 days maximum

## Impact

- **Scope:** `.github/workflows/`, `.github/dependabot.yml`
- **Risk:** Low — all changes are additive CI hardening
- **Rollback:** Revert workflow file changes
- **No service code changes**
