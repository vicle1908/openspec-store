# Spec Delta

## MODIFIED Requirements

### Requirement: Muse Code configuration, credentials, and MCP router bridge SHALL enforce workstation security and multiplexing standards

Muse Code user configuration and credential files under `~/.config/muse/` SHALL enforce restrictive user-only file permissions, persist `OMNIROUTE_API_KEY` using the non-interactive file credential backend (`schema_version: 1`) without macOS file-based Keychain pointers, connect to the workstation's central `mcp-router` over stdio without duplicate point-to-point MCP entries, and expose canonical workstation skills.

#### Scenario: Restrictive permissions on Muse Code configuration and credential stores
- **WHEN** filesystem permissions and credential configuration under `~/.config/muse` are audited
- **THEN** directory `~/.config/muse` SHALL have permission mode `0700`
- **AND** `~/.config/muse/settings.json` and `~/.config/muse/auth.json` SHALL have permission mode `0600`
- **AND** `OMNIROUTE_API_KEY` SHALL be seeded via `TBH_CREDENTIAL_BACKEND=file muse auth set --provider meta --api-key-stdin` (after unlinking any prior `schema_version: 2` keychain-referenced file to prevent `FM-008`), persisting `schema_version: 1` with `providers.meta.api_key` in `~/.config/muse/auth.json` without committing literal secrets to version control
- **AND** no `ai.meta.dev.credentials` generic password entry SHALL remain in `~/Library/Keychains/login.keychain-db`

#### Scenario: Background GUI usage polling and headless execution complete without SecurityAgent prompts
- **WHEN** `Orca.app` or another GUI process invokes `/opt/homebrew/bin/muse usage --json` without `TBH_CREDENTIAL_BACKEND` in its process environment, or when `muse exec --disable-approval --no-session-log` runs
- **THEN** `muse` SHALL read `providers.meta.api_key` directly from `~/.config/muse/auth.json` (`schema_version: 1`) without calling `SecItemCopyMatching` on `login.keychain-db`
- **AND** the command SHALL exit `0` without spawning `SecurityAgent` password dialogs or encountering `macOS Keychain didn't answer within 5 seconds` timeouts

#### Scenario: Multiplexed MCP router registration and skill discovery
- **WHEN** `~/.config/muse/settings.json` and available skills are inspected
- **THEN** `mcpServers.mcp-router` (or legacy alias `mcp_servers.mcp-router`) SHALL declare `"transport": "stdio"`, `"command": "npx"`, `"args": ["-y", "@mcp_router/cli@latest", "connect"]`, `"mode": "optional"`, and `env.MCPR_TOKEN`
- **AND** no redundant individual stdio definitions for `gitnexus`, `graphify`, or `agentmemory` SHALL be duplicated in `settings.json`
- **AND** workstation skills SHALL be discoverable via `muse skills list` (and imported via `muse skills import --from claude --apply` when applicable)

### Requirement: Muse Code entrypoint compatibility SHALL use URL-prefix rewriting without chunk mutation or static catalog bypass

OmniRoute container startup (`/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`) SHALL inject `MUSE_CODE_REWRITE_V3` into `/app/peer-stamp.mjs` to rewrite `/muse-code` and `/api/provider` prefixes to `/v1/muse-code` and `/v1/api/provider` without Muse-specific chunk rewrites, while applying the non-Muse runtime compatibility rules across server chunk files.

#### Scenario: Entrypoint rewrites /muse-code paths without modifying Next.js server chunks
- **WHEN** `container-entrypoint-compat.sh` or `ensure-muse-wire-compat.sh` runs inside the `omniroute` container (`v3.8.52+`)
- **THEN** `/app/peer-stamp.mjs` SHALL strip any prior V1 or `MUSE_CODE_COMPAT_V2` block and contain the `MUSE_CODE_REWRITE_V3` URL prefix rewrite (`req.url = "/v1" + req.url` for `/muse-code`, `/muse-code/*`, and `/muse-code?*`) without injecting a static model catalog
- **AND** `/app/.build/next/server/chunks/*.js` SHALL contain zero Muse-specific rewrites while enforcing the required fail-closed server chunk markers
- **AND** authenticated `GET /muse-code/models` and `GET /v1/muse-code/models` SHALL return HTTP `200` from upstream's native route advertising `muse-spark-1.3`, while anonymous `GET` returns HTTP `401` when catalog authentication is enabled

#### Scenario: Muse Code binary resolves via canonical Homebrew cask symlink
- **WHEN** `/opt/homebrew/bin/muse` is inspected by workstation toolchain inventory (`inventory-workstation-toolchain.py`)
- **THEN** `/opt/homebrew/bin/muse` SHALL be a symbolic link to the installed Caskroom binary (`/opt/homebrew/Caskroom/muse-code/<version>/muse-binary`) with `is_symlinked_from_brew_bin == True`
- **AND** `~/.config/muse/auth.json` (`mode 0600`) SHALL be maintained on `schema_version: 1` (`TBH_CREDENTIAL_BACKEND=file`) rather than `schema_version: 2` (`"storage": "keychain"`) so Cask binary upgrades never invalidate macOS Keychain ACLs or trigger `SecurityAgent` prompts
