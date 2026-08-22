## 1. Graphify Server — ✅ COMPLETED

- [x] 1.1 Updated mcp-router database: command=`/Users/androidteam/.local/share/uv/tools/graphifyy/bin/python`, args=`["-m","graphify.serve","/Users/androidteam/Developer/go-microservices/graphify-out/graph.json"]`
- [x] 1.2 Installed `mcp` package in graphifyy environment
- [x] 1.3 Verified `~/Developer/go-microservices/graphify-out/graph.json` exists (17MB)
- [x] 1.4 Restarted mcp-router — graphify tools appear: 10 tools ✅

## 2. Wiki Server — Code Fixed, Electron App Needs Rebuild

### Completed
- [x] 2.1 Ported wiki server from MCP 2.0 FastMCP to MCP 1.29.0 low-level Server API
- [x] 2.2 Added `_filter_blank_stdin()` matching graphify's implementation
- [x] 2.3 Verified wiki server works standalone (initialize + tools/list → 6 tools)
- [x] 2.4 Verified wiki server works with Node.js MCP client (same SDK as mcp-router)
- [x] 2.5 Updated mcp-router database: replaced old wiki entry with new one
- [x] 2.6 Deleted old disabled wiki entry to avoid name collisions

### Remaining (Blocked)
- [ ] 2.7 **Rebuild mcp-router Electron app** — current app (v0.6.3, built Jul 22) bundles older MCP SDK that may not connect to wiki server properly. After rebuild, wiki tools should appear.
- [ ] 2.8 Test wiki tools from mcp-router HTTP API after rebuild
- [ ] 2.9 End-to-end test: call wiki_search from Claude Code

## 3. Validation

- [ ] 3.1 After Electron app rebuild: restart mcp-router
- [ ] 3.2 Verify both wiki and graphify tools appear in tool list
- [ ] 3.3 Test wiki tools: wiki_search, wiki_read, wiki_index, wiki_ingest, wiki_links, wiki_stale
- [ ] 3.4 Test graphify tools: query_graph, graph_stats, etc.
- [ ] 3.5 Archive the OpenSpec change
