## ADDED Requirements

### Requirement: Cached Voyage AI Qdrant Embeddings, Health-Check Point Guard, and FTS5 OR Hybrid Retrieval

OmniRoute SHALL keep Hybrid Memory enabled (`enabled: true`, `skillsEnabled: false`, `strategy: "hybrid"`, `vectorStore: "qdrant"`, `voyage-ai/voyage-code-3`, `voyage-ai/rerank-2.5`), SHALL cache 1024d vectors in `globalThis.__omnirouteQdrantEmbedCache` inside `qdrant.ts:embedText()` (`chunks/54843.js`), SHALL skip Qdrant persistence when `apiKeyId === "health-check"`, and SHALL join FTS5 query tokens with `OR` in `sanitizeFts5Query()`.

#### Scenario: Repeated semantic memory queries hit the in-memory LRU embedding cache without duplicate Voyage AI HTTP calls
- **WHEN** `searchSemanticMemory()` executes for a query text whose `("voyage-ai/voyage-code-3", text)` vector is already present in `globalThis.__omnirouteQdrantEmbedCache`
- **THEN** `qdrant.ts:embedText()` SHALL return the cached 1024-dimension vector in `<1 ms` without issuing an outbound `POST /v1/embeddings` request to `voyage-ai`
- **AND** on a cache miss, `qdrant.ts:embedText()` SHALL store the returned vector in `globalThis.__omnirouteQdrantEmbedCache` so any subsequent retrieval step in the same or later turn reuses the cached vector

#### Scenario: Clean memory seeding populates Qdrant points and `/api/memory/health` leaves zero orphaned points
- **WHEN** `POST /api/memory` seeds a workspace memory and `GET /api/memory/health` runs `verifyExtractionPipeline("health-check")`
- **THEN** the workspace memory SHALL be indexed in both `vec_memories` (`needsReindex: 0`) and Qdrant `omniroute_memory`, while `apiKeyId === "health-check"` probes SHALL NOT leave orphaned points in `omniroute_memory`

#### Scenario: Multi-word prompt matches FTS5 keyword memories via boolean `OR`
- **WHEN** `retrieveHybrid` builds FTS5 keyword candidates via `sanitizeFts5Query(query)` (`chunks/54843.js` module `541915`)
- **THEN** `sanitizeFts5Query` SHALL join sanitized tokens (`length > 2`) with `" OR "` rather than implicit `" "` (`AND`) so memories sharing relevant keywords are ranked by BM25 and fused with Qdrant cosine results via RRF (`k=60`)

### Requirement: Dedicated 11-Pro-Account Auto Pool for `gemini-3.8-flash-high` and Ultra Quota Isolation

OmniRoute SHALL configure `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) with `strategy: "auto"`, `context_cache_protection: false`, `targetTimeoutMs: 25000`, `predictiveTtftMs: 25000`, and 11 `kind: "model"` steps scoped exclusively to the 11 active `g1-pro-tier` `agy` connections (excluding the 3 `g1-ultra-tier` accounts and `free-tier`), and SHALL enable `rateLimitProtection: true` on all 14 active `agy` accounts via `POST /api/rate-limits`.

#### Scenario: `gemini-3.8-flash-high` routes across the 11 Pro accounts without consuming Ultra Gemini quota
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is inspected or invoked
- **THEN** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, and `models` SHALL contain 11 `agy/gemini-3.8-flash-high` steps mapped to the 11 `g1-pro-tier` connections with non-empty email `label`s
- **AND** none of the 3 `g1-ultra-tier` `connectionId`s (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`) SHALL appear in `gemini-3.8-flash-high`

#### Scenario: All 3 Ultra accounts and 11 Pro accounts enforce `rateLimitProtection: true`
- **WHEN** `GET /api/rate-limits` is queried
- **THEN** all 3 `g1-ultra-tier` `agy` accounts (`62af823b`, `0532bad4`, `338764b8`) and all 11 `g1-pro-tier` `agy` accounts SHALL report `rateLimitProtection: true` and `enabled: true`

### Requirement: Tier-Matched Combo Timeouts, Cold-Start Semantic Cache Bridge, and Fail-Closed Entrypoint Guard

OmniRoute SHALL configure `targetTimeoutMs: 180000` and `predictiveTtftMs: 60000` on deep-reasoning combos (`gemini-4-argon*` and `claude-opus-5.5`), SHALL configure `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`, and `maxRetries: 1` on `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash`, SHALL auto-invoke `ensureSemanticCacheDbBridge()` on semantic cache initialization, and SHALL assert all runtime patch markers fail-closed in `container-entrypoint-compat.sh`.

#### Scenario: Deep-reasoning and high-TTFT combos enforce tier-matched timeouts without premature 25s aborts
- **WHEN** `GET /api/combos` is queried
- **THEN** `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `claude-opus-5.5` SHALL each have `config.targetTimeoutMs === 180000` and `config.predictiveTtftMs === 60000`
- **AND** `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash` SHALL each have `config.targetTimeoutMs === 120000`, `config.predictiveTtftMs === 45000`, and `config.maxRetries === 1`

#### Scenario: Entrypoint verification fails closed across all runtime markers and semantic cache bridge initializes on cold start
- **WHEN** `container-entrypoint-compat.sh` runs on container startup
- **THEN** it SHALL verify all patch markers across the compiled server chunks without skipping missing chunk filenames (`process.exit(1)` on any missing marker)
- **AND** `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_TIMEOUT_MS=3000` and `OMNIROUTE_SEMANTIC_CACHE_TTL_MS=18000000` SHALL be set in `/Users/androidteam/Omniroute/.env` with `ensureSemanticCacheDbBridge()` auto-invoked on `/v1/responses` and `/v1/messages` cold starts
