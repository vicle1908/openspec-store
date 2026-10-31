# Design: Post-Matrix OmniRoute Runtime Remediation and Spec Reconciliation

## Context

Following the evaluation and archival of `2026-10-31-document-omniroute-runtime-customization-matrix` (`50777db7`), five concrete findings (`W1`–`W3`, `S1`–`S2`) were remediated and verified against the live OmniRoute `v3.8.52` deployment (`edab7c3a59bf7d6f040d581dbda3a46adbee0d57`, image `sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65`). Per `openspec-runtime-governance` (`Archive immutability verification and forward-remediated range auditing`), `openspec/changes/archive/2026-10-31-document-omniroute-runtime-customization-matrix/` is preserved byte-for-byte at `50777db7` while this active change records the remediated runtime state and delta specs.

## Decisions

### 1. Fail-Closed 46-Marker Entrypoint Verification and Dual-Chunk Coverage (`W1`)

Source: `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh:1-327`.

- **Remove Missing-File Skip**: Deleted the `if (marker.fileMatch && !targetFiles.some(...)) continue;` guard so that if any target chunk is missing or renamed in a future build, the entrypoint fails closed with `[COMPAT_ERROR] Required marker <name> (<fileMatch>) missing! Fail closed.` and exits `1`.
- **Assert Non-Chunk and Previously Unasserted Rules**:
  - Added `requiredNonChunkMarkers` (`lines 241-251`) asserting `peer_stamp_muse_rewrite` (`/app/peer-stamp.mjs`), `next_resolve_routes_accept_encoding` (`resolve-routes.js`), and `next_router_server_sse_compress` (`router-server.js`).
  - Added `99834.js`-scoped rules (`lines 199-208`) for `embedText` (`async function o(a,b)`) and `upsertSemanticMemoryPoint` (`async function p(a)`) so both compiled Qdrant chunks (`54843.js` and `99834.js`) receive identical 5-minute embedding cache and `"health-check"` short-circuit patches.
  - Expanded `requiredMarkers` (`lines 253-299`) to **43 chunk markers across 11 chunk files** (`37174.js`, `7449.js`, `32946.js`, `55661.js`, `45121.js`, `62537.js`, `86370.js`, `72053.js`, `95293.js`, `88137.js`, `14461.js`, `54843.js`, `99834.js`, `72089.js`, `87878.js`, `13275.js` — 16 total chunk files covered across `replacements` and `requiredMarkers`).
- **Rebind Single-File Mount Inode via Recreation**: Recreated `omniroute-base` (`docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base`) so `/app/container-entrypoint-compat.sh` binds to the current host inode (`327` lines) and `sh /app/container-entrypoint-compat.sh --patch-only` returns `already_ok` (`exit 0`).

### 2. Host Ollama Metal Service Restoration and `sp:<sha256_16>` System-Policy Cache Partitioning (`W2`)

Source: `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh:116-130` (`95293.js`).

- **Host Ollama Service**: Stopped stale `/Applications/Ollama.app` processes (`PID 3949, 4073`) whose bundle lacked `llama-server` and started Homebrew `ollama 0.40.13` (`brew services start ollama` / `sh.brew.ollama`). `POST /api/settings/cache-config/test-embedding` (`ollama-local/nomic-embed-text`, `768d`) now succeeds (`ok: true`, `137 ms`).
- **System-Policy Partition Hashing (`sp:<sha256_16>`)**:
  - Updated `R12` (`module 396505`, `isCompleteTextProjection`) to remove `c && ["system","developer"].includes(String(a.role))` so OpenAI-format requests containing `system` or `developer` messages remain eligible for Layer-2 vector caching while `normalizeConversationForEmbedding` (`excludeSystemPrompt: true`) continues to embed only user/assistant/tool turns.
  - Updated `R14` (`lookup`) and `R15` (`store`) in `SemanticCacheManager` (`95293.js`) to compute `_sp` across `a.body?.system`, `a.body?.instructions`, `a.body?.systemInstruction`, and `messages[]` `system`/`developer` content, appending `sp:<sha256(JSON.stringify(_sp)).slice(0,16)>` to `cacheKey` (`_ck`). Requests with identical system policies hit Layer-2 (`X-OmniRoute-Cache: HIT`, `similarity: 1.0000`), while requests with different system policies miss (`X-OmniRoute-Cache: MISS`).

### 3. Memory `expires_at` SQL Filtering on Vector and Hybrid Retrieval (`W3`)

Source: `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh:219-220` (`72089.js`, `87878.js`, `13275.js`, `54843.js`).

- Appended `AND (expires_at IS NULL OR datetime(expires_at) > datetime('now'))` to `SELECT * FROM memories WHERE id IN (${c})` in `fetchMemoriesByIds` (`72089.js`, `87878.js`) and `AND (m.expires_at IS NULL OR datetime(m.expires_at) > datetime('now'))` to `JOIN memories m` in `VectorStoreImpl.searchVector` and `searchHybrid` (`13275.js`, `54843.js`), guarded by markers `fetch_memories_expires_72089`, `fetch_memories_expires_87878`, `vec_memories_expires_13275`, and `vec_memories_expires_54843`.

### 4. Combo Pool Hygiene, Main-Spec Reconciliation, and Archive Immutability (`S1`, `S2`)

- **Combo Pool Hygiene (`S2`)**: Pruned banned `agy` Pro connection `47f334b1-b801-41f6-a709-4ebabb7a86d6` (`vicgnome19091@gmail.com`) from `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) via `PUT /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388`, leaving exactly the 11 active `g1-pro-tier` steps (`hasBanned: false`).
- **Spec & Wiki Reconciliation (`S1`)**: Reconciled the 7 intra-spec drifts in `openspec/specs/omniroute-compression-and-routing/spec.md` and updated `/Users/androidteam/Developer/wiki/entities/omniroute.md` (`b0a0475`), while restoring `openspec/changes/archive/2026-10-31-document-omniroute-runtime-customization-matrix/` to its `50777db7` commit snapshot (`git diff 50777db7 -- openspec/changes/archive/` is empty).
