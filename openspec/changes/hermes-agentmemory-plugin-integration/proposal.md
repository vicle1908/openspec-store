# hermes-agentmemory-plugin-integration

## Why

Hermes Agent currently has two independent memory systems:
1. **Built-in memory** — flat MEMORY.md/USER.md files + SQLite FTS5 session search
2. **agentmemory** — installed globally (v0.9.28), registered in mcp-router, but server not running and no Hermes plugin installed

The result: Hermes has no episodic cross-session memory, no pre-LLM context injection, no automatic turn-level capture, and no session compaction protection. Every new session starts from scratch. The agentmemory ecosystem (95.2% retrieval accuracy, hybrid BM25+vector+graph search, cross-agent shared memory) is available but not wired into Hermes.

The `developer-memory` OpenSpec spec already defines agentmemory as the shared developer-memory layer. The MCP server is registered in mcp-router with auto_start=1. The missing piece is the Hermes plugin that provides deep lifecycle integration — 6 hooks that make agentmemory transparent to the agent, not just another tool.

## What Changes

### Phase 1: Start agentmemory server
- Verify agentmemory v0.9.28 is installed and healthy
- Start the agentmemory server on localhost:3111
- Verify health endpoint responds
- Verify MCP tools are reachable through mcp-router (auto_start=1 already configured)

### Phase 2: Install Hermes memory provider plugin
- Copy `integrations/hermes/` from the agentmemory repo to `~/.hermes/plugins/agentmemory/`
- Files: `__init__.py`, `plugin.yaml`, `README.md`
- The plugin provides `AgentMemoryProvider` class implementing the `MemoryProvider` interface
- 6 lifecycle hooks:
  - `prefetch()` — inject relevant memories before each LLM call
  - `sync_turn()` — capture every conversation turn in background
  - `on_session_end()` — mark sessions complete for summarization
  - `on_pre_compress()` — re-inject context before compaction
  - `on_memory_write()` — mirror MEMORY.md writes to agentmemory
  - `system_prompt_block()` — inject project profile at session start
- 3 tools: `memory_recall`, `memory_save`, `memory_search`

### Phase 3: Configure Hermes
- Set `memory.provider: agentmemory` in `~/.hermes/config.yaml`
- Verify environment variables (AGENTMEMORY_URL defaults to http://localhost:3111)
- No additional config needed — plugin auto-reads `~/.agentmemory/.env`

### Phase 4: Verify end-to-end
- `hermes memory status` shows agentmemory as available
- Save a test memory, recall it in a new session
- Verify prefetch injects context before LLM calls
- Verify sync_turn captures conversation in background
- Verify on_pre_compress preserves context during compaction
- Verify MCP tools work through mcp-router (memory_save, memory_smart_search, etc.)

### Phase 5: Documentation
- Update workspace-knowledge-tools skill to reflect plugin status
- Update wiki agentmemory entity page
- Commit all changes

## Compatibility

- **Backward compatible**: Hermes built-in memory (MEMORY.md/USER.md + SQLite FTS5) continues to work alongside agentmemory
- **agentmemory supplements**: Does not replace Hermes built-in memory — adds structured episodic memory on top
- **Cross-agent**: Memories saved from Hermes are visible to Claude Code, Codex, OpenCode, and vice versa via shared agentmemory store
- **Zero cloud**: Runs fully local with local embeddings (ollama fable-5.5-coder:7b), no API key required
- **Port conflict**: agentmemory uses ports 3111 (REST), 3112 (streams), 3113 (viewer), 49134 (engine) — verify no conflicts

## Rollout

1. Start server → verify health → verify MCP tools
2. Install plugin → configure provider → restart Hermes session
3. Verify all 6 hooks fire correctly
4. Monitor for 24 hours — check viewer at localhost:3113

## Rollback

1. Remove `memory.provider` from config.yaml
2. Remove `~/.hermes/plugins/agentmemory/`
3. Stop agentmemory server
4. Hermes reverts to built-in memory only — no data loss (agentmemory store preserved at ~/.agentmemory/)
