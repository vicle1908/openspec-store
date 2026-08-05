# workspace-knowledge-integration

## Why

The workspace has four knowledge tools, but actual usage is minimal despite tooling being in place:

1. **graphify** (v0.9.31): CLI installed. Skills installed for **Claude Code ✅** and **Codex ✅** only. Pi ❌, Hermes ❌, OpenCode ❌. Only **1 of 18 repos** (tdt-core) has a valid `graph.json`. graphify-out/ exists in 2 other repos but has no graph.json. graphify has its own MCP server (`graphify-mcp`) but it is per-repo (takes a `graph.json` path argument) and significantly overlaps with GitNexus tools — registering it in mcp-router is not recommended.

2. **GitNexus** (v1.6.9): All 17 repos indexed. MCP tools **already routed through mcp-router** ✅ (9 tools: query, context, impact, trace, cypher, detect_changes, rename, explain, check). No wiki generated for any repo.

3. **agentmemory** (v0.9.27): Running, healthy. MCP tools **already routed through mcp-router** ✅ (6 tools: memory_recall, memory_save, memory_smart_search, memory_audit, memory_export, memory_sessions). Connected to **Codex** ✅ only. **0 sessions, 1 memory** — tools are available but effectively unused.

4. **LLM Wiki** (Karpathy pattern): **Does not exist**. No curated, cross-referenced knowledge base for architecture decisions, debugging playbooks, or cross-repo patterns.

5. **mcp-router** (v0.6.3): Serves as the single transport hub. Hermes connects via CLI bridge. GitNexus and agentmemory tools already flow through it. No new MCP registrations needed for these.

The actual gap is not "tools exist but aren't wired" — it's "tools are wired but barely used, and the curated knowledge layer doesn't exist."

## What Changes

### Phase 1: Complete Agent Skill Coverage

Install graphify skills for the 3 remaining agents: Pi, Hermes, OpenCode. Claude Code and Codex already have them.

### Phase 2: Initialize LLM Wiki

Create `~/Developer/wiki/` with the Karpathy three-layer structure. Seed from GitNexus repo metadata, go-microservices docs, and agent-harness workflow documentation.

### Phase 3: Wiki MCP Server + mcp-router Registration

Build a lightweight MCP server (~200 LOC, Python) for wiki operations. Register in mcp-router so all agents get wiki tools automatically via their existing mcp-router connection.

### Phase 4: Hermes Orchestration

Add wiki maintenance cron (weekly lint) and post-task wiki capture pattern (extract insights from complex agent sessions → ingest into wiki).

## Non-Goals

- **graphify MCP registration in mcp-router**: Per-repo (needs `graph.json` path), overlaps with GitNexus tools, CLI via Bash already works for installed agents.
- **agentmemory MCP registration**: Already in mcp-router. The gap is usage, not registration.
- **GitNexus changes**: Already fully integrated.
- **App source code changes**: No Go, Python, or Node.js repo modifications.
- **Hermes config.yaml changes**: No new MCP server entries. All knowledge tools flow through mcp-router.

## Capabilities

### New Capabilities
- `workspace-knowledge-layer`: Cross-agent knowledge base (LLM Wiki) with MCP access via mcp-router, curation workflows, and maintenance automation.

### Modified Capabilities
- None. No existing spec requirements change.

## Impact

- **Primary target:** Workspace dot-folders (Pi, Hermes, OpenCode skills), `~/Developer/wiki/` (new), `~/Developer/wiki-mcp-server/` (new), mcp-router server registry.
- **Affected agents:** Pi, Hermes, OpenCode (graphify skill install), all agents (wiki MCP tools via mcp-router).
- **Repositories:** No repo source code changes.
- **Risk:** Low. All changes are additive. Rollback: delete wiki directory, remove wiki server from mcp-router, revert skill installs.
