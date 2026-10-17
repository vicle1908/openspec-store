# Verification Evidence: `package-and-deploy-mcp-router-v0-6-4-runtime`

- **Change**: `package-and-deploy-mcp-router-v0-6-4-runtime`
- **Target Repository**: `/Users/androidteam/Developer/platform/mcp-router`
- **Commit SHA**: `7bce8df3f6109247ec03a6a6e6c0794e8c0f1818` (`fix(electron): restore TS7/Node26 packaging and per-request stateless MCP transport`, 10 files changed, `+416 / -273`)
- **Date**: 2026-10-17

## 1. Build, Typecheck, Lint & Unit Test Evidence

| Gate | Command | Exit Code | Result |
|---|---|---|---|
| **pnpm Config Check** | `pnpm config get node-linker` | `0` | `hoisted` (`packageManager: "pnpm@12.14.0"` in `package.json`; `overrides` and `onlyBuiltDependencies` in `pnpm-workspace.yaml`) |
| **Monorepo Typecheck** | `pnpm typecheck` (`turbo run typecheck`) | `0` | **8/8 tasks passed** (`@mcp_router/shared`, `@mcp_router/remote-api-types`, `@mcp_router/ui`, `@mcp_router/cli`, `@mcp_router/electron`) |
| **Workspace Test Suite** | `pnpm test` (`pnpm -r test`) | `0` | **71/71 tests passed** (`apps/electron`: 64/64 across 16 suites; `packages/shared`: 4/4; `apps/cli`: 3/3) |
| **Production Build** | `pnpm build` (`turbo run build`) | `0` | **4/4 build targets succeeded** |
| **i18n Key Parity** | `node tools/find-unused-i18n.mjs` | `0` | `No unused i18n keys found.` |
| **Electron Packaging** | `pnpm --filter @mcp_router/electron run package` | `0` | Packaged `/Users/androidteam/Developer/platform/mcp-router/apps/electron/out/MCP Router-darwin-arm64/MCP Router.app` under `pnpm@12.14.0` |

## 2. Deployment, Code Signature, SQLite Migration & Live Port `3282` Evidence

- **Bundle Version**: `defaults read "/Applications/MCP Router.app/Contents/Info" CFBundleShortVersionString` $\rightarrow$ `0.6.4`
- **Code Signature & ASAR Integrity**: `codesign --verify --deep --strict "/Applications/MCP Router.app"` $\rightarrow$ exit code `0` (`ElectronAsarIntegrity` SHA-256 verified)
- **Rollback Backup**: `/tmp/MCP-Router-backup-20261017.app` preserved
- **Live SQLite Migration (`~/Library/Application Support/MCP Router/mcprouter.db`)**:
  - `SELECT * FROM migrations WHERE id='20261016_add_key_pool_and_headers_columns';` $\rightarrow$ `20261016_add_key_pool_and_headers_columns|1792238012`
  - `PRAGMA table_info(servers);` $\rightarrow$ `22|key_pool_config|TEXT|0||0`, `23|custom_headers|TEXT|0||0`
- **Live Listener (`127.0.0.1:3282`)**:
  - `lsof -i :3282` $\rightarrow$ `MCP\x20Ro 30820 androidteam 58u IPv4 ... TCP localhost:datusorb (LISTEN)`
- **Consecutive Live MCP Tool Calls (Stateless Transport Verification)**:
  - `wiki_read` (`{"path": "entities/mcp-router.md"}`) $\rightarrow$ succeeded (`status: active`)
  - `resolve_library_id` (`{"query": "Electron safeStorage API", "libraryName": "electron"}`) $\rightarrow$ succeeded (`/electron/electron`, 5367 snippets)
