# Design

## Context

Oh My Pi (OMP 18.2.6) incorporates a native discovery engine (`la = "native"`, priority 100) that looks for user-level MCP configuration at `~/.omp/agent/mcp.json`. Prior to this change, only `~/.pi/agent/mcp.json` existed (created prior to the binary cutover to `omp`), leaving OMP without native MCP tool routes.

The running MCP Router daemon (`localhost:3282`) validates incoming connections against tokens configured in `~/Library/Application Support/MCP Router/shared-config.json`. The token registered for `clientId: "pi"` is `mcpr_yxjuHImh-NIxCy7sRujfb3bI8xX1Gal0` with active access granted across all 19 server backends.

One of these local backends, `wiki-mcp-server`, relies on `/Users/androidteam/Developer/wiki-mcp-server/.venv/bin/python`. The virtual environment was missing, resulting in spawn failure (exit code 127) and degraded health reports in `~/.hermes/scripts/mcp-router-health.sh`.

## Goals / Non-Goals

**Goals:**
- Provide native user-level MCP configuration for OMP in `~/.omp/agent/mcp.json`.
- Synchronize `~/.pi/agent/mcp.json` to reference the canonical `pi` token.
- Secure all token-bearing configuration files with file mode `600`.
- Restore `wiki-mcp-server/.venv` using `uv sync` and verify full local server health (all 6 local servers running).
- Verify end-to-end tool execution through OMP non-interactive mode.

**Non-Goals:**
- Committing `.mcp.json` or `.cursor/mcp.json` in `~/Developer/` or individual Git repositories (preserving OpenSpec opt-in workspace governance).
- Modifying MCP Router binary or SQLite schema directly.

## Decisions

### Decision 1: Stdio Bridge via `@mcp_router/cli connect`
- **Rationale**: While MCP Router exposes an HTTP/SSE endpoint on port 3282, all workspace coding assistants (Claude Code, Cursor, Codex, Hermes, OpenCode, Zed) standardize on `npx -y @mcp_router/cli@latest connect` with `MCPR_TOKEN` passed in the process environment. This ensures protocol compatibility, automated stream reconnection, and seamless stdio transport inside OMP.

### Decision 2: Reuse Pre-registered `pi` Client Token
- **Rationale**: `shared-config.json` already contains `clientId: "pi"` (`mcpr_yxjuHImh-NIxCy7sRujfb3bI8xX1Gal0`) with permissions configured for all 19 registered MCP servers. Reusing this token preserves the immutable token baseline required by operational readiness specs.

### Decision 3: Standardize `wiki-mcp-server` Runtime on `uv`
- **Rationale**: `wiki-mcp-server` already defines `pyproject.toml` and `uv.lock`. Executing `uv sync` deterministically builds the `.venv` with Python 3.14.5 and `mcp>=2.0.0` in ~1.2s without polluting global site-packages.

## Risks / Trade-offs

- **Cache Eviction Risk**: Routine disk cleanups (`uv cache clean`, temp folder purges) might delete `wiki-mcp-server/.venv`.
  - *Mitigation*: The Hermes health watchdog (`mcp-router-health.sh`) monitors process health and logs missing servers. Document the `uv sync` recovery step in operational docs.
- **Credential Protection**: Storing bearer tokens in plain JSON files.
  - *Mitigation*: Files are stored in `$HOME/.omp/agent/` outside Git tracking and hardened with mode `600` (`-rw-------`).
