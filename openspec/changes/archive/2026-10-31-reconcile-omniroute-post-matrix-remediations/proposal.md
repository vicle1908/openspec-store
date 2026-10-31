# Proposal: Reconcile OmniRoute Post-Matrix Runtime Remediations and Spec Drift

## Why

During the evaluation of `document-omniroute-runtime-customization-matrix` (archived at `50777db7`), live verification exposed three runtime/compatibility defects (`W1`–`W3`) and two configuration/documentation drifts (`S1`–`S2`):
1. **`W1` — Fail-Open Marker Skip, Unasserted Patch Groups, and Detached Single-File Mount Inode**: `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` skipped `requiredMarkers` entries when a `fileMatch` chunk was absent (`continue;`), left 18 rules (`N1–N3`, `R1–R8`, `R21`, and dual-compiled chunks `87878.js`/`99834.js`) without marker assertions, and had a detached single-file mount inode inside the running container after atomic host edits.
2. **`W2` — Stale Host Ollama Process (`HTTP 500`) and System-Policy Semantic Cache Collision**: Stale `/Applications/Ollama.app` processes lacked `llama-server` (`HTTP 500`), causing Layer-2 semantic cache to fail open on every lookup/store, while `OMNIROUTE_SEMANTIC_CACHE_EXCLUDE_SYSTEM=true` caused `isCompleteTextProjection` (`R12`) to reject OpenAI requests containing `role: "system"` and allowed top-level `body.system` / `body.instructions` to collide across different system policies (`R14`/`R15`).
3. **`W3` — Memory `expires_at` Filter Omission on Vector & Hybrid Paths**: `fetchMemoriesByIds` (`72089.js`, `87878.js`) and `VectorStoreImpl.searchVector` / `searchHybrid` (`13275.js`, `54843.js`) did not filter `expires_at`, allowing expired records to return on vector and hybrid queries.
4. **`S1` & `S2` — Main-Spec Intra-Spec Drift, Wiki Drift, and Banned `agy` Pro Step in `gemini-3.8-flash-high`**: `gemini-3.8-flash-high` retained banned Pro connection `47f334b1-b801-41f6-a709-4ebabb7a86d6` (`12` steps instead of `11`), while `openspec/specs/omniroute-compression-and-routing/spec.md` and `/Users/androidteam/Developer/wiki/entities/omniroute.md` carried pre-remediation values.

## What Changes

- Harden `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`1-327` lines) to remove the missing-file marker skip, add `requiredNonChunkMarkers` (`peer-stamp.mjs`, `resolve-routes.js`, `router-server.js`), expand `requiredMarkers` to 43 chunk markers across 11 chunk files (46 total fail-closed assertions including `87878.js` and `99834.js`), and recreate `omniroute-base` (`--force-recreate`) to rebind the single-file host mount.
- Stop stale `/Applications/Ollama.app` processes and run Homebrew `ollama 0.40.13` (`sh.brew.ollama`) so `ollama-local/nomic-embed-text` (`768d`) serves Layer-2 embeddings on Apple Metal, while updating `R12`, `R14`, and `R15` to allow `system`/`developer` roles in `isCompleteTextProjection` and partition `cacheKey` by `sp:<sha256(system_instructions).slice(0,16)>`.
- Patch `fetchMemoriesByIds` (`72089.js`, `87878.js`) and `VectorStoreImpl.searchVector` / `searchHybrid` (`13275.js`, `54843.js`) in `container-entrypoint-compat.sh` to enforce `AND (expires_at IS NULL OR datetime(expires_at) > datetime('now'))`.
- Prune banned `agy` Pro connection `47f334b1-b801-41f6-a709-4ebabb7a86d6` from `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) so it routes across the 11 active `g1-pro-tier` connections.
- Reconcile main specs (`omniroute-compression-and-routing`, `omniroute-runtime-customization`) and `/Users/androidteam/Developer/wiki/entities/omniroute.md` while preserving `openspec/changes/archive/2026-10-31-document-omniroute-runtime-customization-matrix/` immutably at its `50777db7` archive snapshot.

## Capabilities

### Modified Capabilities

- `omniroute-runtime-customization`: Codify the 46 fail-closed marker assertions (3 non-chunk files + 43 chunk markers across 11 chunk files), removal of the missing-chunk skip, single-file mount inode rebinding on `--force-recreate`, and `expires_at` filtering across vector/hybrid memory retrieval.
- `omniroute-compression-and-routing`: Codify `sp:<sha256_16>` system-policy semantic-cache partitioning, Homebrew `ollama 0.40.13` `nomic-embed-text` readiness, 11-active-Pro-account `gemini-3.8-flash-high` pool hygiene, and reconciled intra-spec requirements.

## Impact

- Planning & spec owner: `/Users/androidteam/Developer/platform/openspec-store`.
- Runtime surface: `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`, `omniroute` container, Host Ollama service (`sh.brew.ollama`), and `/Users/androidteam/Developer/wiki/entities/omniroute.md`.
