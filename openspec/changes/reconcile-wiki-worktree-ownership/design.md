## Context
`wiki-cron-validator` is a detached worktree, not a separate repository. The canonical owner is `wiki`.
## Decisions
- Preserve canonical `wiki` checkout.
- Require zero active Orca/OpenSpec references before retirement.
- Keep the detached view if ownership remains ambiguous.
## Risks / Trade-offs
Retiring a useful working view can disrupt current work; fail closed on ambiguity.
