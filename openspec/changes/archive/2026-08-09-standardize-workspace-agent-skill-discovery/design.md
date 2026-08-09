## Context

See `proposal.md` for motivation and `specs/workspace-openspec-skill-discovery/spec.md` for the behavioral contract.

The workspace contains independent Git repositories under `~/Developer/`. Codex officially scans repository `.agents/skills` only from the current directory to that repository's Git root, plus user-level `~/.agents/skills`; it follows symlinked skill roots. Claude Code officially scans `.claude/skills` from the current directory to the repository root and follows symlinks. Therefore workspace-root product directories are not automatically inherited by independent child repositories.

`~/Developer/.agents/skills/` contains both direct skill roots and container directories. User-level `~/.agents/skills/` also contains seven real global `npx skills -g` installations with separate lockfile provenance. The workspace root is not a Git repository, so operational scripts and manifests placed only there have no durable owner. Existing repositories have unrelated dirty state that cannot be folded into this change.

## Goals / Non-Goals

**Goals:**

- Establish one canonical workspace collection of direct Agent Skill roots.
- Expose selected shared skills to independent repositories using supported user-level links without overwriting global installations.
- Preserve native Claude skills/commands and Codex-specific configuration/governance.
- Produce accurate inventory and provenance reports.
- Verify native discovery with fresh read-only sessions and no filesystem-search fallback.
- Move synchronization sources into a tracked owning repository.

**Non-Goals:**

- Normalize every community skill or force all shared skills into each product's startup index.
- Remove product-specific configuration roots.
- Modify archived OpenSpec history.
- Commit unrelated Graphify, GitNexus, source, or generated-file changes.

## Decisions

### 1. Canonical shared collection is workspace `.agents/skills`

Only immediate child directories with a root `SKILL.md` count as direct skills. Directories such as `generated/` and `gitnexus/` are containers and are inventoried separately.

**Alternative considered:** Treat every immediate directory as a skill. Rejected because it inflates counts and creates invalid synchronization entries.

### 2. User-level links bridge independent Git roots

A tracked manifest selects workspace skills that should be exposed as `~/.agents/skills/<name>` symlinks. The synchronizer preserves real global directories and fails on name collisions.

**Alternative considered:** Copy shared skills under `.codex/skills`. Rejected because Codex natively supports user-level `.agents/skills`, copied content drifts, and `.codex` has distinct ownership.

### 3. Claude uses native `.claude` surfaces

Generated OpenSpec skills and all twelve `/opsx:*` commands remain under workspace `.claude`. Shared non-OpenSpec skills required by Claude are exposed through `.claude/skills` symlinks only after explicit native discovery probes.

**Alternative considered:** Assume Claude reads workspace `.agents/skills` through instructions. Rejected because instructions can tell Claude where to search but do not prove native skill discovery.

### 4. Codex-specific governance remains under `.codex`

`.codex/skills` contains bundled/system or genuinely Codex-specific skills only. `config.toml`, custom roles, hooks, automation, memories, and governance remain intact. Shared skills are not copied there.

### 5. Synchronization sources are tracked by openspec-store

The link manifest and synchronizer are owned by `openspec-store`, which already owns the governing specification and generated OpenSpec skill targets. Workspace convenience paths may be symlinked to those tracked sources, but the authoritative implementation remains in Git.

**Alternative considered:** Leave scripts only under `~/Developer/.agents/`. Rejected because the workspace umbrella is not Git-tracked.

### 6. Native probes are evidence gates

Fresh Claude and Codex sessions explicitly invoke selected skills from at least two independent repositories. Logs must not show manual filesystem search fallback. Large or malformed skill artifacts are reported separately; the Agent Skills 500-line recommendation is not treated as a hard parser limit without parser evidence.

## Risks / Trade-offs

- **[Startup index budget omits skills]** → Keep product-visible selections explicit and verify critical skills natively; do not claim every canonical skill is loaded at startup.
- **[Global skill collision]** → Preserve real directories and fail synchronization on collisions.
- **[Generated OpenSpec targets differ intentionally]** → Compare target inventories and `generatedBy`, not byte hashes across different adapters.
- **[Dirty repository state obscures ownership]** → Review file-level diffs and stage/commit only change-owned paths.
- **[Claude or Codex cache masks discovery changes]** → Use fresh non-resumed sessions and inspect logs.
- **[Graphify artifact is not natively indexed]** → Validate frontmatter, duplicates, cache, and minimized-artifact behavior before attributing cause.

## Migration Plan

1. Capture structural inventory, lockfile provenance, product-native surfaces, and dirty-state baseline.
2. Validate the governing OpenSpec delta.
3. Move the synchronization manifest/script into `openspec-store` and expose a workspace convenience link if needed.
4. Reconcile user-level `.agents/skills` links without touching real global installs.
5. Prove native Claude and Codex discovery; add only necessary product-native symlinks.
6. Remove remaining copied shared skills from `.codex/skills` after successful probes.
7. Update active documentation and reusable guidance.
8. Run focused and full verification, keeping unrelated baseline failures separate.
9. Archive the change and commit only the store-owned artifacts after all tasks pass.

Rollback removes change-owned user/workspace symlinks and restores the prior tracked specification; real global skill directories and product configuration remain untouched.
