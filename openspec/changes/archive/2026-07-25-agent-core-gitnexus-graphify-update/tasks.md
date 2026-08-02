## 1. GitNexus Re-index

- [x] 1.1 Run `node .gitnexus/run.cjs analyze` to re-index agent-core (takes ~2-5 min)
- [x] 1.2 Verify index is fresh: `node .gitnexus/run.cjs status` shows "fresh"
- [x] 1.3 Verify symbol count > 0, relationship count > 0, process count > 0

## 2. Graphify Update

- [x] 2.1 Update Graphify: `pip install --upgrade graphifyy`
- [x] 2.2 Verify version: `graphify --version` shows >= 0.9.14
- [x] 2.3 Run `graphify install --platform claude` to register with Claude Code

## 3. Graphify Generation

- [x] 3.1 Run `graphify analyze .` to generate knowledge graph
- [x] 3.2 Verify graphify-out/ directory exists with:
  - graph.json (queryable graph)
  - graph.html (interactive visualization)
  - GRAPH_REPORT.md (analysis report)

## 4. Documentation Update

- [x] 4.1 Update AGENTS.md GitNexus section with re-index command
- [x] 4.2 Add Graphify section with query/path/explain commands
- [x] 4.3 Add usage examples for both tools
