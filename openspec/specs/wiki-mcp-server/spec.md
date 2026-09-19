# wiki-mcp-server Specification

## Purpose
Define the packaging, runtime, and registration specifications for the workspace LLM Wiki MCP server (`wiki-mcp-server`), ensuring self-healing environment execution via `uv run`, standard console script entrypoint packaging, and resilient stdio MCP integration across MCP Router and AI coding agents.

## Requirements

### Requirement: Standard CLI console script entrypoint
The `wiki-mcp-server` package SHALL expose a console script entrypoint named `wiki-mcp-server` within its `pyproject.toml` packaging configuration that boots the MCP server over stdio transport.

#### Scenario: Direct execution of console script
- **WHEN** the `wiki-mcp-server` entrypoint binary is invoked within an active project environment
- **THEN** it SHALL start the MCP server listening on stdio
- **AND** respond to MCP `initialize` JSON-RPC requests with server name `wiki`.

#### Scenario: Script execution via project runner
- **WHEN** invoking `uv run --directory <wiki-mcp-server-dir> wiki-mcp-server`
- **THEN** `uv` SHALL resolve the declared entrypoint without error
- **AND** bridge stdio streams directly to the MCP server process.

### Requirement: Reproducible execution via uv project runner
Execution of the wiki MCP server SHALL be driven by `uv run` referencing the project directory and lockfile, eliminating dependency on direct invocation of interpreter binaries inside `.venv/bin/python`.

#### Scenario: Execution after virtual environment recreation
- **WHEN** the `.venv` directory in `wiki-mcp-server` is purged or absent
- **AND** the server is invoked with `uv run --directory <wiki-mcp-server-dir> wiki-mcp-server`
- **THEN** `uv` SHALL automatically recreate and synchronize the virtual environment from `uv.lock` before starting the server
- **AND** the server SHALL start successfully without throwing `ENOENT` or broken symlink errors.

#### Scenario: Locked dependency adherence
- **WHEN** dependencies in `pyproject.toml` are modified
- **THEN** `uv.lock` SHALL be updated via `uv sync` before deploying or registering the runtime
- **AND** runtime invocation SHALL strictly conform to locked dependencies.

### Requirement: Resilient MCP Router and client registration
The registration configuration for the `wiki` server in MCP Router (`mcprouter.db`) and standalone client configuration files (`~/.claude.json`, `~/.cursor/mcp.json`, `~/.codex/config.toml`) SHALL utilize the `uv run --directory` command invocation pattern.

#### Scenario: MCP Router process launch
- **WHEN** MCP Router spawns the `wiki` server process
- **THEN** the command SHALL be `uv` (or an absolute path to the `uv` executable)
- **AND** the arguments SHALL include `["run", "--directory", "<wiki-mcp-server-dir>", "wiki-mcp-server"]`
- **AND** MCP Router SHALL establish a healthy stdio transport session and aggregate the wiki tools.

#### Scenario: Standalone agent client launch
- **WHEN** an AI coding agent (e.g. Cursor or Codex) launches the server directly from local configuration
- **THEN** the server configuration SHALL specify command `uv` with args `["run", "--directory", "<wiki-mcp-server-dir>", "wiki-mcp-server"]`
- **AND** the client SHALL discover the MCP tools without requiring manual shell activation.

### Requirement: Preservation of core wiki tool contracts
The modernization of the server packaging and execution layer SHALL preserve all 6 core wiki tools and their functional behavior across `~/Developer/wiki`.

#### Scenario: Tool discovery and listing
- **WHEN** a client sends a `tools/list` request to the running server
- **THEN** the server SHALL return exactly 6 tools: `wiki_search`, `wiki_read`, `wiki_index`, `wiki_ingest`, `wiki_links`, and `wiki_stale`
- **AND** their input schemas SHALL remain backwards compatible.

#### Scenario: Wiki root path resolution
- **WHEN** `WIKI_ROOT` environment variable is unset
- **THEN** the server SHALL default to resolving wiki markdown files from `$HOME/Developer/wiki`
- **AND** **WHEN** `WIKI_ROOT` is explicitly set
- **THEN** the server SHALL resolve all page queries against the specified custom directory.
