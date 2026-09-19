# Tasks

## 1. Package Modernization in wiki-mcp-server

- [ ] 1.1 Expose callable `main()` function in `src/wiki_mcp_server/server.py` that invokes `server.run(transport="stdio")` and ensure `if __name__ == "__main__":` delegates to `main()`. Verify with `python -c "import wiki_mcp_server.server as s; assert callable(s.main)"`.
- [ ] 1.2 Add console script entrypoint `wiki-mcp-server = "wiki_mcp_server.server:main"` under `[project.scripts]` in `pyproject.toml`. Verify with `grep -A 2 '\[project.scripts\]' pyproject.toml`.
- [ ] 1.3 Synchronize dependencies and build the entrypoint binary via `uv sync` in `/Users/androidteam/Developer/wiki-mcp-server`. Verify with `uv run --directory /Users/androidteam/Developer/wiki-mcp-server wiki-mcp-server --help` or direct python import check.
- [ ] 1.4 Test direct stdio MCP JSON-RPC protocol initialization using `uv run --directory /Users/androidteam/Developer/wiki-mcp-server wiki-mcp-server` to confirm `initialize` returns `serverInfo.name == "wiki"`.

## 2. MCP Router Database Migration

- [ ] 2.1 Create a backup snapshot of `mcprouter.db` at `~/Library/Application Support/MCP Router/mcprouter.db.backup.<timestamp>`. Verify backup file exists and matches size.
- [ ] 2.2 Update the `wiki` server entry (ID `2af2f157-2c80-4182-abb6-1dfed0adde48`) in SQLite database `mcprouter.db`: set `command = 'uv'` and `args = '["run","--directory","/Users/androidteam/Developer/wiki-mcp-server","wiki-mcp-server"]'`. Verify query returns the updated command and args.
- [ ] 2.3 Restart MCP Router or trigger server reload to pick up the updated database record. Verify with `lsof -i :3282` that MCP Router is listening.

## 3. Verification and Integration Validation

- [ ] 3.1 Verify MCP Router HTTP endpoint (`http://localhost:3282/mcp`) lists all 6 wiki tools (`wiki_search`, `wiki_read`, `wiki_index`, `wiki_ingest`, `wiki_links`, `wiki_stale`) with bearer token authentication.
- [ ] 3.2 Execute an end-to-end `tools/call` for `wiki_search` through MCP Router to confirm search results are returned from `~/Developer/wiki`.
- [ ] 3.3 Validate self-healing behavior by testing `uv run --directory /Users/androidteam/Developer/wiki-mcp-server wiki-mcp-server` when `.venv` is temporarily simulated as unlinked, verifying that `uv` cleanly recreates the environment without crashing.
- [ ] 3.4 Document standalone client configurations in `wiki-mcp-server/README.md` for Claude Code, Cursor, and Codex.
