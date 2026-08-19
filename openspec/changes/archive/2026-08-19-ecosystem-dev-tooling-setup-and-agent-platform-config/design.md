## Context

The workspace runs 4 major dev tools (gitnexus, graphify, openspec, agentmemory) across 8 agent platforms (Claude, Hermes, Pi, Codex, Copilot, OpenCode, Advance, agents). Each platform has its own skills directory, MCP configuration, and hook setup. Over time, these drifted: skills were at different versions, hooks were missing, the knowledge refresh script had no error recovery, and the skill directories had an inverted structure (universal skills in workspace, workspace skills in global hub).

See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Make all dev tools accessible to all agent platforms
- Ensure knowledge refresh is self-healing
- Establish clear global vs workspace skill separation
- Document the setup for future reference

**Non-Goals:**
- Change tool behavior or add new features
- Modify individual repo configurations
- Set up new agent platforms

## Decisions

### D1: Two-tier skill architecture

**Choice**: Split skills into global (`~/.agents/skills/`) and workspace (`~/Developer/.agents/skills/`):
- Global: universal skills (graphify, tavily, brightdata, search, etc.)
- Workspace: workspace-specific skills (gitnexus, openspec, agentmemory, etc.)
- Each tier symlinks to the other for cross-access

**Rationale**: Universal skills should be available regardless of which workspace an agent is working in. Workspace skills depend on repo-specific infrastructure (indexed repos, openspec-store) and should stay local.

### D2: CLAUDE.md symlinked to AGENTS.md

**Choice**: Replace `~/.claude/CLAUDE.md` with a symlink to `~/Developer/AGENTS.md`.

**Rationale**: AGENTS.md is the comprehensive workspace instruction file (17KB). CLAUDE.md had only228B (graphify trigger). Symlinking ensures Claude reads the same comprehensive instructions as other agents.

### D3: AgentMemory via plugin mechanism

**Choice**: Use AgentMemory's plugin system for MCP integration rather than manual `.claude/mcp.json` configuration.

**Rationale**: The plugin handles server lifecycle, hook registration, and MCP tool exposure. Manual configuration requires maintaining absolute paths that break on upgrades.

### D4: Graphify skills updated per-platform

**Choice**: Run `graphify install --platform <P>` for each stale platform individually.

**Rationale**: `graphify install` without `--platform` only updates the default platform. Codex uses a different subagent API (`spawn_agent` vs Agent tool), so its SKILL.md is intentionally different.

## Risks / Trade-offs

- **[Risk] Symlink chains can break** → Mitigated by keeping chains short (max 2 hops) and using absolute paths
- **[Risk] AgentMemory server not auto-starting** → No LaunchAgent created; server starts on demand. Acceptable for current usage pattern.
- **[Trade-off] Skill duplication** → Some skills exist in multiple locations (graphify in global + workspace). Acceptable for resilience; one copy is canonical.

## Migration Plan

1. Apply skill directory restructuring (global/workspace split)
2. Install agentmemory skills
3. Symlink CLAUDE.md → AGENTS.md
4. Update AGENTS.md with correct paths and versions
5. Verify all platforms can access required skills

## Open Questions

_(none — all decisions are grounded in the audit findings)_
