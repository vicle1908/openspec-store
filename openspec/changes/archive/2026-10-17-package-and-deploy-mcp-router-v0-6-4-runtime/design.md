# Design: Package and Deploy MCP Router v0.6.4 Runtime

## Context

`platform/mcp-router` was upgraded in commits `68c047d` and `8550cb9` (`2026-10-17-upgrade-mcp-router-multi-key-load-balancing`) to support per-server multi-key pools, quota-aware load balancing, and `safeStorage` secret encryption, while earlier dependency modernization upgraded the workspace to TypeScript `7.0.2`, Node `26.12.0`, `@modelcontextprotocol/sdk@1.29.0`, and `pnpm@12.14.0`. Packaging the macOS `arm64` `.app` bundle and deploying it to `/Applications/MCP Router.app` required resolving four build/runtime incompatibilities.

## Decisions

### Decision 1: `pnpm@12.14.0` Workspace Settings Migration (`package.json`, `pnpm-workspace.yaml`)
`pnpm 12` deprecates the `"pnpm"` block in `package.json` (`ERR_PNPM_VERIFY_DEPS_BEFORE_RUN`) and `.npmrc` hoisting directives (`node-linker`). We moved `overrides` and `onlyBuiltDependencies` out of `package.json` into `pnpm-workspace.yaml` alongside `verifyDepsBeforeRun: false`, `nodeLinker: hoisted`, and `shamefullyHoist: true`, while setting `"packageManager": "pnpm@12.14.0"` in `package.json`.

### Decision 2: TypeScript 7.0.2 (`tsgo`) Webpack Loader & Node 26 Packaging Hooks (`webpack.*`, `forge.config.ts`)
- Replaced `ts-loader` and `ForkTsCheckerWebpackPlugin` (which invoke `typescript.readConfigFile`, removed in TypeScript 7.0.2) with `apps/electron/webpack-esbuild-loader.cjs` (`esbuild.transform` with `jsx: "automatic"`, `target: "es2022"`). Full static typechecking runs via `pnpm typecheck` (`tsc --noEmit`).
- Overrode `@electron/packager/dist/unzip.js` `extractElectronZip` in `apps/electron/forge.config.ts` on `darwin` to use `/usr/bin/ditto -x -k` (bypassing `extract-zip` / `fd-slicer` stream stalls on Node 26) and patched cached `minimatch` instances in `require.cache` so `@electron/asar` works with `brace-expansion@5`'s `{ expand }` CJS export shape.

### Decision 3: Per-Request Stateless `StreamableHTTPServerTransport` (`aggregator-server.ts`, `mcp-http-server.ts`)
In `@modelcontextprotocol/sdk@1.29.0`, `WebStandardStreamableHTTPServerTransport` enforces single-use when `sessionIdGenerator` is `undefined` (`_hasHandledRequest`). `AggregatorServer` now exposes `createServer()` and `closeServer(server)` tracked in `activeServers`, and `MCPHttpServer` creates and cleans up a fresh `Server` + `StreamableHTTPServerTransport` per `POST /mcp` request and per `GET /mcp/sse` session.

### Decision 4: Non-Blocking Encrypted Secret Preservation in `mapRowToEntity` (`mcp-server-manager.repository.ts`)
`McpServerManagerRepository.mapRowToEntity` preserves `env`, `customHeaders`, `keyPoolConfig`, and `bearerToken` values as stored in SQLite (`mcpr-secret:v1:...`) without calling `decryptSecret` or `secretToStorage` on read. Decryption occurs strictly just-in-time in `MCPClient.connectToMCPServer`, `MCPKeyPoolManager.buildDerivedConfig`, and `MCPKeyPoolManager.revealKeySecret`, preventing startup `getAllServers()` from blocking on macOS Keychain `SecurityAgent` prompts and keeping secrets encrypted across `mcp:list` IPC.
