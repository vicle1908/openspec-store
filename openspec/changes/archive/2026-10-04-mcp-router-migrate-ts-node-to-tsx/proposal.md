# Proposal: Migrate Legacy ts-node to tsx and esbuild in MCP Router

## Why
Following the TypeScript 7 upgrade, `ts-node` crashed across the `platform/mcp-router` test suites with `TypeError: Cannot read properties of undefined (reading 'fileExists')` due to reliance on removed internal `ts.sys` APIs, while in `apps/cli` `node --loader ts-node/esm` failed to resolve workspace packages. Migrating from unmaintained `ts-node` to `tsx` (powered by esbuild) restores fast test execution, enables sub-millisecond TypeScript transpilation, and ensures full compatibility with TypeScript 7 and Node 26.

## What Changes
- **MCP Router Desktop (`platform/mcp-router/apps/electron`)**:
  - Removed `"ts-node": "^10.9.2"` and installed `"tsx": "^4.23.15"`.
  - Migrated test runner scripts in `security-utils.test.cjs`, `mcp-http-server-auth.test.cjs`, and `token-manager.test.cjs` from `require("ts-node/register/transpile-only")` to `require("tsx/cjs")`.
  - Migrated `service-retirement.test.cjs` from removed runtime compiler API `ts.transpileModule` to `esbuild.transformSync`.
  - Added unit test script `"test": "node --test tests/*.test.cjs"`.
- **MCP Router CLI (`platform/mcp-router/apps/cli`)**:
  - Migrated CLI test script from `node --loader ts-node/esm` to `node --import tsx --test tests/*.test.mjs`.
- **Shared Package (`platform/mcp-router/packages/shared`)**:
  - Added explicit named export for `normalizeProxiedToolResult` in `src/index.ts` to support static Node ESM consumers.
- **Root Manifest (`platform/mcp-router/tsconfig.json`)**:
  - Corrected non-relative path mapping syntax to `./packages/shared/src` to comply with TypeScript 7 TS5090 rules.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Extend requirements to mandate `ts-node` deprecation in favor of `tsx` and `esbuild` for test execution, and require leading relative path notation (`./`) in `paths` mappings when `baseUrl` is omitted under TypeScript 7.

## Non-Goals
- Migrating webpack loaders (`ts-loader`) in this change (scoped strictly to test runners and runtime compilation).

## Affected Ownership Boundaries
- `platform/mcp-router`
