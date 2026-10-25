# Verification Evidence: optimize-omniroute-voyage-memory-ultra-isolation-and-hygiene

## 1. Pre-Mutation Snapshots & Claude Pools Archival (Tasks 1.1 & 1.2)
- Captured rollback snapshots into `/tmp/omniroute-voyage-snapshots/` (`combos.json`, `providers.json`, `provider-models.json`, `rate-limits.json`, `settings-memory.json`, `.env.bak`, `container-entrypoint-compat.sh.bak`, and manual SQLite snapshot `db_2026-10-25T16-02-32-440Z_manual.sqlite` [529.5 MB]).
- Verified `configure-claude-combos-antigravity-pools` is archived under `openspec/changes/archive/2026-10-25-configure-claude-combos-antigravity-pools/`.

## 2. Ultra Accounts Quota Isolation & RateLimitProtection (Tasks 2.1 & 2.2)
- Enabled `rateLimitProtection: true` on `0532bad4-2486-4286-8f06-510e9c678620` (`vinhvumobile@gmail.com`) and `338764b8-1cd7-4946-b789-ee5dad4c5073` (`vinhghtk1908@gmail.com`) via `POST /api/rate-limits`. Verified all 3 Ultra accounts report `rateLimitProtection: true, enabled: true`.
- Updated `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) from `strategy: "context-relay"` (15 steps) to `strategy: "auto"`, `context_cache_protection: false`, `targetTimeoutMs: 25000`, and exactly 11 `g1-pro-tier` steps (excluding the 3 Ultra accounts and `free-tier` `ce95e1cb`).
- Verified live `call_logs` after `16:15Z`: 26 consecutive Flash requests were routed across Pro accounts (`cdac4585`, `d5c3465f`, `20369f65`, `d902fb26`), with **0 requests** routed to Ultra accounts (`62af823b`, `0532bad4`, `338764b8`).

## 3. Tier-Matched Timeouts on Claude & Nexus Combos (Task 2.3)
- `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`): `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000` (15 `agy/claude-opus-4-6-thinking` steps).
- `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`): `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`, `maxRetries: 1` (15 `agy/claude-sonnet-4-6` steps).
- `kimi-k3.1-pro` (`c9a838ef-a011-4a21-8d73-c577cfa9a628`): `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`, `maxRetries: 1`.
- `deepseek-v4.1-flash` (`c028902e-f32f-41f3-8098-5134a0e90215`): `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`, `maxRetries: 1`.

## 4. Custom Model Cleanup, Dead Provider Disabling & SQLite Pruning (Tasks 3.1 & 3.2)
- Deleted custom `claude-opus-5-5-high` and `claude-sonnet-5-5-high` from `provider_models` under `agy` and `antigravity`, and deleted alias `test-opus-55-high` from `/api/models/alias`.
- Disabled expired connection `6fb701a5-d060-422c-bc34-0cca543d0eda` (`ollama-cloud`) while leaving `phanmemvip` and `muse-code` active for their dedicated combos, and updated `auto/*` combos to restrict `config.candidatePool` to `["agy", "codex", "github"]`.
- Deleted all 7 stale pre-subscription regex memories from SQLite `memories` and cleared 2 leaked `health-check` points from Qdrant `omniroute_memory` (`points_count: 0`), deleted 1,555 expired rows from `semantic_cache`, and executed `PRAGMA wal_checkpoint(TRUNCATE)`.

## 5. Paid Voyage AI Hybrid Memory Optimization & Entrypoint Verification (Tasks 4.1, 4.2 & 4.3)
- Updated `/Users/androidteam/Omniroute/.env` (`OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_TIMEOUT_MS=3000`, `OMNIROUTE_SEMANTIC_CACHE_TTL_MS=18000000`, stripped comment on `QUOTA_STORE_DRIVER=sqlite`).
- Updated `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` to wire `globalThis.__omnirouteQdrantEmbedCache` (LRU `Map`, capacity `1,000`, TTL `300s`) into `embedText`, short-circuit `upsertSemanticMemoryPoint` on `apiKeyId === "health-check"`, join FTS5 tokens (`length > 2`) with `" OR "`, and verified all runtime patch markers pass fail-closed.
- Recreated `omniroute-base` container. Configured `PUT /api/settings/memory` (`skillsEnabled: false`, `strategy: "hybrid"`, `vectorStore: "qdrant"`, `embeddingProviderModel: "voyage-ai/voyage-code-3"`, `rerankProviderModel: "voyage-ai/rerank-2.5"`).
- Seeded clean architecture memory (`architecture:omniroute_ultra_isolation`). Verified `GET /api/memory/engine-status` reports `needsReindex: 0` and Qdrant reports `points_count: 1`.
- Verified `POST /api/memory/retrieve-preview` retrieves the seeded memory via Qdrant Cosine + FTS5 BM25 RRF + Voyage reranking (`tier: "qdrant"`, `itemsCount: 1`, `rerankApplied: true`).
