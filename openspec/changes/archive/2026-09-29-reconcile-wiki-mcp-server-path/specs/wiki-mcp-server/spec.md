# Spec Delta

## MODIFIED Requirements

### Requirement: Resilient MCP Router and client registration
The registration configuration for the `wiki` server in MCP Router (`mcprouter.db`) and standalone client configuration files (`~/.claude.json`, `~/.cursor/mcp.json`, `~/.codex/config.toml`) SHALL utilize the `uv run --directory` command invocation pattern pointing to the canonical repository path under `ai-tooling/wiki-mcp-server`.

#### Scenario: MCP Router process launch
- **WHEN** MCP Router spawns the `wiki` server process
- **THEN** the command SHALL be `uv` (or an absolute path to the `uv` executable)
- **AND** the arguments SHALL specify `["run", "--directory", "/Users/androidteam/Developer/ai-tooling/wiki-mcp-server", "wiki-mcp-server"]`
- **AND** MCP Router SHALL establish a healthy stdio transport session and aggregate the wiki tools without spawning failures or missing-directory errors.

#### Scenario: Standalone agent client launch
- **WHEN** an AI coding agent (e.g. Cursor or Codex) launches the server directly from local configuration
- **THEN** the server configuration SHALL specify command `uv` with args `["run", "--directory", "/Users/androidteam/Developer/ai-tooling/wiki-mcp-server", "wiki-mcp-server"]`
- **AND** the client SHALL discover the MCP tools without requiring manual shell activation.
