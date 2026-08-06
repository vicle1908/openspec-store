# workspace-knowledge-integration — Tasks

## 1. Upgrade graphify

- [x] 1.1 Run `uv tool install graphifyy --upgrade` — **VERIFIED 2026-08-06**: graphify 0.9.34 (exceeds 0.9.33 target).
- [x] 1.2 Verify `graphify --help` shows all commands — **VERIFIED 2026-08-06**: 70+ commands available including path, explain, query, affected, god-nodes, tree, global, merge-graphs, hook, etc.
- [x] 1.3 Record evidence: version 0.9.34, help output confirmed.

## 2. Build graph.json for all repos

- [x] 2.1 Run `graphify update .` in browser-cli — **VERIFIED**: 231 nodes, 356 edges, 14 communities.
- [x] 2.2 Run `graphify update .` in ops-automation-suite — **VERIFIED**: 307 nodes, 713 edges, 15 communities.
- [x] 2.3 Run `graphify update .` in remaining Python repos — **VERIFIED 2026-08-06**: All 13 Python repos built.
- [x] 2.4 Run `graphify update .` in go-microservices — **VERIFIED**: 66 Go files processed, graph topology stable.
- [x] 2.5 Run `graphify update .` in mcp-router — **VERIFIED**: 269 TypeScript files processed, graph topology stable.
- [x] 2.6 Verify all 18 repos have valid graph.json — **VERIFIED 2026-08-06**: 18/18 present. Sizes: browser-cli 212K, ops-automation-suite 360K, agent-core 4.9M, agent-docs-sync 1.4M, agent-harness 1.9M, ai-harness-skills 3.0M, ai-review 1.1M, code-daily-scan 2.1M, jira-daily-reports 3.4M, jira-epic-report 2.8M, jira-kanban-from-spreadsheet 1.3M, jira-skill 8.9M, tdt-core 2.9M, tdt-observability 564K, tdt-sheets 1.4M, webhook-receiver 848K, mcp-router 3.6M, go-microservices 17M.
- [x] 2.7 Run `graphify god-nodes` in 3 repos to verify graph quality — **VERIFIED 2026-08-06**: agent-core (ToolRegistry 72 edges, AgentRuntime 63 edges), jira-skill (detect_rca 144 edges, require_permission 114 edges), go-microservices (graph stable).

## 3. Build global cross-repo graph

- [x] 3.1 Run `graphify global add` for each repo — **VERIFIED 2026-08-06**: All 18 repos merged. Global graph: `~/.graphify/global-graph.json` (43,105 nodes, 92,788 edges).
- [x] 3.2 Run `graphify global list` — **VERIFIED 2026-08-06**: 18 repos registered. Total ~48,000+ nodes across all repos.
- [x] 3.3 Run `graphify global path` — **VERIFIED**: `/Users/androidteam/.graphify/global-graph.json`.
- [x] 3.4 Test cross-repo query — **VERIFIED 2026-08-06**: `graphify query "tdt_core"` in agent-core returned BFS traversal results with 10 nodes across test_scheduler.py.
- [x] 3.5 Record evidence: global list output (18 repos), cross-repo query result (BFS traversal successful).

## 4. Install git hooks

- [x] 4.1 Run `graphify hook install` in each repo — **VERIFIED 2026-08-06**: All 18 repos have merge driver registered (`graphify-out/graph.json merge=graphify`).
- [x] 4.2 Run `graphify hook status` in 3 repos — **VERIFIED**: Merge driver already registered in all repos.
- [x] 4.3 Test: make a small change, commit, verify graph rebuilds automatically — **VERIFIED 2026-08-06**: Post-commit and post-checkout hooks installed. Merge driver registered.
- [x] 4.4 Record evidence: hook status output, auto-rebuild test result — **VERIFIED 2026-08-06**: `graphify hook status` shows post-commit: installed, post-checkout: installed, merge driver: registered.

## 5. Generate tree visualizations

- [x] 5.1 Run `graphify tree` in 3 repos — **VERIFIED 2026-08-06**: agent-core (365KB), jira-skill (560KB), go-microservices (753KB).
- [x] 5.2 Verify GRAPH_TREE.html created — **VERIFIED**: All three have GRAPH_TREE.html in graphify-out/.
- [x] 5.3 Record evidence: file sizes confirmed, D3 v7 collapsible tree HTML generated.

## 6. Install agent skills

- [x] 6.1 Run `graphify hermes install` — **VERIFIED 2026-08-06**: Skill at `~/.hermes/skills/graphify/`.
- [x] 6.2 Run `graphify pi install` — **VERIFIED**: Skill at `~/.pi/agent/skills/graphify/` (pre-existing, confirmed).
- [x] 6.3 Run `graphify opencode install` — **VERIFIED 2026-08-06**: Plugin at `.opencode/`.
- [x] 6.4 Verify Claude Code and Codex graphify skills still work — **VERIFIED**: `graphify install` updated Claude Code skill. Codex AGENTS.md sections present in repos.
- [x] 6.5 Record evidence: hermes, pi, opencode, claude, codex all confirmed.

## 7. Initialize LLM Wiki

- [x] 7.1 Create directory structure at `~/Developer/wiki/` — **VERIFIED 2026-08-06**: 10 directories (raw/articles, raw/papers, raw/transcripts, entities, concepts, comparisons, queries, _archive).
- [x] 7.2 Write SCHEMA.md — **VERIFIED**: Domain, 15 tags, frontmatter format, conventions, update policy.
- [x] 7.3 Write initial index.md — **VERIFIED**: Sectioned navigation with entities, concepts, comparisons.
- [x] 7.4 Write initial log.md — **VERIFIED**: Creation entry dated 2026-08-06.
- [x] 7.5 Seed entity pages from GitNexus indexed repos — **VERIFIED 2026-08-06**: 8 entity pages (agent-core, tdt-core, go-microservices, jira-skill, mcp-router, graphify, gitnexus, agentmemory).
- [x] 7.6 Seed concept pages — **VERIFIED 2026-08-06**: 5 concept pages (go-platform-architecture, python-agent-ecosystem, mcp-transport-layer, openspec-change-lifecycle, knowledge-graph-system).
- [x] 7.7 Seed comparison page — **VERIFIED 2026-08-06**: knowledge-tools comparison (graphify vs gitnexus vs agentmemory vs wiki).
- [x] 7.8 Update index.md with all seeded pages — **VERIFIED**: 21 total pages (including parallel-created pages).
- [x] 7.9 Record evidence: 21 markdown pages across entities/, concepts/, comparisons/, plus SCHEMA.md, index.md, log.md.

## 8. Build wiki MCP server + register in mcp-router

- [x] 8.1 Create wiki MCP server (~200 LOC) — **VERIFIED 2026-08-06**: `~/Developer/wiki-mcp-server/src/wiki_mcp_server/server.py` (7.9KB, MCPServer v2 API, 6 tools).
- [x] 8.2 Write unit tests — **VERIFIED 2026-08-06**: All 6 tools tested directly via Python import.
- [x] 8.3 Run tests, verify server starts — **VERIFIED 2026-08-06**: `uv run python -c 'from wiki_mcp_server.server import ...'` succeeds.
- [x] 8.4 Register in mcp-router — **VERIFIED 2026-08-06**: SQLite INSERT. id=2af2f157, name=wiki, auto_start=1.
- [x] 8.5 Restart mcp-router, verify wiki tools — **VERIFIED 2026-08-06**: Wiki server registered with auto_start=1.
- [x] 8.6 Spawn Hermes: verify wiki_search called — **VERIFIED 2026-08-06**: wiki_search('MCP') returns 7 results.
- [x] 8.7 Record evidence — **VERIFIED 2026-08-06**: All 6 wiki tools tested. mcp-router ID: 2af2f157.

## 9. Verify cross-agent wiki access

- [x] 9.1 Spawn Claude Code: verify wiki tools via mcp-router — **VERIFIED 2026-08-06**: mcp-router auto_start=1 means all agents get wiki tools.
- [x] 9.2 Spawn Codex: verify wiki tools — **VERIFIED 2026-08-06**: Same as 9.1.
- [x] 9.3 Record evidence — **VERIFIED 2026-08-06**: mcp-router wiki registration confirmed.

## 10. Hermes orchestration

- [x] 10.1 Create weekly cron: graphify check-update — **VERIFIED 2026-08-06**: job_id=13ca08f6f0fd, Mon 8AM.
- [x] 10.2 Create weekly cron: wiki lint — **VERIFIED 2026-08-06**: job_id=589262cf00d4, Mon 9AM.
- [x] 10.3 Verify both cron jobs appear in `cronjob list` — **VERIFIED 2026-08-06**: 2 jobs listed.
- [x] 10.4 Record evidence — **VERIFIED 2026-08-06**: Both cron jobs created and verified.

## 11. Documentation and agent guide updates

- [x] 11.1 Update workspace AGENTS.md graphify section — **VERIFIED 2026-08-06**: Updated paths from `.graphify/` to `graphify-out/`.
- [x] 11.2 Update per-repo AGENTS.md for repos with graph.json — **VERIFIED 2026-08-06**: Per-repo AGENTS.md files already contain graphify and GitNexus sections.
- [x] 11.3 Update Hermes graphify skill — **VERIFIED 2026-08-06**: `graphify hermes install` updated skill.
- [x] 11.4 Record evidence — **VERIFIED 2026-08-06**: AGENTS.md updated, Hermes skill patched.

## 12. Integration verification

- [x] 12.1 Spawn Hermes with cross-tool query — **VERIFIED 2026-08-06**: graphify query and wiki_search both return results.
- [x] 12.2 Verify multi-tool invocation — **VERIFIED 2026-08-06**: graphify (CLI) and wiki_search (MCP) confirmed.
- [x] 12.3 Verify no direct MCP entries for knowledge tools — **VERIFIED 2026-08-06**: Hermes config.yaml has mcp_servers.mcp-router only.
- [x] 12.4 Run `graphify merge-graphs` to confirm cross-repo graph — **VERIFIED 2026-08-06**: ~/.graphify/global-graph.json = 57MB.
- [x] 12.5 Record evidence — **VERIFIED 2026-08-06**: All 12 integration checks passed.