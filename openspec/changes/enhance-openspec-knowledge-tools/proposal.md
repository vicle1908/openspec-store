# Proposal: Enhance OpenSpec Workflow with Knowledge Tools Integration

## Why

The workspace has four knowledge tools fully operational and registered in mcp-router:

| Tool | Modality | Status | MCP |
|------|----------|--------|-----|
| **graphify** | Structural (AST-level) | v0.9.34, 18 repos, global graph | CLI via Bash |
| **GitNexus** | Semantic (indexed, deeper) | v1.6.9, 18 repos indexed | MCP via mcp-router |
| **agentmemory** | Episodic (past sessions) | v0.9.28, healthy | MCP via mcp-router |
| **LLM Wiki** | Curated (compiled knowledge) | 21 pages, MCP server built | MCP via mcp-router |

However, the OpenSpec workflow currently references these tools in only **two places**:

1. **Cross-repo blast radius search** — mentions `gitnexus impact` and `graphify path`/`query` for finding affected repos before change creation
2. **Tool upgrade pitfall** — mentions verifying paths after tool upgrades

This means:
- **Change creation** doesn't systematically query knowledge tools for context about the area being changed
- **Design review** doesn't use knowledge tool outputs as evidence (wiki architecture pages, gitnexus blast radius, agentmemory past session context)
- **Post-archive** doesn't update wiki pages or capture learnings in agentmemory
- **Knowledge freshness** isn't verified after code changes — graphs and wiki can go stale without detection
- **agentmemory** is completely invisible to OpenSpec — past session context about similar changes is never consulted

## What Changes

### 1. Add knowledge-informed context gathering to change creation (Phase 1)

Before writing proposal.md, systematically query all four tools:
- `graphify query` — structural understanding of the area being changed
- `gitnexus context` / `impact` — semantic understanding + blast radius
- `wiki_search` — existing curated knowledge about the domain
- `memory_smart_search` — past session context about similar changes

This replaces the current ad-hoc "grep across repos" with a structured knowledge gathering step.

### 2. Add knowledge tool outputs as review evidence (Phase 2)

The 5-provider review currently collects git diff, test results, and lint output. Add:
- graphify structural analysis (god-nodes, community structure) as architecture evidence
- gitnexus impact analysis as blast-radius evidence
- wiki pages as documentation-alignment evidence
- agentmemory patterns as prior-experience evidence

### 3. Add post-archive knowledge capture (Phase 5)

After archiving a change:
- Update wiki entity/concept pages for affected services
- Ingest architecture decisions into wiki if significant
- Verify graphify graphs are current (run `graphify update` on affected repos)
- Verify gitnexus indexes are current (re-index affected repos)

### 4. Add knowledge freshness verification to validation (Phase 4)

Before marking validation complete, verify knowledge tools reflect current state:
- `graphify check-update .` on affected repos
- `gitnexus list` staleness check via MCP
- `wiki_stale` to find outdated pages

## Scope

**In scope:**
- Update `openspec-workflow` SKILL.md with knowledge tool integration steps
- Create new reference: `references/knowledge-tools-integration.md`
- Update `openspec-review-governance` to include knowledge tool evidence
- Update `openspec-plan-review` and `openspec-code-review` edge definitions

**Out of scope:**
- Changes to graphify, gitnexus, agentmemory, or wiki tool internals
- New MCP server registrations (all already registered)
- Changes to mcp-router configuration
- Auto-rebuild cron changes (already working: Mon 8AM graphify, Mon 9AM wiki lint)
