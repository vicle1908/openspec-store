## Why

The primary APFS data volume is 88% full, and the current inventory identifies large user, developer, VM, cache, and Trash locations without an approval-gated record for any cleanup. This change establishes a read-only evidence trail and prevents deletion of personal data, active state, or VM files without explicit target approval.

## What Changes

- Record filesystem boundaries and exclude the nonstandard Nicegram wrapper and network/FUSE mounts from interpretation.
- Record bounded size, age, Docker, and Trash evidence using paths, sizes, dates, and risk classifications only.
- Define an approval gate requiring exact cleanup targets before any mutation.
- Define app-native cleanup procedures for Docker, npm/pnpm, Xcode/Simulator, and Homebrew.
- Keep all destructive cleanup tasks unchecked until explicit approval and post-action verification.
- Non-goals: deleting files, emptying Trash, pruning Docker resources, clearing caches, changing applications, or modifying active repositories in this change.

## Capabilities

### New Capabilities

- `disk-space-audit`: Read-only, filesystem-aware inventory of large and old storage with confidence and cleanup-risk classification.
- `approval-gated-cleanup`: Exact-target approval and verification rules for any subsequent cleanup action.

### Modified Capabilities

None.

## Impact

- Affected ownership boundaries: workstation filesystem, Docker Desktop-managed VM storage, Xcode/Simulator-managed storage, package-manager caches, user data, and OpenSpec evidence.
- No production application code or active repository source is changed.
