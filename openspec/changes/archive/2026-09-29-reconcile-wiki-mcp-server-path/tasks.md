# Tasks

## 1. Specification & Documentation Alignment

- [x] 1.1 Update `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server/README.md` to reference the canonical directory `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server`. Verify that all CLI and MCP client configuration snippets reference the canonical path.

## 2. MCP Router Database Registration & Application Restart

- [x] 2.1 Update the `args` column for the `wiki` server entry in SQLite database `~/Library/Application Support/MCP Router/mcprouter.db` to `["run","--directory","/Users/androidteam/Developer/ai-tooling/wiki-mcp-server","wiki-mcp-server"]`. Verify the query output.
- [x] 2.2 Perform a graceful restart of `MCP Router.app` via `osascript -e 'quit app "MCP Router"'`, wait for teardown, and relaunch with `open -a "MCP Router"`.

## 3. End-to-End Operational Verification

- [x] 3.1 Run `~/.hermes/scripts/mcp-router-health.sh --json` after the restart stabilization period (35s) and verify that `status` is `healthy` with `wiki` listed in `healthy_servers` and `critical_missing` empty.
- [x] 3.2 Verify live tool execution by invoking a wiki tool (`wiki_search` or `wiki_index`) through MCP Router to confirm valid JSON-RPC tool response and knowledge base access.
