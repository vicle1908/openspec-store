## Why

The workspace dev toolings (gitnexus, graphify, openspec, agentmemory) and agent platforms (Claude, Hermes, Pi, Codex, etc.) had accumulated inconsistencies: stale skills across platforms, broken knowledge refresh, missing hooks, disorganized skill directories, and unconfigured agentmemory integration. A comprehensive audit and remediation was needed to ensure all agents can use all tools correctly.

## What Changes

- **GitNexus knowledge refresh**: Added 2-stage fallback chain (repair-fts → force) to `refresh-knowledge-indexes.sh`, fixing 13 repos that failed nightly
- **Graphify skills**: Updated across 8 agent platforms to 0.9.46
- **AgentMemory**: Installed skills, re-registered hooks, configured for Claude Code
- **Knowledge refresh**: Fixed version detection bug in `knowledge-status.sh`
- **Skill directory restructuring**: Split `~/.agents/` (universal hub) and `~/Developer/.agents/` (workspace-specific) with proper symlinks
- **CLAUDE.md**: Symlinked to comprehensive AGENTS.md
- **Documentation**: Updated AGENTS.md with correct paths, versions, and store stats

## Capabilities

### New Capabilities

_(none — pure setup/documentation, no spec-level behavior changes)_

### Modified Capabilities

_(none — infrastructure changes, not spec-governed behavior)_

**skip_specs: true** — This change modifies tool configurations, skill distributions, and documentation. No spec-governed behavior changes.

## Impact

- **Scripts modified**: `refresh-knowledge-indexes.sh`, `knowledge-status.sh`
- **Skills updated**: graphify (8 platforms), agentmemory (7 skills in Claude)
- **Directories restructured**: `~/.agents/skills/`, `~/Developer/.agents/skills/`
- **Documentation**: `~/Developer/AGENTS.md`, `~/.claude/CLAUDE.md` (symlinked)
- **Hooks**: tdt-scheduler post-merge hook installed
- **Processes**: Stale Codex/Happy MCP killed (~960MB reclaimed)
- **Risk**: LOW — configuration changes, no code changes
