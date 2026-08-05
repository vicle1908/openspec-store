# workspace-knowledge-integration — Design

## Verified Current State

| Tool | Version | Latest | Status | Gap |
|------|---------|--------|--------|-----|
| graphify | 0.9.31 | **0.9.33** | Skills: Claude Codex only. graph.json: 1/18 repos. No hooks, global graph, memory, tree, check-update. | 2 versions behind with critical data-integrity bugs. |
| GitNexus | 1.6.9 | 1.6.9 | All 17 repos indexed. 9 MCP tools in mcp-router. No wiki generated. | Wiki generation unused. |
| agentmemory | 0.9.27 | 0.9.27 | 6 MCP tools in mcp-router. Codex connected. 0 sessions, 1 memory. | Tools available, not invoked. |
| LLM Wiki | N/A | N/A | Does not exist. | Full creation needed. |

### Why Upgrade Matters (0.9.31 -> 0.9.33)

- **v0.9.32**: Incremental rebuilds no longer drop cross-file call edges. Tier-aware merge (AST re-extract keeps semantic layer). Directed flag preserved. `graphify update` writes manifest.json to correct directory.
- **v0.9.33**: C# partial-class regression fixed. Worker crash recovery (extract no longer silently loses files). Incremental edge preservation verified.
- **Impact without upgrade**: `graphify update` produces graphs missing cross-module relationships, directed graphs silently become undirected, partial worker failures go undetected.

## Architecture

```
Agents (Hermes, Claude, Codex, Pi, fable-5, OpenCode)
  |
  +-- graphify CLI --------> graphify-out/graph.json (per-repo, via Bash)
  |                          ~/.graphify/global-graph.json (cross-repo)
  |
  +-- mcp-router CLI bridge (stdio -> HTTP localhost:3282)
       |
       +-- GitNexus MCP ----> query, context, impact, trace, cypher,
       |                       detect_changes, rename, explain, check
       |
       +-- agentmemory MCP -> memory_recall, memory_save,
       |                       memory_smart_search, memory_audit,
       |                       memory_export, memory_sessions
       |
       +-- Wiki MCP (NEW) --> wiki_search, wiki_read, wiki_index,
                               wiki_ingest, wiki_links, wiki_stale
```

## Phase 1: Upgrade and Activate graphify

### 1a. Upgrade to 0.9.33

```bash
uv tool install "graphifyy[all,postgres]" --upgrade
# Verify: graphify --version -> 0.9.33
```

Backward-compatible. Existing graphify-out/ and skill files preserved.

### 1b. Build graph.json for All Repos

Run `graphify update .` in each repo. For Python repos, local AST extraction (no API key). For Go, `--code-only`. Skip openspec-store (no meaningful code).

**Order**: Small repos first (browser-cli, ops-automation-suite) to validate, then batch.

Repos to process (17 repos, tdt-core already has graph.json):
- Python (16): agent-core, agent-docs-sync, agent-harness, ai-harness-skills, ai-review, browser-cli, code-daily-scan, jira-daily-reports, jira-epic-report, jira-kanban-from-spreadsheet, jira-skill, ops-automation-suite, tdt-observability, tdt-sheets, webhook-receiver
- Go (1): go-microservices
- Node.js (1): mcp-router (has graphify-out/ but no graph.json)

### 1c. Build Global Cross-Repo Graph

```bash
for repo in ~/Developer/*/; do
  [ -f "$repo/graphify-out/graph.json" ] && \
    graphify global add "$repo/graphify-out/graph.json" --as "$(basename $repo)"
done
# Result: ~/.graphify/global-graph.json
```

Enables cross-repo queries via the global graph.

### 1d. Install Git Hooks

```bash
for repo in ~/Developer/*/; do
  [ -d "$repo/.git" ] && (cd "$repo" && graphify hook install)
done
```

Post-commit: auto-rebuild graph (AST-only, fast). Post-checkout: ensure freshness.

### 1e. Generate Tree Visualizations

For each repo with valid graph.json:
```bash
cd <repo> && graphify tree --label "<repo-name>"
```

Output: `graphify-out/GRAPH_TREE.html` (D3 v7 collapsible-tree).

### 1f. Install Remaining Agent Skills

| Agent | Command | Target |
|-------|---------|--------|
| Pi | `graphify install pi` | `~/.pi/agent/skills/graphify/` |
| Hermes | `graphify install hermes` | `~/.hermes/skills/graphify/` |
| OpenCode | `graphify install opencode` | `.opencode/` workspace |

### 1g. Memory Feedback Loop

Agents can save query outcomes for institutional memory:
```bash
graphify save-result --question "..." --answer "..." --type query \
  --nodes "NodeA" "NodeB" --outcome useful
```

Periodic aggregation:
```bash
graphify reflect --graph ~/.graphify/global-graph.json
```

## Phase 2: Initialize LLM Wiki

### Directory Structure

```
~/Developer/wiki/
  SCHEMA.md, index.md, log.md
  raw/articles/, raw/papers/, raw/transcripts/
  entities/, concepts/, comparisons/, queries/
  _archive/
```

### SCHEMA.md

Domain: Workspace intelligence.
Tags: service, pattern, decision, dataflow, api-contract, debugging, playbook, incident, deployment, monitoring, agent, tool, mcp, skill, configuration.

### Seeding

1. GitNexus repo metadata -> entity pages (one per indexed repo)
2. go-microservices/docs/ -> raw/articles/ -> concept pages
3. Agent-harness workflow -> concept page
4. Graphify global graph stats -> concept page

## Phase 3: Wiki MCP Server + mcp-router

### Server

`~/Developer/wiki-mcp-server/wiki_mcp_server.py` (~200 LOC Python). stdio transport. Stateless.

Tools: wiki_search, wiki_read, wiki_index, wiki_ingest, wiki_links, wiki_stale.

### mcp-router Registration

Add Server via UI or API: command python3, args with server path, auto-start enabled.

All agents get `mcp__mcp_router__wiki_*` via existing mcp-router connection.

## Phase 4: Hermes Orchestration

### Cron Jobs

1. **Weekly graphify freshness** (Monday 8:00 AM): `graphify check-update .` across all repos.
2. **Weekly wiki lint** (Monday 9:00 AM): orphans, broken links, stale pages.

### Post-Task Wiki Capture

After complex agent tasks, Hermes extracts insights and ingests into wiki.

## Phase 5: Documentation and Agent Guide Updates

### Files to Update

| File | Changes |
|------|---------|
| `~/Developer/AGENTS.md` (lines 294-305) | Expand graphify section: global graph, tree, memory, check-update, wiki reference |
| Per-repo `AGENTS.md` files | Add graphify hook/freshness instructions where graph.json exists |
| `~/.hermes/skills/graphify/SKILL.md` | Add global graph, tree, memory, check-update commands |
| Wiki SCHEMA.md | Create (new) |
| Wiki index.md | Create (new) |

### Workspace AGENTS.md Graphify Section (Replacement for lines 294-305)

```
## graphify

Knowledge graph at graphify-out/ with community structure and cross-file
relationships. Global cross-repo graph at ~/.graphify/global-graph.json.

Per-repo: query, path, explain, affected, god-nodes, update, tree,
check-update. Cross-repo: global path/add/remove/list.
Memory: save-result, reflect. Hooks: hook install/status.

After modifying code, run graphify update . to keep graph fresh.
```

### Per-Repo AGENTS.md Additions

For repos with graph.json, add:
```
## graphify

Run graphify hook install once to enable auto-rebuild on commit.
After code changes, graphify update . refreshes the graph.
graphify check-update . detects staleness (cron-safe).
```
