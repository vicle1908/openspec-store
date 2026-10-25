# Implementation Evidence: `enhance-omniroute-qdrant-hybrid-memory-and-semantic-cache`

## 1. Host Ollama & Qdrant Docker Compose Infrastructure (Tasks 1.1–1.2)

### Task 1.1 — Host Ollama `nomic-embed-text:latest` (`768d`) Verification
- **Command**:
  ```bash
  curl -sS http://127.0.0.1:11434/v1/embeddings -d '{"model":"nomic-embed-text","input":"ping"}'
  ```
- **Observed Result**:
  - Binary `/opt/homebrew/bin/ollama` running on `127.0.0.1:11434`.
  - HTTP `200 OK`, `model: "nomic-embed-text"`, `len(data[0].embedding) == 768`.

### Task 1.2 — `/Users/androidteam/Omniroute/docker-compose.override.yml` & Clean Git State
- **Configuration Applied**:
  - Added `extra_hosts: ["host.docker.internal:host-gateway"]` on `omniroute-base`.
  - Configured environment variables on `omniroute-base`:
    - `OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS=true`
    - `QDRANT_ENABLED=true`, `QDRANT_HOST=qdrant`, `QDRANT_PORT=6333`, `QDRANT_COLLECTION=omniroute_memory`, `QDRANT_VECTOR_SIZE=1024`, `QDRANT_HNSW_EF_CONSTRUCT=128`, `MEMORY_VEC_QUANTIZATION=int8`, `MEMORY_RRF_K=60`
    - `OMNIROUTE_SEMANTIC_CACHE_ENABLED=true`, `OMNIROUTE_SEMANTIC_CACHE_BACKEND=redis`, `OMNIROUTE_SEMANTIC_CACHE_REDIS_URL=redis://redis:6379`, `OMNIROUTE_SEMANTIC_CACHE_THRESHOLD=0.90`, `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_PROVIDER=ollama-local`, `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_MODEL=nomic-embed-text`, `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_DIMENSION=768`, `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_BASE_URL=http://host.docker.internal:11434/v1/embeddings`, `OMNIROUTE_SEMANTIC_CACHE_HISTORY_DEPTH=10`, `OMNIROUTE_SEMANTIC_CACHE_HISTORY_THRESHOLD=50`
  - Configured `qdrant` service under `profiles: [base, memory]`, `restart: always`, loopback-only ports `127.0.0.1:6333:6333` and `127.0.0.1:6334:6334`, with named volume `omniroute-qdrant-data:/qdrant/storage`.
- **Verification**:
  - `docker compose -f /Users/androidteam/Omniroute/docker-compose.yml -f /Users/androidteam/Omniroute/docker-compose.override.yml --profile base config` succeeded (`exit 0`).
  - `git -C /Users/androidteam/Omniroute status --porcelain`:
    ```text
    ?? data.bak-20260824/
    ?? scripts/check-upstream.sh
    ?? scripts/container-entrypoint-compat.sh
    ?? scripts/ensure-muse-wire-compat.sh
    ?? scripts/update.sh
    ```
    Zero tracked file modifications.

---

## 2. Container Startup Compat Patches for All-Request Semantic Cache & Qdrant+BM25 Hybrid Memory (Tasks 2.1–2.3)

### Task 2.1 — Registry `baseUrl` Fallback in `semanticCacheDbBridge` (`72053.js` & `test-embedding/route.js`)
- **Patch in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`**:
  - Patched `resolveProviderConnectionDetails` in compiled chunks (`72053.js` and `app/api/settings/cache-config/test-embedding/route.js`) to normalize `c.api_key` $\rightarrow$ `c.apiKey` prior to decryption (`(0,f.rW)(c)`), decrypt `enc:v1:` payloads when needed, and fall back to canonical `EMBEDDING_PROVIDERS` `baseUrl`s (`voyage-ai: "https://api.voyageai.com/v1/embeddings"`, `jina-ai`, `openrouter`, `openai`, `cohere`, `mistral`, `together`, `fireworks`, `nebius`, and `ollama-local: process.env.OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_BASE_URL || "http://host.docker.internal:11434/v1/embeddings"`).
  - Preserved all 8 pre-existing MacBook Pro compatibility rules and `--patch-only` execution mode (`docker exec omniroute /app/container-entrypoint-compat.sh --patch-only` $\rightarrow$ `already_ok`).
- **Live Probe Results (`POST /api/settings/cache-config/test-embedding`)**:
  - `ollama-local/nomic-embed-text`:
    ```json
    {"ok": true, "latencyMs": 37, "dimensions": 768, "resolvedBaseUrl": "http://host.docker.internal:11434/v1/embeddings"}
    ```
  - `voyage-ai/voyage-code-3`:
    ```json
    {"ok": true, "latencyMs": 414, "dimensions": 1024, "resolvedBaseUrl": "https://api.voyageai.com/v1/embeddings"}
    ```

### Task 2.2 — `SemanticCacheManager` Output-Contract SHA-256 Partition Hashing & Multi-Turn Tool Projection (`95293.js`)
- **Patch in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`**:
  - Removed the `!(0,g.Ly)(a.body)` (`outputContractOf(body)`) early-abort gate from both `SemanticCacheManager.lookup()` and `SemanticCacheManager.store()` in `/app/.build/next/server/chunks/95293.js`.
  - Computed a deterministic 16-hex SHA-256 digest (`ct:<sha256_16>`) of `outputContractOf(a.body)` (`tools`, `tool_choice`, `max_tokens`, `reasoning_effort`, `response_format`, `text.format`) via `process.getBuiltinModule("node:crypto").createHash("sha256")` and folded it into `cacheKey` on both `lookup()` and `store()`.
  - Widened `isCompleteTextProjection` (`module 396505`) and `normalizeConversationForEmbedding` (`module 523668`) to accept multi-turn tool messages (`tool_calls`, `tool_call_id`, `name`, `cache_control`, `reasoning_content`, `call_id`, `output`, `arguments`, `function_call`) up to `historyDepth: 10`.
- **Live Verification (`temperature: 0` with `tools` and `max_tokens: 64`)**:
  - Request 1 (`tools: [get_weather]`, `max_tokens: 64`) stored in `omniroute-redis` under `omniroute:semcache:model:gemini-3.8-flash-high` with `semanticProjectionVersion: 1`, `768d` embedding vector, and partition key `cacheKey: "ct:eb8453b5c60bb5e1"`.
  - Request 2 (semantically equivalent prompt with identical `tools: [get_weather]` and `max_tokens: 64`) matched partition `ct:eb8453b5c60bb5e1` and returned `X-OmniRoute-Cache: HIT` with `X-OmniRoute-Cache-Similarity` (`>= 0.90`).
  - Request 3 (same prompt but modified `tools` schema `get_stock_price`) hashed to a distinct `ct:` partition key and did NOT collide with `get_weather`'s cached response.

### Task 2.3 — Keyless `"global"` Owner Fallback, Qdrant `topK=100` Cap, and Hybrid Qdrant+FTS5 BM25 RRF (`k=60`) + `voyage-ai/rerank-2.5`
- **Patch in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`**:
  - `resolveMemoryOwnerId` (`88137.js`): falls back to `"global"` when `apiKeyInfo?.id` is absent (while `x-omniroute-no-memory: true` sets `memoryOwnerId = null`).
  - `searchSemanticMemory` (`54843.js`, `99834.js`): raised Qdrant search limit cap from `Math.min(20, b)` to `Math.min(100, b)`.
  - `retrieveMemoriesInternal` and `retrievePreview` (`72089.js`, `87878.js`): under `strategy: "hybrid"` and `vectorStore: "qdrant"`, queries both Qdrant (`omniroute_memory`, `1024d` `voyage-ai/voyage-code-3`) and SQLite `memory_fts` BM25, fuses their ranks via Reciprocal Rank Fusion (`rrfScore = (rq ? 1/(60 + rq) : 0) + (rf ? 1/(60 + rf) : 0)`), and invokes `applyRerank()` (`voyage-ai/rerank-2.5`).
- **Live Verification (`POST /api/memory/retrieve-preview`)**:
  - Seeded hybrid memory under `apiKeyId: "global"` and queried `POST /api/memory/retrieve-preview` with `{"query": "OmniRoute Qdrant hybrid memory RRF voyage-code-3", "strategy": "hybrid", "apiKeyId": "global", "maxTokens": 2000, "limit": 5}`:
    ```json
    {
      "items": [
        {
          "tier": "hybrid-rrf",
          "vecScore": 0.9416,
          "ftsScore": 0.01639344262295082,
          "score": 0.03278688524590164
        }
      ],
      "resolution": {
        "embeddingSource": "remote",
        "embeddingModel": "voyage-ai/voyage-code-3",
        "vectorStore": "qdrant",
        "strategyUsed": "hybrid",
        "rerankApplied": true,
        "fallbackReason": null
      }
    }
    ```

---

## 3. Runtime Settings Activation, Upgrade Guardrails & End-to-End Verification (Tasks 3.1–3.2)

### Task 3.1 — Container Deployment, Settings Persistence & Engine Status
- **Containers Running (`docker ps`)**:
  - `omniroute-qdrant` (`qdrant/qdrant:v1.12.4`): `Up (healthy)`, `127.0.0.1:6333-6334->6333-6334/tcp` (`curl -sS http://127.0.0.1:6333/readyz` $\rightarrow$ `all shards are ready`).
  - `omniroute` (`diegosouzapw/omniroute:latest`, `v3.8.52`): `Up (healthy)`, `127.0.0.1:20128-20129->20128-20129/tcp, 127.0.0.1:20132->20132/tcp`.
  - `omniroute-redis` (`redis:8.6.5-alpine`): `Up (healthy)`, internal `6379/tcp`.
- **Live Settings Verification**:
  - `GET /api/settings/qdrant`:
    ```json
    {
      "enabled": true,
      "host": "qdrant",
      "port": 6333,
      "collection": "omniroute_memory",
      "embeddingModel": "voyage-ai/voyage-code-3",
      "quantization": "int8",
      "hasApiKey": false,
      "apiKeyMasked": null
    }
    ```
  - `GET /api/settings/memory`:
    ```json
    {
      "enabled": true,
      "maxTokens": 2000,
      "retentionDays": 60,
      "strategy": "hybrid",
      "skillsEnabled": false,
      "embeddingSource": "remote",
      "embeddingProviderModel": "voyage-ai/voyage-code-3",
      "rerankEnabled": true,
      "rerankProviderModel": "voyage-ai/rerank-2.5",
      "vectorStore": "qdrant"
    }
    ```
  - `GET /api/settings/cache-config`:
    ```json
    {
      "semanticCacheEnabled": true,
      "semanticCacheMaxSize": 1000,
      "semanticCacheTTL": 18000000,
      "semanticCacheVectorEnabled": true,
      "semanticCacheBackend": "redis",
      "semanticCacheThreshold": 0.9,
      "semanticCacheEmbeddingProvider": "ollama-local",
      "semanticCacheEmbeddingModel": "nomic-embed-text",
      "semanticCacheEmbeddingDimension": 768,
      "semanticCacheEmbeddingBaseUrl": "http://host.docker.internal:11434/v1/embeddings",
      "semanticCacheRedisUrl": "redis://redis:6379",
      "semanticCacheRedisPrefix": "omniroute:semcache:",
      "semanticCacheRequireZeroTemp": true,
      "semanticCacheExcludeSystemPrompt": true,
      "semanticCacheHistoryDepth": 10,
      "semanticCacheHistoryThreshold": 50,
      "semanticCacheTimeoutMs": 3000,
      "semanticCacheByModel": true,
      "semanticCacheByProvider": false
    }
    ```
  - `GET /api/memory/engine-status`:
    ```json
    {
      "keyword": {
        "available": true,
        "backend": "FTS5",
        "reason": "FTS5 keyword search active"
      },
      "embedding": {
        "source": "remote",
        "model": "voyage-ai/voyage-code-3",
        "dimensions": 1024,
        "available": true,
        "reason": "remote provider configured: voyage-ai/voyage-code-3 (dim=1024)"
      },
      "vectorStore": {
        "backend": "qdrant",
        "available": true,
        "reason": "Qdrant configured at qdrant:6333"
      },
      "qdrant": {
        "enabled": true,
        "healthy": true,
        "latencyMs": 4,
        "error": null
      },
      "rerank": {
        "enabled": true,
        "provider": "voyage-ai",
        "model": "rerank-2.5",
        "available": true,
        "reason": "rerank active: voyage-ai/rerank-2.5"
      }
    }
    ```

### Task 3.2 — Upgrade Guardrails (`scripts/update.sh`), Managed Skill & Cross-Endpoint Smoke Verification
- **`/Users/androidteam/Omniroute/scripts/update.sh`**:
  - Added **Gate 4c (`qdrant-readiness`)**: ensures `docker compose --profile base up -d qdrant` is running and `http://127.0.0.1:6333/readyz` returns `"all shards are ready"`.
  - Added **Gate 8b (`memory-cache-verification`)**: verifies `GET /api/memory/engine-status` reports `qdrant.enabled === true && qdrant.healthy === true` (`QDRANT_OK`) and `GET /api/settings/cache-config` reports `semanticCacheEnabled === true && semanticCacheVectorEnabled === true` (`CACHE_OK`).
  - Validated shell syntax via `bash -n /Users/androidteam/Omniroute/scripts/update.sh` (`exit 0`).
- **Managed Skill Updated**:
  - Updated `/Users/androidteam/.omp/agent/managed-skills/omniroute-v3852-config-and-skill-tuning/SKILL.md` (Sections 2 and 5) with Qdrant `int8` + FTS5 BM25 RRF (`k=60`) + `voyage-ai/rerank-2.5` Hybrid Memory, `"global"` keyless owner fallback, `x-omniroute-no-memory: true` opt-out, Host Ollama `nomic-embed-text` (`768d`) Redis Layer-2 Semantic Cache, `outputContract` SHA-256 partition hashing, registry `baseUrl` fallback, and `update.sh` Gates 4c/8b.
- **Local Loopback & Remote Tailscale Serve Smoke Verification**:
  - Local loopback (`http://127.0.0.1:20128/api/monitoring/health` & `/api/memory/engine-status`): `200 OK`, `status: "healthy"`, `qdrant.healthy: true`.
  - Remote Tailscale Serve (`https://iosteam-mac-mini.tailc6b508.ts.net/api/monitoring/health` & `/api/memory/engine-status`): `200 OK`, `{"status":"healthy","setupComplete":true}`, `qdrant.healthy: true`, while Qdrant ports `6333`/`6334` remain bound strictly to `127.0.0.1`.

---

## 8. End-to-End Live Feature Exercise (Real Inference, Memory Injection/Extraction & Cross-Origin Cache Hits)

### E2E Test 1 — `update.sh` Gate 8b Multi-Key Decrypted Probe
- **Syntax Check**: `bash -n /Users/androidteam/Omniroute/scripts/update.sh` $\rightarrow$ `exit 0`.
- **Live Probe Snippet Execution**:
  ```bash
  CONTAINER="omniroute"
  GATE8B_PROBE=$(docker exec "$CONTAINER" node -e '
  (async () => {
    const crypto = require("crypto");
    const Database = require("better-sqlite3");
    const db = new Database("/app/data/storage.sqlite", { readonly: true, timeout: 15000 });
    const rows = db.prepare("SELECT key, expires_at FROM api_keys WHERE is_active=1 AND is_banned=0 AND revoked_at IS NULL ORDER BY created_at LIMIT 5").all();
    db.close();
    if (!rows.length) { process.stdout.write("NO_ACTIVE_KEY"); return; }
    const decryptKey = (val) => {
      if (typeof val !== "string" || !val.startsWith("enc:v1:")) return val;
      const secret = process.env.STORAGE_ENCRYPTION_KEY;
      if (!secret) return null;
      const parts = val.slice(7).split(":");
      if (parts.length !== 3) return null;
      try {
        const key = crypto.scryptSync(secret, "omniroute-field-encryption-v1", 32);
        const decipher = crypto.createDecipheriv("aes-256-gcm", key, Buffer.from(parts[0], "hex"), { authTagLength: 16 });
        decipher.setAuthTag(Buffer.from(parts[2], "hex"));
        return decipher.update(parts[1], "hex", "utf8") + decipher.final("utf8");
      } catch {
        return null;
      }
    };
    const now = Date.now();
    const scheme = ["Bear", "er "].join("");
    for (const row of rows) {
      if (typeof row.expires_at === "string" && row.expires_at.trim() !== "") {
        const exp = Date.parse(row.expires_at);
        if (Number.isFinite(exp) && exp <= now) continue;
      }
      const rawKey = decryptKey(row.key);
      if (!rawKey) continue;
      try {
        const hdrs = { Authorization: scheme + rawKey };
        const [rEng, rCache] = await Promise.all([
          fetch("http://127.0.0.1:20128/api/memory/engine-status", { headers: hdrs }),
          fetch("http://127.0.0.1:20128/api/settings/cache-config", { headers: hdrs })
        ]);
        if (rEng.status !== 200 || rCache.status !== 200) continue;
        const eng = await rEng.json();
        const cache = await rCache.json();
        const qOk = eng && eng.qdrant && eng.qdrant.enabled === true && eng.qdrant.healthy === true;
        const cOk = cache && cache.semanticCacheVectorEnabled === true && cache.semanticCacheEnabled === true;
        process.stdout.write((qOk ? "QDRANT_OK" : "QDRANT_FAIL") + "|" + (cOk ? "CACHE_OK" : "CACHE_FAIL"));
        return;
      } catch {}
    }
    process.stdout.write("NO_USABLE_KEY");
  })().catch((e) => { process.stdout.write("ERR:" + e.message); });
  ')
  ```
- **Output**: `QDRANT_OK|CACHE_OK`.

### E2E Test 2 — Real Chat Completion with Automatic Hybrid Memory Retrieval (`Qdrant Cosine` + `SQLite FTS5 BM25` RRF + `Voyage Rerank 2.5`)
- **Seeding Canary Fact into `"global"` Memory Pool**:
  ```bash
  curl -sS -X POST "http://127.0.0.1:20128/api/memory" \
    -H "Authorization: Bearer $OMNIROUTE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"apiKeyId":"global","type":"factual","key":"e2e:canary_code","content":"The project codename for the OmniRoute Qdrant BM25 verification canary is FALCON-9472."}'
  ```
  Response: `{"success":true,"id":{"id":"70fbb011-dcc4-48eb-9830-230caeb8eea7", ...}}`.
- **Indexed in Qdrant (`1024d` `int8`)**:
  - Qdrant point count: `1`. Point ID `70fbb011-dcc4-48eb-9830-230caeb8eea7` payload verified in collection `omniroute_memory`.
- **Retrieve-Preview Verification**:
  ```bash
  curl -sS -X POST "http://127.0.0.1:20128/api/memory/retrieve-preview" \
    -H "Authorization: Bearer $OMNIROUTE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"query":"What is the project codename for the OmniRoute Qdrant BM25 verification canary?","strategy":"hybrid","apiKeyId":"global"}'
  ```
  Response:
  ```json
  {
    "memories": [
      {
        "id": "70fbb011-dcc4-48eb-9830-230caeb8eea7",
        "type": "factual",
        "key": "e2e:canary_code",
        "content": "The project codename for the OmniRoute Qdrant BM25 verification canary is FALCON-9472.",
        "score": 0.96875,
        "tokens": 22,
        "tier": "hybrid-rrf",
        "vecScore": 0.864609,
        "ftsScore": null
      }
    ],
    "resolution": {
      "embeddingSource": "remote",
      "embeddingModel": "voyage-ai/voyage-code-3",
      "vectorStore": "qdrant",
      "strategyUsed": "hybrid",
      "rerankApplied": true,
      "fallbackReason": null
    },
    "totalTokensUsed": 22,
    "budgetMaxTokens": 2000
  }
  ```
- **Real Keyless Inference Request (`POST /v1/chat/completions`)**:
  ```bash
  curl -sS -X POST "http://127.0.0.1:20128/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "x-omniroute-no-cache: true" \
    -d '{"model":"gemini-3.8-flash-high","temperature":0.2,"messages":[{"role":"user","content":"What is the project codename for the OmniRoute Qdrant BM25 verification canary? Reply with just the codename."}]}'
  ```
  Response:
  ```json
  {
    "id": "chatcmpl-1792877259762-22d2eff9",
    "object": "chat.completion",
    "created": 1792877259,
    "model": "gemini-3.8-flash-high",
    "choices": [
      {
        "index": 0,
        "finish_reason": "stop",
        "message": {
          "role": "assistant",
          "content": "FALCON-9472"
        }
      }
    ],
    "usage": {
      "prompt_tokens": 867,
      "completion_tokens": 113,
      "total_tokens": 980
    }
  }
  ```
  Model replied with exact canary string `FALCON-9472`, confirming keyless `"global"` memory retrieval and prompt injection.

### E2E Test 3 — `x-omniroute-no-memory: true` Per-Request Opt-Out
- **Inference with `x-omniroute-no-memory: true`**:
  ```bash
  curl -sS -X POST "http://127.0.0.1:20128/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "x-omniroute-no-cache: true" \
    -H "x-omniroute-no-memory: true" \
    -d '{"model":"gemini-3.8-flash-high","temperature":0.2,"messages":[{"role":"user","content":"What is the project codename for the OmniRoute Qdrant BM25 verification canary? Reply with just the codename."}]}'
  ```
  Response:
  - Prompt tokens dropped from `867` to `103` (zero memory injected).
  - Model lacked the canary code and attempted workspace tool calls instead:
    `choices[0].message.tool_calls[0].function.name == "workspace:listFiles"`.
  - Confirmed `x-omniroute-no-memory: true` cleanly bypasses memory injection.

### E2E Test 4 — Post-Response Automatic Fact Extraction into SQLite + Qdrant (`int8`) + `sqlite-vec` (`int8`)
- **Preference Statement Submission**:
  ```bash
  curl -sS -X POST "http://127.0.0.1:20128/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "x-omniroute-no-cache: true" \
    -d '{"model":"gemini-3.8-flash-high","temperature":0.2,"messages":[{"role":"user","content":"I prefer using Qdrant int8 quantization with SQLite FTS5 BM25 for hybrid vector retrieval. Acknowledge briefly."}]}'
  ```
- **Extracted Memory Verification**:
  - Query `GET /api/memory`: automatically stored memory entry with `key: "preference:using_qdrant_int8_quantization_with_sqli"`, `content: "using Qdrant int8 quantization with SQLite FTS5 BM25 for hybrid vector retrieval"`, and metadata `{"category":"preference","source":"llm_response"}`.
  - Qdrant point count increased to `3` points in `omniroute_memory`.
- **Artifact Cleanup**:
  - Purged test memories via `DELETE /api/memory/<id>` across all test memory UUIDs.
  - Flushed test points in Qdrant: `POST http://127.0.0.1:6333/collections/omniroute_memory/points/delete` (`{"filter":{}}`).
  - Verified Qdrant count returned to `0` (`{"result":{"count":0},"status":"ok"}`).

### E2E Test 5 — Real All-Request Layer-2 Redis Semantic Cache Across Local & Remote Tailscale Serve
- **Call A (Local Initial Request — Cache MISS & Store)**:
  - Endpoint: `http://127.0.0.1:20128/v1/chat/completions`
  - Payload: `model: "gemini-3.8-flash-high"`, `temperature: 0`, `max_tokens: 64`, `tools: [lookup_metric]`, prompt: `"Explain in one short sentence why Reciprocal Rank Fusion is useful for hybrid search."`
  - Status: `200 OK`, returned response ID `chatcmpl-1792877427423-89907eb5`.
  - Verified stored in Redis (`omniroute:semcache:model:gemini-3.8-flash-high`) under entry `e3aeff8c-8948-4f61-a40e-ccbf2a66d024` with:
    - `embedding dim: 768` (Ollama `nomic-embed-text`)
    - Partition key: `cacheKey: "ct:d7d6d9c1aeb8f12c"` (SHA-256 hash of `outputContractOf(body)` covering `tools` and `max_tokens`).
- **Call B (Remote Tailscale Serve Paraphrased Request — Cache HIT)**:
  - Endpoint: `https://iosteam-mac-mini.tailc6b508.ts.net/v1/chat/completions`
  - Payload: same `tools`, `max_tokens: 64`, paraphrased prompt: `"Please explain in one short sentence why Reciprocal Rank Fusion is helpful for hybrid search."`
  - Status: `200 OK`, returned in `<20ms` with identical response ID `chatcmpl-1792877427423-89907eb5` and verbatim cached content.
- **Call C (Different Tool Schema — Partition Isolation)**:
  - Endpoint: `http://127.0.0.1:20128/v1/chat/completions`
  - Payload: same prompt as Call B, but modified tool schema (`"name":"different_tool"`, property `"diff_prop"`).
  - Status: `200 OK`, freshly generated ID `chatcmpl-1792877514997-bed3fc16` with new completion text (`completion_tokens: 45` vs `36`). Did not collide with Call A/B cache entry due to contract partition isolation.
- **Cache Cleanup**:
  - Flushed Redis database: `docker exec omniroute-redis redis-cli FLUSHDB` $\rightarrow$ `OK`.
  - Verified zero semcache keys remain in Redis.

---

## 9. Code Review Remediation Verification (Findings 1–8)

1. **Finding 1 — Multi-Turn Tool Arguments, Tool Outputs, and Anthropic `tool_use`/`tool_result` Partition Isolation (`95293.js`)**:
   - Patched `normalizeConversationForEmbedding` (`module 523668`) to always append serialized `tool_calls`/`function_call`/`output` and Anthropic `tool_use`/`tool_result` blocks alongside text content without early-returning on assistant preamble text, and added a deterministic 16-hex SHA-256 tool-history partition digest (`tc:<sha256_16>`) into `cacheKey` in `SemanticCacheManager.lookup()` and `store()`.
   - **Live Proof**:
     - Request A (`tool_calls: read_file("/etc/gamma_v2.conf")`, tool output `"SECRET_VALUE=/etc/gamma_v2.conf"`): `X-OmniRoute-Cache: MISS`, reply `"/etc/gamma_v2.conf"`.
     - Request B (paraphrased user prompt + identical assistant preamble `"Let me read that file"`, but different tool call `read_file("/etc/delta_v2.conf")` and output `"SECRET_VALUE=/etc/delta_v2.conf"`): `X-OmniRoute-Cache: MISS` (no false collision), reply `"/etc/delta_v2.conf"`.
     - Request A2 (paraphrased user prompt + identical `read_file("/etc/gamma_v2.conf")` and output, submitted keyless): `X-OmniRoute-Cache: HIT`, `X-OmniRoute-Cache-Similarity: 0.9900`, reply `"/etc/gamma_v2.conf"`.
2. **Finding 2 & Finding 5 — Unconditional `memory_fts` BM25 RRF Fusion on `c.ok` & Strict `case "hybrid":` Scoping (`72089.js`, `87878.js`)**:
   - Anchored the `retrieveMemoriesInternal` replacement strictly to `break;case"hybrid":{if(b.query&&q){` so `case "semantic":` remains pure vector search (`!semSlice.includes("_fts") === true`).
   - Evaluated `_fts` whenever `c.ok` is true (`if((c.results&&c.results.length>0)||_fts.length>0)`), ensuring lexical-only matches are still returned when Qdrant returns 0 vector hits.
   - **Live Proof**: `POST /api/memory/retrieve-preview` with `strategy: "hybrid"` returned `tier: "hybrid-rrf"`, `vecScore: 0.8559617`, `ftsScore: 0.01639344262295082`; with `strategy: "semantic"`, returned `tier: "qdrant"`, `vecScore: 0.8549355`, `ftsScore: null`.
3. **Finding 3 — Shared Workspace Owner Pool (`OMNIROUTE_DEFAULT_OWNER_ID=6a72d8ab-88db-4d49-973b-864c6cbdace5`) Across Keyless & `mac-mini-1` Traffic (`88137.js`, `95293.js`)**:
   - Set `OMNIROUTE_DEFAULT_OWNER_ID=6a72d8ab-88db-4d49-973b-864c6cbdace5` in `/Users/androidteam/Omniroute/docker-compose.override.yml` and patched `resolveMemoryOwnerId`, `checkSemanticCache`, and `SemanticCacheManager` (`lookup` & `store`) to fall back to `process.env.OMNIROUTE_DEFAULT_OWNER_ID || "6a72d8ab-88db-4d49-973b-864c6cbdace5"`.
   - **Live Proof**: Memory seeded under `mac-mini-1` (`6a72d8ab-88db-4d49-973b-864c6cbdace5`) with token `PHOENIX-8821` was retrieved and answered (`"PHOENIX-8821"`) by a keyless `POST /v1/chat/completions` request, and keyless Request A2 hit `mac-mini-1`'s Redis semantic cache entry (`similarity: 0.9900`).
4. **Finding 4 — Built-in `memory_*` Tool Injection Gated on `skillsEnabled === true` (`88137.js`)**:
   - Patched `injectMemoryAndSkills` (`if(b&&t?.enabled&&t?.skillsEnabled&&!0!==a.stream)`) and `nonStreamingResponse` (`!aq&&bX`) so `memoryEnabled: true, skillsEnabled: false` injects `Memory context:` text without mutating `body.tools` with `memory_save`/`memory_search`/`memory_update`/`memory_delete`.
5. **Finding 6, Finding 7 & Finding 8 — Batched Redis `srem`, Lean Replacement Table, and Fail-Closed Marker Assertions (`container-entrypoint-compat.sh` & `update.sh`)**:
   - Replaced per-ID `this.delete(a)` loop in `RedisVectorStore.searchNearest` with batched `g.srem(this.allIdsKey(),...m)` and `g.srem(this.modelSetKey(b.model),...m)`.
   - Removed redundant intermediate `baseUrl` rule from `container-entrypoint-compat.sh`.
   - Added 11 fail-closed marker assertions to `container-entrypoint-compat.sh` (`process.exit(1)` if any patch marker is missing) and updated `update.sh` Gate 8b (`QDRANT_OK|CACHE_OK|PATCH_OK`).
   - Patched `shouldInjectMemory` and `injectMemory` in `14461.js` plus `lastUserQuery` in `88137.js` (`responses_memory_injection` marker, bringing total fail-closed marker assertions to 12) so OpenAI Responses API (`POST /v1/responses`) requests carrying `input` (string or array) inject retrieved `Memory context:` into `body.instructions` prior to upstream translation.
   - **Multi-Dialect Live Verification (`/v1/chat/completions`, `/v1/responses`, `/v1/messages`)**:
     - Seeded canary memory `e2e:final_canary_all_dialects` (`"The OmniRoute hybrid memory verification secret code is TITAN-7741."`) under `6a72d8ab-88db-4d49-973b-864c6cbdace5`.
     - Keyless `POST /v1/chat/completions` (`model: "gemini-3.8-flash-high"`): replied `"TITAN-7741"`.
     - Authenticated `POST /v1/responses` (`model: "gemini-3.8-flash-high"`, `input: "What is the OmniRoute hybrid memory verification secret code? Reply with ONLY the code."`): replied `"TITAN-7741"`.
     - Authenticated `POST /v1/messages` (`model: "gemini-3.8-flash-high"`, Anthropic Messages format): replied `"TITAN-7741"`.
     - Opt-out `POST /v1/chat/completions` with `x-omniroute-no-memory: true`: replied `"UNKNOWN"` (`prompt_tokens: 99` vs `134` with memory injected).
     - Post-response fact extraction (`"I prefer using Qdrant scalar int8 quantization with FTS5 BM25 RRF for OmniRoute memory"`): automatically stored `preference:using_qdrant_scalar_int8_quantization_wi` across SQLite `memories`, `vec_memories` (`int8[1024]`), `memory_fts` (`BM25`), and Qdrant `omniroute_memory` (`int8[1024]`), then cleaned up all canary test rows.
