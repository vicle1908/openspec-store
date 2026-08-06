# REVIEW CONTEXT BUNDLE (FINAL — 2026-08-06)

## Strategy Summary

| Service | Provider | Model | Endpoint | Cost |
|---------|----------|-------|----------|------|
| **LLM** (compression) | shopapikey | fable-5 | api.phanmemvip.shop/v1 | Same as Hermes |
| **Embeddings** (vector search) | Ofable-5 | nomic-embed-text | localhost:11434/v1 | Free (local) |

## .env Target
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

## Key Evidence
- Ofable-5 nomic-embed-text: 768-dim vectors, cosine 1.00/0.47 same/cross-topic ✅
- shopapikey fable-5: confirmed available at api.phanmemvip.shop ✅
- iii engine: not running (missing iii-config.yaml) — Phase 0 fix
- Ports 3111/3112/49134: all free — no conflicts
- Hardware: Mac mini M1, 16GB RAM

## Hardware: Mac mini M1, 16GB RAM
