## Current State

All GitHub Actions use mutable tag references:
```yaml
uses: actions/checkout@v7        # not pinned
uses: actions/setup-go@v7        # not pinned
uses: docker/build-push-action@v7 # not pinned
```

Only one action is SHA-pinned:
```yaml
uses: aquasecurity/trivy-action@a9c7b0f06e461e9d4b4d1711f154ee024b8d7ab8 # v0.36.0
```

No OpenSSF Scorecard workflow exists. No secret scanning in CI.

## Recommended Approach

### 1. SHA Pin All Actions

Pin to full 40-char SHA with version comment. Use `pinact` or `actions-up`
to bootstrap, then Dependabot maintains updates:

```yaml
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
uses: actions/setup-go@d35c59abb061a4a6fb18e82ac0862c26744d6ab5 # v6.0.0
```

**Critical:** After the tj-actions/reviewdog incident, SHA pinning is the only
defense against tag-repointing attacks. Dependabot already configured for
`github-actions` — it will auto-propose SHA updates.

### 2. Add OpenSSF Scorecard

Weekly scheduled scan + push to main. Publish SARIF to GitHub Security tab.
Treat Critical checks (Dangerous-Workflow, Pinned-Dependencies, Token-Permissions)
as merge blockers.

```yaml
name: scorecard
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 3 * * 0'

permissions:
  contents: read
  id-token: write
  security-events: write

jobs:
  scorecard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<sha>  # v4
        with:
          persist-credentials: false
      - uses: ossf/scorecard-action@<sha>  # v2
        with:
          results_format: sarif
          results_file: results.sarif
          publish_results: true
      - uses: github/codeql-action/upload-sarif@<sha>  # v3
        with:
          sarif_file: results.sarif
      - uses: actions/upload-artifact@<sha>  # v4
        with:
          name: scorecard-sarif
          path: results.sarif
          retention-days: 7
```

### 3. Add Gitleaks Secret Scanning

```yaml
- name: Scan for secrets
  uses: gitleaks/gitleaks-action@<sha>  # v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4. Add go mod verify

```yaml
- name: Verify Go module integrity
  run: go mod verify
```

### 5. Shorten Artifact Retention

Change all `retention-days: 90` to `retention-days: 30` and
`retention-days: 365` to `retention-days: 30`.
