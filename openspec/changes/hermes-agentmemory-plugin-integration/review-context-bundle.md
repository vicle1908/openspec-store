## EVIDENCE BUNDLE: hermes-agentmemory-plugin-integration (REVISED 2026-08-06)

### 1. agentmemory install status
- Version: 0.9.28 (latest)
- Path: /Users/androidteam/.npm-global/bin/agentmemory
- .env: /Users/androidteam/.agentmemory/.env (exists, readable)

### 2. agentmemory .env (current → target)
```
# CURRENT (needs update):
EMBEDDING_PROVIDER=local                    → EMBEDDING_PROVIDER=openai
# no embedding model override               → OPENAI_EMBEDDING_MODEL=nomic-embed-text
# no dimension override                     → OPENAI_EMBEDDING_DIMENSIONS=768
OPENAI_MODEL=fable-5.5-coder:7b            → OPENAI_MODEL=fable-5:3b

# UNCHANGED:
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
AGENTMEMORY_HOST=127.0.0.1
AGENTMEMORY_PORT=3111
AGENTMEMORY_VIEWER_PORT=3113
```

### 3. Ofable-5 status
- Version: 0.32.6 (running, port 11434)
- Models pulled:
  - nomic-embed-text: 261MB, 137M params, 768 dims, F16 quantization ✅
  - fable-5.5:0.5b: 379MB (too small for compression)
- Embedding API tested: `POST /v1/embeddings` returns 768-dim vectors ✅
- Auth header: Ofable-5 accepts `Authorization: Bearer ollama` gracefully ✅
- Semantic discrimination: cosine 1.00 same-topic, ~0.47 cross-topic ✅

### 4. Running processes
- **agentmemory** (PID 93422): DEGRADED — port 3113 only, port 3111 closed
- **agentmemory-mcp** (PID 90932): SHIM FALLBACK — 7 tools only
- **Ofable-5** (PID 88072/88084): RUNNING — nomic-embed-text loaded

### 5. Port status (verified 2026-08-06)
| Port | Status | Owner |
|------|--------|-------|
| 3111 | FREE | — |
| 3112 | FREE | — |
| 3113 | OCCUPIED | agentmemory viewer (PID 93422) |
| 49134 | FREE | — |
| 11434 | OCCUPIED | Ofable-5 (PID 88084) |

### 6. iii engine
- Binary: ~/.agentmemory/bin/iii (arm64, v0.11.2, 28MB)
- Status: NOT RUNNING as separate process
- Root cause: ~/.agentmemory/iii-config.yaml MISSING
- Bundled config: ~/.npm-global/lib/node_modules/@agentmemory/agentmemory/iii-config.yaml
- Data directory: ~/.agentmemory/data/ (exists, empty)

### 7. Embedding model comparison
| Model | Params | Dims | Size | Source | Speed | Status |
|-------|--------|------|------|--------|-------|--------|
| all-MiniLM-L6-v2 | 22M | 384 | ~90MB | @xenova/transformers | CPU | NOT used |
| nomic-embed-text | 137M | 768 | 261MB | Ofable-5 | GPU (M1) | ✅ PULLed |

**nomic-embed-text advantages:**
- 3.4x more parameters (137M vs 22M)
- 2x embedding dimensions (768 vs 384)
- GPU-accelerated via M1 Neural Engine
- Already pulled, no first-run download
- Single dependency (Ofable-5 handles LLM + embeddings)

### 8. agentmemory embedding provider detection
```javascript
// detectEmbeddingProvider() checks in order:
1. EMBEDDING_PROVIDER env var (explicit override) — SET TO "openai"
2. GEMINI_API_KEY → "gemini"
3. OPENAI_API_KEY → "openai"  — would also trigger if EMBEDDING_PROVIDER not set
4. VOYAGE_API_KEY → "voyage"
5. fable-5_API_KEY → "fable-5"
6. OPENROUTER_API_KEY → "openrouter"
7. null → falls back to "local" (@xenova/transformers)
```

**With EMBEDDING_PROVIDER=openai:**
- Uses `OPENAI_EMBEDDING_BASE_URL || OPENAI_BASE_URL` → http://localhost:11434/v1
- Uses `OPENAI_EMBEDDING_MODEL` || "text-embedding-3-small" → nomic-embed-text
- Uses `OPENAI_EMBEDDING_DIMENSIONS` → 768 (required, not in built-in table)
- Uses `OPENAI_EMBEDDING_API_KEY || OPENAI_API_KEY` → "ollama"

### 9. Dependencies status
| Dependency | Version | Status |
|-----------|---------|--------|
| Node.js | >= 20 | ✅ Installed |
| agentmemory | 0.9.28 | ✅ Installed (latest) |
| agentmemory-mcp | 0.9.28 | ✅ Installed (latest) |
| iii engine | 0.11.2 | ✅ Binary present |
| @xenova/transformers | 2.17.2 | ✅ Installed (NOT used for embeddings) |
| Ofable-5 | 0.32.6 | ✅ Running |
| nomic-embed-text | latest | ✅ PULLed (261MB) |
| Hermes plugin | — | ❌ Not installed |
| iii-config.yaml | — | ❌ Missing from ~/.agentmemory/ |
| fable-5:3b | — | ❌ Not pulled (~2GB) |

### 10. Hardware
- Mac mini M1 (Macmini9,1)
- 16GB RAM, 8 cores (4P + 4E)
- macOS 26.6
- Apple Silicon arm64

### 11. Hermes config
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

### 12. Plugin directory
~/.hermes/plugins/agentmemory/ — DOES NOT EXIST
