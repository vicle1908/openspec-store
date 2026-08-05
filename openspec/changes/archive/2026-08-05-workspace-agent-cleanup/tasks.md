# Tasks: Workspace Agent Cleanup

## Task 1: Remove empty agent dot-folders
- [x] Remove `.agent/` (empty skills dir)
- [x] Remove `.cursor/` (empty)
- [x] Remove `.factory/` (empty)
- [x] Remove `.fable-5/` (empty)
- [x] Remove `.omp/` (empty)
- [x] Remove `.pi/` (empty)
- [x] Remove `.kilocode/` (empty)
- [x] Remove `.fable-5/` (empty)

## Task 2: Remove repo-level duplicate skills
- [x] Remove `.agents/skills/` contents (36 skills duplicated from root workspace `~/.agents/`)
- [x] Remove `.fable-5/` contents (12 openspec skills duplicated from root workspace `~/.fable-5kills/`)
- [x] Remove `.claude/skills/` contents (generated, gitnexus, graphify — provided by root workspace `~/.claude/skills/`)
- [x] Remove `.codex/skills/` contents (openspec, graphify — provided by root workspace `~/.fable-5/`)
- [x] Remove `agent/skills/` contents (16 agentmemory skills — provided by root workspace)
- [x] Remove `.opencode/` entirely (61MB node_modules, no skills used)

## Task 3: Preserve repo-specific config
- [x] Verify `.claude/settings.json` hooks (graphify hook-guard) are retained
- [x] Verify `.claude/settings.local.json` permissions are retained
- [x] Verify `.claude/CLAUDE.md` is retained
- [x] Verify `.codex/hooks.json` (graphify hook-check) is retained
- [x] Verify `.codex/AGENTS.md` is retained
- [x] Verify root AGENTS.md is retained

## Task 4: Remove stale tracked files
- [x] `git rm --cached agent-skills-manifest.json`
- [x] `git rm --cached skills-lock.json`
- Note: `.bak` files were not tracked (gitignored)

## Task 5: Clean up temp directories
- [x] Remove `services/.contract-check-first.*` (3 dirs)
- [x] Remove `services/.contract-check-second.*` (3 dirs)

## Task 6: Fix .gitignore
- [x] Remove duplicate `.fable-5/` entry
- [x] Remove phantom `.fable-5kills/graphify/` reference
- [x] Add `agent-skills-manifest.json` and `skills-lock.json` to gitignore
- [x] Clean up structure and remove stale per-CLI patterns

## Task 7: Fix AGENTS.md
- [x] Replace broken `.fable-5kills/graphify/SKILL.md` reference (line 88) with correct Hermes graphify skill reference

## Task 8: Validate
- [x] `git status` — clean state
- [x] `git diff --stat` — expected changes are removals only (106 files, 15428 deletions)
- [x] `git diff --check` — no whitespace errors
- [x] Verify no unintended files removed
- [x] Verify root workspace configs untouched
