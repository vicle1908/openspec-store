# Proposal

## Why

The `wiki-mcp-server` is currently registered in MCP Router and client configurations using a fragile, unmanaged direct virtual environment path (`/Users/androidteam/Developer/wiki-mcp-server/.venv/bin/python`), lacking a standard `[project.scripts]` CLI entrypoint and risking launch failures whenever virtual environments are cleaned up or recreated. Adopting standard `uv` project execution (`uv run --directory ... wiki-mcp-server`) with a formal console script ensures self-healing environment synchronization, lockfile integrity, and resilience across cache invalidations and Python runtime updates.

## What Changes

- **Add CLI entrypoint to package metadata**: Configure `[project.scripts]` in `pyproject.toml` exposing `wiki-mcp-server = "wiki_mcp_server.server:main"`.
- **Expose executable `main()` function**: Refactor `src/wiki_mcp_server/server.py` to provide a clean `main()` function wrapping `server.run(transport="stdio")` while preserving `if __name__ == "__main__":` backwards compatibility.
- **Synchronize uv lockfile and project environment**: Run `uv sync` in `wiki-mcp-server` to build and link the console script entrypoint into the project virtualenv.
- **Modernize MCP Router registration**: Update the MCP Router SQLite database (`~/Library/Application Support/MCP Router/mcprouter.db`) server entry for `wiki` from raw `.venv/bin/python` to `uv run --directory /Users/androidteam/Developer/wiki-mcp-server wiki-mcp-server`.
- **Document standard client configurations**: Provide reference `uv run` MCP client configurations for Claude Code (`~/.claude.json`), Cursor (`~/.cursor/mcp.json`), and Codex (`~/.codex/config.toml`).
- **Explicit Non-Goals**:
  - We do NOT alter the 6 core wiki tools (`wiki_search`, `wiki_read`, `wiki_index`, `wiki_ingest`, `wiki_links`, `wiki_stale`) or their JSON-RPC signatures.
  - We do NOT modify the underlying wiki documentation files or wiki directory structure at `~/Developer/wiki`.
  - We do NOT replace or deprecate MCP Router (`mcp-aggregator`); we update the registration command within the router's database.

## Capabilities

### New Capabilities

- `wiki-mcp-server`: Runtime, packaging, and execution contracts for the workspace LLM Wiki MCP server, covering standard `uv` project entrypoint packaging, reproducible lockfile execution, stdio transport, and resilient MCP router/client registration.

### Modified Capabilities

None.

## Impact

- **Affected Repository**: `/Users/androidteam/Developer/wiki-mcp-server` (`pyproject.toml`, `src/wiki_mcp_server/server.py`, `uv.lock`).
- **Affected System Databases**: `/Users/androidteam/Library/Application Support/MCP Router/mcprouter.db` (`servers` table entry `2af2f157-2c80-4182-abb6-1dfed0adde48`).
- **Ownership Boundaries**: The change is bounded to `wiki-mcp-server` packaging and local MCP Router server registration. It does not affect `go-microservices`, `tdt-core`, `agent-core`, or other Python services.
- **Dependencies**: Requires `uv` (installed at `/opt/homebrew/bin/uv` or in PATH) and `mcp>=2.0.0`.
