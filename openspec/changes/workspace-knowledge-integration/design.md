# workspace-knowledge-integration — Design

## Architecture Overview

Four knowledge modalities, one transport hub (mcp-router):

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENTS                                     │
│  Hermes · Claude Code · Codex · Pi · fable-5 · OpenCode         │
│                                                                 │
│  Each agent connects to mcp-router CLI (stdio bridge)           │
│  → gets ALL tools from ALL registered MCP servers               │
├─────────────────────────────────────────────────────────────────┤
│                   mcp-router (localhost:3282)                    │
│                   Transport Hub & Aggregator                     │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ GitNexus  │ │Brave/Tavily│ │agentmemory│ │   Wiki MCP      │   │
│  │ (indexed) │ │(web search) │ │(episodic) │ │   (new)         │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
│                                                                 │
│  All tools aggregated as mcp__mcp_router__*                     │
│  Single connection per agent, all tools available                │
├─────────────────────────────────────────────────────────────────┤
│                   KNOWLEDGE SOURCES                              │
│                                                                 │
│  graphify (AST)     → CLI tool, AGENTS.md integration           │
│  GitNexus (KG)      → MCP via mcp-router                        │
│  agentmemory (episodic) → MCP via mcp-router                    │
│  LLM Wiki (curated) → MCP via mcp-router + ~/wiki/ markdown    │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decision: mcp-router as Single Transport Hub

**All MCP-based knowledge tools MUST route through mcp-router.** No new MCP server entries should be added to Hermes config.yaml, Claude's MCP config, or any agent's direct MCP configuration.

**Why:**
- mcp-router already aggregates GitNexus, Brave, Tavily, Exa, and agentmemory tools
- The CLI `connect` command bridges HTTP→stdio for all agents
- Agents already have one connection (`npx @mcp_router/cli@latest connect`)
- Adding direct MCP connections per agent defeats the purpose of a central hub
- mcp-router manages server lifecycle (start/stop/restart, health checks)

**Exception:** graphify is a CLI tool (not an MCP server), so it integrates via AGENTS.md/skills that tell agents to run `graphify query/path/explain` through Bash. This is correct — graphify's output format doesn't fit the MCP tool model well (it returns structured text, not tool-callable results).

## Phase 1: Agent Wiring — Detailed Design

### graphify Integration

**Current state:** graphify v0.9.31 binary installed. `graphify install <platform>` writes platform-specific integration. Zero agents currently have it installed.

**Approach:** Run `graphify install` for each platform:

| Platform | Command | Integration Type |
|----------|---------|-----------------|
| Hermes | `graphify install hermes` | Skill file at `~/.hermes/skills/graphify/` |
| Claude Code | `graphify install claude` | AGENTS.md section + skill in workspace `.claude/` |
| Codex | `graphify install codex` | AGENTS.md section in workspace `.codex/` |
| Pi | `graphify install pi` | Skill at `~/.pi/agent/skills/graphify/` |
| OpenCode | `graphify install opencode` | AGENTS.md section + plugin in workspace `.opencode/` |

**Why CLI, not MCP:** graphify operates on local `graph.json` files. Its commands (`query`, `path`, `explain`) read pre-computed JSON artifacts. Wrapping this in MCP would add latency and complexity for no benefit — the agent can call `graphify query "..."` directly via Bash.

**Cross-reference pattern:** graphify queries complement GitNexus queries:
- `graphify query "order processing"` → structural AST relationships (fast, no API cost)
- `gitnexus query "order processing"` → semantic execution flows (deeper, indexed)
- Agents should try graphify first (free), GitNexus for deeper analysis

### agentmemory Integration

**Current state:** agentmemory v0.9.27 running at localhost:3111, 0 sessions, 1 memory. Not connected to any agent.

**Approach:** Two integration paths:

1. **MCP path (preferred):** Register agentmemory as an MCP server in mcp-router. Its MCP shim (`agentmemory mcp`) exposes tools: `memory_recall`, `memory_save`, `memory_smart_search`, `memory_audit`, `memory_export`. Once registered, all agents get these tools via mcp-router.

2. **Direct connect (fallback):** `agentmemory connect --all` wires agents directly. Use only if mcp-router registration fails.

**Scope:** `AGENTMEMORY_AGENT_SCOPE=shared` means all agents share the same memory store. This is intentional — cross-agent context sharing is the goal.

### Cross-Reference Additions

Add brief cross-references to workspace AGENTS.md. Current count is 1876 words (limit 550) — the graphify section (lines 294-305) already exists and is sufficient. No additional AGENTS.md changes needed for graphify.

## Phase 2: LLM Wiki — Detailed Design

### Directory Structure

```
~/Developer/wiki/
├── SCHEMA.md           # Domain, conventions, tag taxonomy
├── index.md            # Sectioned content catalog
├── log.md              # Chronological action log
├── raw/                # Immutable source material
│   ├── articles/       # Web articles, PR descriptions
│   ├── papers/         # Research (Karpathy patterns, etc.)
│   └── transcripts/    # Session insights
├── entities/           # Per-service pages (order-service, inventory-service, etc.)
├── concepts/           # Patterns (CQRS, saga, event-sourcing, agent coordination)
├── comparisons/        # Agent capabilities, tool trade-offs
├── queries/            # Filed answers to architectural questions
└── _archive/           # Superseded content
```

### SCHEMA.md Design

Domain: **Workspace intelligence** — Go microservices architecture, Python agent ecosystem, cross-repo patterns, debugging playbooks, tool configurations, agent coordination patterns.

Tag taxonomy (15 tags):
- **Architecture:** `service`, `pattern`, `decision`, `dataflow`, `api-contract`
- **Operations:** `debugging`, `playbook`, `incident`, `deployment`, `monitoring`
- **Ecosystem:** `agent`, `tool`, `mcp`, `skill`, `configuration`

Page thresholds:
- Create a page when an entity/concept appears in 2+ sources OR is central to one source.
- Never create pages for passing mentions.
- Split pages over 200 lines into sub-topics with cross-links.

### Seeding Strategy

Seed from existing workspace knowledge rather than starting empty:

1. **From GitNexus indexed repos:** Each indexed repo gets an entity page summarizing purpose, key modules, and cross-repo dependencies. Use `gitnexus context` output as source material.
2. **From graphify-out/wiki/ (go-microservices):** Extract concept pages and feed as raw sources.
3. **From go-microservices/docs/:** Ingest architecture decision records and operational runbooks.
4. **From agent-harness workflow:** Document the 12-stage LangGraph workflow as a concept page.
5. **From workspace AGENTS.md:** Extract cross-repo dependencies and conventions.

**Trade-off:** Seeding from existing sources is faster than starting blank but risks importing stale content. Mitigation: feed raw sources into `raw/`, then curate entity/concept pages from them.

## Phase 3: Wiki MCP Server — Detailed Design

### Architecture

A stateless Python MCP server that reads/writes the wiki directory. Registered as a local MCP server in mcp-router's server manager.

**Server location:** `~/Developer/wiki-mcp-server/wiki_mcp_server.py`

**Why a separate directory (not under ~/.hermes/skills/):** The wiki MCP server is a standalone tool that happens to serve the wiki. It's not a Hermes skill — it's a mcp-router backend. Keeping it at `~/Developer/wiki-mcp-server/` makes it visible, testable, and maintainable independently.

**Transport:** stdio (launched by mcp-router as a child process). No HTTP endpoint needed — mcp-router handles the HTTP→stdio bridge.

### Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `wiki_search` | Search wiki pages by content/tags | `query: str`, `section: str (optional)` |
| `wiki_read` | Read a specific wiki page | `page_path: str` |
| `wiki_index` | Get the content catalog | `section: str (optional)` |
| `wiki_ingest` | Suggest a new page or update | `content: str`, `type: entity\|concept\|comparison` |
| `wiki_links` | Get cross-references for a page | `page_path: str` |
| `wiki_stale` | Find pages needing refresh | `days: int = 90` |

### mcp-router Registration

Register the wiki server in mcp-router through the Electron UI:

1. Open mcp-router → Add Server → Local
2. Command: `python3`
3. Args: `["/Users/androidteam/Developer/wiki-mcp-server/wiki_mcp_server.py"]`
4. Auto-start: enabled
5. Name: `wiki`

Or programmatically via the SQLite database at mcp-router's app data directory.

Once registered, mcp-router:
- Starts the server on launch (auto-start)
- Discovers its tools
- Aggregates them alongside GitNexus, agentmemory, Brave, etc.
- Routes tool calls to the wiki server
- All agents connected to mcp-router get `mcp__mcp_router__wiki_*` tools

### Why Not a Unified "Super-Query" Server

A server that wraps graphify + GitNexus + agentmemory + wiki behind one `ask_workspace()` tool was considered but rejected:

- **Complexity:** Four backends with different output formats and error patterns. Wrapping them increases surface area.
- **Agent tool preference:** Agents already have per-tool patterns (graphify for structure, GitNexus for impact). A unified tool would obscure which backend answered.
- **Incremental value:** Wiring existing tools + wiki MCP gives 90% of the value at 30% of the build cost.

## Phase 4: Hermes Orchestration — Detailed Design

### Weekly Wiki Maintenance Cron

```
Schedule: 0 9 * * 1  (Monday 9:00 AM)
Prompt: |
  Run LLM Wiki lint on ~/Developer/wiki/.
  Check: orphan pages, broken wikilinks, index completeness, 
  frontmatter validation, stale pages (>90 days), source drift.
  Report issues grouped by severity.
  Append summary to wiki log.md.
```

### Post-Task Wiki Capture

Add a pattern to Hermes delegation workflows:

1. After a coding agent completes a complex task (5+ tool calls), Hermes inspects the session.
2. If the task involved novel debugging, architecture decisions, or cross-repo patterns, Hermes extracts insights.
3. Hermes ingests insights into the wiki as entity or concept pages.
4. This is triggered by Hermes memory patterns, not by agent output parsing.

**Trade-off:** Automated capture risks ingesting noise. Mitigation: only capture when explicitly flagged by the task completion pattern.

### Graphify Post-Commit Awareness

Repos with `graphify-out/` should refresh their graph after significant code changes. Rather than a mandatory hook, add awareness to agent workflows:

- When Hermes delegates a code change to an agent, include: "After committing, run `graphify update .` if graphify-out/ exists in the target repo."
- This is advisory, not enforced.
