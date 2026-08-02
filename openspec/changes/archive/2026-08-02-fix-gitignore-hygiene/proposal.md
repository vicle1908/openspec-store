## Why

The `.gitignore` was missing patterns for common build artifacts and temporary
files, causing tracked `.pyc` files and untracked junk in `git status`.

## What Changes

- Added `__pycache__/`, `*.pyc`, `*.bak` to `.gitignore`
- Added `tools/agentguide/agentguide` to compiled binaries section
- Removed 5 tracked `.pyc` files from git index (`git rm --cached`)

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. Repository tooling hygiene only.

## Impact

- **Ownership boundary:** Repository tooling and hygiene only.
- **Repository surfaces:** `.gitignore` only.
- **Contracts and data:** No service, API, database, or event changes.
- **Rollout:** Commit the `.gitignore` update and index cleanup.
- **Rollback:** Re-add files to the git index if needed.
