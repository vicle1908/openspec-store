# Tasks

## 1. Harden Entrypoint Compatibility Script and Rebind Single-File Mount (`W1`, `W3`)

- [x] 1.1 Remove the missing-chunk `continue;` skip in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`, add `requiredNonChunkMarkers` (`peer-stamp.mjs`, `resolve-routes.js`, `router-server.js`), add dual-chunk `99834.js` Qdrant cache/health-check rules, and expand `requiredMarkers` to 43 chunk markers across 11 chunk files (46 total fail-closed assertions).
- [x] 1.2 Add runtime SQL replacement rules in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` enforcing `AND (expires_at IS NULL OR datetime(expires_at) > datetime('now'))` in `fetchMemoriesByIds` (`72089.js`, `87878.js`) and `VectorStoreImpl.searchVector` / `searchHybrid` (`13275.js`, `54843.js`), and verify expired records return 0 hits.
- [x] 1.3 Recreate `omniroute-base` (`docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base`) to rebind the single-file host mount inode and verify `docker exec omniroute sh /app/container-entrypoint-compat.sh --patch-only` outputs `already_ok` with exit code `0`.

## 2. Remediate Host Ollama Service, System-Policy Cache Isolation, and Combo Pool Hygiene (`W2`, `S2`)

- [x] 2.1 Terminate stale `/Applications/Ollama.app` processes, start Homebrew `ollama 0.40.13` (`brew services start ollama`), and verify `POST /api/settings/cache-config/test-embedding` (`ollama-local/nomic-embed-text`, `768d`) returns `ok: true`.
- [x] 2.2 Update `R12`, `R14`, and `R15` in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`95293.js`) to permit `system`/`developer` roles in `isCompleteTextProjection` and hash `sp:<sha256(system_instructions).slice(0,16)>` into `cacheKey` (`_ck`), then verify live `MISS` -> `HIT` (`similarity: 1.0000`) on matching system policy and `MISS` on differing system policy.
- [x] 2.3 Prune banned `agy` Pro connection `47f334b1-b801-41f6-a709-4ebabb7a86d6` from `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) via `PUT /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` and verify `stepCount === 11` (`hasBanned: false`).

## 3. Reconcile Main Specs, Wiki, and Archive Immutability (`S1`)

- [x] 3.1 Reconcile the 7 intra-spec drifts in `/Users/androidteam/Developer/platform/openspec-store/openspec/specs/omniroute-compression-and-routing/spec.md` and update `/Users/androidteam/Developer/wiki/entities/omniroute.md` (`b0a0475`) to reflect the 46 fail-closed markers, `sp:` cache partitioning, `expires_at` filters, and 11-step `gemini-3.8-flash-high` Pro pool.
- [x] 3.2 Restore `openspec/changes/archive/2026-10-31-document-omniroute-runtime-customization-matrix/evidence.md` to its exact `50777db7` archive snapshot (`git diff 50777db7 -- openspec/changes/archive/` empty) and validate `reconcile-omniroute-post-matrix-remediations` with `openspec validate --strict --store openspec-store` and `validate-archive-readiness.py --strict`.
