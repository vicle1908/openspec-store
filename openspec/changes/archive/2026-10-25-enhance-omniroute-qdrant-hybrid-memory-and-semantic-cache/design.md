# Design

## Context

See `proposal.md - Why` for motivation and problem background.

OmniRoute (`v3.8.52`) runs as a Docker Compose stack (`base` profile) from `/Users/androidteam/Omniroute`, serving both local Mac Mini clients (`http://127.0.0.1:20128` and `:20129`, `/Users/androidteam`) and remote MacBook Pro Tailnet sessions (`https://iosteam-mac-mini.tailc6b508.ts.net` -> `100.101.64.56`, `macbook-pro-ca-l-1.tailc6b508.ts.net`, `/Users/vinhlk`). Both machines authenticate to OmniRoute using the shared `mac-mini-1` API key (`id: 6a72d8ab-88db-4d49-973b-864c6cbdace5`, `21,850` logged calls) alongside `3,153` keyless local calls.

Because `/Users/androidteam/Omniroute` is an upstream-tracking checkout (`diegosouzapw/omniroute:latest`), all infrastructure overrides MUST live in untracked `/Users/androidteam/Omniroute/docker-compose.override.yml`, runtime behavioral patches MUST execute idempotently on container startup via `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (which is also invoked with `--patch-only` by `scripts/ensure-muse-wire-compat.sh` at Gate 4b of `scripts/update.sh`), and persistent configuration MUST be written through OmniRoute's management REST APIs (`PUT /api/settings/qdrant`, `PUT /api/settings/memory`, `PUT /api/settings/cache-config`, `PATCH /api/settings/database`).

## Goals / Non-Goals

**Goals:**
- Deploy an internal `omniroute-qdrant` (`qdrant/qdrant:v1.12.4`) sidecar on the Docker Compose network (and loopback `127.0.0.1:6333`/`6334`) with scalar `int8` quantization (`always_ram: true`, `rescore: true`), paired with local SQLite `vec_memories` (`int8[1024]`) and `memory_fts` (BM25) fallback.
- Implement true Hybrid Memory retrieval (`strategy: "hybrid"`, `vectorStore: "qdrant"`) across both `retrieveMemoriesInternal` and `retrievePreview` (`72089.js` and `87878.js`) that fuses Qdrant Cosine rankings with SQLite `memory_fts` BM25 rankings via Reciprocal Rank Fusion (`RRF, k = 60`) and reranks top candidates via `voyage-ai/rerank-2.5` (`POST /v1/rerank`), using `voyage-ai/voyage-code-3` (`1024d`) embeddings.
- Enable always-on memory across both keyless and `mac-mini-1` API-key local/remote requests (`memoryOwnerId = apiKeyInfo?.id || process.env.OMNIROUTE_DEFAULT_OWNER_ID || "6a72d8ab-88db-4d49-973b-864c6cbdace5"`), while honoring `x-omniroute-no-memory: true` per-request opt-out and keeping `skillsEnabled: false` (so built-in `memory_*` tools are not injected into `body.tools`).
- Enable Layer-2 Redis Semantic Response Caching (`omniroute-redis`, `redis://redis:6379`, threshold `0.90`, `historyDepth: 10`) powered by `<10ms` local Apple Metal embeddings via Host Ollama (`http://host.docker.internal:11434/v1/embeddings`, `nomic-embed-text`, `768d`), and support all requests (`tools`, `tool_choice`, `max_tokens`, `reasoning_effort`, `response_format`, `text.format`) on both `lookup()` and `store()` by hashing `outputContractOf(body)` into the vector partition key (`cacheKey`) instead of skipping Layer-2.
- Preserve 100% compatibility with the MacBook Pro OMP session's 8 active `container-entrypoint-compat.sh` rules, `--patch-only` execution mode, `OMNIROUTE_SQLITE_SLOW_MS=200`, and all 8 routing combos (`gemini-4-argon*` pinned to Ultra `agy` accounts `338764b8` and `0532bad4`, `default-caveman` compression assignments).

**Non-Goals:**
- Exposing Qdrant ports (`6333`/`6334`) directly to remote machines over Tailscale Serve or LAN.
- Modifying tracked upstream files in `/Users/androidteam/Omniroute` (git working tree MUST remain clean).
- Enabling OmniRoute's internal `skillsEnabled` prompt injection (`skillsEnabled` remains `false` so workspace `.agents/skills/` and MCP tools remain authoritative).
- Modifying any routing combo targets (`gemini-4-argon*`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `muse-spark-1.3`, `phanmemvip`) or compression pipeline settings.

## Decisions

### 1. Cross-Machine Coordination with MacBook Pro OMP Session (`container-entrypoint-compat.sh` & Shared `mac-mini-1` Key)
- **Decision**:
  - Retain all 8 existing chunk replacement pairs in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`^gemini-(?:[34]...`, `\bmodel(?!\s+turn\b)` x2, `"antigravity"===ag(a)||"agy"===ag(a)` x2, `{id:"model-turn",pattern:/ending with a model turn/i}`, unconditional `function v(a){return"stop"===(0,f._)(a.status,a.errorText)}`, and `"aicode-consumers"===d?null:d` header omission in `86370.js`) and preserve the `--patch-only` CLI contract used by `scripts/ensure-muse-wire-compat.sh` and `scripts/update.sh`.
  - Both local (`Mac Mini`) and remote (`MacBook Pro`) OMP/Claude/Codex clients that authenticate with `mac-mini-1` (`id: 6a72d8ab-88db-4d49-973b-864c6cbdace5`) and keyless local clients (`OMNIROUTE_DEFAULT_OWNER_ID=6a72d8ab-88db-4d49-973b-864c6cbdace5`) share the `6a72d8ab-88db-4d49-973b-864c6cbdace5` memory and semantic-cache partition.

### 2. Hybrid Embedding Split: Host Ollama (`nomic-embed-text` `768d`) for Semantic Cache vs. `voyage-ai/voyage-code-3` (`1024d`) + `voyage-ai/rerank-2.5` for Memory
- **Decision**:
  - **Layer-2 Semantic Cache**: Use Host Ollama (`http://host.docker.internal:11434/v1/embeddings`, model `nomic-embed-text`, `768d`) with `OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS=true`, `extra_hosts: ["host.docker.internal:host-gateway"]`, and `OMNIROUTE_SEMANTIC_CACHE_*` environment variables on `omniroute-base` (ensuring `/v1/responses`, `/v1/messages`, and `/v1/chat/completions` all bootstrap `SemanticCacheManager` identically even before `ensureSemanticCacheDbBridge()` runs).
  - **Hybrid Memory (`Qdrant` + `sqlite-vec`)**: Use `voyage-ai/voyage-code-3` (`1024d`) with OmniRoute's built-in 1,000-entry `MEMORY_EMBEDDING_CACHE`, followed by `voyage-ai/rerank-2.5` via loopback `POST /v1/rerank`.
  - **Registry `baseUrl` Fallback in `semanticCacheDbBridge`**: Patch `resolveProviderConnectionDetails` in compiled `semanticCacheDbBridge` chunks (`72053.js` and `test-embedding/route.js`) so when `provider_specific_data.baseUrl` is unset in SQLite, it falls back to canonical provider `baseUrl` map (`voyage-ai: "https://api.voyageai.com/v1/embeddings"`, `jina-ai: "https://api.jina.ai/v1/embeddings"`, `openrouter: "https://openrouter.ai/api/v1/embeddings"`, `openai: "https://api.openai.com/v1/embeddings"`, `cohere: "https://api.cohere.com/v2/embed"`, `mistral: "https://api.mistral.ai/v1/embeddings"`).
- **Rationale**:
  - Semantic cache lookup lies on the critical synchronous path of every `temperature: 0` cache miss. Host Ollama runs natively on Apple Silicon Metal (`~5–10ms` latency, zero WAN jitter, zero rate limits), whereas a synchronous WAN call to Voyage AI would add `~150–300ms` to every uncached request.
  - Conversely, durable memory retrieval benefits from code-specialized `1024d` representations (`voyage-code-3`) and cross-encoder reranking (`voyage-ai/rerank-2.5`) to prevent irrelevant memories from consuming the `2,000`-token injection budget.

### 3. All-Request Layer-2 Semantic Cache via Output-Contract Partition Hashing on Both `lookup()` and `store()`
- **Decision**:
  - In `open-sse/handlers/chatCore.ts`, both non-streaming (`lines 3102-3115`) and streaming (`lines 3311-3324`) completion paths already invoke `getSemanticCacheManager().store(...)` alongside legacy `setCachedResponse(...)`.
  - However, inside `/app/.build/next/server/chunks/95293.js`:
    1. `SemanticCacheManager.lookup()` (`module 995293`) aborts before embedding if `(0,g.Ly)(a.body)` (`outputContractOf(a.body)`) is truthy or `!(0,n.m)(f, ...)` (`isCompleteTextProjection`) is false.
    2. `SemanticCacheManager.store()` (`module 995293`) skips generating `embedding` (`b = undefined`, `semanticProjectionVersion = undefined`) whenever `(0,g.Ly)(a.body)` is truthy or `!(0,n.m)(e, ...)` is false!
    3. `isCompleteTextProjection` (`module 396505`) rejects messages containing keys outside `["role", "content", "type"]` (e.g., `tool_calls`, `tool_call_id`, `name`, `cache_control`, `reasoning_content`) and `normalizeConversationForEmbedding` (`module 523668`) only extracts plain `content` text.
  - We patch `/app/.build/next/server/chunks/95293.js` via `scripts/container-entrypoint-compat.sh` so:
    1. Neither `lookup()` nor `store()` aborts on `(0,g.Ly)(a.body)`. Instead, when `const contract = (0,g.Ly)(a.body)` is non-null, a deterministic SHA-256 digest of `contract` is folded into the effective `cacheKey` partition (`const effKey = [headerKey, contract ? "ct:" + sha256(JSON.stringify(contract)).slice(0,16) : ""].filter(Boolean).join("|") || undefined`), which is stored on `s.cacheKey` in `store()` and matched via `o.cacheKey` in `lookup()`.
    2. `isCompleteTextProjection` (`module 396505`) allows standard message keys (`role`, `content`, `type`, `tool_calls`, `tool_call_id`, `name`, `cache_control`, `reasoning_content`, `call_id`, `output`, `arguments`, `function_call`) up to `historyDepth` (`10`), `normalizeConversationForEmbedding` (`module 523668`) always appends serialized `tool_calls` / `function_call` / `output` and Anthropic `tool_use` / `tool_result` content blocks alongside any text content (never returning early before tool fields), and `RedisVectorStore.searchNearest` (`module 733553`) batches stale set member cleanup via `srem`.

### 4. True Hybrid RRF (`Qdrant Cosine` + `SQLite FTS5 BM25`) + Cross-Encoder Rerank & Shared Workspace Owner Fallback
- **Decision**:
  - Run `omniroute-qdrant` (`qdrant/qdrant:v1.12.4`) in `docker-compose.override.yml` under `profiles: [base, memory]`, bound only to `127.0.0.1:6333` and `127.0.0.1:6334`.
  - Note on `PUT /api/settings/qdrant` schema (`src/shared/schemas/qdrant.ts`): `QdrantSettingsUpdateSchema` uses `.strict()` and accepts ONLY `{ enabled, host, port, collection, embeddingModel, quantization, apiKey }`. Meanwhile, `vectorSize` (`1024`) and `hnswEfConstruct` (`128`) are read by `normalizeQdrantConfig()` (`src/lib/memory/qdrant.ts:116-128`) from environment variables `QDRANT_VECTOR_SIZE=1024` and `QDRANT_HNSW_EF_CONSTRUCT=128`.
  - Patch `searchSemanticMemory` in `/app/.build/next/server/chunks/54843.js` and `99834.js` to raise Qdrant search limit cap from `Math.min(20, b)` to `Math.min(100, b)`.
  - Patch `retrieveMemoriesInternal` (anchored specifically to `case "hybrid":` so `case "semantic":` remains pure vector search) and `retrievePreview` in `/app/.build/next/server/chunks/72089.js` and `87878.js` so when `strategy === "hybrid"` and `vectorStore === "qdrant"`, OmniRoute:
    1. Queries Qdrant (`searchSemanticMemory(query, 100, { apiKeyId })`) **and** SQLite `memory_fts` BM25 (`buildFtsRows(apiKeyId, ftsColConfig)`) whenever `qres.ok` is true (including when Qdrant returns 0 vector hits but `memory_fts` has lexical matches).
    2. Fuses the Qdrant rank (`r_qdrant`, 0-based index + 1) and FTS5 BM25 rank (`r_fts`, 0-based index + 1) across the union of candidate memory IDs via Reciprocal Rank Fusion (`k = 60`):
       `rrfScore = (r_qdrant ? 1 / (60 + r_qdrant) : 0) + (r_fts ? 1 / (60 + r_fts) : 0)`
    3. Passes the RRF-ranked items (`tier: "qdrant"`) through `applyRerank()` (`voyage-ai/rerank-2.5` via loopback `POST /v1/rerank`) before applying the `maxTokens: 2000` budget walk.
    4. Falls back automatically to Tier-1 `sqlite-vec` (`int8[1024]`) + `memory_fts` RRF if Qdrant is unreachable or both Qdrant and FTS5 return 0 hits.
  - Patch `resolveMemoryOwnerId` (`module 20282`), `injectMemoryAndSkills` / `nonStreamingResponse` (`88137.js`), and semantic cache `apiKeyId` resolution (`88137.js` and `95293.js`) so keyless requests default to `process.env.OMNIROUTE_DEFAULT_OWNER_ID || "6a72d8ab-88db-4d49-973b-864c6cbdace5"` (unifying keyless and `mac-mini-1` memory and cache pools), and built-in `memory_*` tool injection is gated on `skillsEnabled === true` so `memoryEnabled: true, skillsEnabled: false` only injects `Memory context:` text without mutating `body.tools`.
  - Enforce a fail-closed marker assertion in `scripts/container-entrypoint-compat.sh` so any missing patch marker across compiled chunks causes the entrypoint and `ensure-muse-wire-compat.sh` to exit non-zero.

```
+-----------------------------------------------------------------------------------+
|                 HYBRID MEMORY RETRIEVAL PIPELINE (strategy="hybrid")              |
+-----------------------------------------------------------------------------------+
|  Incoming Query (memoryOwnerId = apiKeyInfo?.id || OMNIROUTE_DEFAULT_OWNER_ID)    |
|         |                                                                         |
|         +-------------------------------+-------------------------------+         |
|         | Dense Semantic Leg            | Lexical BM25 Leg              |         |
|         v                               v                               |         |
|  [voyage-ai/voyage-code-3 (1024d)]   [SQLite FTS5 `memory_fts`]         |         |
|         |                               | ORDER BY f.rank (BM25)        |         |
|         v                               |                               |         |
|  [Tier 2: Qdrant HNSW Cosine (int8)]    |                               |         |
|   (Fallback -> Tier 1: sqlite-vec int8) |                               |         |
|         |                               |                               |         |
|         +---------------+---------------+                               |         |
|                         |                                               |         |
|                         v                                               |         |
|        [Reciprocal Rank Fusion (RRF, k = 60)]                           |         |
|        score(d) = 1/(60 + rank_vec(d)) + 1/(60 + rank_fts(d))           |         |
|                         |                                               |         |
|                         v                                               |         |
|        [Cross-Encoder Rerank: voyage-ai/rerank-2.5 (/v1/rerank)]        |         |
|                         |                                               |         |
|                         v                                               |         |
|        [Token Budget Walk (maxTokens <= 2000, cacheSafe injection)]     |         |
+-----------------------------------------------------------------------------------+
```

## Risks / Trade-offs

- **[Risk] Overwriting or breaking MacBook Pro's 8 active `container-entrypoint-compat.sh` rules or `--patch-only` contract** → **Mitigation**: Keep all 8 existing `replacements` entries and the `--patch-only` CLI handler verbatim in `scripts/container-entrypoint-compat.sh`, adding the new cache/memory patches as modular, idempotent blocks verified by `scripts/ensure-muse-wire-compat.sh`.
- **[Risk] Compiled Next.js server chunk filenames change across OmniRoute image upgrades** → **Mitigation**: `scripts/container-entrypoint-compat.sh` locates target chunk files dynamically by content signature (`grep` / `includes`) rather than hardcoded chunk numbers, applies idempotent Node.js replacements guarded by sentinel markers, and `scripts/update.sh` verifies Qdrant, Hybrid Memory RRF, and Semantic Cache health before clearing `update-available`.
- **[Risk] Host Ollama daemon stopped or unreachable from container** → **Mitigation**: Ensure `ollama` service is running on host (`brew services` / launchd) and verify `http://host.docker.internal:11434/v1/embeddings` during deployment; `generateEmbeddingWithTimeout` (`3000ms`) fails open to Layer-1 exact SQLite/LRU cache so inference never fails if Ollama is down.
- **[Risk] `PUT /api/settings/qdrant` `.strict()` Zod schema rejects `vectorSize` and `hnswEfConstruct`** → **Mitigation**: Supply `QDRANT_VECTOR_SIZE=1024` and `QDRANT_HNSW_EF_CONSTRUCT=128` via `docker-compose.override.yml` environment variables (which `normalizeQdrantConfig()` reads directly) and send only `{ enabled, host, port, collection, embeddingModel, quantization }` in `PUT /api/settings/qdrant`.
- **[Risk] Canonical OpenSpec preservation on `omniroute-compression-and-routing`** → **Mitigation**: Use `## MODIFIED Requirements` on `### Requirement: Built-in Memory and Skills Injection Disabled in Favor of Dedicated AgentMemory` (preserving its exact requirement header and both existing `#### Scenario:` headers while updating the normative text for always-on memory + `x-omniroute-no-memory: true` opt-out and `skillsEnabled: false`) and `## ADDED Requirements` for the three new Qdrant, Hybrid Memory RRF, and Semantic Cache requirements.

## Migration Plan

1. **Host Ollama Verification**: Confirm `/opt/homebrew/bin/ollama` is serving `nomic-embed-text:latest` (`768d`) on `127.0.0.1:11434`.
2. **Compose Override & Compat Script Update**:
   - Update `/Users/androidteam/Omniroute/docker-compose.override.yml` to add `qdrant` (`profiles: [base, memory]`, `127.0.0.1:6333`, `127.0.0.1:6334`, volume `qdrant-data:/qdrant/storage`), `extra_hosts: ["host.docker.internal:host-gateway"]`, and environment variables (`OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS=true`, `QDRANT_ENABLED=true`, `QDRANT_HOST=qdrant`, `QDRANT_PORT=6333`, `QDRANT_VECTOR_SIZE=1024`, `QDRANT_HNSW_EF_CONSTRUCT=128`, `MEMORY_VEC_QUANTIZATION=int8`, `OMNIROUTE_SEMANTIC_CACHE_ENABLED=true`, `OMNIROUTE_SEMANTIC_CACHE_BACKEND=redis`, `OMNIROUTE_SEMANTIC_CACHE_REDIS_URL=redis://redis:6379`, `OMNIROUTE_SEMANTIC_CACHE_THRESHOLD=0.90`, `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_PROVIDER=ollama-local`, `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_MODEL=nomic-embed-text`, `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_DIMENSION=768`, `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_BASE_URL=http://host.docker.internal:11434/v1/embeddings`, `OMNIROUTE_SEMANTIC_CACHE_HISTORY_DEPTH=10`, `OMNIROUTE_SEMANTIC_CACHE_HISTORY_THRESHOLD=50`) while preserving `OMNIROUTE_SQLITE_SLOW_MS=200` and all existing env vars.
   - Update `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (preserving all 8 existing MacBook Pro rules and `--patch-only` support) with idempotent patches for:
     - `semanticCacheDbBridge` registry `baseUrl` fallback (`72053.js`, `test-embedding/route.js`)
     - `SemanticCacheManager` (`lookup` & `store`) + `isCompleteTextProjection` + `normalizeConversationForEmbedding` + `RedisVectorStore` output-contract/tool-history partition hashing, multi-turn tool projection, and batched `srem` (`95293.js`)
     - `resolveMemoryOwnerId` and semantic-cache `OMNIROUTE_DEFAULT_OWNER_ID` fallback, `skillsEnabled` gating for built-in `memory_*` tools, and `/v1/responses` `instructions` memory injection (`88137.js`, `14461.js`)
     - `retrieval.ts` (`72089.js`, `87878.js`) Qdrant Cosine + `memory_fts` BM25 RRF fusion and `qdrant.ts` (`54843.js`, `99834.js`) `topK` cap `100`, verified by 12 fail-closed marker assertions
3. **Container Recreate & Runtime API Configuration**:
   - Start `qdrant` and recreate `omniroute-base` via `docker compose --profile base up -d`.
   - Apply settings via `PUT /api/settings/qdrant`, `PUT /api/settings/memory`, `PUT /api/settings/cache-config`, and `PATCH /api/settings/database`.
4. **Rollback Strategy**:
   - Revert `PUT /api/settings/memory` (`enabled: false`), `PUT /api/settings/qdrant` (`enabled: false`), and `PUT /api/settings/cache-config` (`semanticCacheVectorEnabled: false`), and restore the prior `docker-compose.override.yml` and `container-entrypoint-compat.sh`.
