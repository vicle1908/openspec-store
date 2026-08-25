## 1. Graphify Server — ✅ COMPLETED

- [x] 1.1 Updated mcp-router database command to `python -m graphify.serve`
- [x] 1.2 Installed `mcp` package in graphifyy environment
- [x] 1.3 Verified `graphify-out/graph.json` exists (17MB)
- [x] 1.4 Verified 10 graphify tools served and visible in mcp-router
- [x] 1.5 Verified graphify tools callable via mcp-router HTTP API (graph_stats returns 12329 nodes)

## 2. Wiki Server — ✅ COMPLETED

- [x] 2.1 Investigated root cause and fixed wiki server code (MCP 2.0 MCPServer)
- [x] 2.2 Restored original database entry (id: 2af2f157-2c80-4182-abb6-1dfed0adde48)
- [x] 2.3 Verified wiki server starts as child of mcp-router
- [x] 2.4 Verified wiki server connected via unix sockets
- [x] 2.5 Verified wiki tools appear in tools/list (6 tools)
- [x] 2.6 Verified wiki tools callable via mcp-router HTTP API (wiki_search returns results)

## 3. Validation — ✅ COMPLETED

- [x] 3.1 Graphify tools verified end-to-end (graph_stats returns 12329 nodes)
- [x] 3.2 Wiki tools verified end-to-end (wiki_search returns search results)
- [x] 3.3 Total: 13 servers, 142 tools served
- [x] 3.4 Archive the OpenSpec change
