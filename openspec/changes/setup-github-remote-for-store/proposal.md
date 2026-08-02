## Why

The openspec-store currently has no git remote configured. Teammates cannot
clone and register the store, and `openspec store doctor` cannot print
actionable clone instructions. The `store.yaml` lacks the `remote` field
that the official pattern recommends for team onboarding.

## What Changes

- Create a GitHub repository for the openspec-store
- Add the git remote to the local store checkout
- Update `.openspec-store/store.yaml` with the `remote` field
- Push the store to GitHub
- Verify `openspec store doctor` prints the clone URL

## Capabilities

### New Capabilities

- `store-github-remote`: Configures the store's git remote for team sharing and updates store.yaml with the clone URL

### Modified Capabilities

- None

## Impact

- **Store structure:** No directory changes — only `store.yaml` updated
- **Team onboarding:** `openspec store doctor` will print clone + register instructions
- **No application code change:** This is a planning-store-only change
- **Risk:** LOW — adds a remote URL, does not modify specs or changes

## Non-Goals

- CI/CD setup for the repository
- Branch protection rules
- GitHub Actions workflows
- Modifying any code repos
