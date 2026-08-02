# Agentmemory Integration — Tasks

## 1. Installation & Environment Setup

- [x] 1.1 ✓ Install agentmemory globally via npm
- [x] 1.2 ✓ Verify agentmemory CLI is on PATH and version ≥ 0.9.24
- [x] 1.3 ✓ Initialize config directory with `agentmemory init`
- [x] 1.4 ✓ Verify Ollama is running on localhost:11434
- [x] 1.5 ✓ Pull nomic-embed-text model via `ollama pull nomic-embed-text`
- [x] 1.6 ✓ Verify OmniRoute credentials exist in ~/.tdt/.env

## 2. Configuration

- [x] 2.1 ✓ Create ~/.agentmemory/.env with TDT workspace tuning
- [x] 2.2 ✓ Configure LLM provider (OmniRoute gateway with DeepSeek V4 Pro)
- [x] 2.3 ✓ Configure embedding provider (Ollama nomic-embed-text 768-dim)
- [x] 2.4 ✓ Set search weights (BM25=0.4, VECTOR=0.6, GRAPH=0.2)
- [x] 2.5 ✓ Enable consolidation with 30-day decay threshold
- [x] 2.6 ✓ Enable graph extraction
- [x] 2.7 ✓ Set tool visibility to all MCP tools (53 tools in agentmemory 0.9.24)
- [x] 2.8 ✓ Verify config with `agentmemory doctor`

## 3. Server Startup & Health Check

- [x] 3.1 ✓ Start agentmemory server with `source ~/.tdt/.env && agentmemory`
- [x] 3.2 ✓ Verify health endpoint responds at http://localhost:3111/agentmemory/health
- [x] 3.3 ✓ Verify viewer accessible at http://localhost:3113
- [x] 3.4 ✓ Run demo to seed sample sessions with `agentmemory demo`
- [x] 3.5 ✓ Verify demo observations appear in viewer/API

## 4. Claude Code Integration

- [x] 4.1 ✓ Wire agentmemory into Claude Code, Codex, and pi (connect/manual extension)
- [x] 4.2 ✓ Verify MCP server connection via Claude Code config and MCP tools/list
- [x] 4.3 ✓ Verify all 53 MCP tools are available
- [x] 4.4 ✓ Test memory_smart_search tool with verification query
- [x] 4.5 ✓ Test memory_save tool to save a test observation
- [x] 4.6 ✓ Verify saved observation is searchable

## 5. Lifecycle Hooks Configuration

- [x] 5.1 ✓ Verify SessionStart hook is registered and firing
- [x] 5.2 ✓ Verify UserPromptSubmit hook is registered and firing
- [x] 5.3 ✓ Verify PreToolUse hook is registered and firing
- [x] 5.4 ✓ Verify PostToolUse hook is registered and firing
- [x] 5.5 ✓ Verify Stop hook is registered and firing
- [x] 5.6 ✓ Verify hooks execute without blocking agent operations
- [x] 5.7 ✓ Verify observations appear in viewer/API in real-time
- [x] 5.8 ✓ Verify no duplicate observation IDs (idempotency check)

## 6. Search & Recall Verification

- [x] 6.1 ✓ Run test Claude Code session
- [x] 6.2 ✓ Verify observations captured for lifecycle events
- [x] 6.3 ✓ Start new session and test memory recall/search
- [x] 6.4 ✓ Verify hybrid search returns relevant results
- [x] 6.5 ✓ Verify search latency p50 < 20ms
- [x] 6.6 ✓ Test memory_export to verify data persistence

## 7. Consolidation & Lifecycle

- [x] 7.1 ✓ Verify consolidation is enabled in config/status
- [x] 7.2 ✓ Trigger consolidation pipeline manually for immediate verification
- [x] 7.3 ✓ Check audit trail with memory_audit/agentmemory API
- [x] 7.4 ✓ Verify decay threshold is 30 days
- [x] 7.5 ✓ Verify graph extraction flag and graph query endpoint (0 nodes until richer data)

## 8. Performance & Monitoring

- [x] 8.1 ✓ Verify server startup time < 5 seconds
- [x] 8.2 ✓ Verify hook execution overhead < 100ms per observation
- [x] 8.3 ✓ Verify viewer loads < 2 seconds on 100+ observations
- [x] 8.4 ✓ Monitor disk usage and memory status
- [x] 8.5 ✓ Verify durable agentmemory/iii-engine state is present

## 9. Documentation & Verification Scripts

- [x] 9.1 ✓ Create verification script for installation
- [x] 9.2 ✓ Create verification script for OmniRoute + Ollama config
- [x] 9.3 ✓ Create verification script for MCP integration
- [x] 9.4 ✓ Create verification script for hooks
- [x] 9.5 ✓ Document startup pattern (source ~/.tdt/.env && agentmemory)
- [x] 9.6 ✓ Document rollback procedure

## 10. Optional Enhancements

- [x] 10.1 ✓ Import historical Claude Code sessions with `agentmemory import-jsonl --max-files 50`
- [x] 10.2 ✓ Verify imported sessions in viewer Replay tab/status
- [x] 10.3 ✓ Verify session replay UI exposes play/pause/speed controls
- [x] 10.4 ✓ Verify knowledge graph UI is present (data pending richer graph extraction)
- [x] 10.5 ✓ Test manual memory governance delete path
