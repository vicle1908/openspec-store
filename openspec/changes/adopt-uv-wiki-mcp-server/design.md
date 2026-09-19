# Design

## Context

The `wiki-mcp-server` repository at `~/Developer/wiki-mcp-server` provides the workspace with MCP-based access to the curated LLM wiki at `~/Developer/wiki`. See `proposal.md` for motivation.

Currently, MCP Router (`~/Library/Application Support/MCP Router/mcprouter.db`) executes the server via an unmanaged direct virtualenv interpreter:
```
command: /Users/androidteam/Developer/wiki-mcp-server/.venv/bin/python
args: ["/Users/androidteam/Developer/wiki-mcp-server/src/wiki_mcp_server/server.py"]
```
This configuration bypasses `uv`'s project management lifecycle. If `.venv` is deleted or corrupted (as observed during historical cache cleanups), execution fails with missing interpreter or file descriptor leak issues.

## Goals / Non-Goals

**Goals:**
- Provide a standardized console script entrypoint `wiki-mcp-server` in `pyproject.toml`.
- Refactor `src/wiki_mcp_server/server.py` to provide a clean, callable `main()` function.
- Synchronize and lock the project environment with `uv sync`.
- Update the MCP Router SQLite database registration to invoke the server via `uv run --directory <path> wiki-mcp-server`.
- Provide verified fallback/standalone configuration recipes for AI coding agents (Claude Code, Cursor, Codex).

**Non-Goals:**
- Modify the 6 MCP tools (`wiki_search`, `wiki_read`, `wiki_index`, `wiki_ingest`, `wiki_links`, `wiki_stale`) or their JSON-RPC signatures.
- Change the underlying wiki storage format or markdown schema at `~/Developer/wiki`.
- Replace or re-architect MCP Router.

## Decisions

### 1. Standard Console Script Packaging
Configure standard `hatchling` / PEP 621 script entrypoint in `pyproject.toml`:
```toml
[project.scripts]
wiki-mcp-server = "wiki_mcp_server.server:main"
```
*Rationale*: Enables clean CLI dispatch without hardcoding source file paths.

### 2. Callable `main()` Function in `server.py`
Expose an explicit entrypoint function:
```python
def main() -> None:
    """Main entrypoint for wiki MCP server."""
    server.run(transport="stdio")

if __name__ == "__main__":
    main()
```
*Rationale*: Conforms to standard Python packaging best practices while remaining runnable via `python server.py`.

### 3. Invocation Pattern via `uv run --directory`
Register the server in MCP Router using:
- `command`: `uv` (or `/opt/homebrew/bin/uv` if absolute path is preferred for daemons without full shell PATH)
- `args`: `["run", "--directory", "/Users/androidteam/Developer/wiki-mcp-server", "wiki-mcp-server"]`

*Alternatives considered*:
- *Invoking `.venv/bin/wiki-mcp-server` directly*: Still susceptible to breakage if `.venv` is purged.
- *Running `uv run python -m wiki_mcp_server.server`*: Functional, but less standard than a named console script.

### 4. Database Migration Safety & Verification
Update SQLite row in `mcprouter.db`:
- Backup `mcprouter.db` before modification.
- Execute targeted `UPDATE servers SET command = 'uv', args = '["run","--directory","/Users/androidteam/Developer/wiki-mcp-server","wiki-mcp-server"]', updated_at = ... WHERE id = '2af2f157-2c80-4182-abb6-1dfed0adde48'`.
- Verify MCP Router live responsiveness and tool aggregation.

## Risks / Trade-offs

- **Process PATH Availability**: In GUI daemons (like Electron-based MCP Router), `PATH` might not include `/opt/homebrew/bin`.
  *Mitigation*: MCP Router's `mcp-client.ts` uses `getUserShellEnv()` to load the user's login shell environment, ensuring `uv` in `/opt/homebrew/bin` is resolved. Using `/opt/homebrew/bin/uv` or verifying shell PATH avoids ambiguity.
- **Lockfile Drift**: If dependencies change without updating `uv.lock`, `uv run` may attempt a lock sync at runtime.
  *Mitigation*: Pre-sync and verify with `uv sync` during implementation.
