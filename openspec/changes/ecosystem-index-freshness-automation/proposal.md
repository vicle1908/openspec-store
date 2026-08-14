# Proposal: Ecosystem Index Freshness Automation

## Problem

GitNexus and Graphify knowledge graph indexes across the workspace go stale because no automated refresh mechanism exists. Only `go-microservices` has manual refresh (`make knowledge-refresh`) and a Graphify post-commit hook. The remaining 17+ indexed repos have no automation. CLAUDE.md warns "GitNexus indexes may be behind HEAD" and "Graphify graph may be stale" but offers no fix. AGENTS.md claims "Weekly crons: graphify freshness (Mon 8AM), wiki lint (Mon 9AM)" but these crons do not exist — `crontab -l` shows only a Jenkins cleanup entry.

## Additional Problems

Beyond nightly staleness, two gaps prevent coding agents from using fresh indexes effectively:

1. **Post-main-commit lag**: When a PR merges to main, agents working on subsequent tasks get stale index results. The current Graphify post-commit hook only covers `go-microservices` and skips worktrees. GitNexus has no post-commit hook at all (deferred). Agents like Claude Code, Codex, and Hermes need fresh indexes within minutes of a merge, not hours.

2. **Worktree blindness**: The workspace uses git worktrees extensively (currently 4 active: `agent-core`, `centralize-mcp-knowledge-servers`, `implement-grok-build-cli`, `tdt-core`). Each worktree has its own `.gitnexus/` index but shares the main checkout's `graphify-out/`. The existing Graphify hook explicitly skips worktrees (COMMONDIR check). When agents work in worktrees, they get stale Graphify graphs and potentially stale GitNexus indexes.

## Non-Goals

- Changing GitNexus or Graphify CLI internals
- Modifying the existing `gitnexus-stable-contract` or `developer-code-intelligence` specs
- Embeddings or PDG refresh (expensive, should remain on-demand)
- Touching AgentMemory (already fully automated via LaunchAgent)
- Changing the `gitnexus-stable-contract` deferred post-commit policy (that contract governs what GitNexus exposes to consumers, not workspace-level refresh scheduling)

## Affected Ownership Boundaries

- **Workspace root** (`~/Developer/`): New LaunchAgent, refresh scripts, worktree-aware refresh
- **go-microservices**: Existing `knowledge-tools.sh` may need extension
- **AGENTS.md**: Fix stale cron claims
- **CLAUDE.md**: Update staleness warnings

## Existing Infrastructure

| Component | Status | Location |
|---|---|---|
| AgentMemory auto-refresh | ✅ Complete | `~/Library/LaunchAgents/com.agentmemory.server.plist` |
| GitNexus manual refresh | ⚠️ go-microservices only | `make knowledge-refresh` → `scripts/knowledge-tools.sh refresh` |
| Graphify post-commit hook | ⚠️ go-microservices only, skips worktrees | `.git/hooks/post-commit` (COMMONDIR check) |
| Graphify incremental update | ✅ Available | `graphify update .` (AST-only, no API cost) |
| Weekly crons (claimed) | ❌ Don't exist | AGENTS.md:360 claims they do |
| Workspace-level scripts | ❌ None | No `~/Developer/scripts/` directory |
| `refresh-gitnexus-index-groups` spec | ⚠️ Minimal | 33 lines, no automation requirements |
| Worktree usage | ✅ Active | 4 worktrees under `~/Developer/.worktrees/` and elsewhere |
| GitNexus per-worktree indexing | ✅ Works | Each worktree has its own `.gitnexus/` directory |
| LaunchAgent pattern | ✅ Proven | AgentMemory + workstation-tool-update both use it |

## Approach

### Part 1: Nightly bulk refresh (baseline)

Create a workspace-level scheduled refresh system modeled after AgentMemory's LaunchAgent pattern:

1. **Refresh script** (`~/Developer/scripts/refresh-knowledge-indexes.sh`): Iterates all repos with existing `.gitnexus/` or `graphify-out/` state, runs `gitnexus analyze . --index-only --default-branch main` and `graphify update .` for each
2. **LaunchAgent** (`com.developer.index-refresh.plist`): Nightly execution (e.g., 2:30 AM) with logging
3. **Status command**: `~/Developer/scripts/knowledge-status.sh` for quick staleness check across all repos

### Part 2: Post-merge trigger for agent freshness

When code lands on any repo's main branch, trigger a delayed refresh so agents get fresh indexes within minutes:

4. **Post-merge hook** (installed in each indexed repo): Detects merges to main, sleeps 30-60s (lets git operations settle), then runs `gitnexus analyze . --index-only` + `graphify update .` in the background
5. **Debounce logic**: If multiple commits land rapidly (e.g., merge queue), only refresh once after the last commit + delay
6. **Worktree-aware**: The hook runs from the main checkout only (not worktrees), using the same COMMONDIR check pattern that Graphify's existing hook uses

### Part 3: Worktree support

When agents work in worktrees, ensure indexes are available:

7. **GitNexus worktree indexing**: Each worktree already has its own `.gitnexus/`. The nightly refresh scans all worktrees (discovered via `git worktree list`) and refreshes each one's index
8. **Graphify worktree awareness**: Worktrees share the main checkout's `graphify-out/`. The refresh script detects worktrees and ensures the main checkout's graph is fresh before agents start work in any worktree
9. **Worktree creation hook**: When `git worktree add` is run, the post-checkout hook (already installed by Graphify) triggers a Graphify refresh in the main checkout

### Part 4: Documentation

10. **Fix AGENTS.md**: Remove stale cron claims, document the actual LaunchAgent + hook system
11. **Update CLAUDE.md**: Replace staleness warnings with documentation of the automated system
