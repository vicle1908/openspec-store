# Spec Delta: omniroute-agent-cli-routing

## MODIFIED Requirements

### Requirement: Muse Code entrypoint compatibility SHALL use URL-prefix rewriting without chunk mutation or static catalog bypass
OmniRoute container startup (`/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`) SHALL inject `MUSE_CODE_REWRITE_V3` into `/app/peer-stamp.mjs` to rewrite `/muse-code` and `/api/provider` prefixes to `/v1/muse-code` and `/v1/api/provider` without Muse-specific chunk rewrites, while applying the 48 non-Muse runtime compatibility rules across 21 server chunk files.

#### Scenario: Entrypoint rewrites /muse-code paths without modifying Next.js server chunks
- **WHEN** `container-entrypoint-compat.sh` or `ensure-muse-wire-compat.sh` runs inside the `omniroute` container (`v3.8.52+`)
- **THEN** `/app/peer-stamp.mjs` SHALL strip any prior V1 or `MUSE_CODE_COMPAT_V2` block and contain the `MUSE_CODE_REWRITE_V3` URL prefix rewrite (`req.url = "/v1" + req.url` for `/muse-code`, `/muse-code/*`, and `/muse-code?*`) without injecting a static model catalog
- **AND** `/app/.build/next/server/chunks/*.js` SHALL contain zero Muse-specific rewrites while enforcing the 57 required fail-closed server chunk markers (`60` total markers across `24` compiled files)
- **AND** authenticated `GET /muse-code/models` and `GET /v1/muse-code/models` SHALL return HTTP `200` from upstream's native route advertising `muse-spark-1.3`, while anonymous `GET` returns HTTP `401` when catalog authentication is enabled

#### Scenario: Muse Code binary resolves via canonical Homebrew cask symlink
- **WHEN** `/opt/homebrew/bin/muse` is inspected by workstation toolchain inventory (`inventory-workstation-toolchain.py`)
- **THEN** `/opt/homebrew/bin/muse` SHALL be a symbolic link to the installed Caskroom binary (`/opt/homebrew/Caskroom/muse-code/<version>/muse-binary`) with `is_symlinked_from_brew_bin == True`
- **AND** the macOS Keychain entry `ai.meta.dev.credentials` SHALL be seeded via `muse auth set --provider meta --api-key-stdin` with `~/.config/muse/auth.json` (`mode 0600`) on `schema_version: 2` (`"storage": "keychain"`) so `muse` executes non-interactively without requiring a `TBH_CREDENTIAL_BACKEND=file` override

### Requirement: 15-Account Antigravity Auto Pools for `claude-opus-5.5` and `claude-sonnet-5.5` Without Unentitled Custom 5.5 Model IDs
OmniRoute SHALL configure `claude-opus-5.5` (`15` active `agy` steps matching each connection's `syncedAvailableModels` entry: `agy/claude-opus-5-5-high` or `agy/claude-opus-4-6-thinking`, `0` `combo-ref` steps, `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`) and `claude-sonnet-5.5` (`15` active `agy` steps: `agy/claude-sonnet-5-5-high` or `agy/claude-sonnet-4-6`, `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`) with `strategy: "auto"` and `context_cache_protection: false`.

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route across 15 `agy` accounts with tier-matched timeouts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** `claude-opus-5.5` SHALL contain 15 `kind: "model"` steps matching each active connection's `syncedAvailableModels` catalog (`agy/claude-opus-5-5-high` on `38782750` and `agy/claude-opus-4-6-thinking` on the remaining 14 active `agy` accounts, excluding banned `47f334b1`) with `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`
- **AND** `claude-sonnet-5.5` SHALL contain 15 `kind: "model"` steps matching each active connection's `syncedAvailableModels` catalog (`agy/claude-sonnet-5-5-high` on `38782750` and `agy/claude-sonnet-4-6` on the remaining 14 active `agy` accounts) with `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Unentitled `claude-*-5-5-high` custom models and unstable auto-pool providers are excluded without breaking dedicated combos
- **WHEN** `GET /api/provider-models`, `GET /api/models/alias`, `GET /api/providers`, and `GET /api/combos` are queried
- **THEN** `/api/provider-models` SHALL NOT contain custom `claude-opus-5-5-high` or `claude-sonnet-5-5-high` overrides under `agy` or `antigravity`, and `/api/models/alias` SHALL NOT contain `test-opus-55-high`
- **AND** expired connection `6fb701a5-d060-422c-bc34-0cca543d0eda` (`ollama-cloud`) SHALL have `isActive: false`, while `auto/*` combos SHALL restrict `config.candidatePool` to `["agy", "codex", "github"]` so dedicated combos (`phanmemvip` and `muse-spark-1.3`) remain intact
