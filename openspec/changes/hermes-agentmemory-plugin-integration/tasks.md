# Tasks: hermes-agentmemory-plugin-integration

## Phase 0: Fix prerequisites
- [ ] Kill stale agentmemory process (PID 93422, stuck in 1489+ reconnect attempts)
- [ ] Kill stale agentmemory-mcp process (PID 90932, 7-tool shim fallback mode)
- [ ] Copy iii-config.yaml to ~/.agentmemory/iii-config.yaml (use bundled config with absolute paths)
- [ ] Verify ~/.agentmemory/data/ directory exists (for state_store.db and stream_store)
- [ ] Verify Ofable-5 is running (curl http://localhost:11434/api/tags)
- [ ] Verify nomic-embed-text is pulled (should be in Ofable-5 model list)
- [ ] Pull Ofable-5 `fable-5:3b` model (~2GB) for LLM compression
- [ ] Configure .env for Ofable-5 embeddings:
  - EMBEDDING_PROVIDER=openai
  - OPENAI_EMBEDDING_MODEL=nomic-embed-text
  - OPENAI_EMBEDDING_DIMENSIONS=768
  - OPENAI_API_KEY=ollama
  - OPENAI_BASE_URL=http://localhost:11434/v1
  - OPENAI_MODEL=fable-5:3b
- [ ] Set AGENTMEMORY_DROP_STALE_INDEX=true (handle 384→768 dimension migration)
- [ ] Verify ports 3111, 3112, 3113, 49134 are free

## Phase 1: Start agentmemory server
- [ ] Start agentmemory server in background (`agentmemory` or `npx -y @agentmemory/agentmemory`)
- [ ] Wait for health endpoint (`curl http://localhost:3111/agentmemory/health`)
- [ ] Verify iii engine is running as separate process (`ps aux | grep iii`)
- [ ] Verify port 3111 is open (`lsof -i :3111`)
- [ ] Verify port 3112 is open (`lsof -i :3112`)
- [ ] Verify port 3113 is open (`lsof -i :3113`)
- [ ] Verify MCP tools reachable through mcp-router (54 tools, not 7-tool shim)
- [ ] If mcp-router tools don't appear, restart MCP Router.app to pick up the running server

## Phase 2: Install Hermes plugin
- [ ] Fetch integrations/hermes/ from agentmemory repo (curl raw GitHub files)
- [ ] Create ~/.hermes/plugins/agentmemory/ directory
- [ ] Write __init__.py (AgentMemoryProvider class, 6 hooks)
- [ ] Write plugin.yaml (name, version, hooks list)
- [ ] Write README.md (installation docs)
- [ ] Verify plugin files are in place

## Phase 3: Configure Hermes
- [ ] Add memory.provider: agentmemory to ~/.hermes/config.yaml
- [ ] Verify AGENTMEMORY_URL defaults to http://localhost:3111
- [ ] Verify ~/.agentmemory/.env exists and is readable
- [ ] Confirm no port conflicts (3111, 3112, 3113)

## Phase 4: Verify end-to-end
- [ ] `hermes memory status` shows agentmemory as available
- [ ] Save a test memory via plugin tool (`memory_save`)
- [ ] Recall the test memory (`memory_recall`)
- [ ] Verify prefetch injects context before LLM calls
- [ ] Verify sync_turn captures conversation in background
- [ ] Verify on_pre_compress preserves context during compaction
- [ ] Verify MCP tools work through mcp-router
- [ ] Open viewer at http://localhost:3113 and confirm memories visible
- [ ] Verify nomic-embed-text embeddings (768-dim vectors in vector index)

## Phase 5: Documentation & cleanup
- [ ] Update workspace-knowledge-tools skill with plugin installation status
- [ ] Update wiki agentmemory entity page with Hermes integration status
- [ ] Commit all changes to openspec-store

## Archive
- [ ] Run `openspec archive hermes-agentmemory-plugin-integration --store openspec-store --yes`
- [ ] Commit store: `cd ~/Developer/openspec-store && git add openspec/ && git commit -m "archive: hermes-agentmemory-plugin-integration"`

## Evidence Collected (2026-08-06)

### Hardware
- Mac mini M1, 16GB RAM, 8 cores, macOS 26.6

### Installed Versions
- agentmemory: 0.9.28 (latest)
- agentmemory-mcp: 0.9.28 (latest)
- iii engine: 0.11.2 (binary at ~/.agentmemory/bin/iii, arm64)
- @xenova/transformers: 2.17.2 (in agentmemory node_modules — NOT used for embeddings)
- Ofable-5: 0.32.6 (running, port 11434)

### Ofable-5 Models Pulled
- nomic-embed-text: 261MB, 137M params, 768 dims, F16 quantization
- fable-5.5:0.5b: 379MB (NOT suitable for compression — too small)

### Running Processes
- agentmemory (PID 93422): DEGRADED — port 3113 only, port 3111 closed, 1489+ reconnect attempts
- agentmemory-mcp (PID 90932): SHIM FALLBACK — 7 tools only
- Ofable-5 (PID 88072/88084): RUNNING — nomic-embed-text loaded

### Root Cause
- iii engine not starting because ~/.agentmemory/iii-config.yaml is missing
- Bundled config exists at ~/.npm-global/lib/node_modules/@agentmemory/agentmemory/iii-config.yaml
- Config references relative paths (./data/) that need to be absolute

### Embedding Model Comparison
| Model | Params | Dims | Size | Source | Status |
|-------|--------|------|------|--------|--------|
| all-MiniLM-L6-v2 | 22M | 384 | ~90MB | @xenova/transformers | NOT used |
| nomic-embed-text | 137M | 768 | 261MB | Ofable-5 | ✅ PULLed |

### .env Configuration (target state)
```
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=nomic-embed-text
OPENAI_EMBEDDING_DIMENSIONS=768
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=fable-5:3b
AGENTMEMORY_HOST=127.0.0.1
AGENTMEMORY_PORT=3111
AGENTMEMORY_VIEWER_PORT=3113
```
