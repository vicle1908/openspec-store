# Proposal

## Why

The local OmniRoute `v3.8.52` deployment and host tooling retain legacy compatibility hacks—compiled Next.js chunk patching, an unauthenticated static `/muse-code/models` catalog bypass, APFS path-casing `.env` shadow warnings in `~/.local/bin/omniroute`, and a shell wrapper replacing `/opt/homebrew/bin/muse`—that are no longer required by upstream `v3.8.52` and diverge from official setup practices.

Empirical testing against `v3.8.52` and Meta Muse Code CLI (`1.4.11`) proves that Muse Code natively accepts stock `v3.8.52` SSE keepalive frames (`id: "resp_keepalive_omniroute"`), authenticates against upstream's native `/api/v1/muse-code/models` route (requiring only a 1-line `/muse-code` → `/v1/muse-code` URL rewrite in `peer-stamp.mjs`), and that passing `--env-file=/dev/null` to Bun alongside `OMNIROUTE_CLI_SKIP_DEFAULT_DATA_ENV=1` and `OMNIROUTE_CLI_SKIP_REPO_ENV=1` in `~/.local/bin/omniroute` eliminates all 64 self-shadowing `.env` warnings.

## What Changes

- **Retire Compiled Chunk Patching & Unauthenticated Static Catalog Injection (`~/Omniroute/scripts/container-entrypoint-compat.sh` & `~/Omniroute/scripts/update.sh`)**:
  - Replace `MUSE_CODE_COMPAT_V2` (stripping any existing V1 or `MUSE_CODE_COMPAT_V2` block and removing the `/app/.build/next/server/chunks/*.js` regex mutation) with a minimal `MUSE_CODE_REWRITE_V3` hook in `/app/peer-stamp.mjs` that only rewrites `/muse-code` URL prefixes to `/v1/muse-code`, delegating model discovery to upstream's native authenticated `src/app/api/v1/muse-code/models/route.ts` handler and leaving compiled Next.js server chunks untouched.
  - Update `~/Omniroute/scripts/update.sh` Gate 8 (`endpoints`) to verify `/v1/models`, `/v1/muse-code/models`, and `/muse-code/models` in a single unified in-container `AUTH_PROBE` when catalog auth is enabled (`401` anonymous + `200` authenticated in-container advertising `muse-spark-1.3` in `data[]`), or anonymous `200` when catalog auth is disabled.
- **Eliminate Bun `.env` Pre-Load & Duplicate Shadow Warnings in Host CLI Bridge (`~/.local/bin/omniroute`)**:
  - Spawn `bun` with `--env-file=/dev/null`, set `OMNIROUTE_CLI_SKIP_DEFAULT_DATA_ENV="1"`, `OMNIROUTE_CLI_SKIP_REPO_ENV="1"`, and `STORAGE_ENCRYPTION_KEY ||= "ephemeral-bridge-key"`, and use `ephemeralDir` as `cwd` when invoked inside `/Users/androidteam/OmniRoute`, eliminating all 64 `⚠ ... is ignored` stderr warnings and removing the obsolete `resolveSpawnCwd` loop.
- **Restore Canonical Homebrew Cask Symlink for `/opt/homebrew/bin/muse`**:
  - Delete the stale pre-codesign `ai.meta.dev.credentials` entry in macOS Keychain, re-seed it natively via `muse auth set --provider meta --api-key-stdin` (migrating `~/.config/muse/auth.json` to `schema_version: 2` `"storage": "keychain"` with zero plaintext API keys on disk and removing the custom `TBH_CREDENTIAL_BACKEND=file` override from `~/.zshenv`), and restore `/opt/homebrew/bin/muse` to the canonical Homebrew cask symlink `../Caskroom/muse-code/1.4.11-R6667.1/muse-binary`.

## Non-Goals

- Switching `/app/data` from the `omniroute-data` Docker named volume to a host bind mount (named volume remains mandatory on macOS to prevent VirtIO-FS SQLite WAL corruption).
- Modifying git-tracked files in `/Users/androidteam/Omniroute`.
- Removing the host CLI bridge's ephemeral `DATA_DIR` isolation or remote-truth `status` / `keys list` / `providers list` handlers.

## Affected Ownership Boundaries

- **OmniRoute Deployment Root**: `/Users/androidteam/Omniroute` (untracked `scripts/container-entrypoint-compat.sh`, `scripts/ensure-muse-wire-compat.sh`, and `scripts/update.sh`).
- **Host CLI Bridge & Homebrew Bin**: `/Users/androidteam/.local/bin/omniroute` and `/opt/homebrew/bin/muse`.
- **OpenSpec Governance Store**: `/Users/androidteam/Developer/platform/openspec-store` (`openspec/specs/bifrost-gateway/spec.md`, `openspec/specs/omniroute-agent-cli-routing/spec.md`, `openspec/specs/omniroute-agent-skills/spec.md`, `tests/test_omniroute_lock_and_watchdog.py`, and `tests/test_omniroute_cli_bridge.py`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bifrost-gateway`: Update Gate 8 (`endpoints`) requirements so `/v1/muse-code/models` and `/muse-code/models` are verified under the configured opt-out catalog authentication policy (`200` when public, or `401` anonymous + authenticated in-container `200` with `muse-spark-1.3` in `data[]`).
- `omniroute-agent-cli-routing`: Update the Muse Code compatibility layer requirements so `container-entrypoint-compat.sh` and `ensure-muse-wire-compat.sh` perform only the `/muse-code` → `/v1/muse-code` URL prefix rewrite in `/app/peer-stamp.mjs` (`MUSE_CODE_REWRITE_V3`), delegating catalog responses to upstream's native authenticated route and leaving compiled Next.js server chunks unmodified, and require `/opt/homebrew/bin/muse` to remain a canonical Homebrew cask symlink.
- `omniroute-agent-skills`: Require `~/.local/bin/omniroute` to spawn `bun` with `--env-file=/dev/null`, `OMNIROUTE_CLI_SKIP_DEFAULT_DATA_ENV=1`, `OMNIROUTE_CLI_SKIP_REPO_ENV=1`, and an ephemeral `STORAGE_ENCRYPTION_KEY` default so pass-through CLI invocations emit zero `.env` shadowing warnings on `stderr`.

## Impact

- **Upstream Alignment & Security**: Eliminates container writable-layer bundle patching and unauthenticated catalog bypasses while preserving seamless Muse Code CLI operation.
- **CLI & Toolchain Hygiene**: Silences 64 spurious `.env` shadowing warnings on pass-through `omniroute` CLI commands and restores `brew-cask` symlink provenance for `/opt/homebrew/bin/muse`.
