# workspace-knowledge-integration

## Why

The workspace has four knowledge tools with significant gaps between installation and actual usage:

1. **graphify** (v0.9.31 installed, **v0.9.33 latest**): Only 1 of 18 repos has a valid graph.json. Skills installed for Claude Code and Codex only. No git hooks, no global cross-repo graph, no memory feedback loop, no staleness monitoring. The 0.9.32 and 0.9.33 releases fix critical incremental rebuild bugs — without the upgrade, `graphify update` silently drops cross-file call edges and makes directed graphs undirected.

2. **GitNexus** (v1.6.9): All 17 repos indexed. MCP tools routed through mcp-router. No wiki generated.

3. **agentmemory** (v0.9.27): Running, healthy. MCP tools routed through mcp-router. Connected to Codex only. 0 sessions, 1 memory — tools available but unused.

4. **LLM Wiki** (Karpathy pattern): Does not exist. No curated knowledge base.

The gap is not just "tools aren't wired" — it's that graphify is two versions behind with critical data-integrity fixes, only 1 repo has a valid graph, no cross-repo graph exists, no automated freshness monitoring runs, and the curated knowledge layer doesn't exist.

## What Changes

### Phase 1: Upgrade and Activate graphify

- Upgrade graphify from 0.9.31 to 0.9.33 (critical fixes: incremental edge preservation, tier-aware merge, worker crash recovery, directed flag preservation).
- Run `graphify update` across all 18 repos to build valid graph.json files.
- Build global cross-repo graph (`graphify global add` per repo → `~/.graphify/global-graph.json`).
- Install git hooks (`graphify hook install`) for auto-rebuild on commit/checkout.
- Generate tree visualizations (`graphify tree`) for repos with valid graphs.
- Install graphify skills for remaining agents: Pi, Hermes, OpenCode.

### Phase 2: Initialize LLM Wiki

- Create `~/Developer/wiki/` with the Karpathy three-layer structure.
- Seed from GitNexus repo metadata, go-microservices docs, and agent-harness workflow.

### Phase 3: Wiki MCP Server + mcp-router Registration

- Build wiki MCP server (~200 LOC Python). Register in mcp-router.

### Phase 4: Hermes Orchestration

- Weekly cron: graphify check-update (staleness) + wiki lint (orphans/links).
- Post-task wiki capture pattern.
- Graphify memory feedback loop (agents save query outcomes).

### Phase 5: Update Documentation and Agent Guides

- Update workspace AGENTS.md with graphify global graph and wiki references.
- Update per-repo AGENTS.md files with graphify hooks and freshness instructions.
- Update Hermes graphify skill with global graph and new commands.
- Update Claude Code, Codex, Pi, OpenCode graphify integrations.

## Non-Goals

- graphify MCP registration in mcp-router (per-repo, overlaps GitNexus).
- GitNexus or agentmemory source changes.
- App source code changes in any repo.
- Hermes config.yaml MCP additions (all through mcp-router).

## Capabilities

### New Capabilities
- `workspace-knowledge-layer`: LLM Wiki with MCP access via mcp-router.
- `graphify-global-graph`: Cross-repo merged knowledge graph.
- `graphify-automation`: Git hooks, staleness monitoring, memory feedback loop.

### Modified Capabilities
- None.

## Impact

- Primary target: graphify binary upgrade, all 18 repos (graph.json generation), workspace dot-folders (agent skills), ~/Developer/wiki/ (new), ~/Developer/wiki-mcp-server/ (new), mcp-router registry.
- Risk: Low-Medium. graphify upgrade is backward-compatible. graph.json generation is non-destructive. Wiki and MCP server are additive.
