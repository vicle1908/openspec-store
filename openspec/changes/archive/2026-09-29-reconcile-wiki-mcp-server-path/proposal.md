# Proposal

## Why

Following the workspace reorganization into first-class organizational namespaces (`ai-tooling/`), the `wiki-mcp-server` repository was relocated from `/Users/androidteam/Developer/wiki-mcp-server` to `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server`. However, MCP Router's database configuration (`~/Library/Application Support/MCP Router/mcprouter.db`) and documentation still point to the old pre-reorganization path. Whenever MCP Router is restarted, spawned processes for the `wiki` MCP server fail immediately with `os error 2 (No such file or directory)`, causing the health check (`mcp-router-health.sh`) to report critical degradation and preventing coding agents from accessing workspace LLM Wiki tools.

## What Changes

- **Update MCP Router registration arguments**: Reconcile the `args` field in SQLite database `mcprouter.db` for server `wiki` (`id: 2af2f157-2c80-4182-abb6-1dfed0adde48`) to reference `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server`.
- **Update documentation**: Align `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server/README.md` to reference the canonical path `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server`.
- **Synchronize OpenSpec specification**: Update the capability specification `wiki-mcp-server` to mandate the canonical `ai-tooling/wiki-mcp-server` project path for MCP Router spawn invocations.
- **Explicit Non-Goals**:
  - We do NOT modify the 6 core wiki tools (`wiki_search`, `wiki_read`, `wiki_index`, `wiki_ingest`, `wiki_links`, `wiki_stale`) or their JSON-RPC signatures.
  - We do NOT modify the underlying wiki documentation content at `~/Developer/wiki`.
  - We do NOT alter the `mcp-router` Electron application source code or token permission models.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wiki-mcp-server`: Update the MCP Router registration scenario to require the canonical project path `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server` in the `uv run --directory` invocation arguments.

## Impact

- **Affected System Databases**: `/Users/androidteam/Library/Application Support/MCP Router/mcprouter.db` (`servers` table entry `2af2f157-2c80-4182-abb6-1dfed0adde48`).
- **Affected Documentation & Configuration**: `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server/README.md`.
- **Affected Runtime Processes**: Running instances of `MCP Router` will be gracefully restarted to load updated database records.
- **Dependencies**: Requires `uv` (installed at `/opt/homebrew/bin/uv`) and active Python 3.11+ environment in `ai-tooling/wiki-mcp-server`.
