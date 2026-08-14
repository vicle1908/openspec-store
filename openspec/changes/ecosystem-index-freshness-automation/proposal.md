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
| AgentMemory auto-refresh | ✅ Complete | `~/Library/LaunchAgents/com.agentmemory.server.plist` + watchdog |
| GitNexus manual refresh | ⚠️ go-microservices only | `make knowledge-refresh` → `scripts/knowledge-tools.sh refresh` |
| Graphify post-commit hook | ✅ All 18 repos | `.git/hooks/post-commit` (code-only AST rebuild) |
| Graphify post-merge hook | ✅ All 18 repos | `.git/hooks/post-merge` (marks stale + rebuilds) |
| Graphify incremental update | ✅ Available | `graphify update .` (AST-only, no API cost) |
| Graphify watch | ✅ Running | Currently watching `~/Developer` (PID 27309) |
| Weekly crons (claimed) | ❌ Don't exist | AGENTS.md:360 claims they do |
| Workspace-level scripts | ❌ None | No `~/Developer/scripts/` directory |
| `refresh-gitnexus-index-groups` spec | ⚠️ Minimal | 33 lines, no automation requirements |
| Worktree usage | ✅ Active | 7 worktrees across 5 repos |
| GitNexus per-worktree indexing | ✅ Works | Each worktree has its own `.gitnexus/` directory |
| LaunchAgent pattern | ✅ Proven | AgentMemory + workstation-tool-update both use it |
| Knowledge state dir | ✅ Exists | `go-microservices/.knowledge-state/` with locks/ |

### Current Staleness (2026-08-14)

**GitNexus** — 8 of 18 repos STALE:
- STALE: agent-core, agent-docs-sync, agent-harness, ai-harness-skills, ai-review, openspec-store, tdt-core, (and more)
- FRESH: browser-cli, code-daily-scan, jira-*, mcp-router, ops-automation-suite, webhook-receiver

**Graphify** — Most repos have recent graphs (Aug 14), some stale (Aug 6-10):
- FRESH: agent-core, agent-docs-sync, agent-harness, ai-harness-skills, tdt-core (Aug 14)
- STALE: jira-daily-reports (Aug 7), tdt-observability (Aug 6), tdt-sheets (Aug 6)

### Critical Finding: Graphify Post-Merge Hook Already Exists

All 18 repos already have a Graphify post-merge hook that:
1. Skips during rebase/merge/cherry-pick (advisory, doesn't block)
2. Checks for graphify state (`.graphify/graph.json` or `graphify-out/graph.json`)
3. Marks graph as stale (writes `.graphify/needs_update`)
4. Rebuilds code-only graph in background (`graphify hook-rebuild`)

**This means we don't need to create a new post-merge hook for Graphify.** We only need to extend it to also trigger GitNexus refresh.

## Approach

### Part 1: Nightly bulk refresh (baseline)

Create a workspace-level scheduled refresh system modeled after AgentMemory's LaunchAgent pattern:

1. **Refresh script** (`~/Developer/scripts/refresh-knowledge-indexes.sh`): Iterates all repos with existing `.gitnexus/` or `graphify-out/` state, runs `gitnexus analyze . --index-only --default-branch main` for GitNexus and `graphify extract . --code-only` for Graphify (official foreground pattern from knowledge-tools.sh)
2. **LaunchAgent** (`com.developer.index-refresh.plist`): Nightly execution (e.g., 2:30 AM) with logging
3. **Status command**: `~/Developer/scripts/knowledge-status.sh` for quick staleness check across all repos

### Part 2: Extend existing post-merge hook for GitNexus

The Graphify post-merge hook already exists in all 18 repos and handles Graphify refresh. We extend it to also trigger GitNexus refresh:

4. **Extend post-merge hook**: Add GitNexus refresh to the existing Graphify post-merge hook (after the Graphify rebuild)
5. **Use official owner lock**: Acquire `gitnexus-workspace.lock` before refresh (coordinates with any running GitNexus operations)
6. **Worktree-aware**: The hook already runs from main checkout only (COMMONDIR check). GitNexus worktree indexing is handled by the nightly refresh.

### Part 3: Worktree support

When agents work in worktrees, ensure indexes are available:

7. **GitNexus worktree indexing**: Each worktree already has its own `.gitnexus/`. The nightly refresh scans all worktrees (discovered via `git worktree list`) and refreshes each one's index
8. **Graphify worktree awareness**: Worktrees share the main checkout's `graphify-out/`. The post-merge hook refreshes the main checkout's graph, which worktrees use
9. **Worktree creation hook**: The existing post-checkout hook (installed by Graphify) handles worktree creation

### Part 4: Documentation

10. **Fix AGENTS.md**: Remove stale cron claims, document the actual LaunchAgent + hook system
11. **Update CLAUDE.md**: Replace staleness warnings with documentation of the automated system
