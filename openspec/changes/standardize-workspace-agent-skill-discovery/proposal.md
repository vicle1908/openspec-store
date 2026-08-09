## Why

The workspace skill setup currently mixes copied product-specific mirrors, untracked workspace files, global `npx skills` installations, and standard `.agents/skills` discovery, while the governing specification still requires an obsolete copied Codex layout. This causes version drift, duplicate names, unreliable discovery claims, and cleanup changes that cannot be verified consistently across independent repositories.

## What Changes

- Make `~/Developer/.agents/skills/` the canonical workspace collection for shared Agent Skills.
- Expose a verified, curated subset through standard user-level `~/.agents/skills/` symlinks so independent Git repositories can discover shared skills without copied `.codex/skills` mirrors.
- Preserve real global `npx skills -g` installations and both project/global lockfile provenance.
- Keep `.claude/skills/` and `.claude/commands/opsx/` for Claude-native skills and commands, verified from independent repositories.
- Keep `.codex/` for Codex configuration, roles, hooks, automation, memories, system skills, and genuinely Codex-specific skills only.
- Replace the obsolete `workspace-openspec-skill-discovery` requirements that mandate copied Codex skill mirrors.
- Add deterministic synchronization and verification for selected user-level links, collisions, stale links, broken links, and product-specific duplicates.
- Preserve repository-specific skills and unrelated dirty Graphify/GitNexus artifacts.

### Non-Goals

- Rewriting or normalizing all community skill content.
- Removing `.codex/`, `.claude/`, or existing global `npx skills -g` installations.
- Committing unrelated repository changes or generated knowledge-graph output.
- Modernizing archived OpenSpec history.

## Capabilities

### New Capabilities

<!-- None. -->

### Modified Capabilities

- `workspace-openspec-skill-discovery`: Replace copied Codex mirrors with standard `.agents/skills` discovery, preserve product-native surfaces, and require evidence-backed synchronization and discovery verification.

## Impact

- Workspace surfaces: `~/Developer/.agents/`, `~/.agents/`, `~/Developer/.claude/`, and `~/Developer/.codex/`.
- Tracked planning and operational ownership: `~/Developer/openspec-store/`.
- Agent behavior: Claude Code, Codex CLI, and other Agent Skills-compatible coding agents.
- Repository instructions: workspace and affected repository `AGENTS.md`/`CLAUDE.md` files.
- Existing repository working trees remain protected; unrelated modifications are outside this change's write scope.
