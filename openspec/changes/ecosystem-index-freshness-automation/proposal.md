# Proposal: Ecosystem Index Freshness Automation

## Problem

GitNexus and Graphify knowledge graph indexes across the workspace go stale because no automated refresh mechanism exists. Only `go-microservices` has manual refresh (`make knowledge-refresh`) and a Graphify post-commit hook. The remaining 17+ indexed repos have no automation. CLAUDE.md warns "GitNexus indexes may be behind HEAD" and "Graphify graph may be stale" but offers no fix. AGENTS.md claims "Weekly crons: graphify freshness (Mon 8AM), wiki lint (Mon 9AM)" but these crons do not exist — `crontab -l` shows only a Jenkins cleanup entry.

## Non-Goals

- Changing GitNexus or Graphify CLI internals
- Modifying the existing `gitnexus-stable-contract` or `developer-code-intelligence` specs
- Enabling automatic GitNexus post-commit indexing (deferred per knowledge-graphs.md:139)
- Touching AgentMemory (already fully automated via LaunchAgent)
- Embeddings or PDG refresh (expensive, should remain on-demand)

## Affected Ownership Boundaries

- **Workspace root** (`~/Developer/`): New LaunchAgent, refresh script
- **go-microservices**: Existing `knowledge-tools.sh` may need extension
- **AGENTS.md**: Fix stale cron claims
- **CLAUDE.md**: Update staleness warnings

## Existing Infrastructure

| Component | Status | Location |
|---|---|---|
| AgentMemory auto-refresh | ✅ Complete | `~/Library/LaunchAgents/com.agentmemory.server.plist` |
| GitNexus manual refresh | ⚠️ go-microservices only | `make knowledge-refresh` → `scripts/knowledge-tools.sh refresh` |
| Graphify post-commit hook | ⚠️ go-microservices only | Installed via `make knowledge-install-hooks` |
| Graphify incremental update | ✅ Available | `graphify update .` (AST-only, no API cost) |
| Weekly crons (claimed) | ❌ Don't exist | AGENTS.md:360 claims they do |
| Workspace-level scripts | ❌ None | No `~/Developer/scripts/` directory |
| `refresh-gitnexus-index-groups` spec | ⚠️ Minimal | 33 lines, no automation requirements |

## Approach

Create a workspace-level scheduled refresh system modeled after AgentMemory's LaunchAgent pattern:

1. **Refresh script** (`~/Developer/scripts/refresh-knowledge-indexes.sh`): Iterates all repos with existing `.gitnexus/` or `graphify-out/` state, runs `gitnexus analyze . --index-only --default-branch main` and `graphify update .` for each
2. **LaunchAgent** (`com.developer.index-refresh.plist`): Nightly execution (e.g., 2:30 AM) with logging
3. **Status command**: `~/Developer/scripts/knowledge-status.sh` for quick staleness check across all repos
4. **Fix AGENTS.md**: Remove stale cron claims, document the actual LaunchAgent
5. **Extend existing spec**: Add automation requirements to `refresh-gitnexus-index-groups`
