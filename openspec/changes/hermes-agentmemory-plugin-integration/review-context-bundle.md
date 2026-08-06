## EVIDENCE BUNDLE: hermes-agentmemory-plugin-integration (REVISED 2026-08-06)

### 1. agentmemory install status
- Version: 0.9.28 (latest)
- Path: /Users/androidteam/.npm-global/bin/agentmemory
- .env: /Users/androidteam/.agentmemory/.env (exists, readable)

### 2. agentmemory .env (current)
```
# B+ Feature Flags
AGENTMEMORY_TOOLS=all
GRAPH_EXTRACTION_ENABLED=true
SNAPSHOT_ENABLED=true
CONSOLIDATION_ENABLED=true
AGENTMEMORY_SLOTS=memory
AGENTMEMORY_REFLECT=true
AGENTMEMORY_INJECT_CONTEXT=true
LESSON_DECAY_ENABLED=true
AGENTMEMORY_AGENT_SCOPE=shared

# Embeddings — LOCAL (all-MiniLM-L6-v2 via @xenova/transformers)
EMBEDDING_PROVIDER=local

# LLM Provider — Ofable-5 (NO MODEL PULLED)
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=fable-5.5-coder:7b  ← NEEDS CHANGE to fable-5:3b

# Server binding
AGENTMEMORY_HOST=127.0.0.1
AGENTMEMORY_PORT=3111
AGENTMEMORY_VIEWER_PORT=3113
```

### 3. Running processes
- **agentmemory** (PID 93422): node /Users/androidteam/.npm-global/bin/agentmemory
  - CWD: /Users/androidteam/Developer/go-microservices
  - Port 3113: LISTENING (viewer)
  - Port 3111: NOT LISTENING (REST API — iii engine failed)
  - Logs: 1489+ reconnect attempts to iii engine
  - LOG: ~/.agentmemory/log/agentmemory.log (335KB)
- **agentmemory-mcp** (PID 90932): npm exec @agentmemory/mcp
  - Running via mcp-router
  - 7-tool shim fallback mode (server unreachable)
- **Ofable-5** (PID 88072/88084): /Applications/Ollama.app
  - Port 11434: LISTENING
  - Models: NONE PULLED (empty model list)

### 4. Port status (verified 2026-08-06)
| Port | Status | Owner |
|------|--------|-------|
| 3111 | FREE | — |
| 3112 | FREE | — |
| 3113 | OCCUPIED | agentmemory viewer (PID 93422) |
| 49134 | FREE | — |
| 11434 | OCCUPIED | Ofable-5 (PID 88084) |

### 5. iii engine
- Binary: ~/.agentmemory/bin/iii (arm64, v0.11.2, 28MB)
- Status: NOT RUNNING as separate process
- Root cause: ~/.agentmemory/iii-config.yaml MISSING
- Bundled config: ~/.npm-global/lib/node_modules/@agentmemory/agentmemory/iii-config.yaml
- Data directory: ~/.agentmemory/data/ (exists, empty)
- iii.pid: NOT PRESENT (no engine was ever started)

### 6. Dependencies status
| Dependency | Version | Status |
|-----------|---------|--------|
| Node.js | >= 20 | ✅ Installed |
| agentmemory | 0.9.28 | ✅ Installed (latest) |
| agentmemory-mcp | 0.9.28 | ✅ Installed (latest) |
| iii engine | 0.11.2 | ✅ Binary present |
| @xenova/transformers | 2.17.2 | ✅ Installed (for local embeddings) |
| Ofable-5 | 0.32.6 | ✅ Running (no models pulled) |
| Hermes plugin | — | ❌ Not installed |
| iii-config.yaml | — | ❌ Missing from ~/.agentmemory/ |
| Ofable-53.2:3b | — | ❌ Not pulled (~2GB) |

### 7. mcp-router registration
```
agentmemory|npx|["-y","@agentmemory/mcp"]|1|0
```
auto_start=1, registered correctly.

### 8. Hermes memory config
```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 3000
  user_char_limit: 2000
  nudge_interval: 10
  flush_min_turns: 6
```
No `memory.provider` set — using built-in memory only.

### 9. Plugin directory
~/.hermes/plugins/agentmemory/ — DOES NOT EXIST

### 10. Hardware
- Mac mini M1 (Macmini9,1)
- 16GB RAM, 8 cores (4P + 4E)
- macOS 26.6
- Apple Silicon arm64

### 11. Existing developer-memory spec
- Status: IMPLEMENTED (for Cursor, Claude Code, Codex, OpenCode, pi)
- Hermes integration: NOT IMPLEMENTED (this change)
- Ports: 3111, 3112, 3113 — no conflicts
- Single server constraint: only ONE agentmemory server should run

### 12. Upstream plugin.yaml version
```yaml
name: agentmemory
version: 0.8.0
description: "Persistent cross-session memory for Hermes Agent via agentmemory."
author: "Rohit Ghumare"
hooks:
  - prefetch
  - sync_turn
  - on_session_end
  - on_pre_compress
  - on_memory_write
  - system_prompt_block
```

### 13. Embedding model analysis
- **Recommended**: all-MiniLM-L6-v2 via @xenova/transformers (local, free)
- 22M params, ~90MB, offline, agentmemory's default
- Already installed (@xenova/transformers@2.17.2)
- First-run download: ~90MB to ~/.cache/xenova/
- **Rejected**: nomic-embed-text (550MB, requires Ollama), OpenAI/Gemini (API keys needed)

### 14. LLM model analysis
- **Recommended**: fable-53.2:3b via Ofable-5 (~2GB RAM)
- Adequate for compression tasks (<2K tokens in, <500 out)
- Zero cost, ~22 tok/s on M1
- **Rejected**: fable-5:7b (~4.7GB, overkill for compression), API providers (cost/dependency)
