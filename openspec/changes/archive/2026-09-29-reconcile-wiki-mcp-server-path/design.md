# Design

## Context

See `proposal.md` for motivation.

Following the organizational namespace migration, workspace tools were grouped under `~/Developer/<org>/`. In this structure, `wiki-mcp-server` resides at `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server`. The MCP Router SQLite configuration stored in `~/Library/Application Support/MCP Router/mcprouter.db` contained a stale reference to `/Users/androidteam/Developer/wiki-mcp-server`. On restart, the router spawned `uv run --directory /Users/androidteam/Developer/wiki-mcp-server wiki-mcp-server`, which threw `os error 2` because the directory was not found.

## Goals / Non-Goals

**Goals:**
- Reconcile `mcprouter.db` to point to `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server` using valid JSON array formatting.
- Reconcile documentation and setup snippets in `ai-tooling/wiki-mcp-server/README.md`.
- Execute a clean restart cycle of the MCP Router application.
- Verify end-to-end operational health via `mcp-router-health.sh` and live JSON-RPC tool availability.

**Non-Goals:**
- Modifying MCP Router application binaries or Electron code.
- Modifying the wiki data store at `~/Developer/wiki`.
- Modifying tool schemas or method definitions in `wiki-mcp-server`.

## Decisions

### Decision 1: Direct SQLite Update on `mcprouter.db`
Update the `args` column for server `wiki` in `servers` table:
```sql
UPDATE servers
SET args = '["run","--directory","/Users/androidteam/Developer/ai-tooling/wiki-mcp-server","wiki-mcp-server"]',
    updated_at = strftime('%s','now') * 1000
WHERE name = 'wiki';
```
*Rationale*: MCP Router persists local server configurations in SQLite. `args` MUST be a valid JSON array string; bare strings cause runtime parsing failures.

### Decision 2: Graceful Electron Application Restart
Execute standard macOS application lifecycle commands:
1. `osascript -e 'quit app "MCP Router"'`
2. Wait for process exit.
3. Relaunch with `open -a "MCP Router"`.
4. Allow initialization buffer (35s) for child processes (`gitnexus`, `brave`, `wiki`, etc.) to boot.

### Decision 3: Documentation Alignment
Update `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server/README.md` to reference the canonical path `/Users/androidteam/Developer/ai-tooling/wiki-mcp-server` across all CLI examples and MCP configuration snippets.

## Risks / Trade-offs

- **[Risk]** In-memory cache overwrite if MCP Router writes to SQLite during quit.
  *Mitigation*: Quit the application before updating SQLite, or verify that the updated row in `mcprouter.db` persists after relaunch.
- **[Risk]** Child process startup race condition.
  *Mitigation*: Poll `mcp-router-health.sh --json` after the designated startup wait period to confirm `healthy_servers` includes `wiki` and `critical_missing` is empty.
