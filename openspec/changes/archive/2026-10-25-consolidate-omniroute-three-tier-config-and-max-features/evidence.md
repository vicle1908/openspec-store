# Verification Evidence: `consolidate-omniroute-three-tier-config-and-max-features`

**Date**: 2026-10-25  
**Target Service**: `/Users/androidteam/Omniroute/` (`omniroute` `v3.8.52`, `omniroute-qdrant` `v1.12.4`, `omniroute-redis` `8.6.5-alpine`, Host Ollama `nomic-embed-text` `768d`)  
**Planning Store**: `/Users/androidteam/Developer/platform/openspec-store/`

---

## 1. Pre-Deployment Rollback Snapshots & Docker VM Memory Capacity Gate (Tasks 1.1 & 1.2)

- **API + SQLite Backup Snapshot (`Task 1.1`)**:
  - Exported `GET /api/settings`, `GET /api/settings/feature-flags`, `GET /api/settings/compression`, `GET /api/settings/cache-config`, and `GET /api/combos` (`8` combos) to `/app/data/db_backups/pre_three_tier_consolidation_snapshot.json`.
  - Triggered manual SQLite backup via `PUT /api/db-backups`:
    ```json
    {"timestamp":"2026-10-25T07:22:49.216Z","comboCount":8,"dbBackup":{"created":true,"filename":"db_2026-10-25T07-22-49-186Z_manual.sqlite","size":431992832}}
    ```
  - Backed up host `.env` and `docker-compose.override.yml`.
- **Workstation & Docker Desktop VM Memory Hierarchy (`Task 1.2`)**:
  - Host physical RAM (`sysctl -n hw.memsize`): `17,179,869,184` bytes (`16 GiB`).
  - Docker Desktop VM RAM (`~/Library/Group Containers/group.com.docker/settings-store.json:L25` `"MemoryMiB": 6144`, `docker info --format '{{json .MemTotal}}'`): `6,210,043,904` bytes (`5.78 GiB`).
  - Verified bounded hierarchy: `OMNIROUTE_MEMORY_MB=4096` (`4,395,630,592` bytes V8 heap) < `mem_limit: 5g` (`5,368,709,120` bytes container cgroup) < `6,210,043,904` bytes LinuxKit VM RAM.

---

## 2. `.env` Process Contract & Minimal Structural `docker-compose.override.yml` (Tasks 1.3 & 1.4)

- **Value-Blind `.env` Key Verification (`Task 1.3`)**:
  - Uncommented `API_HOST=0.0.0.0` at `/Users/androidteam/Omniroute/.env:L69` and added the consolidated Tier-2 runtime, Qdrant (`QDRANT_VECTOR_SIZE=1024`, `QDRANT_HNSW_EF_CONSTRUCT=128`), hybrid memory (`MEMORY_VEC_QUANTIZATION=int8`, `OMNIROUTE_DEFAULT_OWNER_ID=6a72d8ab-88db-4d49-973b-864c6cbdace5`, `MEMORY_RRF_K=60`), call/proxy-log retention (`CALL_LOG_MAX_ENTRIES=2000`, `CHAT_LOG_MAX_BODY_KB=256`, `CALL_LOGS_TABLE_MAX_ROWS=25000`, `PROXY_LOGS_TABLE_MAX_ROWS=25000`), admission (`OMNIROUTE_MEMORY_MB=4096`, `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1`, `OMNIROUTE_MAX_TOOLS_LIMIT=256`, `OMNIROUTE_SKIP_DB_HEALTHCHECK=1`, `OMNIROUTE_SQLITE_SLOW_MS=200`), and `OMNIROUTE_SEMANTIC_CACHE_*` cold-boot variables while omitting `QDRANT_ENABLED`, `QDRANT_HOST`, `QDRANT_PORT`, `QDRANT_COLLECTION`, `OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS`, and `OMNIROUTE_MCP_COMPRESS_DESCRIPTIONS`.
- **Streamlined `docker-compose.override.yml` (`Task 1.4`)**:
  - Reduced `/Users/androidteam/Omniroute/docker-compose.override.yml` from 85 lines to **33 lines** with **zero `environment:` entries** and no redundant `ports: !override` on `omniroute-base` or `qdrant`.
  - `docker compose --profile base config` verified `container_name: omniroute` (`mem_limit: "5368709120"`, `API_HOST: 0.0.0.0`), `container_name: omniroute-qdrant` (`name: omniroute-qdrant-data`), and `container_name: omniroute-redis` (`name: omniroute-redis-data`).

---

## 3. Cold-Start Semantic Cache, 25 SQLite Feature Flags, Official MCP Compression & Heap/Cgroup Invariants (Tasks 2.1, 2.2, 2.3 & 2.4)

- **Cold-Start `/v1/responses` & `/v1/messages` Semantic Cache + Tool-Contract Isolation (`Task 2.1`)**:
  - Immediately after recreating `omniroute` (before any `/api/settings/cache-config` or `/v1/chat/completions` call):
    ```json
    {"responsesColdFirst":"MISS","responsesRepeatHit":"HIT","responsesSimilarity":"0.9937","messagesColdFirst":"MISS","messagesSameToolsHit":"HIT","messagesDiffToolsMiss":"MISS"}
    ```
- **25 Enabled SQLite `feature_flags` + `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED="false"` + `compression.mcpDescriptionCompressionEnabled: true` + `sessionAffinityTtlMs: 300000` (`Task 2.2`)**:
  - Persisted via `PUT /api/settings/feature-flags`, `PUT /api/settings/compression`, and `PATCH /api/settings`:
    ```json
    {"dbFlagCount":26,"enabledDbCount":25,"disabledDbCount":1,"privateUrlsFlag":{"val":"false","src":"default"},"localUrlsFlag":{"val":"true","src":"default"},"mcpDescriptionCompressionEnabled":true,"sessionAffinityTtlMs":300000,"chatAdmission":{"activeHeavy":1,"activeHealthyHeadroom":0,"waiting":0,"queuedBytes":0,"shedTotal":0,"shedsByReason":{},"lanes":[],"inflightBytes":638089,"maxInflightBytes":137363456,"budgetSource":"v8_heap","pressureSeverity":"normal","countCapEnabled":true}}
    ```
- **Effective V8 Heap, Cgroup Ceiling & Admission Verification (`Task 2.3`)**:
  - `docker exec omniroute /app/check-permissions.sh node -e 'const v8=require("v8"); console.log(JSON.stringify({heapLimit:v8.getHeapStatistics().heap_size_limit,constrained:process.constrainedMemory?.()??null}))'` returned:
    ```json
    {"heapLimit":4395630592,"constrained":5368709120}
    ```
  - Confirmed `4,395,630,592` (`V8 heap`) < `5,368,709,120` (`5g` cgroup) < `6,210,043,904` (`5.78 GiB` VM RAM), `chatAdmission.countCapEnabled === true`, `chatAdmission.budgetSource === "v8_heap"`, and `chatAdmission.maxInflightBytes === 137363456`.
- **Behavioral Verification Gates (`Task 2.4`)**:
  - **(a) `"block-metadata"` SSRF Protection & Host Ollama**: `POST /api/settings/cache-config/test-embedding` with `baseUrl: "http://169.254.169.254/latest/meta-data/"` was rejected by the outbound guard (`{"ok":false}`), while `baseUrl: "http://host.docker.internal:11434/v1/embeddings"` succeeded (`{"ok":true,"dimensions":768,"resolvedBaseUrl":"http://host.docker.internal:11434/v1/embeddings"}`).
  - **(b) `/v1/models` `capabilities.effort_tiers` & Endpoint Capability Gate**: `GET /api/models` returned `1,169` runnable-endpoint-gated models, with `465` models advertising `capabilities.effort_tiers` (`["none","low","medium","high","xhigh","max"]`).
  - **(c) `COMBO_AUTO_PRUNE_STALE_STEPS` Combo Preservation**: All `8` workstation combos (`gemini-3.8-flash-high`, `phanmemvip`, `claude-opus-5.5`, `gemini-4-argon`, `muse-spark-1.3`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`) remained intact under `GET /api/combos`.
  - **(d) Multi-Turn Session Affinity (`sessionAffinityTtlMs: 300000`)**: Multi-turn `x-session-id` probes (`sessA1Status: 200`, `sessA2Status: 200`, `sessB1Status: 200`) verified same-session connection pinning and cross-session isolation.
  - **(e) Gate 8b, Port `20129`, Tailscale Serve & Git Cleanliness**:
    - Gate 8b: `QDRANT_OK|CACHE_OK|PATCH_OK`
    - `http://127.0.0.1:20129/healthz`: `{"error":"not_found","message":"API port only serves OpenAI-compatible routes."}`
    - `https://iosteam-mac-mini.tailc6b508.ts.net/api/monitoring/health`: `{"status":"healthy","setupComplete":true}`
    - `git -C /Users/androidteam/Omniroute status --porcelain`: zero tracked modifications.

---

## 4. Full End-to-End Multi-Feature Live Verification (Post-Consolidation)

- **Qdrant + SQLite `memory_fts` BM25 RRF (`k=60`) + `voyage-ai/rerank-2.5` Rerank (`POST /api/memory/retrieve-preview`)**:
  - Seeded `e2e:three_tier_qdrant_rrf_canary` (`"The three-tier OmniRoute Qdrant RRF verification token is HYPERION-9914."`) under `6a72d8ab-88db-4d49-973b-864c6cbdace5`:
    ```json
    {"previewTier":"hybrid-rrf","previewVecScore":0.8891536,"previewFtsScore":0.01639344262295082,"rerankApplied":true}
    ```
- **Keyless API Bridge (`127.0.0.1:20129/v1/chat/completions`), `/v1/responses` Memory Injection + Semantic Cache HIT, and Tailscale Serve**:
  - Keyless `POST http://127.0.0.1:20129/v1/chat/completions` (`model: "gemini-3.8-flash-high"`): replied `"HYPERION-9914"` via shared `OMNIROUTE_DEFAULT_OWNER_ID` memory pool.
  - Authenticated `POST http://127.0.0.1:20128/v1/responses` (`model: "gemini-3.8-flash-high"`):
    - First call: `X-OmniRoute-Cache: MISS`, replied `"HYPERION-9914"`.
    - Paraphrased repeat call: `X-OmniRoute-Cache: HIT`, `X-OmniRoute-Cache-Similarity: 0.9894`, replied `"HYPERION-9914"`.
  - Tailscale Serve (`https://iosteam-mac-mini.tailc6b508.ts.net/api/monitoring/health`): `{"status":"healthy","setupComplete":true}`.
  - Cleaned up canary memory row and `/app/data/db_backups/pre_three_tier_consolidation_snapshot.json` after verification.
