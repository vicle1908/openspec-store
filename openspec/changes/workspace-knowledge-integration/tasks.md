# workspace-knowledge-integration — Tasks

## 1. Upgrade graphify to 0.9.33

- [ ] 1.1 Run `uv tool install "graphifyy[all,postgres]" --upgrade` and verify `graphify --version` returns 0.9.33.
- [ ] 1.2 Verify `graphify --help` still shows all commands (install, update, query, path, explain, affected, god-nodes, tree, global, save-result, reflect, check-update, hook, extract).
- [ ] 1.3 Record evidence: version output, help output.

## 2. Build graph.json for all repos

- [ ] 2.1 Run `graphify update .` in browser-cli (small, validates process). Verify graph.json created.
- [ ] 2.2 Run `graphify update .` in ops-automation-suite. Verify graph.json created.
- [ ] 2.3 Run `graphify update .` in remaining Python repos (agent-core, agent-docs-sync, agent-harness, ai-harness-skills, ai-review, code-daily-scan, jira-daily-reports, jira-epic-report, jira-kanban-from-spreadsheet, jira-skill, tdt-observability, tdt-sheets, webhook-receiver).
- [ ] 2.4 Run `graphify update . --code-only` in go-microservices (Go AST extraction).
- [ ] 2.5 Run `graphify update .` in mcp-router (Node.js/TypeScript).
- [ ] 2.6 Verify all 18 repos have valid graph.json. Record sizes.
- [ ] 2.7 Run `graphify graph_stats` in 3 repos to verify graph quality (node count, edge count, community count).

## 3. Build global cross-repo graph

- [ ] 3.1 Run `graphify global add <repo>/graphify-out/graph.json --as <repo-name>` for each repo with valid graph.json.
- [ ] 3.2 Run `graphify global list` to verify all repos registered.
- [ ] 3.3 Run `graphify global path` to verify global graph path.
- [ ] 3.4 Test cross-repo query: `graphify query "tdt_core" --graph ~/.graphify/global-graph.json`.
- [ ] 3.5 Record evidence: global list output, cross-repo query result.

## 4. Install git hooks

- [ ] 4.1 Run `graphify hook install` in each repo with graph.json.
- [ ] 4.2 Run `graphify hook status` in 3 repos to verify hooks installed.
- [ ] 4.3 Test: make a small change, commit, verify graph rebuilds automatically.
- [ ] 4.4 Record evidence: hook status output, auto-rebuild test result.

## 5. Generate tree visualizations

- [ ] 5.1 Run `graphify tree --label "<repo>"` in 3 repos with graph.json.
- [ ] 5.2 Verify GRAPH_TREE.html created in graphify-out/.
- [ ] 5.3 Record evidence: file sizes, HTML opens correctly.

## 6. Install remaining agent skills

- [ ] 6.1 Run `graphify install hermes` and verify skill at `~/.hermes/skills/graphify/`.
- [ ] 6.2 Run `graphify install pi` and verify skill at `~/.pi/agent/skills/graphify/`.
- [ ] 6.3 Run `graphify install opencode` and verify skill + plugin at workspace `.opencode/`.
- [ ] 6.4 Verify Claude Code and Codex graphify skills still work after upgrade (existing install should pick up new skill content on next `graphify install`).
- [ ] 6.5 Record evidence: file paths for each agent.

## 7. Initialize LLM Wiki

- [ ] 7.1 Create directory structure at `~/Developer/wiki/` (raw/, entities/, concepts/, comparisons/, queries/, _archive/).
- [ ] 7.2 Write SCHEMA.md: domain, conventions, frontmatter format, 15-tag taxonomy, page thresholds, update policy.
- [ ] 7.3 Write initial index.md with sectioned headers and creation date.
- [ ] 7.4 Write initial log.md with creation entry.
- [ ] 7.5 Seed entity pages from GitNexus indexed repos (one per repo) using gitnexus context output.
- [ ] 7.6 Seed concept pages: "Go microservices platform", "Python agent ecosystem", "MCP transport layer", "OpenSpec change lifecycle", "Graphify knowledge graph system".
- [ ] 7.7 Seed comparison page: "Knowledge tools" (graphify vs GitNexus vs agentmemory vs LLM Wiki).
- [ ] 7.8 Update index.md with all seeded pages, verify count.
- [ ] 7.9 Record evidence: directory listing, index.md, log.md.

## 8. Build wiki MCP server + register in mcp-router

- [ ] 8.1 Create `~/Developer/wiki-mcp-server/wiki_mcp_server.py` (~200 LOC).
  Tools: wiki_search, wiki_read, wiki_index, wiki_ingest, wiki_links, wiki_stale.
  Python MCP SDK stdio transport. Stateless.
- [ ] 8.2 Write unit tests for each tool.
- [ ] 8.3 Run tests, verify server starts and responds to MCP tool discovery.
- [ ] 8.4 Register in mcp-router: Add Server -> Local -> command python3, args [server path], auto-start enabled, name wiki.
- [ ] 8.5 Restart mcp-router, verify wiki tools in aggregated tool list.
- [ ] 8.6 Spawn Hermes: "Search the wiki for debugging playbooks" -- verify `mcp__mcp_router__wiki_search` called.
- [ ] 8.7 Record evidence: test output, mcp-router server list, search result.

## 9. Verify cross-agent wiki access

- [ ] 9.1 Spawn Claude Code with: "Check the wiki for architecture patterns" -- verify wiki tools via mcp-router.
- [ ] 9.2 Spawn Codex with: "Search the wiki for agent coordination patterns" -- verify wiki tools.
- [ ] 9.3 Record evidence: per-agent invocation outputs.

## 10. Hermes orchestration

- [ ] 10.1 Create weekly cron (Monday 8:00 AM): graphify check-update across all repos. Report repos needing re-extraction.
- [ ] 10.2 Create weekly cron (Monday 9:00 AM): wiki lint (orphans, broken links, stale pages).
- [ ] 10.3 Verify both cron jobs appear in `cronjob list`.
- [ ] 10.4 Record evidence: cron definitions, test run outputs.

## 11. Documentation and agent guide updates

- [ ] 11.1 Update workspace AGENTS.md graphify section (lines 294-305): add global graph, tree, memory, check-update, wiki reference. Stay within 550-word limit.
- [ ] 11.2 Update per-repo AGENTS.md for repos with graph.json: add hook install, update, check-update instructions.
- [ ] 11.3 Update Hermes graphify skill: add global graph, tree, memory, check-update commands.
- [ ] 11.4 Record evidence: AGENTS.md diffs, skill file diffs.

## 12. Integration verification

- [ ] 12.1 Spawn Hermes with cross-tool query: "How does order processing work? Use graphify for structure, GitNexus for impact, agentmemory for past sessions, and wiki for compiled knowledge."
- [ ] 12.2 Verify Hermes calls graphify via Bash + GitNexus/agentmemory/wiki via mcp-router.
- [ ] 12.3 Verify no direct MCP entries in Hermes config.yaml for knowledge tools.
- [ ] 12.4 Run `graphify global list` to confirm cross-repo graph intact.
- [ ] 12.5 Record evidence: multi-tool outputs, config audit, global graph status.
