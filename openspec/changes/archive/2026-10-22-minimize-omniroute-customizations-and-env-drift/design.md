# Design

## Context

See `proposal.md` — Why for motivation and empirical findings, and `specs/bifrost-gateway/spec.md`, `specs/omniroute-agent-cli-routing/spec.md`, and `specs/omniroute-agent-skills/spec.md` for normative requirements.

Currently:
1. `~/Omniroute/scripts/container-entrypoint-compat.sh` (mounted at `/app/container-entrypoint-compat.sh:ro`) injects a 42-line `MUSE_CODE_COMPAT_V2` static 13-model catalog into `/app/peer-stamp.mjs` (bypassing `requireAuthForModels`) and mutates `/app/.build/next/server/chunks/*.js` in the container writable layer to rewrite `response.in_progress` keepalive frames.
2. Live probe verification against Meta Muse Code CLI (`1.4.11`) on an ephemeral HTTP SSE server proved that `muse` natively accepts `v3.8.52`'s stock `{"id":"resp_keepalive_omniroute","status":"in_progress"}` keepalive frame (`RC=0`, `STDOUT=STOCK_KEEPALIVE_OK`) and sends `GET /muse-code/models` with `Authorization: Bearer <OMNIROUTE_API_KEY>`. Meanwhile, upstream's native `src/app/api/v1/muse-code/models/route.ts` serves a 40-model dynamic catalog (`muse-spark-1.3` first) when authenticated (given the active `muse-code` connection `51795cf9-4c03-4c22-af9d-9ce4de975dc1`), while `next.config.mjs` rewrites `/v1/:path*` → `/api/v1/:path*` but lacks a rewrite for bare `/muse-code/:path*`.
3. Because `~/.local/bin/omniroute` runs under `#!/opt/homebrew/bin/bun` and spawns `bun` with `cwd` set to `/Users/androidteam/Omniroute`, Bun's built-in `.env` auto-loader reads `/Users/androidteam/OmniRoute/.env` into `process.env` before `bin/omniroute.mjs` starts. When `bin/omniroute.mjs` then runs `loadEnvFile()` (`lines 134-205`), all 64 keys in `.env` are already in `process.env`, emitting 64 `⚠ ... is ignored, the environment set it first` warnings on `stderr`. Furthermore, every script in `/Users/androidteam/OmniRoute/bin/` resolves `package.json` from `import.meta.url`, never `process.cwd()`.
4. `/opt/homebrew/bin/muse` was replaced with a 146-byte shell script instead of the Homebrew cask symlink `../Caskroom/muse-code/1.4.11-R6667.1/muse-binary` because a stale pre-codesign macOS Keychain entry (`svce="ai.meta.dev.credentials"`) causes `securityd` to block when `muse-binary` runs without `TBH_CREDENTIAL_BACKEND=file`.

## Goals / Non-Goals

**Goals:**
- Reduce `container-entrypoint-compat.sh` from 85 lines to a ~25-line `MUSE_CODE_REWRITE_V3` script that only rewrites `/muse-code` URL prefixes to `/v1/muse-code` in `/app/peer-stamp.mjs`, completely eliminating compiled Next.js chunk patching and unauthenticated static catalog responses.
- Update `~/Omniroute/scripts/update.sh` Gate 8 to verify `/v1/muse-code/models` and `/muse-code/models` under opt-out catalog authentication (`200` when public, or `401` anonymous + authenticated in-container `200` containing `id === "muse-spark-1.3"` in `data[]`).
- Eliminate all 64 duplicate `.env` shadowing warnings in `~/.local/bin/omniroute` by spawning `bun` with `--env-file=/dev/null`, setting `OMNIROUTE_CLI_SKIP_DEFAULT_DATA_ENV=1`, `OMNIROUTE_CLI_SKIP_REPO_ENV=1`, and `STORAGE_ENCRYPTION_KEY ||= "ephemeral-bridge-key"`, and keeping `cwd` out of `/Users/androidteam/OmniRoute`.
- Restore `/opt/homebrew/bin/muse` to its canonical Homebrew cask symlink, remove the custom `TBH_CREDENTIAL_BACKEND=file` override from `~/.zshenv`, and refresh `ai.meta.dev.credentials` in macOS Keychain via `muse auth set --provider meta --api-key-stdin` (`schema_version: 2`, `"storage": "keychain"`).

**Non-Goals:**
- Modifying git-tracked files in `/Users/androidteam/Omniroute`.
- Switching `/app/data` away from the `omniroute-data` Docker named volume.

## Decisions

### 1. Minimal `MUSE_CODE_REWRITE_V3` in `/app/peer-stamp.mjs` & Zero Chunk Patching
- **Choice**: In `container-entrypoint-compat.sh`, remove the `chunksDir` (`/_next/server/chunks/*.js`) patching loop, strip any prior V1 rewrite or `/* MUSE_CODE_COMPAT_V2 */[\s\S]*?stampPeerIp\(req\);` block in `/app/peer-stamp.mjs`, and insert a single-line URL prefix rewrite (`/* MUSE_CODE_REWRITE_V3 */ if (req.url && (req.url === "/muse-code" || req.url.startsWith("/muse-code/") || req.url.startsWith("/muse-code?"))) { req.url = "/v1" + req.url; }\n    stampPeerIp(req);`).
- **Rationale**: Upstream `v3.8.52` already emits a non-null string `id: "resp_keepalive_omniroute"` (`#15202`), which `muse` 1.4.11 decodes cleanly without chunk mutation (`EXACT_FRAME_OK`), and upstream's native `/api/v1/muse-code/models` route serves the authenticated 40-model catalog. Stripping `MUSE_CODE_COMPAT_V2` ensures idempotent in-place upgrades from V2 to V3.
- **Alternatives Considered**:
  - *Remove `container-entrypoint-compat.sh` completely*: Rejected because `next.config.mjs` does not rewrite bare `/muse-code/models` to `/api/v1/muse-code/models`, which would return an HTML 404 when `muse` fetches `/muse-code/models`.

### 2. Unified Gate 8 Opt-Out Catalog Auth Verification in `update.sh`
- **Choice**: In `~/Omniroute/scripts/update.sh` Gate 8, extend the existing single in-container `AUTH_PROBE` (`docker exec "$CONTAINER" node -e`) so that when catalog auth is enabled (`401` on anonymous `GET /v1/models`, `/v1/muse-code/models`, and `/muse-code/models`), the single decrypted active API key from `/app/data/storage.sqlite` verifies all three endpoints (`/v1/models` count > 0, and `/v1/muse-code/models` + `/muse-code/models` returning HTTP `200` with `id === "muse-spark-1.3"` in `data[]`) in one container exec; when catalog auth is disabled (`200`), verify anonymous `GET` bodies with `verify_muse_catalog_json`.
- **Rationale**: Reusing the single `AUTH_PROBE` avoids duplicating 35 lines of SQLite + `scryptSync` + `aes-256-gcm` decryption code in `update.sh`.

### 3. Suppressing Bun `.env` Pre-Load & Shadow Warnings in `~/.local/bin/omniroute`
- **Choice**: Pass `--env-file=/dev/null` when spawning `bun`, set `OMNIROUTE_CLI_SKIP_DEFAULT_DATA_ENV = "1"`, `OMNIROUTE_CLI_SKIP_REPO_ENV = "1"`, and `process.env.STORAGE_ENCRYPTION_KEY ||= "ephemeral-bridge-key"`, and replace `resolveSpawnCwd` with `originalCwd` (falling back to `ephemeralDir` when `originalCwd` is inside `/Users/androidteam/OmniRoute`).
- **Rationale**: Prevents Bun from pre-loading `/Users/androidteam/OmniRoute/.env` into `process.env` before `bin/omniroute.mjs` runs, prevents `bin/omniroute.mjs:157` from loading `.env` from `process.cwd()`, and prevents `shouldProvisionStorageKey()` from generating a throwaway `.env` in `ephemeralDir`.
### 4. Transaction & State Boundaries
- **Container Entrypoint & Recreate Boundary**: Recreating `omniroute-base` under `/usr/bin/lockf` on `~/.omniroute/update.lock` restores `/app/.build/next/server/chunks/*.js` and `/app/peer-stamp.mjs` from the immutable image layers before `container-entrypoint-compat.sh` applies `MUSE_CODE_REWRITE_V3` to `/app/peer-stamp.mjs`.
- **Host Symlink & Keychain Boundary**: Deleting the stale `ai.meta.dev.credentials` Keychain entry, seeding a fresh Keychain item via `muse auth set --provider meta --api-key-stdin` (`schema_version: 2` `"storage": "keychain"` in `~/.config/muse/auth.json`), removing `TBH_CREDENTIAL_BACKEND=file` from `~/.zshenv`, and atomically replacing `/opt/homebrew/bin/muse` with `ln -sf ../Caskroom/muse-code/1.4.11-R6667.1/muse-binary /opt/homebrew/bin/muse` ensures both zsh and non-zsh callers authenticate against the official macOS Keychain backend without `securityd` prompts.

## Risks / Trade-offs

- **[Risk] If all `muse-code` rows in `provider_connections` were deleted in the future, upstream's `/api/v1/muse-code/models` route would return `data: []`** → **Mitigation**: `update.sh` Gate 8 asserts that `data[]` contains `id === "muse-spark-1.3"`, failing closed if the `muse-code` connection is ever removed.
- **[Risk] Non-zsh process invoking `/opt/homebrew/bin/muse` without `TBH_CREDENTIAL_BACKEND=file` in environment** → **Mitigation**: Seeding `ai.meta.dev.credentials` via `muse auth set --provider meta --api-key-stdin` (`schema_version: 2`, `"storage": "keychain"`) and removing `TBH_CREDENTIAL_BACKEND=file` from `~/.zshenv` unifies all callers on the official Keychain backend.
