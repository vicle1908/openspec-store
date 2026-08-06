# Tasks: hermes-agentmemory-plugin-integration

## Phase 1: Start agentmemory server
- [ ] Verify agentmemory v0.9.28 is installed (`agentmemory --version`)
- [ ] Start agentmemory server in background (`agentmemory &` or `npx -y @agentmemory/agentmemory`)
- [ ] Verify health endpoint (`curl http://localhost:3111/agentmemory/health`)
- [ ] Verify MCP tools reachable through mcp-router (test `memory_smart_search`)

## Phase 2: Install Hermes plugin
- [ ] Fetch `integrations/hermes/` from agentmemory repo (curl raw GitHub files)
- [ ] Create `~/.hermes/plugins/agentmemory/` directory
- [ ] Write `__init__.py` (AgentMemoryProvider class, 6 hooks)
- [ ] Write `plugin.yaml` (name, version, hooks list)
- [ ] Write `README.md` (installation docs)
- [ ] Verify plugin files are in place

## Phase 3: Configure Hermes
- [ ] Add `memory.provider: agentmemory` to `~/.hermes/config.yaml`
- [ ] Verify AGENTMEMORY_URL defaults to http://localhost:3111
- [ ] Verify `~/.agentmemory/.env` exists and is readable
- [ ] Confirm no port conflicts (3111, 3112, 3113, 49134)

## Phase 4: Verify end-to-end
- [ ] `hermes memory status` shows agentmemory as available
- [ ] Save a test memory via plugin tool (`memory_save`)
- [ ] Recall the test memory (`memory_recall`)
- [ ] Verify prefetch injects context before LLM calls
- [ ] Verify sync_turn captures conversation in background
- [ ] Verify on_pre_compress preserves context during compaction
- [ ] Verify MCP tools work through mcp-router
- [ ] Open viewer at http://localhost:3113 and confirm memories visible

## Phase 5: Documentation & cleanup
- [ ] Update workspace-knowledge-tools skill with plugin installation status
- [ ] Update wiki agentmemory entity page with Hermes integration status
- [ ] Commit all changes to openspec-store
