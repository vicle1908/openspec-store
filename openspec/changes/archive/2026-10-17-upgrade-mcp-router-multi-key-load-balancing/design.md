# Design

## Context

See `proposal.md` (`Why`) and `specs/mcp-router-multi-key-load-balancing/spec.md` for motivation and normative requirements.

`platform/mcp-router` is a pnpm 10.22.0 / Turborepo 2.11.7 / TypeScript 7.0.2 monorepo whose Electron main process (`apps/electron`) hosts the local MCP HTTP/SSE aggregator on `127.0.0.1:3282`. Deep codebase and security inspection identified seven key architectural constraints:
1. `MCPServerManager` (`mcp-server-manager.ts:284`) stores a 1-to-1 `this.clients: Map<string, Client>` per `serverId`, and `RequestHandlers` (`request-handlers.ts:713`) / `ToolCatalogHandler` (`tool-catalog-handler.ts:311`) execute `client.callTool` directly without retry or key rotation.
2. `McpServerManagerRepository` (`mcp-server-manager.repository.ts:21-46, 208-219`) initializes fresh tables via `CREATE_TABLE_SQL` and encrypts `bearer_token` via `secretToStorage(..., safeStorage)` (`mcpr-secret:v1:` prefix in `secret-storage.ts`), whereas `servers.env` is persisted as plaintext JSON and `CloudSyncService.serializeServer` (`cloud-sync.service.ts:369-386`) serializes workspace server bundles.
3. `MCPServerManager.updateServer` (`mcp-server-manager.ts:366-392`) updates SQLite and in-memory metadata without reconnecting active client transports when credentials or URLs change, and `PlatformAPIManager.configureForWorkspace` (`platform-api-manager.ts:110-165`) switches workspace databases without tearing down multi-key client slots or cooldown timers.
4. `McpLoggerService.recordMcpRequestLog` (`mcp-logger.service.ts:111-136`) mutates `logEntry.params` in-place and does not sanitize URL query secrets (`?api_key=...`), Bearer tokens, or upstream error messages before writing to SQLite `requestLogs`.
5. `ServerDetailsRemote.tsx:38, 106-113` disables editing `remoteUrl` after server creation and renders `bearerToken` in plaintext in view mode; `ServerDetailsEnvironment.tsx:111-121` renders `env` values in plaintext; `mcp-server-utils.ts:44` rejects remote `url` entries during JSON import.
6. `packages/shared/src/types/platform-api/domains/app-api.ts:8-18` declares duplicate local `Token` and `TokenGenerateOptions` interfaces that conflict with `packages/shared/src/types/token-types.ts:13-30`, while `ElectronPlatformAPI.apps.tokens` (`electron-platform-api.ts:93-103`) throws unimplemented errors instead of wiring `TokenManager` (`token-manager.ts`) over IPC.
7. `packages/remote-api-types/src/schema/servers.ts:5-55` defines `mcpServerConfigSchema` (Zod validator used by `RemotePlatformAPI`), `tools/eslint-rules/no-scattered-types.js` and `no-type-reexport.js` enforce strict type placement in `packages/shared/src/types/`, `tools/find-unused-i18n.mjs` scans `en.json`, `ja.json`, and `zh.json` for unused/missing locale keys, and `knip.json` enforces zero unused exports/types.

## Goals / Non-Goals

**Goals:**
- Provide a unified, per-server multi-API-key pool and quota-aware load balancer (`MCPKeyPoolManager`) supporting URL templates, Bearer tokens, custom HTTP headers, stdio environment variables, and CLI arguments.
- Comply with the official Model Context Protocol Specification (`2026-07-28`) and `@modelcontextprotocol/sdk@1.32.0` transport contracts for both protocol/transport errors and tool-execution error payloads.
- Maintain strict at-rest secret encryption (`safeStorage`), just-in-time (JIT) decryption at the transport creation boundary, log/error secret redaction, and UI secret masking.
- Synchronize all four layers of `PlatformAPI` (`@mcp_router/shared`, `preload.ts` + `global.d.ts`, IPC handlers, and `ElectronPlatformAPI` / `RemotePlatformAPI`) plus `@mcp_router/remote-api-types` Zod schemas so `turbo run typecheck`, `knip`, `find-unused-i18n.mjs`, and ESLint pass with zero violations.

**Non-Goals:**
- Cross-server shared global key vaults (each MCP server owns its key pool configuration directly, keeping export/import and lifecycle self-contained).
- Modifying `@mcp_router/cli` (`apps/cli`), which acts solely as a downstream stdio/HTTP bridge (`commands/connect.ts`, `commands/serve.ts`) and does not touch `MCPServerConfig` or SQLite.
- Re-enabling retired cloud sync or remote workspace tRPC mutations (`SERVICE_RETIRED = true`).

## Decisions

### Decision 1: Per-Server Client Slot Pool with Lazy Stdio Spawning & Workspace Teardown (`MCPKeyPoolManager`)
- **Choice**: Extend `MCPServerManager` with `MCPKeyPoolManager` (`apps/electron/src/main/modules/mcp-server-manager/mcp-key-pool-manager.ts`). When `server.keyPoolConfig?.enabled` is `false` or absent, the manager preserves legacy single-client behavior (`this.clients.get(serverId)`). When `enabled: true` with $N$ active keys:
  - **Remote (`remote` / `remote-streamable`)**: Maintain lightweight `Client` slots keyed by `(serverId, keyId)`. Each slot resolves its interpolated `remoteUrl`, `bearerToken`, or `customHeaders`.
  - **Local (`local` stdio)**: Spawn the primary selected key slot on `startServer`, and lazily spawn secondary stdio `Client` slots on demand when the strategy selects them or when a failover occurs.
  - **Hot-Reload & Workspace Lifecycle**:
    - `MCPServerManager.updateServer` diffs connection-affecting fields (`command`, `args`, `env`, `remoteUrl`, `bearerToken`, `customHeaders`, `keyPoolConfig`) and calls `keyPoolManager.reconcileServer(id, updatedServer)` when `server.status === "running"`.
    - **Hot-Reload Reconnection Failure State**: If reconnecting an updated server fails (`connectResult.status !== "success"` or exception caught), `MCPServerManager.updateServer` MUST transition `server.status = "error"`, record `server.errorMessage` (from `connectResult.error` or exception message), and emit `server-updated`, rather than leaving the server in `"running"` status with zero active client slots or stale connections.
    - `MCPKeyPoolManager.reset()` cancels all pending cooldown `NodeJS.Timeout` timers, clears in-memory rate-limit counters, and closes all secondary `Client` slots. It is invoked from `MCPServerManager.clearAllServers()`, `MCPServerManager.initializeAsync()`, and `PlatformAPIManager.configureForWorkspace()` (`platform-api-manager.ts:125-155`).
- **Rationale**: Reuses the existing `MCPClient.connectToMCPServer` (`mcp-client.ts:24`) factory while avoiding redundant child processes at startup and preventing cross-workspace timer/socket leaks.

### Decision 2: Dual-Layer Quota Error Classification Validated Against Official MCP Spec (`2026-07-28`)
- **Choice**: Implement `QuotaErrorDetector` (`apps/electron/src/main/modules/mcp-server-manager/quota-error-detector.ts`) that inspects both thrown errors and resolved `CallToolResult` payloads:
  1. **Transport / Protocol Layer**: Checks `StreamableHTTPError.code` (`@modelcontextprotocol/sdk/client/streamableHttp.js`), `SseError.code` (`@modelcontextprotocol/sdk/client/sse.js`), and `McpError` messages for HTTP `429`, `402`, or `401`/`403` accompanied by quota/rate-limit indicators, extracting `Retry-After` delta-seconds when available.
  2. **Tool Execution Layer (`CallToolResult`) & False-Positive Quota Defense**: Per the official MCP Specification (`2026-07-28`, *Server -> Tools -> Error Handling*), upstream API rate limits reported inside tool results use `isError: true` or structured JSON text in `result.content[*].text` (such as Tavily's `{"error":"Search failed","status":429,"detail":{"error":"...excessive requests..."}}`). To prevent false-positive cooldown on successful search results returning documentation, technical blogs, or prose referencing rate limits:
     - `QuotaErrorDetector.inspectToolResult` MUST ONLY classify a `CallToolResult` as a quota/rate-limit failure when `result.isError === true`, OR when `result.content[*].text` strictly parses as a valid JSON object whose top-level `status === 429` or nested `error.status === 429` / `error.code === 429`.
     - When `result.isError` is `false` or undefined, unstructured text strings containing `"HTTP 429 Too Many Requests"` or rate-limit terms (e.g. documentation search results) MUST NOT be classified as quota errors and MUST NOT trigger key cooldown.
- **Rationale**: Live verification against Tavily MCP confirmed that upstream MCP servers frequently return HTTP 200 JSON-RPC responses wrapping a `429` JSON payload inside `content[0].text`, while broad string matching caused spurious cooldown on informational searches.

### Decision 3: Template-Aware URL Security Validation & Clean Header Construction
- **Choice**:
  - Add `normalizeRemoteMcpUrlTemplate(rawUrl: string): string` and `interpolateRemoteMcpUrl(rawUrl: string, keySecret?: string): string` in `apps/electron/src/main/utils/remote-url-security.ts`:
    1. Reject any URL where `{{KEY}}` or `${KEY}` appears before the path/query boundary (forbidding placeholders in scheme, username, password, hostname, or port).
    2. Temporarily substitute `__MCPR_KEY_PLACEHOLDER__` to validate protocol (`https:`), credentials absence, and hostname SSRF rules via `normalizeRemoteMcpUrl`, then restore the original `{{KEY}}` / `${KEY}` token in the returned normalized string so `McpServerManagerRepository.serializeEntityData` (`mcp-server-manager.repository.ts:204`) does not corrupt `{{KEY}}` into `%7B%7BKEY%7D%7D`.
    3. **WHATWG URL Path Percent-Encoding Safeguard**: Per WHATWG URL standards, `new URL("https://host/v1/{{KEY}}/mcp").toString()` percent-encodes braces in `pathname` to `%7B%7BKEY%7D%7D` (and `${KEY}` to `%24%7BKEY%7D`) while leaving query string braces literal. `interpolateRemoteMcpUrl` and URL template substitution in `mcp-client.ts` and `remote-url-security.ts` MUST match and replace both literal `{{KEY}}`/`${KEY}` and percent-encoded `%7B%7BKEY%7D%7D`/`%24%7BKEY%7D` with `encodeURIComponent(secret)`.
    4. At connect time, substitute `encodeURIComponent(decryptedKey)` before calling `validateRemoteMcpUrl`.
  - Validate `customHeaders` names and values against HTTP control characters (`<= 0x1f` or `0x7f`), and fix `mcp-client.ts:50-54` so `StreamableHTTPClientTransport` only attaches `Authorization: Bearer ...` when a non-empty token is present.

### Decision 4: Encryption at Rest (`safeStorage`), JIT Decryption, Workspace Bundle Parity, and Log Redaction
- **Choice**:
  - **Dual Schema Initialization**: Update both `McpServerManagerRepository.CREATE_TABLE_SQL` (`mcp-server-manager.repository.ts:21-46` for fresh workspaces and `WorkspaceService.copyDataToNewWorkspace` at `workspace.service.ts:281-342`) and `MainDatabaseMigration` (`20261016_add_key_pool_and_headers_columns` in `main-database-migration.ts` for existing workspaces) with `key_pool_config TEXT` and `custom_headers TEXT`.
  - **At-Rest Encryption, Renderer IPC Redaction, & JIT Decryption Boundary**:
    - Export `SENSITIVE_KEY_PATTERN` and `redactSensitiveText(text: string, knownSecrets?: string[]): string` in `apps/electron/src/main/utils/sensitive-data.ts`.
    - In `McpServerManagerRepository.serializeEntityData`, encrypt `bearerToken`, every `keyPoolConfig.keys[*].secret`, every `customHeaders[k]` matching `SENSITIVE_KEY_PATTERN`, and every `entity.env[k]` matching `SENSITIVE_KEY_PATTERN` via `secretToStorage(..., safeStorage)`.
    - **Renderer IPC Secret Redaction & JIT Decryption Boundary**: In `McpServerManagerRepository.mapRowToEntity`, `keyPoolConfig.keys[*].secret` values MUST remain encrypted (`mcpr-secret:v1:`) (or be stripped/masked before `mcp:list` IPC serialization). Plaintext secrets are NEVER broadcast over Electron IPC to the renderer process during standard server listing. Decryption is performed strictly just-in-time inside the main process when `MCPClient` or `MCPKeyPoolRuntime` constructs the upstream transport, or via an explicit user-initiated single-key reveal action.
    - Include `keyPoolConfig` and `customHeaders` in `CloudSyncService.serializeServer` (`cloud-sync.service.ts:369-386`) so workspace bundle serialization/rollback preserves them.
  - **Log & Error Redaction**:
    - In `McpLoggerService.recordMcpRequestLog` (`mcp-logger.service.ts:111-136`), clone `logEntry.params` instead of mutating `request.params` in-place, and apply `sanitizeForSecurityBoundary` + `redactSensitiveText` to `requestParams`, `responseData`, and `errorMessage`.
    - In `MCPClient.connectToMCPServer` (`mcp-client.ts:118-123`), redact any resolved URL query secrets or key secrets from `errorMessage` before logging or returning.
- **Transaction Boundaries**:
  - Schema migration `20261016_add_key_pool_and_headers_columns` runs inside `SqliteManager`'s migration transaction (`BEGIN` / `COMMIT`).
  - Server config updates write atomically to the `servers` row (`id PRIMARY KEY`) in `better-sqlite3`.
  - Downstream client token mutations (`TokenManager` $\rightarrow$ `SharedConfigManager`) execute synchronous atomic JSON writes to `shared-config.json`.

### Decision 5: Downstream Client Token Unification (`app-api.ts` & `TokenManager`) & `RemotePlatformAPI` Parity
- **Choice**:
  - Remove the duplicate local `interface Token` and `interface TokenGenerateOptions` from `packages/shared/src/types/platform-api/domains/app-api.ts:8-18` and import `Token` and `TokenGenerateOptions` from `../../token-types`.
  - Wire `AppAPI.tokens` (`list(): Promise<Token[]>`, `generate(options: TokenGenerateOptions): Promise<Token>`, `revoke(tokenId: string): Promise<boolean>`, `rotate(clientId: string, options?: Partial<TokenGenerateOptions>): Promise<Token>`) through `mcp-apps-manager.ipc.ts` $\rightarrow$ `preload.ts` $\rightarrow$ `electron-platform-api.ts`.
  - In `TokenManager.generateToken` (`token-manager.ts:20, 40`), omit `expiresAt` (`undefined`) when `options.neverExpires === true` or `options.expiresIn === 0`, and in `rotateToken`, preserve the client's existing `serverAccess` permissions by default while keeping `TokenManager.validateToken` backward-compatible with legacy/expired tokens (`apps/electron/tests/token-manager.test.cjs:72-105`).
  - Extend `packages/remote-api-types/src/schema/servers.ts` (`mcpServerConfigSchema`) with Zod schemas for `customHeaders` and `keyPoolConfig`, and add `resetKeyCooldown` and `resetKeyUsage` to `RemotePlatformAPI.servers` (`remote-platform-api.ts`) so `@mcp_router/remote-api-types` and `@mcp_router/electron` compile cleanly.

### Decision 6: Three-Locale Synchronization & Static i18n Key Scanning
- **Choice**: Add all new UI translation keys across `apps/electron/src/locales/en.json`, `ja.json`, and `zh.json` using literal `t("...")` or template prefix `t(\`...\${var}\`)` patterns compatible with `tools/find-unused-i18n.mjs`.

## Risks / Trade-offs

- **[Risk] Non-idempotent tool calls retried on false-positive quota match** $\rightarrow$ **Mitigation**: Restrict `QuotaErrorDetector` payload matching strictly to `isError: true` or valid JSON payloads with top-level/error `status === 429` / `code === 429`. Prose text containing rate-limit references without `isError` never triggers cooldown.
- **[Risk] WHATWG URL path percent-encoding breaking placeholder substitution** $\rightarrow$ **Mitigation**: `interpolateRemoteMcpUrl` and `mcp-client.ts` match and replace both literal `{{KEY}}`/`${KEY}` and percent-encoded `%7B%7BKEY%7D%7D`/`%24%7BKEY%7D` tokens.
- **[Risk] Hot-reload reconnection failure leaves zombie running server** $\rightarrow$ **Mitigation**: Transition `server.status = "error"`, record `server.errorMessage`, and emit `server-updated` when reconnection fails.
- **[Risk] Plaintext API keys leaked over Electron IPC to renderer** $\rightarrow$ **Mitigation**: Keep secrets encrypted (`mcpr-secret:v1:`) in repository entity mapping; decrypt strictly JIT in main process before transport connection.
- **[Risk] Excess child processes or leaked timers across workspace switches** $\rightarrow$ **Mitigation**: Use lazy on-demand worker slot creation for `local` servers and invoke `MCPKeyPoolManager.reset()` during `clearAllServers()`, `initializeAsync()`, and `PlatformAPIManager.configureForWorkspace()`.
- **[Risk] Custom ESLint (`no-scattered-types`, `no-type-reexport`) or Knip (`unused exports/types`) failures** $\rightarrow$ **Mitigation**: Place all shared interfaces and type aliases in `packages/shared/src/types/` and consume all exported types across `apps/electron` and `packages/remote-api-types`.
## Migration Plan

1. **Database Migration**: On startup, `MainDatabaseMigration` checks `PRAGMA table_info(servers)` and executes `ALTER TABLE servers ADD COLUMN key_pool_config TEXT` and `ALTER TABLE servers ADD COLUMN custom_headers TEXT` idempotently, matching `McpServerManagerRepository.CREATE_TABLE_SQL`. Existing servers default to `keyPoolConfig: undefined` and `customHeaders: undefined`.
2. **Rollback**: Because the new SQLite columns are nullable and legacy single-key fields (`bearer_token`, `env`, `remote_url`) remain intact, rolling back to the prior commit continues operating with existing server records without data loss.
