# Design

## Context

See `proposal.md` — Why for problem statement and upstream `v3.8.52` release overview, and `specs/bifrost-gateway/spec.md` + `specs/omniroute-agent-cli-routing/spec.md` for normative requirements.

OmniRoute runs as a Docker Compose service (`omniroute-base`, container `omniroute`, image `diegosouzapw/omniroute:latest`) from `/Users/androidteam/Omniroute` with an untracked `docker-compose.override.yml` mounting the Docker named volume `omniroute-data` (`omniroute_omniroute-data`) at `/app/data` and `./scripts/container-entrypoint-compat.sh:/app/container-entrypoint-compat.sh:ro` as the container entrypoint. Upgrades are coordinated via `/usr/bin/lockf` on FD `9` (`~/.omniroute/update.lock`) shared between `~/Omniroute/scripts/update.sh` and `~/Developer/scripts/omniroute-watchdog.sh` (mirrored at `platform/openspec-store/scripts/omniroute-watchdog.sh`).

Currently:
- Running container `omniroute` (`597e69347118`) is on `v3.8.51` (`sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218`), SQLite migration `196`, with compacted `/app/data/storage.sqlite` (`1.07 GB`, `api_keys = 1`, `provider_connections = 32`, `combos = 8`, `0` `opencode`/`oc` rows).
- Upstream `diegosouzapw/omniroute:latest` and `diegosouzapw/omniroute:3.8.52` resolve to multi-arch index digest `sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c` (`linux/arm64` manifest `sha256:fb7f91836fd95f382a5a04af740d859e2e9731804b5c0ba43f5d2e7f9ad64794`).
- Local `/Users/androidteam/Omniroute` git `main` is at `e62b4b71c5cf1b99d022bc48cb0f30da22f982c0`; upstream tag `v3.8.52` is at `ad6f33f66bda34eba98645d3bfdabbde294bc843` and `origin/main` is at `fa6e0f14fb41f031c4c0e9901a4bc3a042eed175` (1 commit ahead of `v3.8.52`, resyncing `electron/package-lock.json`).

## Goals / Non-Goals

**Goals:**
- Upgrade the running `omniroute` container from `v3.8.51` to `v3.8.52` (`sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c`) through all 10 fail-closed gates of `~/Omniroute/scripts/update.sh 3.8.52` while holding the `/usr/bin/lockf` kernel descriptor lock on `~/.omniroute/update.lock`.
- Fast-forward `/Users/androidteam/Omniroute` git `main` to `origin/main` (`fa6e0f14fb41f031c4c0e9901a4bc3a042eed175`) so the host Bun CLI bridge (`~/.local/bin/omniroute`) and the 45 local skills in `/Users/androidteam/Omniroute/skills/` match `v3.8.52` without dirtying any git-tracked file.
- Adapt `scripts/container-entrypoint-compat.sh`, `scripts/ensure-muse-wire-compat.sh`, and `scripts/update.sh` (Gates 8 and 9) to `v3.8.52`'s SSE keepalive constant, `/v1/muse-code/models` catalog authentication enforcement, and mandatory pre-migration `VACUUM INTO` backup file.

**Non-Goals:**
- Altering Docker Compose profiles, port bindings, Redis container (`redis:8.6.5-alpine`), or `docker-compose.override.yml` startup deferral flags (`DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED=true`, `OMNIROUTE_SKIP_DB_HEALTHCHECK=1`, `NODE_OPTIONS=--max-old-space-size=4096`).
- Disabling or bypassing `migrationRunner.ts`'s pre-migration safety snapshot during migration execution (cleanup occurs only in Gate 9 after migrations and post-deploy integrity checks complete).

## Decisions

### 1. Pre-Upgrade Adaptation of `container-entrypoint-compat.sh` and `ensure-muse-wire-compat.sh`
- **Choice**: Reuse the existing compose-mounted `/app/container-entrypoint-compat.sh` pattern and `scripts/ensure-muse-wire-compat.sh` (Gate 4b) for both `v3.8.52` Muse Code compatibility adjustments:
  1. **Responses SSE Keepalive Normalization**: Widen the Next.js chunk replacement regex from `/response:\{id:null,status:"in_progress"\}/g` to `/response:\{id:(?:null|"resp_keepalive_omniroute"|[A-Za-z0-9_$]+\.[A-Za-z0-9_$]+),status:"in_progress"\}/g` so `v3.8.51` (`id:null`), unminified `v3.8.52` (`id:"resp_keepalive_omniroute"`, from `open-sse/utils/responsesSequence.ts:37`), and webpack-minified `v3.8.52` (`id:d.O1` in `/app/.build/next/server/chunks/20286.js`) are all rewritten to `response:{id:"resp_keepalive",object:"response",status:"in_progress",output:[],error:null}`.
  2. **Combo-Backed `/v1/muse-code/models` & `/muse-code/models` Catalog Response**: In `v3.8.52`, `src/app/api/v1/muse-code/models/route.ts:95-112` replaced the static `CATALOG_PAYLOAD` response with `getProviderModels(request, { params: Promise.resolve({ provider: "muse-code" }) })` (`src/app/api/v1/providers/[provider]/models/route.ts:106-110`), which filters `getUnifiedModelsResponse` by `acceptedOwners = new Set(["muse-code", "mc"])` and enforces `requireAuthForModels`. Because this workstation has `0` `muse-code` rows in `provider_connections` and routes `muse-spark-1.3` through an OmniRoute combo (`owned_by: "combo"`), upstream's `v3.8.52` route returns HTTP `401` unauthenticated and `{"object":"list","data":[]}` (empty `data`) even when authenticated! In `/app/peer-stamp.mjs` (`wrapRequestListenerWithPeerStamp`), intercept `GET`/`HEAD`/`OPTIONS` requests to `/muse-code/models` and `/v1/muse-code/models` (ignoring query string) and serve the canonical 13-model Muse Code catalog JSON (`muse-spark-1.3` et al., `status: 200`, `content-type: application/json`), while continuing to rewrite any other `/muse-code/*` path to `/v1/muse-code/*`.
- **Rationale**: Serving the Muse Code catalog from the existing `peer-stamp.mjs` hook in `container-entrypoint-compat.sh` and `ensure-muse-wire-compat.sh` avoids brittle minified webpack edits to `/app/.build/next/server/app/api/v1/muse-code/models/route.js`, keeps git-tracked files clean, satisfies `GET /v1/muse-code/models` and `GET /muse-code/models` with `muse-spark-1.3` metadata for both Muse Code CLI and `update.sh` Gate 8, and applies before Next.js starts so Gate 4b sees `already_ok` without a second container restart.
- **Alternatives Considered**:
  - *Only pass a Bearer token to upstream's `v3.8.52` `/v1/muse-code/models` route in Gate 8*: Rejected because `getProviderModels` filters `payload.data` by `acceptedOwners = new Set(["muse-code", "mc"])`, which excludes `owned_by: "combo"` and returns `{"object":"list","data":[]}` when no `muse-code` provider connection exists.
  - *Patch `src/app/api/v1/muse-code/models/route.ts` in the local checkout*: Rejected because the container runs the pre-built Docker Hub image (`diegosouzapw/omniroute:latest`) and workstation policy prohibits dirtying tracked files in `~/Omniroute`.

### 2. Gate 8 Content-Verified Probe for `/v1/muse-code/models` and `/muse-code/models`
- **Choice**: Harden `scripts/update.sh` Gate 8 (`lines 310-384`) so that: (a) when `GET /v1/models` returns `401`, the in-container `AUTH_PROBE` decrypts `v3.8.52` encrypted-at-rest `enc:v1:<iv>:<ciphertext>:<authTag>` `api_keys.key` envelopes (`src/lib/db/apiKeys/secretAtRest.ts`) in memory using `process.env.STORAGE_ENCRYPTION_KEY`, and (b) in addition to asserting HTTP `200` on `GET /v1/muse-code/models` and `GET /muse-code/models`, Gate 8 structurally parses both responses with `JSON.parse` (`verify_muse_catalog_json`) and asserts that `Array.isArray(parsed.data)` contains an object entry with `id === "muse-spark-1.3"`.
- **Rationale**: Checking only HTTP `200` or grepping for a raw `"id":"muse-spark-1.3"` substring would falsely pass on an empty `{"object":"list","data":[]}`, malformed JSON, or wrong-shape object (`{"data":[],"id":"muse-spark-1.3"}`). Structural JSON validation of `parsed.data` makes Gate 8 fail-closed against empty, malformed, or wrong-shape catalog regressions.

### 3. Transaction Boundaries & Post-Migration In-Volume Backup Cleanup in Gate 9
- **Transaction Boundaries**:
  - **Host Snapshot & Checkpoint Transaction Boundary (Gate 1)**: Before pulling or recreating the container, `update.sh` runs read-only `PRAGMA quick_check` on live `/app/data/storage.sqlite` (`timeout: 15000`), calls `better-sqlite3` `.backup('/tmp/pre-update-<ts>.sqlite')` (online SQLite backup API), copies the backup to `~/.omniroute/snapshots/pre-update-<ts>.sqlite`, runs host `PRAGMA quick_check`, executes `PRAGMA wal_checkpoint(TRUNCATE)` requiring `0|*` (`busy == 0`) followed by `PRAGMA journal_mode=DELETE;` (so subsequent reads never recreate `-wal`/`-shm` sidecars), removes sidecars only after consolidation, and re-verifies host `PRAGMA quick_check = ok`.
  - **In-Container Schema Migration Transaction Boundary (`v3.8.52` Startup)**: On first boot of `v3.8.52`, `getDbInstance()` (`src/lib/db/core.ts:1312`) invokes `runMigrations()` (`src/lib/db/migrationRunner.ts:928-1175`) inside `runImmediateTransaction(db, ...)` (`BEGIN IMMEDIATE ... COMMIT`). Before applying migration `197`, `createPreMigrationBackup(db)` (`preMigrationBackup.ts:251-319`) executes `VACUUM INTO '/app/data/db_backups/.migration-snapshot-<rand>/snapshot.sqlite'`, `fsync`s, computes SHA-256, and hard-links `/app/data/db_backups/db_state-<sha256>_pre-migration.sqlite` (~1.07 GB), then applies migrations `197`–`212` atomically inside the immediate transaction. Meanwhile, `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED=true` and `OMNIROUTE_SKIP_DB_HEALTHCHECK=1` defer `healthCheckWorker.ts` off the synchronous startup path and skip `PRAGMA quick_check` inside `connection.immediate()`.
  - **Post-Deploy Verification & In-Volume Backup Pruning Boundary (Gate 9)**: Only after Gate 5 (`healthy`), Gate 6 (`version == 3.8.52`), Gate 7 (`image-id`), Gate 8 (`endpoints`), and Gate 9's post-deploy `PRAGMA quick_check = ok`, `api_keys >= BASELINE_API_KEYS` (`1`), and `provider_connections >= BASELINE_CONNS` (`32`) all succeed, Gate 9 removes `/app/data/db_backups/db_state-*_pre-migration.sqlite` inside the container (`docker exec "$CONTAINER" sh -c 'rm -f /app/data/db_backups/db_state-*_pre-migration.sqlite'`). If any migration or gate fails prior to Gate 9 completion, the in-volume pre-migration backup and the host `~/.omniroute/snapshots/pre-update-<ts>.sqlite` snapshot remain untouched for recovery.

### 4. Synchronizing Local Git Checkout, `.env`, and Global Skills
- **Choice**: Fast-forward `/Users/androidteam/Omniroute` `main` to `origin/main` (`fa6e0f14fb41f031c4c0e9901a4bc3a042eed175` via `git fetch origin && git merge --ff-only origin/main`), comment out `CLAUDE_USER_AGENT="claude-cli/2.1.121 (external, cli)"` in `/Users/androidteam/Omniroute/.env`, and refresh `~/.agents/.skill-lock.json` via `npx skills add /Users/androidteam/Omniroute -g --all` if skill hashes changed.
- **Rationale**: `~/.local/bin/omniroute` reads `/Users/androidteam/Omniroute/package.json` and spawns `/Users/androidteam/Omniroute/bin/omniroute.mjs`. Fast-forwarding `~/Omniroute` keeps `omniroute status` reporting `Version: 3.8.52 (CLI: 3.8.52)` and propagates the 33 updated `skills/{omni-*,cli-*}/SKILL.md` manifests immediately through the symlinks in `~/.agents/skills/`. Commenting out the stale `2.1.121` `CLAUDE_USER_AGENT` in `.env` aligns with `v3.8.52` `.env.example:1698` so OmniRoute uses its updated internal default user-agent.

## Risks / Trade-offs

- **[Risk] Pre-migration `VACUUM INTO` + 3× SHA-256 hashing on 1.07 GB `storage.sqlite` adds ~15–30s to first container boot on `v3.8.52`** → **Mitigation**: `docker-compose.override.yml` already sets `start_period: 120s`, `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED=true`, and `OMNIROUTE_SKIP_DB_HEALTHCHECK=1`, and `update.sh` Gate 5 allows up to 300s while holding `/usr/bin/lockf` on `~/.omniroute/update.lock` so `com.omniroute.watchdog` skips (`rc=75`).
- **[Risk] Migration `207` (`207_remove_opencode_free_provider.sql`) deletes keyless `opencode`/`oc` rows in `provider_connections`** → **Mitigation**: Pre-verified against live `/app/data/storage.sqlite` that `0` `opencode`/`oc`/`opencode-zen` rows exist in `provider_connections`; all 32 connections are preserved.
- **[Risk] Modifying `~/Omniroute/.env` could accidentally alter secrets or file permissions** → **Mitigation**: Perform a targeted single-line comment-out of `^CLAUDE_USER_AGENT=` without printing secret lines, and verify key count, SHA-256 of all other lines, and file mode before recreating the container.

## Migration Plan

1. **Pre-Upgrade Script & Checkout Prep**:
   - Fast-forward `/Users/androidteam/Omniroute` `main` to `origin/main` (`fa6e0f14fb41f031c4c0e9901a4bc3a042eed175`) and verify `package.json` version is `3.8.52` and `git status --porcelain --untracked-files=no` is empty.
   - Update `~/Omniroute/scripts/container-entrypoint-compat.sh`, `~/Omniroute/scripts/ensure-muse-wire-compat.sh`, and `~/Omniroute/scripts/update.sh` (Gate 8 Muse catalog auth probe + Gate 9 pre-migration backup cleanup), and add corresponding regression tests in `platform/openspec-store/tests/test_omniroute_lock_and_watchdog.py`.
   - Comment out `CLAUDE_USER_AGENT` in `~/Omniroute/.env`.
2. **Flag & Upgrade Execution**:
   - Run `~/Omniroute/scripts/check-upstream.sh` to populate `~/.omniroute/update-available` with `sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c`.
   - Execute `~/Omniroute/scripts/update.sh 3.8.52` and verify all 10 gates pass, `~/.omniroute/update-available` is removed, and rollback tag `omniroute:rollback-3.8.51-<ts>` and host snapshot `~/.omniroute/snapshots/pre-update-<ts>.sqlite` are created.
3. **Post-Upgrade Verification & Governance Sync**:
   - Verify container health, migration `212` recorded in `schema_migrations`, `/app/data/db_backups/` clean, `omniroute status` (`Version: 3.8.52 (CLI: 3.8.52)`), `omniroute keys list --output json`, `muse exec` 1-turn probe, and Gemini 4 Argon / Flash combos.
   - Update `platform/openspec-store/openspec/config.yaml` and `wiki/entities/omniroute.md`.
4. **Rollback Strategy**:
   - If any gate fails before container recreation, `update.sh` aborts with `v3.8.51` still running.
   - If post-recreation verification fails, restore `~/.omniroute/snapshots/pre-update-<ts>.sqlite` to `/app/data/storage.sqlite` (`1000:1000` ownership) and redeploy tagged rollback image `omniroute:rollback-3.8.51-<ts>`.
