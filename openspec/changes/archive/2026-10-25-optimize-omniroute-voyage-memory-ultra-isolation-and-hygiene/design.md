# Design: Optimize Voyage AI Hybrid Memory, Ultra Quota Isolation, Combo Timeouts & Runtime Hygiene

## Context

Following the Voyage AI subscription upgrade at `2026-10-25T10:18:01Z` (`6,764` consecutive HTTP `200` responses, `0` HTTP `429` errors) and the 3-Ultra-account expansion on `gemini-4-argon*`, a deep architectural and code review of OmniRoute (`v3.8.52`) identified four concrete optimization targets across the request pipeline:

1. **Voyage AI + Qdrant Hybrid Memory Pipeline (`chunks/54843.js` modules `917397` & `541915`)**:
   - In `chunks/54843.js` (module `917397`), `embedText` (`async function n(a,b)`) invokes `createEmbeddingResponse({ model: c, input: b })` directly without an LRU cache, while Next.js duplicates module-local `Map` instances across route bundles. Using a process-wide `globalThis.__omnirouteQdrantEmbedCache` (`Map`, max `1,000` entries, `300,000 ms` TTL) inside `n(a,b)` caches 1024-dimension `voyage-ai/voyage-code-3` vectors across all routes in `<0.1 ms`.
   - In `chunks/54843.js` (module `917397`), `upsertSemanticMemoryPoint` (`async function o(a)`) is called by `verifyExtractionPipeline("health-check")` (`GET /api/memory/health`) without `await` and finishes after `deleteMemory()`, leaking `apiKeyId: "health-check"` points into Qdrant. Short-circuiting `if("health-check"===a.apiKeyId)return{ok:!0,latencyMs:0};` at the start of `o(a)` prevents health-check point leaks.
   - In `chunks/54843.js` (module `541915`), `sanitizeFts5Query` (`function e(a)`) joins up to 32 prompt words with `" "` (`c.map(a=>`"${a}"`).join(" ")`), which SQLite FTS5 evaluates as a 32-term boolean `AND`. Replacing `.map(a=>`"${a}"`).join(" ")` with `.filter(a=>a.length>2).map(a=>`"${a}"`).join(" OR ")` enables boolean `OR` BM25 keyword matching.
   - Deleting all 7 pre-`10:18Z` regex-scraped fragments from SQLite `memories` (`DELETE /api/memory/{id}`) and seeding a clean architecture memory via `POST /api/memory` (`store.ts:createMemory`) natively populates both `vec_memories` and Qdrant `omniroute_memory` (`needsReindex: 0`).
2. **Ultra Account Quota Isolation vs. `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`)**:
   - The 3 `g1-ultra-tier` `agy` accounts (`62af823b-f3d7-4e6b-87a9-98069167d4f6` / `vicgnome19094@gmail.com`, `0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`, `338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com`) are the only accounts entitled to `gemini-4-argon*`.
   - Switching `gemini-3.8-flash-high` from `strategy: "context-relay"` (`15` steps) to `strategy: "auto"`, `context_cache_protection: false`, and **11 steps** (the 11 `g1-pro-tier` accounts at 67–100% quota) reserves 100% of the 3 Ultra accounts' `gemini_weekly` quota for `gemini-4-argon*`.
   - Enabling `rateLimitProtection: true` on `0532bad4` and `338764b8` via `POST /api/rate-limits` (`{"connectionId": "<id>", "enabled": true}`) updates both in-memory `rateLimitManager` state and SQLite (`src/app/api/rate-limits/route.ts:95-103`).
3. **Combo Timeout Alignment & `configure-claude-combos-antigravity-pools` Closure**:
   - Setting `targetTimeoutMs: 180000, predictiveTtftMs: 60000` on `claude-opus-5.5` (`15` `agy/claude-opus-4-6-thinking` steps) and `targetTimeoutMs: 120000, predictiveTtftMs: 45000, maxRetries: 1` on `claude-sonnet-5.5` (`15` `agy/claude-sonnet-4-6` steps), `kimi-k3.1-pro`, and `deepseek-v4.1-flash` prevents premature 25s aborts.
4. **Provider Catalog, Auto-Combo Candidate Pools, Semantic Cache Bridge & Entrypoint/SQLite Hygiene**:
   - Removing custom `claude-opus-5-5-high` and `claude-sonnet-5-5-high` via `DELETE /api/provider-models?provider=agy&model=...` (and `provider=antigravity`) plus `DELETE /api/models/alias?alias=test-opus-55-high` stops `auto/*` combos from hitting non-existent 5.5 endpoints.
   - Setting `isActive: false` only on expired `6fb701a5` (`ollama-cloud`) while restricting `auto/*` combos' `config.candidatePool` to `["agy", "codex", "github"]` protects `auto/*` combos without breaking dedicated callers of `phanmemvip` (`f3aaa87c`) or `muse-spark-1.3` step `[1]` (`51795cf9`).

## Architecture & Partitioning Design

```
+---------------------------------------------------------------------------------------------------+
|                        Antigravity (`agy`) Quota & Tier Isolation Architecture                    |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  1. Ultra Pool (3 `g1-ultra-tier` accounts, POST /api/rate-limits enabled=true)                   |
|     - `62af823b` (vicgnome19094), `0532bad4` (vinhvumobile), `338764b8` (vinhghtk1908)            |
|     - Dedicated 100% of Gemini quota to:                                                          |
|       * `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`    |
|         (`strategy: "auto"`, `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`)                |
|                                                                                                   |
|  2. Pro Pool (11 `g1-pro-tier` accounts, rateLimitProtection=true, 67-100% quota)                 |
|     - Dedicated to:                                                                               |
|       * `gemini-3.8-flash-high` (`strategy: "auto"`, `context_cache_protection: false`,           |
|         `targetTimeoutMs: 25000`, `predictiveTtftMs: 25000`, 11 steps)                            |
|                                                                                                   |
|  3. Claude Pool (All 15 active `agy` accounts — independent Claude quota bucket)                  |
|     - `claude-opus-5.5` -> 15 `agy/claude-opus-4-6-thinking` (`180000 / 60000`)                   |
|     - `claude-sonnet-5.5` -> 15 `agy/claude-sonnet-4-6` (`120000 / 45000`)                        |
+---------------------------------------------------------------------------------------------------+
```
