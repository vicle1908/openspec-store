# Proposal

## Why

Oh My Pi (OMP) lacked its native user-level MCP server configuration (`~/.omp/agent/mcp.json`), preventing the harness from mounting and utilizing the 134 tools exposed by the running MCP Router desktop daemon on `localhost:3282`. In addition, `wiki-mcp-server` was missing its `.venv` runtime dependencies, causing MCP Router's local `wiki` server to crash and degrade health watchdog reporting.

## What Changes

- **Provision Native OMP MCP Configuration**: Create `~/.omp/agent/mcp.json` configured with `@mcp_router/cli@latest connect` and the approved `pi` client bearer token (`mcpr_yxjuHImh-NIxCy7sRujfb3bI8xX1Gal0`).
- **Synchronize Legacy Pi Config**: Update `~/.pi/agent/mcp.json` to reference the canonical `pi` client token.
- **Security Hardening**: Enforce file mode `600` (`-rw-------`) on both `~/.omp/agent/mcp.json` and `~/.pi/agent/mcp.json` per credential protection standards.
- **Restore Wiki MCP Server Environment**: Rebuild `wiki-mcp-server/.venv` via `uv sync` and restart MCP Router to achieve a healthy state with all 6 local servers active.
- **Update Operational Readiness Spec**: Modify `specs/operational-readiness/spec.md` to explicitly recognize OMP (`~/.omp/agent/mcp.json`) alongside Claude Code, Cursor, Codex, OpenCode, and Hermes.
- **Update Workspace Documentation**: Document OMP native MCP router wiring in `AGENTS.md`, `.claude/CLAUDE.md`, and `wiki/entities/mcp-router.md`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `operational-readiness`: Incorporate OMP (`~/.omp/agent/mcp.json`) into the mandatory wired AI coding agent configurations and knowledge server routing contracts.

## Impact

- **Affected Boundaries**: `~/.omp/agent/mcp.json`, `~/.pi/agent/mcp.json`, `~/Developer/wiki-mcp-server/.venv`, `Developer/AGENTS.md`, `Developer/.claude/CLAUDE.md`, `wiki/entities/mcp-router.md`, and OpenSpec store.
- **Non-Goals**: No committed `.mcp.json` or `.cursor/mcp.json` in `~/Developer/` or individual repositories (preserving OpenSpec opt-in governance).
- **Breaking Changes**: None. All existing client configurations remain intact.
