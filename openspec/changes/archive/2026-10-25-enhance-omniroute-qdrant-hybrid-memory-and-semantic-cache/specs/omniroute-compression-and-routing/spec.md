## MODIFIED Requirements

### Requirement: Built-in Memory and Skills Injection Disabled in Favor of Dedicated AgentMemory

OmniRoute SHALL configure `memoryEnabled: true`, `skillsEnabled: false`, and `memoryMaxTokens: 2000` via `/api/settings/memory`, keeping built-in skills and `memory_*` tool injection disabled when `skillsEnabled` is `false` while enabling always-on hybrid memory (`strategy: "hybrid"`, `vectorStore: "qdrant"`, `retentionDays: 60`) with shared workspace keyless owner fallback (`OMNIROUTE_DEFAULT_OWNER_ID` / `"6a72d8ab-88db-4d49-973b-864c6cbdace5"`) and `x-omniroute-no-memory: true` header opt-out.

#### Scenario: Authenticated chat request bypasses built-in memory injection and extraction
- **WHEN** an authenticated or keyless client submits a request carrying `x-omniroute-no-memory: true` to `/v1/chat/completions`, `/v1/messages`, or `/v1/responses`
- **THEN** OmniRoute SHALL set `memoryOwnerId = null` and SHALL neither prepend `Memory context:` nor inject `memory_*` tools nor run post-response regex fact extraction into the `memories` table, while always keeping `skillsEnabled: false` across all requests

#### Scenario: Internal memory store remains empty
- **WHEN** `GET /api/memory?limit=1` is queried before any non-opted-out conversation facts or explicit `POST /api/memory` entries are recorded (or after memory cleanup)
- **THEN** OmniRoute SHALL return `total: 0` and `stats.tokensUsed: 0`, and once entries are stored SHALL scope them by `apiKeyInfo.id` or `OMNIROUTE_DEFAULT_OWNER_ID` (`"6a72d8ab-88db-4d49-973b-864c6cbdace5"`) for keyless traffic without injecting `memory_*` tools into `body.tools` when `skillsEnabled` is `false`

## ADDED Requirements

### Requirement: Internal Qdrant Sidecar Deployment and Scalar int8 Vector Quantization

OmniRoute SHALL run an internal `omniroute-qdrant` (`qdrant/qdrant:v1.12.4`) sidecar bound exclusively to `127.0.0.1:6333` and `127.0.0.1:6334` with persistent named volume `omniroute-qdrant-data`, configure `/api/settings/qdrant` (`enabled: true`, `host: "qdrant"`, `port: 6333`, `collection: "omniroute_memory"`, `embeddingModel: "voyage-ai/voyage-code-3"`, `quantization: "int8"`), and set `QDRANT_VECTOR_SIZE=1024` and `QDRANT_HNSW_EF_CONSTRUCT=128`.

#### Scenario: Qdrant health and collection configuration on local and internal networks
- **WHEN** `GET /api/settings/qdrant` and `GET /api/memory/engine-status` are queried while `omniroute-qdrant` is running
- **THEN** `GET /api/settings/qdrant` SHALL report `enabled: true`, `host: "qdrant"`, `port: 6333`, `collection: "omniroute_memory"`, `embeddingModel: "voyage-ai/voyage-code-3"`, and `quantization: "int8"`, and `GET /api/memory/engine-status` SHALL report `qdrant.enabled: true` and `qdrant.healthy: true` without exposing port `6333` or `6334` on Tailscale Serve or non-loopback host interfaces

#### Scenario: Dual-tier int8 quantization across Qdrant and sqlite-vec fallback
- **WHEN** a memory entry is created or updated via `POST /api/memory` or post-response extraction with `MEMORY_VEC_QUANTIZATION=int8` and `QDRANT_VECTOR_SIZE=1024` enabled
- **THEN** OmniRoute SHALL upsert the `1024`-dimensional `voyage-ai/voyage-code-3` vector into Qdrant with scalar `int8` quantization (`always_ram: true`, `rescore: true`) and into local SQLite `vec_memories` (`int8[1024]`) as the automatic Tier-1 fallback

### Requirement: Always-On Hybrid Memory with Qdrant Cosine, FTS5 BM25 RRF Fusion, and Cross-Encoder Reranking

OmniRoute SHALL configure `/api/settings/memory` with `enabled: true`, `maxTokens: 2000`, `retentionDays: 60`, `strategy: "hybrid"`, `skillsEnabled: false`, `embeddingSource: "remote"`, `embeddingProviderModel: "voyage-ai/voyage-code-3"`, `rerankEnabled: true`, `rerankProviderModel: "voyage-ai/rerank-2.5"`, and `vectorStore: "qdrant"`, and SHALL fuse Qdrant Cosine hits with SQLite `memory_fts` BM25 hits via Reciprocal Rank Fusion (`k = 60`) before reranking.

#### Scenario: Hybrid retrieval fuses Qdrant vector ranks and SQLite FTS5 BM25 ranks with reranking
- **WHEN** `POST /api/memory/retrieve-preview` or chat memory injection runs under `strategy: "hybrid"` and `vectorStore: "qdrant"`
- **THEN** OmniRoute SHALL execute both Qdrant Cosine search (`omniroute_memory`) and SQLite `memory_fts` BM25 search (including when Qdrant returns 0 vector hits while `memory_fts` matches), combine their candidate rankings using Reciprocal Rank Fusion (`rrf_score = 1/(60 + r_qdrant) + 1/(60 + r_fts)`), and rerank the fused candidates via loopback `POST /v1/rerank` using `voyage-ai/rerank-2.5` while leaving `strategy: "semantic"` as pure vector search

#### Scenario: Graceful fallback to sqlite-vec and FTS5 hybrid RRF when Qdrant is unreachable
- **WHEN** `omniroute-qdrant` is unreachable or returns an error during `strategy: "hybrid"` retrieval
- **THEN** OmniRoute SHALL fail open to Tier-1 `sqlite-vec` (`vec_memories`) + `memory_fts` BM25 RRF fusion without failing the inference request

#### Scenario: Always-on memory owner resolution across keyless and API-key local and remote requests
- **WHEN** a local loopback client (`127.0.0.1:20128`/`20129`) or remote Tailnet client (`https://iosteam-mac-mini.tailc6b508.ts.net`) submits a chat or Responses API request without `x-omniroute-no-memory: true`
- **THEN** OmniRoute SHALL resolve `memoryOwnerId` and semantic cache `apiKeyId` to `apiKeyInfo.id` when an API key is present or `OMNIROUTE_DEFAULT_OWNER_ID` (`"6a72d8ab-88db-4d49-973b-864c6cbdace5"`) when keyless, performing both pre-request hybrid memory retrieval and post-response fact extraction without mutating `body.tools` unless `x-omniroute-no-memory: true` is supplied

### Requirement: All-Request Layer-2 Redis Semantic Cache with Host Ollama Embeddings and Output-Contract Partitioning

OmniRoute SHALL configure `/api/settings/cache-config` with `semanticCacheEnabled: true`, `semanticCacheVectorEnabled: true`, `semanticCacheBackend: "redis"`, `semanticCacheRedisUrl: "redis://redis:6379"`, `semanticCacheThreshold: 0.90`, `semanticCacheEmbeddingProvider: "ollama-local"`, `semanticCacheEmbeddingModel: "nomic-embed-text"`, `semanticCacheEmbeddingDimension: 768`, and `semanticCacheEmbeddingBaseUrl: "http://host.docker.internal:11434/v1/embeddings"`.

#### Scenario: Semantic cache hits across requests carrying tools, reasoning_effort, or max_tokens with identical output contracts
- **WHEN** two `temperature: 0` requests with semantically equivalent prompts (`cosine similarity >= 0.90`, up to 10 turns) and identical `outputContractOf(body)` (`tools`, `tool_choice`, `max_tokens`, `reasoning_effort`, `response_format`, `text.format`) are submitted
- **THEN** OmniRoute SHALL partition the Redis vector lookup and store by the SHA-256 digest of `outputContractOf(body)` rather than bypassing Layer-2, returning a semantic cache `HIT` (`X-OmniRoute-Cache: HIT`, `X-OmniRoute-Cache-Similarity`) on the second request

#### Scenario: Requests with different tool schemas or output formats never collide in Layer-2 semantic cache
- **WHEN** a request with `tools` or `response_format` schema `A` follows a semantically similar prompt that was cached under schema `B` (`A != B`)
- **THEN** OmniRoute SHALL isolate their Redis vector partitions by contract digest and SHALL NOT serve schema `B`'s cached response to schema `A`'s request

#### Scenario: Registry baseUrl fallback for cloud embedding providers in semantic cache probe
- **WHEN** `POST /api/settings/cache-config/test-embedding` or `SemanticCacheDbBridge` resolves an embedding provider whose SQLite `provider_connections` row has no custom `provider_specific_data.baseUrl` (such as `voyage-ai`, `jina-ai`, or `openrouter`)
- **THEN** OmniRoute SHALL fall back to the provider's canonical `EMBEDDING_PROVIDERS[provider].baseUrl` while preserving its stored API key
