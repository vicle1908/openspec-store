# Tasks

## 1. Toolchain & Packaging Configuration (`platform/mcp-router`)

- [x] 1.1 Update `"packageManager": "pnpm@12.14.0"` in `/Users/androidteam/Developer/platform/mcp-router/package.json` and migrate `overrides`, `onlyBuiltDependencies`, `verifyDepsBeforeRun: false`, `nodeLinker: hoisted`, and `shamefullyHoist: true` to `/Users/androidteam/Developer/platform/mcp-router/pnpm-workspace.yaml`; verify `pnpm config get node-linker` outputs `hoisted`.
- [x] 1.2 Add `/Users/androidteam/Developer/platform/mcp-router/apps/electron/webpack-esbuild-loader.cjs`, update `webpack.rules.ts` and `webpack.plugins.ts` for TypeScript 7.0.2 compatibility, and update `forge.config.ts` with macOS `/usr/bin/ditto -x -k` zip extraction and `brace-expansion@5` `minimatch` interop; verify `pnpm typecheck` and `pnpm build` succeed.

## 2. Runtime Stateless Transport & Secret Storage Boundaries (`apps/electron`)

- [x] 2.1 Update `AggregatorServer` (`apps/electron/src/main/modules/mcp-server-runtime/aggregator-server.ts`) and `MCPHttpServer` (`apps/electron/src/main/modules/mcp-server-runtime/http/mcp-http-server.ts`) to instantiate and clean up per-request `Server` and stateless `StreamableHTTPServerTransport` instances on `POST /mcp` and per-session `Server` instances on `GET /mcp/sse`, and update `apps/electron/tests/mcp-http-server-auth.test.cjs`; verify `pnpm test` passes all 71 workspace unit tests.
- [x] 2.2 Remove eager `decryptSecret` and redundant `secretToStorage` calls from `McpServerManagerRepository.mapRowToEntity` (`apps/electron/src/main/modules/mcp-server-manager/mcp-server-manager.repository.ts:174-214`) so stored `mcpr-secret:v1:` secrets remain encrypted across `mcp:list` IPC and startup row mapping never blocks on macOS Keychain `SecurityAgent` prompts.

## 3. macOS Bundle Deployment & Live Verification (`/Applications/MCP Router.app`)

- [x] 3.1 Rebuild Electron native modules (`better-sqlite3`, `argon2`) for Electron `39.8.10`, package `out/MCP Router-darwin-arm64/MCP Router.app` via `pnpm --filter @mcp_router/electron run package`, sign and verify with `codesign --verify --deep --strict`, deploy to `/Applications/MCP Router.app` (preserving rollback backup at `/tmp/MCP-Router-backup-20261017.app`), and commit changes in `platform/mcp-router` (`7bce8df3f6109247ec03a6a6e6c0794e8c0f1818`).
- [x] 3.2 Launch `/Applications/MCP Router.app` and verify `defaults read "/Applications/MCP Router.app/Contents/Info" CFBundleShortVersionString` outputs `0.6.4`, SQLite migration `20261016_add_key_pool_and_headers_columns` is applied in `~/Library/Application Support/MCP Router/mcprouter.db`, `lsof -i :3282` confirms the active listener, and consecutive MCP tool calls (`wiki_read` and `resolve_library_id`) succeed.
