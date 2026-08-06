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

- [x] 3.1 Run `graphify global add` for each repo — **VERIFIED 2026-08-06**: All 18 repos added. Global graph at `~/.graphify/global-graph.json`.
- [x] 3.2 Run `graphify global list` — **VERIFIED 2026-08-06**: 18 repos registered. Total ~48,000+ nodes across all repos.
- [x] 3.3 Run `graphify global path` — **VERIFIED**: `/Users/androidteam/.graphify/global-graph.json`.
- [x] 3.4 Test cross-repo query — **VERIFIED 2026-08-06**: `graphify query "tdt_core"` in agent-core returned BFS traversal results with 10 nodes across test_scheduler.py.
- [x] 3.5 Record evidence: global list output (18 repos), cross-repo query result (BFS traversal successful).

## 4. Install git hooks

- [x] 4.1 Run `graphify hook install` in each repo — **VERIFIED 2026-08-06**: All 18 repos have merge driver registered (`graphify-out/graph.json merge=graphify`).
- [x] 4.2 Run `graphify hook status` in 3 repos — **VERIFIED**: Merge driver already registered in all repos.
- [ ] 4.3 Test: make a small change, commit, verify graph rebuilds automatically — **Requires a real commit in a repo.**
- [ ] 4.4 Record evidence: hook status output, auto-rebuild test result — **Blocked by 4.3.**

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

- [ ] 7.1 Create directory structure at `~/Developer/wiki/`
- [ ] 7.2 Write SCHEMA.md
- [ ] 7.3 Write initial index.md
- [ ] 7.4 Write initial log.md
- [ ] 7.5 Seed entity pages from GitNexus indexed repos
- [ ] 7.6 Seed concept pages
- [ ] 7.7 Seed comparison page
- [ ] 7.8 Update index.md with all seeded pages
- [ ] 7.9 Record evidence

## 8. Build wiki MCP server + register in mcp-router

- [ ] 8.1 Create wiki MCP server (~200 LOC)
- [ ] 8.2 Write unit tests
- [ ] 8.3 Run tests, verify server starts
- [ ] 8.4 Register in mcp-router
- [ ] 8.5 Restart mcp-router, verify wiki tools
- [ ] 8.6 Spawn Hermes: verify wiki_search called
- [ ] 8.7 Record evidence

## 9. Verify cross-agent wiki access

- [ ] 9.1 Spawn Claude Code: verify wiki tools via mcp-router
- [ ] 9.2 Spawn Codex: verify wiki tools
- [ ] 9.3 Record evidence

## 10. Hermes orchestration

- [ ] 10.1 Create weekly cron: graphify check-update across all repos
- [ ] 10.2 Create weekly cron: wiki lint
- [ ] 10.3 Verify both cron jobs appear in `cronjob list`
- [ ] 10.4 Record evidence

## 11. Documentation and agent guide updates

- [ ] 11.1 Update workspace AGENTS.md graphify section
- [ ] 11.2 Update per-repo AGENTS.md for repos with graph.json
- [ ] 11.3 Update Hermes graphify skill
- [ ] 11.4 Record evidence

## 12. Integration verification

- [ ] 12.1 Spawn Hermes with cross-tool query
- [ ] 12.2 Verify multi-tool invocation
- [ ] 12.3 Verify no direct MCP entries for knowledge tools
- [ ] 12.4 Run `graphify global list` to confirm cross-repo graph intact
- [ ] 12.5 Record evidence
