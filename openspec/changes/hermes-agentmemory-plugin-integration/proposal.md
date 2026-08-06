# hermes-agentmemory-plugin-integration

## Why

Hermes Agent currently has two independent memory systems:
1. **Built-in memory** — flat MEMORY.md/USER.md files + SQLite FTS5 session search
2. **agentmemory** — installed globally (v0.9.28), registered in mcp-router, but server running in degraded state (iii engine not started) and no Hermes plugin installed

The result: Hermes has no episodic cross-session memory, no pre-LLM context injection, no automatic turn-level capture, and no session compaction protection. Every new session starts from scratch. The agentmemory ecosystem (95.2% retrieval accuracy, hybrid BM25+vector+graph search, cross-agent shared memory) is available but not properly wired into Hermes.

The `developer-memory` OpenSpec spec already defines agentmemory as the shared developer-memory layer. The MCP server is registered in mcp-router with auto_start=1. The missing pieces are:
1. **Fix the iii engine startup** — the server is stuck in a reconnect loop (1489+ attempts) because `iii-config.yaml` is missing from `~/.agentmemory/`
2. **Pull an LLM model** — Ollama is running but has no models for compression/summarization
3. **Install the Hermes plugin** — provides deep lifecycle integration via 6 hooks

## What Changes

### Phase 0: Fix prerequisites
- Kill stale agentmemory process (PID 93422, stuck in reconnect loop)
- Copy `iii-config.yaml` to `~/.agentmemory/iii-config.yaml` with absolute data paths
- Pull `llama3.2:3b` model via Ofable-5 (~2GB) for LLM compression
- Verify `@xenova/transformers` is installed (already present: v2.17.2)
- Verify agentmemory server starts cleanly and port 3111 opens
- Verify iii engine runs as separate process

### Phase 1: Start agentmemory server
- Start the agentmemory server on localhost:3111
- Verify health endpoint responds
- Verify iii engine is running (separate process, port 49134)
- Verify MCP tools are reachable through mcp-router (54 tools, not 7-tool shim)
- If mcp-router tools don't appear, restart MCP Router.app to pick up the running server

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
- Open viewer at http://localhost:3113 and confirm memories visible

### Phase 5: Documentation
- Update workspace-knowledge-tools skill to reflect plugin status
- Update wiki agentmemory entity page
- Commit all changes

## Embedding & LLM Strategy

### Embeddings: `all-MiniLM-L6-v2` via `@xenova/transformers` (local, free)
- **22M params, ~90MB** — negligible on M1 16GB
- **100% offline** — no API keys, no cloud dependency
- **agentmemory's recommended default** — `EMBEDDING_PROVIDER=local` (already configured)
- **Already installed** — `@xenova/transformers@2.17.2` in agentmemory's node_modules
- First-run downloads ~90MB model to `~/.cache/xenova/`

### LLM: Ofable-5 `fable-5.2:3b` (local, free)
- **~2GB RAM** — leaves 14GB for other processes on M1 16GB
- **Adequate quality** — compression tasks are short (<2K tokens in, <500 out)
- **Zero cost** — runs entirely on local hardware
- **Alternative: OpenRouter** `fable-5` at ~$0.40/month if local quality insufficient

## Compatibility

- **Backward compatible**: Hermes built-in memory (MEMORY.md/USER.md + SQLite FTS5) continues to work alongside agentmemory
- **agentmemory supplements**: Does not replace Hermes built-in memory — adds structured episodic memory on top
- **Cross-agent**: Memories saved from Hermes are visible to Claude Code, Codex, OpenCode, and vice versa via shared agentmemory store
- **Zero cloud**: Runs fully local with local embeddings (@xenova/transformers) and local LLM (Ofable-5)
- **Port usage**: 3 ports (3111 REST, 3112 streams, 3113 viewer) — no conflicts with existing services

## Rollout

1. Fix iii engine + pull LLM model → verify server health → verify MCP tools (54 tools)
2. Install plugin → configure provider → restart Hermes session
3. Verify all 6 hooks fire correctly
4. Monitor for 24 hours — check viewer at localhost:3113

## Rollback

1. Remove `memory.provider` from config.yaml
2. Remove `~/.hermes/plugins/agentmemory/`
3. Stop agentmemory server
4. Hermes reverts to built-in memory only — no data loss (agentmemory store preserved at ~/.agentmemory/)

## Archive

This is a skip_specs change with no delta specs. Archive is trivial:
run `openspec archive hermes-agentmemory-plugin-integration --store openspec-store --yes`
and commit the store. No spec merging needed.
