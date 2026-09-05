## Why
The `wiki-cron-validator` path is currently a clean detached worktree of the canonical `wiki` repository at revision `3b610d5`; ownership and retention should be explicit before any future removal.
## What Changes
- Verify Orca/OpenSpec/Git references to the detached worktree.
- Document canonical ownership and retirement prerequisites.
- Retire only if all authorities release it.
## Capabilities
None; lifecycle audit (`skip_specs: true`).
## Impact
`wiki` worktree registry, Orca references, and evidence only.
