# Proposal: Package and Deploy MCP Router v0.6.4 Runtime

## Why

Following the implementation and archive of `2026-10-17-upgrade-mcp-router-multi-key-load-balancing` (`68c047d` and `8550cb9`), the live macOS application bundle at `/Applications/MCP Router.app` still ran the pre-upgrade `v0.6.3` `app.asar` bundle on port `3282`, and the monorepo `package.json` still pinned `"packageManager": "pnpm@10.22.0"` rather than the active workstation `pnpm@12.14.0` toolchain. Furthermore, packaging and booting the `v0.6.4` Electron bundle under Node 26, TypeScript 7.0.2 (`tsgo`), `pnpm@12.14.0`, and `@modelcontextprotocol/sdk@1.29.0` exposed four packaging and runtime defects that blocked `.app` bundle creation and multi-request HTTP routing on `127.0.0.1:3282`.

## What Changes

- **Monorepo `pnpm@12.14.0` & Electron Packaging Compatibility (`package.json`, `pnpm-workspace.yaml`, `apps/electron/webpack.*`, `apps/electron/forge.config.ts`)**:
  - Update `"packageManager": "pnpm@12.14.0"` in `platform/mcp-router/package.json` and migrate workspace `overrides`, `onlyBuiltDependencies`, `verifyDepsBeforeRun: false`, `nodeLinker: hoisted`, and `shamefullyHoist: true` into `pnpm-workspace.yaml` so `pnpm@12.14.0` and `@electron-forge/core` execute natively.
  - Replace legacy `ts-loader` and `ForkTsCheckerWebpackPlugin` (which call `typescript.readConfigFile`, removed in TypeScript 7.0.2 `@typescript/native-preview`) with `apps/electron/webpack-esbuild-loader.cjs` (`esbuild.transform` with `jsx: "automatic"`, `target: "es2022"`).
  - Override `@electron/packager/dist/unzip.js` `extractElectronZip` in `apps/electron/forge.config.ts` to use macOS `/usr/bin/ditto -x -k` (avoiding the Node 26 `extract-zip` / `fd-slicer` stream stall) and normalize `brace-expansion@5` CJS exports on cached `minimatch` instances inside `@electron/asar`.
  - Rebuild native addons (`better-sqlite3`, `argon2`) against Electron `39.8.10` (`ABI 140`).
- **Stateless Per-Request & Per-Session MCP Aggregator Transport (`aggregator-server.ts`, `mcp-http-server.ts`)**:
  - Update `AggregatorServer` (`createServer()` / `closeServer()`) and `MCPHttpServer` (`configureMcpRoute` and `configureMcpSseRoute` with `sseSessionServers`) to instantiate and clean up a fresh `Server` and `StreamableHTTPServerTransport({ sessionIdGenerator: undefined })` per `POST /mcp` request and per `GET /mcp/sse` session, preventing `@modelcontextprotocol/sdk@1.29.0`'s single-use stateless transport guard from throwing HTTP 500 on subsequent requests.
- **Startup Row Mapping Secret Preservation (`mcp-server-manager.repository.ts`)**:
  - Remove eager `decryptSecret` and redundant `secretToStorage` calls from `McpServerManagerRepository.mapRowToEntity` so stored `mcpr-secret:v1:` secrets remain encrypted across `mcp:list` IPC and startup `getAllServers()` never blocks on macOS Keychain `SecurityAgent` dialogs before binding port `3282`.
- **Live `/Applications/MCP Router.app` `v0.6.4` Deployment & Verification**:
  - Package `out/MCP Router-darwin-arm64/MCP Router.app`, verify ad-hoc code signing and `ElectronAsarIntegrity`, deploy to `/Applications/MCP Router.app` (with rollback backup at `/tmp/MCP-Router-backup-20261017.app`), verify SQLite migration `20261016_add_key_pool_and_headers_columns` in `~/Library/Application Support/MCP Router/mcprouter.db`, and verify live multi-request MCP routing on `127.0.0.1:3282`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mcp-router-multi-key-load-balancing`: Add normative requirements for deployed `/Applications/MCP Router.app` `v0.6.4` bundle parity, `pnpm@12.14.0` workspace metadata alignment, per-request stateless `StreamableHTTPServerTransport` isolation on `POST /mcp`, and non-blocking encrypted secret preservation in `McpServerManagerRepository.mapRowToEntity`.

## Impact

- **Repository**: `/Users/androidteam/Developer/platform/mcp-router` (commit `7bce8df3f6109247ec03a6a6e6c0794e8c0f1818`)
- **Live Runtime**: `/Applications/MCP Router.app` (`v0.6.4`, PID `30820` listening on `127.0.0.1:3282`)
- **Documentation**: `/Users/androidteam/Developer/wiki/entities/mcp-router.md` and `/Users/androidteam/Developer/wiki/log.md`
