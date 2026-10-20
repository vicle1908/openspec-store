# Proposal

## Why

The local OmniRoute gateway runtime (`diegosouzapw/omniroute:latest`, `v3.8.51`, image index digest `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218`) and local source checkout (`~/Omniroute` at `e62b4b71c`) lag behind upstream release `v3.8.52` (index digest `sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c`, tag `v3.8.52` at `ad6f33f66bda34eba98645d3bfdabbde294bc843`, `origin/main` at `fa6e0f14fb41f031c4c0e9901a4bc3a042eed175`), and two upstream behavioral changes in `v3.8.52` require updating our local compatibility and upgrade scripts before applying the container upgrade.

Specifically, upstream `v3.8.52` delivers 1,442 documented changes (135 features, 1,112 fixes, 195 maintenance items across 1,386 commits), 16 SQLite schema migrations (`197`–`212`), 33 updated official agent skill manifests (expanding catalog coverage from 358 to 375 providers), and two changes that directly interact with workstation gates:
1. **`/v1/muse-code/models` Dynamic Provider Filtering & Catalog Auth Change (`src/app/api/v1/muse-code/models/route.ts:95-112`)**: Upstream replaced the static `200` catalog handler (`CATALOG_PAYLOAD` built from `muse_codeProvider.models`) with `getProviderModels(request, { params: Promise.resolve({ provider: "muse-code" }) })` → `getUnifiedModelsResponse(request)`, which enforces opt-out catalog authentication (`requireAuthForModels`) and filters by `acceptedOwners = new Set(["muse-code", "mc"])`. Because this workstation has `0` `muse-code` rows in `provider_connections` and exposes `muse-spark-1.3` as a combo (`owned_by: "combo"`), even an authenticated `GET /v1/muse-code/models` in `v3.8.52` returns an empty `{"object":"list","data":[]}` (omitting `muse-spark-1.3`) while anonymous `GET` returns `401`. Serving the Muse Code static catalog directly in `/app/peer-stamp.mjs` (via `container-entrypoint-compat.sh` and `ensure-muse-wire-compat.sh`) for `/v1/muse-code/models` and `/muse-code/models` (or ensuring `update.sh` Gate 8 verifies `muse-spark-1.3` in the returned catalog) keeps both Muse Code CLI discovery and `update.sh` Gate 8 intact.
2. **Responses SSE Keepalive Payload Normalization (`open-sse/utils/sseHeartbeat.ts:18-22`, `#15202`)**: Upstream replaced `response:{id:null,status:"in_progress"}` with `response:{id:"resp_keepalive_omniroute",status:"in_progress"}`, omitting `object:"response",output:[],error:null` required by Meta Muse Code CLI's strict Rust `serde` decoder. Because `~/Omniroute/scripts/container-entrypoint-compat.sh` and `~/Omniroute/scripts/ensure-muse-wire-compat.sh` currently match only `id:null`, their regex must be widened to match `id:(?:null|"resp_keepalive_omniroute")`.
3. **Mandatory Pre-Migration `VACUUM INTO` In-Volume Backup (`src/lib/db/migrationRunner/preMigrationBackup.ts:251-319`)**: Applying migrations `197`–`212` creates a mandatory content-addressed `/app/data/db_backups/db_state-<sha256>_pre-migration.sqlite` (~1.07 GB) inside the `omniroute-data` volume without automatic post-migration pruning. Cleaning up redundant in-volume pre-migration backups in `update.sh` Gate 9 (after Gate 1's verified host snapshot and Gate 9's post-deploy `PRAGMA quick_check = ok` and baseline row-count assertions succeed) preserves the bounded volume hygiene contract established in `specs/bifrost-gateway/spec.md`.

## What Changes

- **Fast-Forward Local Checkout & Refresh Global Skill Lockfile (`~/Omniroute` & `~/.agents/.skill-lock.json`)**:
  - Fast-forward `/Users/androidteam/Omniroute` `main` from `e62b4b71c5cf1b99d022bc48cb0f30da22f982c0` to `origin/main` (`fa6e0f14fb41f031c4c0e9901a4bc3a042eed175`, containing release `v3.8.52` `ad6f33f66bda34eba98645d3bfdabbde294bc843` and lockfile resync `#17212`) while keeping tracked files clean (`git status --porcelain --untracked-files=no` empty) so `~/.local/bin/omniroute` reports `Version: 3.8.52 (CLI: 3.8.52)` and the 33 updated `skills/{omni-*,cli-*}/SKILL.md` manifests propagate to `~/.agents/skills/`.
  - Refresh global skill lockfile hashes via `npx skills add /Users/androidteam/Omniroute -g --all` if needed so `~/.agents/.skill-lock.json` matches the `v3.8.52` skill contents.
- **Update Muse Code Wire-Compatibility Scripts for `v3.8.52` (`~/Omniroute/scripts/container-entrypoint-compat.sh` & `~/Omniroute/scripts/ensure-muse-wire-compat.sh`)**:
  - Update the Next.js server chunk patcher in both scripts to match `response:\{id:(?:null|"resp_keepalive_omniroute"),status:"in_progress"\}` and normalize it to `response:{id:"resp_keepalive",object:"response",status:"in_progress",output:[],error:null}`.
  - Update the `/app/peer-stamp.mjs` compatibility hook in both scripts so `GET /v1/muse-code/models` and `GET /muse-code/models` return HTTP `200` with the Muse Code model catalog advertising `muse-spark-1.3` (even when `0` `muse-code` `provider_connections` exist and `muse-spark-1.3` is backed by an OmniRoute combo) while continuing to rewrite `/muse-code/*` inference paths to `/v1/muse-code/*`.
- **Harden `~/Omniroute/scripts/update.sh` Gate 8 & Gate 9 for `v3.8.52` Catalog Validation and In-Volume Backup Hygiene**:
  - **Gate 8 (`endpoints`)**: Update `/v1/muse-code/models` and `/muse-code/models` verification to assert HTTP `200` with JSON `data` containing `id === "muse-spark-1.3"` (not just status code `200`, which would miss an empty `{"object":"list","data":[]}` regression).
  - **Gate 9 (`post-deploy-data`)**: After verifying post-deploy `PRAGMA quick_check = ok`, `api_keys >= BASELINE_API_KEYS` (`1`), and `provider_connections >= BASELINE_CONNS` (`32`), remove redundant `/app/data/db_backups/db_state-*_pre-migration.sqlite` files inside the container so `/app/data` on `omniroute-data` does not accumulate duplicate ~1.07 GB migration snapshots alongside the verified host snapshots in `~/.omniroute/snapshots/`.
- **Clean Up Stale `CLAUDE_USER_AGENT` Override in `~/Omniroute/.env`**:
  - Comment out the hardcoded stale `CLAUDE_USER_AGENT="claude-cli/2.1.121 (external, cli)"` line in `/Users/androidteam/Omniroute/.env` (matching upstream `v3.8.52` `.env.example:1698`) without exposing or modifying any secret values, allowing OmniRoute `v3.8.52` to use its built-in current Claude CLI user-agent default.
- **Execute Fail-Closed `v3.8.52` Container Upgrade & Post-Upgrade Verification**:
  - Run `~/Omniroute/scripts/check-upstream.sh` to detect remote index digest `sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c` and write `~/.omniroute/update-available`.
  - Execute `~/Omniroute/scripts/update.sh 3.8.52` through all 10 gates (Gates 0, P, 1–4, 4b, 5–9) under `/usr/bin/lockf` on `~/.omniroute/update.lock`.
  - Verify live runtime, database migrations (`212` applied), CLI bridge (`omniroute status`, `omniroute keys list --output json`), Muse Code (`muse exec`), and Gemini 4 Argon / Flash combos.
  - Update `platform/openspec-store/openspec/config.yaml` and `wiki/entities/omniroute.md` to record `v3.8.52`, upgrade date `2026-10-20`, git commit `fa6e0f14f` (`v3.8.52` tag `ad6f33f66`), and index digest `sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c`.

## Non-Goals

- Switching `/app/data` from the `omniroute-data` (`omniroute_omniroute-data`) Docker named volume to a host bind mount.
- Upgrading or recreating the `omniroute-redis` container (`redis:8.6.5-alpine` remains untouched).
- Activating additional Docker Compose profiles (`web`, `cli`, `bifrost`, `memory`, `codex-app-server`).
- Modifying `api_keys`, `provider_connections`, `combos`, or coding-agent CLI model registrations.
- Modifying git-tracked upstream source files under `/Users/androidteam/Omniroute`.

## Affected Ownership Boundaries

- **OmniRoute Deployment Root**: `/Users/androidteam/Omniroute` (git `main` fast-forward to `origin/main`, untracked `scripts/update.sh`, `scripts/container-entrypoint-compat.sh`, `scripts/ensure-muse-wire-compat.sh`, and `.env` `CLAUDE_USER_AGENT` comment-out).
- **Host CLI Bridge & Global Skills**: `/Users/androidteam/.local/bin/omniroute`, `/Users/androidteam/.agents/skills/{omni-*,cli-*}`, `/Users/androidteam/.agents/.skill-lock.json`, and `/Users/androidteam/.omniroute/` runtime state (`update-available`, `update.log`, `snapshots/`).
- **OpenSpec Governance Store & Wiki**: `/Users/androidteam/Developer/platform/openspec-store` (`openspec/specs/bifrost-gateway/spec.md`, `openspec/specs/omniroute-agent-cli-routing/spec.md`, `openspec/config.yaml`, `tests/test_omniroute_lock_and_watchdog.py`) and `/Users/androidteam/Developer/wiki/entities/omniroute.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bifrost-gateway`: Update the fail-closed image upgrade and named-volume snapshot hygiene requirements so `update.sh` Gate 8 verifies that `/v1/muse-code/models` and `/muse-code/models` return HTTP `200` with a non-empty catalog advertising `muse-spark-1.3`, and Gate 9 prunes redundant in-volume `/app/data/db_backups/db_state-*_pre-migration.sqlite` files after post-deploy `PRAGMA quick_check = ok` and baseline row-count verification pass.
- `omniroute-agent-cli-routing`: Update the Muse Code compatibility layer requirements so `container-entrypoint-compat.sh` and `ensure-muse-wire-compat.sh` normalize both legacy `id:null` and `v3.8.52` `id:"resp_keepalive_omniroute"` Responses SSE keepalive frames into full `{id:"resp_keepalive",object:"response",status:"in_progress",output:[],error:null}` payloads and serve the Muse Code model catalog (`muse-spark-1.3`) on `/v1/muse-code/models` and `/muse-code/models` when `muse-spark-1.3` is combo-backed without a direct `muse-code` provider connection.

## Impact

- **Gateway Runtime & Schema**: Upgrades `omniroute` container from `v3.8.51` to `v3.8.52` (`sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c`) and applies SQLite migrations `197`–`212` against the compacted 1.07 GB `/app/data/storage.sqlite` database.
- **Client & CLI Compatibility**: Preserves Meta Muse Code CLI (`muse-spark-1.3`) Rust SSE decoder compatibility and authenticated catalog discovery across `v3.8.52`, eliminates CLI/daemon version skew (`3.8.52 (CLI: 3.8.52)`), and updates 33 official OmniRoute skill manifests.
- **Disk Hygiene**: Prevents `/app/data/db_backups/` inside `omniroute_omniroute-data` from retaining a duplicate ~1.07 GB pre-migration `VACUUM INTO` file after host snapshot and post-deploy integrity gates succeed.
