# Proposal: Enhance OpenSpec Workflow with Knowledge Tools Integration

## Why

### Gap 1: Knowledge tools not integrated into OpenSpec lifecycle

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

### Gap 2: delegate_task reviews fail with vars() serialization bug

The current 5-provider review uses `delegate_task` to spawn subagents. Investigation reveals a confirmed bug in `conversation_loop.py:2631`:

```python
# BUG: No try/except around vars() — Pydantic models with __slots__ fail
resp_attrs = {k: str(v)[:100] for k, v in vars(response).items() if not k.startswith('_')}
```

This causes all delegated subagent reviews to crash with `vars() argument must have __dict__ attribute` when the subagent hits max_iterations and the summary call fails. Meanwhile, `relay_tools.py:100` and `relay_llm.py:1203` DO have try/except around their `vars()` calls — only `conversation_loop.py:2631` is unguarded.

**Proven workaround:** Use external CLI agents (`Advance -p`, `claude -p`, `codex exec`, `agy --print`, `opencode run`, `pi -p`) instead of `delegate_task`. Each runs as an independent process with its own iteration budget and error handling, completely bypassing the Hermes `turn_finalizer.py` path. This was validated in the current review where Advance Code CLI delivered a thorough review while all 5 `delegate_task` reviewers crashed.

## What Changes

### 1. Add knowledge-informed context gathering to change creation (Phase 1)

Before writing proposal.md, systematically query all four tools:
- `graphify query` — structural understanding of the area being changed
- `gitnexus context` / `impact` — semantic understanding + blast radius
- `wiki_search` — existing curated knowledge about the domain
- `memory_smart_search` — past session context about similar changes

### 2. Add knowledge tool outputs as review evidence (Phase 2)

The 5-provider review currently collects git diff, test results, and lint output. Add:
- graphify structural analysis (god-nodes, community structure) as architecture evidence
- gitnexus impact analysis as blast-radius evidence
- wiki pages as documentation-alignment evidence
- agentmemory patterns as prior-experience evidence

### 3. Switch review from delegate_task to external CLI agents

Replace `delegate_task` with external CLI invocations (`kimi -p`, `claude -p`, `codex exec`, `agy --print`, `opencode run`, `pi -p`). Each reviewer runs as an independent process with:
- Generous timeout (300-600s per reviewer)
- Provider-specific model (user's configured default, not delegation.model)
- Stream JSON output for structured parsing
- No dependency on Hermes turn_finalizer (avoids vars() bug)

### 4. Add post-archive knowledge capture (Phase 5) — simplified

After archiving a change:
- Update wiki entity/concept pages for affected services
- Update architecture decisions in wiki if significant (use write_file, not wiki_ingest)
- Verify graphify graphs are current (run `graphify update` on affected repos)
- Verify gitnexus indexes are current (re-index affected repos)

### 5. Add knowledge freshness verification to validation (Phase 4)

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
- Update `openspec/specs/hermes-skills/spec.md` alignment matrix (8→9 edges)
- Add reference for CLI-based review workflow with generous budgets

**Out of scope:**
- Changes to graphify, gitnexus, agentmemory, or wiki tool internals
- New MCP server registrations (all already registered)
- Changes to mcp-router configuration
- Auto-rebuild cron changes (already working: Mon 8AM graphify, Mon 9AM wiki lint)
- Fixing the Hermes vars() bug (report upstream, don't patch framework)
