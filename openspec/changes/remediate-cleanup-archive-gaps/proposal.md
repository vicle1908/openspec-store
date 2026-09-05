## Why

Recent cleanup archives are structurally complete but contain unproven operational claims: the ecosystem cleanup has no durable live-state evidence, and the corrupted-cask cleanup checked manual sideload repairs while its verification only established wrapper metadata. A corrective change is needed to record value-blind verification and keep unresolved user-owned work explicit without rewriting immutable archive history.

## What Changes

- Add a corrective, value-blind evidence register for the archived ecosystem and corrupted-cask cleanup claims.
- Re-run safe read-only workspace checks for repository status, virtual-environment presence, worktree counts, and embedded-copy comparison.
- Verify the two sideloaded applications by checking their actual wrapper executables, not only plist presence.
- Record the sideloaded application verification result conditionally: if both executables verify, record the archived gap as currently resolved with metadata-only evidence; if either check fails, keep manual reinstall requirements blocked and user-owned rather than silently treating them as complete.
- Preserve the archived change directories unchanged.

## Capabilities

### New Capabilities

- cleanup-archive-verification: Durable, value-blind verification and blocker recording for cleanup archive claims.

### Modified Capabilities

- None.

## Non-goals

- Do not edit files under `openspec/changes/archive/`.
- Do not delete worktrees, repositories, applications, or user data.
- Do not reinstall or remove applications.
- Do not change credentials, provider configuration, or unrelated active changes.
- Do not archive this corrective change until its evidence tasks are actually verified.

## Ownership Boundaries

- The OpenSpec store owns the corrective evidence and ledger.
- Repository owners own any unrelated dirty worktrees or uncommitted files.
- The user owns manual sideloaded-application reinstall decisions and execution.
