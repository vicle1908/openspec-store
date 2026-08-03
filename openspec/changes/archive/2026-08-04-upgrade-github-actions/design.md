## Why

All GitHub Actions are outdated (v4/v5/v6) while latest stable versions are
v7/v8. This causes Node.js 20 deprecation warnings and misses security patches.

## Current → Target

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
