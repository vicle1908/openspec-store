# Proposal

## Why

Upstream MCP servers that require API keys in HTTP URLs, request headers, or child-process environment variables fail immediately when a single key exhausts its quota or hits rate limits (`HTTP 429` or MCP tool-execution quota errors), halting agent workflows across all connected clients. Since upstream `mcp-router/mcp-router` entered permanent End of Support on September 18, 2026 (`v0.6.4`), our workstation's standalone `platform/mcp-router` monorepo must natively manage multi-key pools, encrypted secret storage, quota-aware load balancing, transparent failover, and full UI key/token management.

## What Changes

- **Multi-Key Pool & Load-Balancing Engine (`MCPKeyPoolManager`)**:
  - Extend `MCPServerConfig` and `MCPServer` in `@mcp_router/shared` and `mcpServerConfigSchema` in `@mcp_router/remote-api-types` (`packages/remote-api-types/src/schema/servers.ts`) with `keyPoolConfig` (`MCPKeyPoolConfig`) and `customHeaders` (`Record<string, string>`).
  - Support five key injection targets: HTTP URL template (`{{KEY}}` / `${KEY}` in pathname/query), `Authorization: Bearer` header, custom HTTP header (e.g., `X-API-Key: {{KEY}}`), local stdio environment variable (e.g., `TAVILY_API_KEY`), and local CLI argument template (`{{KEY}}`), handling both literal and WHATWG percent-encoded tokens (`%7B%7BKEY%7D%7D` / `%24%7BKEY%7D`).
  - Implement four load-balancing strategies: `round-robin`, `weighted-round-robin`, `tiered-fallback` (priority spillover), and `least-used`, with configurable per-key RPM/quota limits and reset windows (`per-minute`, `daily`, `monthly`, `manual`).
- **Official MCP Spec-Compliant Quota Detection & Failover (`QuotaErrorDetector`)**:
  - Detect rate-limit and quota failures across both MCP error reporting mechanisms defined by the Model Context Protocol Specification (`2026-07-28`):
    1. Transport/protocol errors (`StreamableHTTPError`, `SseError`, `McpError` with HTTP `429`, `401`, `402`, `403` or `Retry-After` headers).
    2. Tool execution errors in `CallToolResult` (`isError: true` or structured JSON payloads such as `{"status": 429, "error": "..."}` / rate-limit text patterns).
  - False-Positive Quota Defense on Tool Search Outputs: Ensure `QuotaErrorDetector.inspectToolResult` strictly classifies a `CallToolResult` as a quota/rate-limit failure only when `result.isError === true`, OR when `result.content[*].text` strictly parses as a JSON object whose top-level `status === 429` or `error.status === 429` / `error.code === 429`, guaranteeing successful tool search results (`isError: false`) containing `"HTTP 429 Too Many Requests"` in prose text never trigger key cooldown.
  - Automatically place exhausted keys into `cooling_down` or `quota_exhausted` state and transparently retry the request on the next healthy key slot without failing the calling agent turn.
- **Hot-Reload Transport Reconciliation & Workspace Lifecycle Hygiene**:
  - Fix `MCPServerManager.updateServer` (`mcp-server-manager.ts`) so updating `keyPoolConfig`, `remoteUrl`, `bearerToken`, `customHeaders`, `env`, or `args` on a running server reconciles and reconnects affected client slots without requiring a manual stop/start.
  - Hot-Reload Reconnection Failure State: If `MCPServerManager.updateServer` fails to reconnect a running server after a config mutation (`remoteUrl`, `keyPoolConfig`, `bearerToken`, `customHeaders`, `env`, `args`), it MUST transition `server.status = "error"`, record `server.errorMessage`, and emit `server-updated` rather than leaving a `"running"` server with zero active client slots.
  - Reset active `MCPKeyPoolManager` client slots, metrics, and cooldown `NodeJS.Timeout` handles during `MCPServerManager.clearAllServers()`, `initializeAsync()`, and `PlatformAPIManager.configureForWorkspace()` (`platform-api-manager.ts`) so workspace switches never leak processes or timers.
- **Encryption at Rest, Just-in-Time (JIT) Decryption, URL Template SSRF Guard, and Log Redaction**:
  - Persist `key_pool_config` and `custom_headers` in SQLite via `McpServerManagerRepository.CREATE_TABLE_SQL` (for fresh workspaces) and `MainDatabaseMigration` (`20261016_add_key_pool_and_headers_columns` for existing workspaces), and preserve both fields in `CloudSyncService.serializeServer` (`cloud-sync.service.ts`).
  - Encrypt all `keyPoolConfig.keys[*].secret` values, `bearerToken`, sensitive `customHeaders` values, and sensitive `servers.env` entries (matching `SENSITIVE_KEY_PATTERN` in `sensitive-data.ts`) at rest using Electron `safeStorage` (`mcpr-secret:v1:` prefix).
  - Renderer IPC Secret Redaction / JIT Decryption Boundary: `keyPoolConfig.keys[*].secret` values MUST remain encrypted (`mcpr-secret:v1:`) in `McpServerManagerRepository.mapRowToEntity` (or be stripped/masked before `mcp:list` IPC serialization) and only decrypted just-in-time inside the main process when `MCPClient` / `MCPKeyPoolRuntime` constructs the upstream transport, preventing plaintext secret broadcast over Electron IPC unless explicitly requested for a single key reveal.
  - Redact resolved URL query secrets (`?api_key=...`), Bearer tokens, custom header secrets, and `mcpr-secret:v1:` ciphertexts from request logs (`mcp-logger.service.ts`) and error messages (`mcp-client.ts`) via `sanitizeForSecurityBoundary` and `redactSensitiveText` (`sensitive-data.ts`).
  - Omit empty `Authorization: ""` headers when `bearerToken` is unset on `StreamableHTTPClientTransport`, and reject HTTP control characters (`\r`, `\n`, NUL) in `customHeaders`.
  - Add `normalizeRemoteMcpUrlTemplate` in `remote-url-security.ts` restricting `{{KEY}}` and `${KEY}` placeholders strictly to URL path and query components (rejecting placeholders in scheme, userinfo, hostname, or port), preserving unencoded `{{KEY}}` / `${KEY}` tokens on save, and substituting `encodeURIComponent(key)` prior to runtime DNS/IP SSRF validation; handle WHATWG URL path percent-encoding where `new URL("https://host/v1/{{KEY}}/mcp").toString()` encodes braces in pathname to `%7B%7BKEY%7D%7D` (and `${KEY}` to `%24%7BKEY%7D`) so URL template substitution in `mcp-client.ts` and `remote-url-security.ts` matches and replaces both literal and percent-encoded placeholders with `encodeURIComponent(secret)`.
- **Key Management UI & Downstream Client Token Wiring**:
  - Add a dedicated **`Keys & Quota`** tab (`ServerDetailsKeyPool.tsx`) inside `ServerDetailsAdvancedSheet.tsx` for adding, masking/revealing, reordering, weighting, and resetting API keys with live usage/cooldown badges.
  - Unlock editing of `remoteUrl` and custom HTTP headers in `ServerDetailsRemote.tsx`, mask secrets in both view and edit modes in `ServerDetailsRemote.tsx` and `ServerDetailsEnvironment.tsx`, display key-pool health badges on `ServerCardCompact.tsx`, and support remote `url` / `headers` / `keyPoolConfig` entries in JSON import (`mcp-server-utils.ts`).
  - Unify `AppAPI.tokens` in `packages/shared/src/types/platform-api/domains/app-api.ts` with `Token` and `TokenGenerateOptions` from `token-types.ts`, wire `list`, `generate`, `revoke`, and `rotate` across all four `PlatformAPI` layers (`app-api.ts` / `server-api.ts`, `mcp-apps-manager.ipc.ts` / `mcp-server-manager.ipc.ts`, `preload.ts` / `global.d.ts`, `electron-platform-api.ts` / `remote-platform-api.ts`), and surface downstream client `MCPR_TOKEN` management in `McpAppsManager.tsx` while preserving existing `serverAccess` on rotation and legacy/expired token compatibility (`token-manager.test.cjs`).

### Explicit Non-Goals

- Re-enabling retired upstream cloud services (`SERVICE_RETIRED = true`), remote cloud sync, billing, or PostHog telemetry.
- Modifying `@mcp_router/cli` (`apps/cli`), which acts solely as a downstream stdio/HTTP client bridge and does not manage `MCPServerConfig` or SQLite.
- Modifying external AI coding client configurations (`~/.omp/agent/mcp.json`, `~/.claude.json`, `~/.cursor/mcp.json`, `~/.codex/config.toml`, `~/.hermes/config.yaml`, `~/.config/goose/config.yaml`), which continue connecting unchanged to `localhost:3282`.
- Introducing external database dependencies outside the existing embedded `better-sqlite3` and `shared-config.json` storage layer.

### Affected Ownership Boundaries

- **Planning Root**: `/Users/androidteam/Developer/platform/openspec-store` (`store_id: openspec-store`).
- **External Implementation Root**: `/Users/androidteam/Developer/platform/mcp-router` (independent Git repository; packages `@mcp_router/shared`, `@mcp_router/remote-api-types`, `@mcp_router/electron`).
- **Two-Phase Commit Governance**: Implementation changes are verified and committed first in `/Users/androidteam/Developer/platform/mcp-router` using path-scoped staging (`git add packages/ apps/ tools/`, NEVER `git add -A` or staging `graphify-out/` per `platform/mcp-router/AGENTS.md`); execution evidence (`evidence.md`), spec sync, archive, and governance commit are recorded second in `/Users/androidteam/Developer/platform/openspec-store`.

## Capabilities

### New Capabilities
- `mcp-router-multi-key-load-balancing`: Multi-API-key pooling, OS keychain encryption at rest, template-based URL/header/stdio key injection, quota-aware load balancing with transparent failover, hot-reload transport reconciliation, workspace lifecycle teardown, and UI key/token management in `platform/mcp-router`.

### Modified Capabilities
<!-- No existing spec requirements in openspec-store are modified. -->

## Impact

- **`packages/shared`**: `src/types/mcp-types.ts`, `src/types/token-types.ts`, `src/types/platform-api/domains/server-api.ts`, `src/types/platform-api/domains/app-api.ts`, `src/types/platform-api/index.ts`, `src/types/index.ts`.
- **`packages/remote-api-types`**: `src/schema/servers.ts` (`mcpServerConfigSchema` Zod validation for `keyPoolConfig` and `customHeaders`).
- **`apps/electron` (Main Process)**:
  - `src/main/infrastructure/database/main-database-migration.ts`
  - `src/main/modules/mcp-server-manager/mcp-server-manager.repository.ts`
  - `src/main/modules/mcp-server-manager/mcp-key-pool-manager.ts` (new)
  - `src/main/modules/mcp-server-manager/quota-error-detector.ts` (new)
  - `src/main/modules/mcp-server-manager/mcp-server-manager.ts` & `mcp-server-manager.ipc.ts`
  - `src/main/modules/workspace/platform-api-manager.ts` & `src/main/modules/cloud-sync/cloud-sync.service.ts`
  - `src/main/modules/mcp-apps-manager/mcp-client.ts`, `token-manager.ts`, `mcp-apps-manager.service.ts`, & `mcp-apps-manager.ipc.ts`
  - `src/main/modules/mcp-server-runtime/request-handlers.ts` & `src/main/modules/tool-catalog/tool-catalog-handler.ts`
  - `src/main/modules/mcp-logger/mcp-logger.service.ts`
  - `src/main/utils/remote-url-security.ts`, `src/main/utils/secret-storage.ts`, & `src/main/utils/sensitive-data.ts`
- **`apps/electron` (Preload, Renderer UI & Locales)**:
  - `src/preload.ts`, `src/global.d.ts`
  - `src/renderer/platform-api/electron-platform-api.ts`, `src/renderer/platform-api/remote-platform-api.ts`
  - `src/renderer/stores/server-editing-store.ts`
  - `src/renderer/components/mcp/server/server-details/ServerDetailsKeyPool.tsx` (new)
  - `src/renderer/components/mcp/server/server-details/ServerDetailsAdvancedSheet.tsx`, `ServerDetailsGeneralSettings.tsx`, `ServerDetailsRemote.tsx`, `ServerDetailsEnvironment.tsx`
  - `src/renderer/components/mcp/server/ServerCardCompact.tsx`, `Manual.tsx`, `utils/mcp-server-utils.ts`
  - `src/renderer/components/mcp/apps/McpAppsManager.tsx`
  - `src/renderer/components/Home.tsx`
  - `src/locales/en.json`, `src/locales/ja.json`, `src/locales/zh.json` & `tools/find-unused-i18n.mjs`
