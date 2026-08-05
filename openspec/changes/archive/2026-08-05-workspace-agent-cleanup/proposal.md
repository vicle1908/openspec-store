# Proposal: Workspace Agent Cleanup

## Why

The `go-microservices` repo has 12 agent dot-folders (`.agent/`, `.agents/`,
`.claude/`, `.codex/`, `.cursor/`, `.factory/`, `.fable-5/`, `.fable-5kills/`,
`.kiro/`, `.omp/`, `.opencode/`, `.pi/`, `.kilocode/`) that were created as
repo-level overrides. However, these are root workspace configurations — the
canonical configs live at `~/Developer/` (`~/.agents/`, `~/.claude/`, `~/.codex/`,
`~/.fable-5kills/`).

This has resulted in:
- 7 completely empty dot-folders consuming inodes
- Skills duplicated across `.agents/skills/`, `.codex/skills/`, `.fable-5/`
  when they already exist in root workspace
- `.opencode/` containing 61MB of `node_modules` for a single plugin
- Stale tracked files: `agent-skills-manifest.json`, `skills-lock.json`
- Broken reference in AGENTS.md (`.fable-5kills/graphify/SKILL.md`)
- `.gitignore` inconsistencies (duplicate entries, phantom paths)

## What Changes

- Remove 10 empty agent dot-folders (`.agent/`, `.cursor/`, `.factory/`,
  `.fable-5/`, `.omp/`, `.pi/`, `.kilocode/`, `.fable-5/`, `.fable-5kills/`)
- Remove repo-level duplicate skills from `.agents/skills/`, `.fable-5kills/`,
  `.claude/skills/`, `.codex/skills/`, `agent/skills/` — all provided by root
  workspace configs
- Remove `.opencode/` entirely (61MB node_modules, no skills used)
- Remove stale tracked files (`agent-skills-manifest.json`, `skills-lock.json`)
- Remove contract-check temp worktree directories
- Fix `.gitignore`: remove duplicate entries, phantom paths, add stale files
- Fix AGENTS.md: replace broken `.fable-5kills/graphify/SKILL.md` reference
  with correct Hermes graphify skill reference

## Scope

- Config/tooling only — **skip_specs: true**
- No code changes, no spec changes, no deployment impact
- Affects go-microservices repo only (root workspace configs are untouched)
