## Why
The wiki validator path is a detached worktree of the canonical `wiki` repository, and ownership should be explicit.
## What Changes
- Verify Orca/OpenSpec/Git references to the detached worktree.
- Document canonical ownership and retirement prerequisites.
- Retire only if all authorities release it.
## Capabilities
None; lifecycle audit (`skip_specs: true`).
## Impact
`wiki` worktree registry, Orca references, and evidence only.
