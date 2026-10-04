# Tasks

## 1. Toolchain Migration and Test Refactoring

- [x] 1.1 Remove `ts-node` and install `tsx` in `platform/mcp-router/apps/electron/package.json`
- [x] 1.2 Refactor `security-utils.test.cjs`, `mcp-http-server-auth.test.cjs`, and `token-manager.test.cjs` to use `require("tsx/cjs")`
- [x] 1.3 Refactor `service-retirement.test.cjs` to use `esbuild.transformSync` instead of removed `ts.transpileModule`
- [x] 1.4 Add explicit named export for `normalizeProxiedToolResult` in `packages/shared/src/index.ts`
- [x] 1.5 Update `apps/cli/package.json` test script to use `node --import tsx --test tests/*.test.mjs`
- [x] 1.6 Fix relative path mappings in root `tsconfig.json` (`./packages/shared/src`) to satisfy TypeScript 7 TS5090

## 2. Verification and Audit

- [x] 2.1 Run `pnpm --filter @mcp_router/electron test` (17/17 passed in 304ms)
- [x] 2.2 Run `pnpm --filter @mcp_router/cli test` (3/3 passed in 513ms)
- [x] 2.3 Run `pnpm run typecheck` across all 6 workspace packages (8/8 successful in 14s)
- [x] 2.4 Author `evidence.md` with verifiable outputs
