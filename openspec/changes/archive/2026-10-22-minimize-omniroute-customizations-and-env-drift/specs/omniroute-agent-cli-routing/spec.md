# Spec Delta

## ADDED Requirements

### Requirement: Muse Code entrypoint compatibility SHALL use URL-prefix rewriting without chunk mutation or static catalog bypass

The compose-mounted `/app/container-entrypoint-compat.sh` and `~/Omniroute/scripts/ensure-muse-wire-compat.sh` SHALL rewrite bare `/muse-code` request paths to `/v1/muse-code` in `/app/peer-stamp.mjs` (`MUSE_CODE_REWRITE_V3`) while delegating `/v1/muse-code/models` to upstream's native authenticated route handler and leaving compiled Next.js server chunks (`/app/.build/next/server/chunks/*.js`) unmodified.

#### Scenario: Entrypoint rewrites /muse-code paths without modifying Next.js server chunks
- **WHEN** `container-entrypoint-compat.sh` or `ensure-muse-wire-compat.sh` runs inside the `omniroute` container (`v3.8.52+`)
- **THEN** `/app/peer-stamp.mjs` SHALL strip any prior V1 or `MUSE_CODE_COMPAT_V2` block and contain the `MUSE_CODE_REWRITE_V3` URL prefix rewrite (`req.url = "/v1" + req.url` for `/muse-code`, `/muse-code/*`, and `/muse-code?*`) without injecting a static model catalog
- **AND** `/app/.build/next/server/chunks/*.js` SHALL remain byte-for-byte identical to the upstream container image layers
- **AND** authenticated `GET /muse-code/models` and `GET /v1/muse-code/models` SHALL return HTTP `200` from upstream's native route advertising `muse-spark-1.3`, while anonymous `GET` returns HTTP `401` when catalog authentication is enabled

#### Scenario: Muse Code binary resolves via canonical Homebrew cask symlink
- **WHEN** `/opt/homebrew/bin/muse` is inspected by workstation toolchain inventory (`inventory-workstation-toolchain.py`)
- **THEN** `/opt/homebrew/bin/muse` SHALL be a symbolic link to the installed Caskroom binary (`/opt/homebrew/Caskroom/muse-code/<version>/muse-binary`) with `is_symlinked_from_brew_bin == True`
- **AND** the macOS Keychain entry `ai.meta.dev.credentials` SHALL be seeded via `muse auth set --provider meta --api-key-stdin` with `~/.config/muse/auth.json` (`mode 0600`) on `schema_version: 2` (`"storage": "keychain"`) so `muse` executes non-interactively without requiring a `TBH_CREDENTIAL_BACKEND=file` override
