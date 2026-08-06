## EVIDENCE BUNDLE: hermes-agentmemory-plugin-integration (REVISED 2026-08-06)

### 1. agentmemory install status
- Version: 0.9.28 (latest)
- Path: /Users/androidteam/.npm-global/bin/agentmemory
- .env: /Users/androidteam/.agentmemory/.env (exists, needs rewrite)

### 2. .env Target Configuration
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

### 3. Ofable-5 status
- Version: 0.32.6 (running, port 11434)
- nomic-embed-text: 261MB, 137M params, 768 dims, F16 ✅
- Embedding API tested: /v1/embeddings returns 768-dim vectors ✅
- Semantic discrimination: cosine 1.00 same-topic, ~0.47 cross-topic ✅

### 4. shopapikey status
- Endpoint: https://api.phanmemvip.shop/v1 ✅
- Model: fable-5 confirmed available ✅
- Key env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY (available in shell) ✅

### 5. Running processes
- agentmemory (PID 93422): DEGRADED — port 3113 only, 1489+ reconnect attempts
- agentmemory-mcp (PID 90932): SHIM FALLBACK — 7 tools only
- Ofable-5 (PID 88072/88084): RUNNING — nomic-embed-text loaded

### 6. Port status
| Port | Status | Owner |
|------|--------|-------|
| 3111 | FREE | — |
| 3112 | FREE | — |
| 3113 | OCCUPIED | agentmemory viewer |
| 49134 | FREE | — |
| 11434 | OCCUPIED | Ofable-5 |

### 7. iii engine
- Binary: ~/.agentmemory/bin/iii (arm64, v0.11.2)
- Status: NOT RUNNING
- Root cause: ~/.agentmemory/iii-config.yaml MISSING

### 8. agentmemory embedding provider detection
```javascript
// EMBEDDING_PROVIDER=openai → OpenAIEmbeddingProvider
// OPENAI_EMBEDDING_BASE_URL → Ofable-5 /v1/embeddings
// OPENAI_EMBEDDING_API_KEY → "ollama" (dummy, Ofable-5 ignores auth)
// OPENAI_EMBEDDING_MODEL → nomic-embed-text
// OPENAI_EMBEDDING_DIMENSIONS → 768 (required, not in built-in table)
```

### 9. Hermes model config
- Primary: fable-5 via shopapikey (https://api.phanmemvip.shop/v1)
- Delegation: fable-5 via shopapikey
- Compression: fable-5 via shopapikey
- All use the same model — agentmemory LLM joins this pattern

### 10. Hardware
- Mac mini M1, 16GB RAM, 8 cores, macOS 26.6
