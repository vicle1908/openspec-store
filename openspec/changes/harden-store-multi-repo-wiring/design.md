# Design: Harden Multi-Repo Store Wiring

## Command Resolution

OpenSpec resolves an invocation in this order: explicit `--store`, nearest
local `openspec/` root, project pointer, machine `defaultStore`, then the
current directory fallback. This change enables only the machine default;
repos remain free of local planning roots and continue to use explicit
`--store openspec-store` in deterministic scripts.

The global setting is written through the supported CLI so it is stored in the
user's OpenSpec config rather than in a repository file. Explicit `--store`
continues to override it.

## Skill Distribution

The repo's `.agents/skills` is the canonical managed surface and its tracked
`.codex/skills` entries are required mirrors. The 12 OpenSpec skill directories
are copied byte-for-byte to the workspace `.codex/skills` surface. No managed
repo mirror is removed or edited. The repo `.claude/skills` directory keeps
`graphify` as its repo-specific directory and relative links into its canonical
`.agents/skills` surface for shared skills; those links are verified rather
than deleted as duplicates.

## Instruction Chain

`~/Developer/AGENTS.md` is the workspace policy. The workspace
`.codex/AGENTS.md` and `.claude/CLAUDE.md` explicitly point back to it, while
repository-level files remain narrower overrides.

## Store Hygiene and Rules

The nested `openspec/openspec/` tree contains no tracked files and is removed.
The existing governance files and reports stay where they are. `rules` is
added to `openspec/config.yaml` with entries for proposal, specs, design, and
tasks; these are advisory generation constraints and do not change runtime
behavior.

## Verification and Rollback

Verification covers both repo types, all-store validation, store health, the
Go mirror/parity gate, and exact workspace skill hashes. Rollback is
non-destructive: remove the workspace skill copies, unset `defaultStore`,
restore the nested directory only if required, and revert the config rules.
