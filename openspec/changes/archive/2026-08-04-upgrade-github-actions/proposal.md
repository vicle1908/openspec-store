## Why

GitHub Actions are outdated. The repo uses v4/v5/v6 while latest stable
versions are v7/v8 for most actions. Upgrading brings:

- Node.js 24 support (Node 20 deprecated)
- Performance improvements
- Security patches
- New features

## Current State

| Action | Current | Latest |
|--------|---------|--------|
| actions/checkout | v4 | v7 |
| actions/setup-go | v5 | v7 |
| actions/cache | v4 | v6 |
| actions/upload-artifact | v4 | v7 |
| actions/download-artifact | v4 | v8 |
| docker/setup-buildx-action | v3 | v4 |
| docker/setup-qemu-action | v3 | v4 |
| docker/login-action | v3 | v4 |
| docker/build-push-action | v6 | v7 |
| actions/create-github-app-token | v1 | v3 |
| actions/setup-node | v4 | v7 |

## Capabilities

### Modified Capabilities

- `ci-workflow-upgrades`: All workflows use latest stable action versions

## Impact

- **Ownership boundary:** CI/CD infrastructure only
- **Repository surfaces:** `.github/workflows/*.yml`
- **Compatibility:** Backward compatible (v7 is stable release)
