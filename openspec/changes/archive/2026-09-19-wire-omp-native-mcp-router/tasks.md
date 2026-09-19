# Tasks

## 1. Native OMP Configuration & Security Hardening

- [x] 1.1 Create `~/.omp/agent/mcp.json` configuring `mcp-router` via `@mcp_router/cli@latest connect` with `mcpr_yxjuHImh-NIxCy7sRujfb3bI8xX1Gal0`
- [x] 1.2 Synchronize `~/.pi/agent/mcp.json` to reference the canonical `pi` token
- [x] 1.3 Harden file permissions to mode 600 (`-rw-------`) on both configuration files

## 2. Wiki MCP Server Runtime & Health Recovery

- [x] 2.1 Rebuild `wiki-mcp-server/.venv` using `uv sync` in `~/Developer/wiki-mcp-server`
- [x] 2.2 Verify MCP Router health and trigger daemon restart via `mcp-router-health.sh --restart`
- [x] 2.3 Confirm all 6 local servers (`agentmemory`, `brave`, `desktop-commander`, `gitnexus`, `node_repl`, `wiki`) report healthy

## 3. Verification & End-to-End Testing

- [x] 3.1 Verify native OMP MCP discovery and stdio bridge connection
- [x] 3.2 Execute live non-interactive tool call (`wiki_index`) through OMP to confirm end-to-end routing
- [x] 3.3 Confirm workspace governance compliance: verify no `.mcp.json` or `.cursor/mcp.json` is committed in `~/Developer`

## 4. Documentation & Spec Synchronization

- [x] 4.1 Update `Developer/AGENTS.md` and `Developer/.claude/CLAUDE.md` documenting OMP native MCP integration
- [x] 4.2 Update `wiki/entities/mcp-router.md` with OMP native client configuration instructions
- [x] 4.3 Validate OpenSpec change via `openspec validate --store openspec-store`
