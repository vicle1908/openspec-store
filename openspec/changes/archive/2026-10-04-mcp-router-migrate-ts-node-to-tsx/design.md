# Design: Migrate Legacy ts-node to tsx and esbuild in MCP Router

## Context
See `proposal.md`. `ts-node@10.9.2` is incompatible with TypeScript 7, crashing on startup due to missing `ts.sys.fileExists`. Node's native test runner (`node:test`) requires a modern transpiler to load TypeScript test files.

## Goals / Non-Goals

**Goals:**
- Replace `ts-node` with `tsx` across `apps/electron` and `apps/cli`.
- Replace legacy `ts.transpileModule` with `esbuild.transformSync` in sandbox test execution.
- Fix TS5090 relative path mapping requirement in root `tsconfig.json`.

**Non-Goals:**
- Modifying production webpack build pipeline.

## Decisions

### Decision 1: Use `tsx/cjs` for native node:test compatibility
- `require("tsx/cjs")` registers esbuild hooks transparently, allowing CommonJS test suites to require TypeScript source modules without intermediate compilation files.

### Decision 2: Use `esbuild.transformSync` for runtime string evaluation
- In `service-retirement.test.cjs`, replacing `ts.transpileModule` with `esbuild.transformSync` achieves instant in-memory transpilation into CommonJS for sandbox execution via `vm.runInNewContext`.

### Decision 3: Relative prefix on `paths` mappings
- In TypeScript 7, omitting `baseUrl` turns bare strings in `paths` into syntax errors (`TS5090`). Adding `./` explicitly resolves packages relative to the `tsconfig.json` file location.
