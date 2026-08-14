# Tasks: hermes-agentmemory-plugin-integration

## Phase 0: Fix prerequisites
- [x] Kill stale agentmemory process (PID 93422, stuck in 1489+ reconnect attempts)
- [x] Kill stale agentmemory-mcp process (PID 90932, 7-tool shim fallback mode)
- [x] Copy iii-config.yaml to ~/.agentmemory/iii-config.yaml (use bundled config with absolute paths)
- [x] Verify ~/.agentmemory/data/ directory exists (for state_store.db and stream_store)
- [x] Configure .env:
  - LLM: `OPENAI_API_KEY` (from HERMES_CUSTOM_SHOPAPIKEY_API_KEY), `OPENAI_BASE_URL=https://api.phanmemvip.shop/v1`, `OPENAI_MODEL=fable-5`
  - Embeddings: `EMBEDDING_PROVIDER=openai`, `OPENAI_EMBEDDING_API_KEY=ollama`, `OPENAI_EMBEDDING_BASE_URL=http://localhost:11434/v1`, `OPENAI_EMBEDDING_MODEL=nomic-embed-text`, `OPENAI_EMBEDDING_DIMENSIONS=768`
- [x] Set AGENTMEMORY_DROP_STALE_INDEX=true (handle 384→768 dimension migration)
- [x] Verify Ofable-5 is running and nomic-embed-text is loaded
- [x] Verify ports 3111, 3112, 3113, 49134 are free

## Phase 1: Start agentmemory server
- [x] Start agentmemory server in background (`agentmemory` or `npx -y @agentmemory/agentmemory`)
- [x] Wait for health endpoint (`curl http://localhost:3111/agentmemory/health`)
- [x] Verify iii engine is running as separate process (`ps aux | grep iii`)
- [x] Verify port 3111 is open (`lsof -i :3111`)
- [x] Verify port 3112 is open (`lsof -i :3112`)
- [x] Verify port 3113 is open (`lsof -i :3113`)
- [x] Verify MCP tools reachable through mcp-router (54 tools, not 7-tool shim)
- [x] If mcp-router tools don't appear, restart MCP Router.app to pick up the running server

## Phase 2: Install Hermes plugin
- [x] Fetch integrations/hermes/ from agentmemory repo (curl raw GitHub files)
- [x] Create ~/.hermes/plugins/agentmemory/ directory
- [x] Write __init__.py (AgentMemoryProvider class, 6 hooks)
- [x] Write plugin.yaml (name, version, hooks list)
- [x] Write README.md (installation docs)
- [x] Verify plugin files are in place

## Phase 3: Configure Hermes
- [x] Add memory.provider: agentmemory to ~/.hermes/config.yaml
- [x] Verify AGENTMEMORY_URL defaults to http://localhost:3111
- [x] Verify ~/.agentmemory/.env exists and is readable
- [x] Confirm no port conflicts (3111, 3112, 3113)

## Phase 4: Verify end-to-end
- [x] `hermes memory status` shows agentmemory as available
- [x] Save a test memory via plugin tool (`memory_save`)
- [x] Recall the test memory (`memory_recall`)
- [x] Verify prefetch injects context before LLM calls
- [x] Verify sync_turn captures conversation in background
- [x] Verify on_pre_compress preserves context during compaction
- [x] Verify MCP tools work through mcp-router
- [x] Open viewer at http://localhost:3113 and confirm memories visible
- [x] Verify nomic-embed-text embeddings (768-dim vectors in vector index)

## Phase 5: Documentation & cleanup
- [x] Update workspace-knowledge-tools skill with plugin installation status
- [x] Update wiki agentmemory entity page with Hermes integration status
- [x] Commit all changes to openspec-store

## Archive
- [x] [historical] Run `openspec archive hermes-agentmemory-plugin-integration --store openspec-store --yes`
- [x] [historical] Commit store: `cd ~/Developer/openspec-store && git add openspec/ && git commit -m "archive: hermes-agentmemory-plugin-integration"`

## Evidence Collected (2026-08-06)

### Hardware
- Mac mini M1, 16GB RAM, 8 cores, macOS 26.6

### Installed Versions
- agentmemory: 0.9.28 (latest)
- agentmemory-mcp: 0.9.28 (latest)
- iii engine: 0.11.2 (binary at ~/.agentmemory/bin/iii, arm64)
- Ofable-5: 0.32.6 (running, port 11434)

### Ofable-5 Models Pulled
- nomic-embed-text: 261MB, 137M params, 768 dims, F16 quantization ✅

### Running Processes
- agentmemory (PID 21846): HEALTHY — all ports open
- iii engine (PID 21935): RUNNING — port 3111 listening
- Ofable-5 (PID 88072/88084): RUNNING — nomic-embed-text loaded

### Root Cause
- iii engine not starting because ~/.agentmemory/iii-config.yaml is missing
- Fixed: iii-config.yaml copied to ~/.agentmemory/ with absolute paths

### .env Target Configuration
```
# LLM — same model as Hermes
OPENAI_API_KEY=<from HERMES_CUSTOM_SHOPAPIKEY_API_KEY>
OPENAI_BASE_URL=https://api.phanmemvip.shop/v1
OPENAI_MODEL=fable-5

# Embeddings — Ofable-5 local
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_API_KEY=ollama
OPENAI_EMBEDDING_BASE_URL=http://localhost:11434/v1
OPENAI_EMBEDDING_MODEL=nomic-embed-text
OPENAI_EMBEDDING_DIMENSIONS=768

# Server
AGENTMEMORY_HOST=127.0.0.1
AGENTMEMORY_PORT=3111
AGENTMEMORY_VIEWER_PORT=3113
```


---

> **Historical record:** This change was archived with 2 incomplete task(s) (38/40 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
