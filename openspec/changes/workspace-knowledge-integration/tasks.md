# workspace-knowledge-integration — Tasks

## 1. Wire graphify into all agents

- [ ] 1.1 Run `graphify install hermes` and verify skill file at `~/.hermes/skills/graphify/`.
- [ ] 1.2 Run `graphify install claude` and verify AGENTS.md section + skill in workspace `.claude/`.
- [ ] 1.3 Run `graphify install codex` and verify AGENTS.md section in workspace `.codex/`.
- [ ] 1.4 Run `graphify install pi` and verify skill at `~/.pi/agent/skills/graphify/`.
- [ ] 1.5 Run `graphify install opencode` and verify AGENTS.md section + plugin in workspace `.opencode/`.
- [ ] 1.6 For each installed agent, spawn a test prompt ("What does graphify-out/ show about this codebase?") and verify the agent invokes graphify CLI.
- [ ] 1.7 Record evidence: file paths created, test prompt outputs for each agent.

## 2. Wire agentmemory into mcp-router

- [ ] 2.1 Verify agentmemory MCP shim works: `agentmemory mcp` starts and responds to tool discovery.
- [ ] 2.2 Register agentmemory in mcp-router as a local MCP server (via UI or database): command `agentmemory`, args `["mcp"]`, auto-start enabled.
- [ ] 2.3 Restart mcp-router to pick up the new server registration.
- [ ] 2.4 Verify agentmemory tools appear in mcp-router's aggregated tool list: `mcp__mcp_router__memory_recall`, `mcp__mcp_router__memory_save`, etc.
- [ ] 2.5 Verify agentmemory status shows connections from mcp-router: `agentmemory status`.
- [ ] 2.6 Record evidence: mcp-router server list, tool discovery output, agentmemory status.

## 3. Initialize LLM Wiki

- [ ] 3.1 Create directory structure at `~/Developer/wiki/`: raw/, raw/articles/, raw/papers/, raw/transcripts/, entities/, concepts/, comparisons/, queries/, _archive/.
- [ ] 3.2 Write `SCHEMA.md` with domain (workspace intelligence), conventions, frontmatter format, tag taxonomy (15 tags), page thresholds, and update policy.
- [ ] 3.3 Write initial `index.md` with sectioned headers (Entities, Concepts, Comparisons, Queries) and creation date.
- [ ] 3.4 Write initial `log.md` with creation entry.
- [ ] 3.5 Seed entity pages from GitNexus indexed repos (one page per repo: agent-core, agent-harness, go-microservices, etc.) with purpose, key modules, and cross-repo dependencies. Use `gitnexus context` output as source material.
- [ ] 3.6 Seed concept pages from workspace architecture: "Go microservices platform", "Python agent ecosystem", "MCP transport layer", "OpenSpec change lifecycle".
- [ ] 3.7 Seed comparison page: "Coding agent capabilities" (graphify vs GitNexus vs agentmemory vs LLM Wiki — what each covers).
- [ ] 3.8 Update index.md with all seeded pages and verify total page count.
- [ ] 3.9 Record evidence: directory listing, index.md contents, log.md entry.

## 4. Build wiki MCP server and register in mcp-router

- [ ] 4.1 Create `~/Developer/wiki-mcp-server/wiki_mcp_server.py` (~200 LOC) implementing tools: wiki_search, wiki_read, wiki_index, wiki_ingest, wiki_links, wiki_stale.
- [ ] 4.2 Server reads/writes `~/Developer/wiki/` directory. No database, no embeddings. Uses Python MCP SDK stdio transport.
- [ ] 4.3 Write unit tests for each tool: search returns matching pages, read returns page content, index returns catalog, ingest creates/updates pages, links returns cross-references, stale returns old pages.
- [ ] 4.4 Run tests and verify server starts: `python3 wiki_mcp_server.py` responds to MCP tool discovery.
- [ ] 4.5 Register wiki server in mcp-router: Add Server → Local → command `python3`, args `["/Users/androidteam/Developer/wiki-mcp-server/wiki_mcp_server.py"]`, auto-start enabled, name `wiki`.
- [ ] 4.6 Restart mcp-router and verify wiki tools appear in aggregated tool list: `mcp__mcp_router__wiki_search`, `mcp__mcp_router__wiki_read`, etc.
- [ ] 4.7 Spawn Hermes with: "Search the wiki for debugging playbooks" and verify it calls `mcp__mcp_router__wiki_search` via mcp-router.
- [ ] 4.8 Record evidence: test output, mcp-router server list, tool discovery logs, manual search result.

## 5. Verify cross-agent wiki access via mcp-router

- [ ] 5.1 Spawn Claude Code with: "Check the wiki for architecture patterns" and verify it calls wiki tools through mcp-router.
- [ ] 5.2 Spawn Codex with: "Search the wiki for agent coordination patterns" and verify wiki tools are available.
- [ ] 5.3 Spawn Pi with: "Read the wiki page for go-microservices platform" and verify wiki tools are accessible.
- [ ] 5.4 Record evidence: per-agent wiki tool invocation outputs.

## 6. Hermes cron for wiki maintenance

- [ ] 6.1 Create a weekly cron job (Monday 9:00 AM) that runs wiki lint: orphan detection, broken wikilinks, index completeness, frontmatter validation, stale pages, source drift.
- [ ] 6.2 Verify cron job appears in `cronjob list` and fires correctly with a test run.
- [ ] 6.3 Record evidence: cron job definition, test run output.

## 7. Post-task wiki capture pattern

- [ ] 7.1 Document the wiki capture pattern in Hermes delegation workflow notes: after complex tasks, extract architectural insights and ingest into wiki.
- [ ] 7.2 Test the pattern: delegate a complex debugging task to an agent, then verify Hermes extracts and ingests insights.
- [ ] 7.3 Record evidence: capture workflow test output, new wiki pages created.

## 8. Integration verification

- [ ] 8.1 Spawn Hermes with a cross-tool query: "How does order processing work? Use graphify for structure, GitNexus for impact, agentmemory for past sessions, and wiki for compiled knowledge."
- [ ] 8.2 Verify Hermes calls multiple tools (graphify via Bash, GitNexus/agentmemory/wiki via mcp-router) and synthesizes results.
- [ ] 8.3 Verify no direct MCP server entries exist in Hermes config.yaml for wiki, agentmemory, or GitNexus — all route through mcp-router.
- [ ] 8.4 Record evidence: multi-tool query outputs, MCP config audit.
