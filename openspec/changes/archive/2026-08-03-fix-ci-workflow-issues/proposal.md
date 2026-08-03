## Why

The CI/CD workflow analysis identified 3 critical issues that need immediate attention:

1. **Inconsistent action versions** — checkout, setup-go, cache, upload-artifact all
   have mixed versions (v4/v5/v6/v7) across workflows. This creates security risks,
   inconsistent behavior, and maintenance burden.

2. **Skill restore in verify.yml** — CI copies skills from `.codex/skills/` which is
   gitignored. This is fragile and breaks when the directory doesn't exist on CI.

3. **No workflow linting** — No actionlint integration to catch YAML issues, syntax
   errors, or deprecated patterns.

## What Changes

- Standardize all action versions to latest stable with SHA pinning
- Fix skill restore mechanism in verify.yml
- Add actionlint to CI pipeline

## Capabilities

### Modified Capabilities

- `ci-workflow-standardization`: All workflows use consistent action versions
- `ci-skill-restore`: Verify workflow properly handles skill restoration
- `ci-workflow-linting`: Actionlint validates all workflow files

## Impact

- **Ownership boundary:** CI/CD infrastructure only
- **Repository surfaces:** `.github/workflows/*.yml`
- **Contracts and data:** No service, API, or contract changes
- **Compatibility:** Existing CI behavior preserved
- **Rollout:** Commit, push PR, verify CI passes
- **Rollback:** Revert workflow file changes
