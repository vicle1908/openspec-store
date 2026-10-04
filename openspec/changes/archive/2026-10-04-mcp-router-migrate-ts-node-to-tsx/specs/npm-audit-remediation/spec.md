# Spec Delta: npm-audit-remediation

## ADDED Requirements

### Requirement: ts-node Deprecation and tsx Test Runner Migration
Node.js test runners executing TypeScript test suites in monorepos SHALL NOT invoke legacy `ts-node` loaders or registrations, and SHALL utilize `tsx` (via `node --import tsx` or `require("tsx/cjs")`) and `esbuild` for runtime TypeScript transpilation under TypeScript 7 and Node 26.

#### Scenario: execution of electron unit tests with tsx
- **WHEN** `pnpm run test` (`node --test tests/*.test.cjs`) is executed in `apps/electron`
- **THEN** all 17 unit tests execute and pass with status 0 without `ts.sys` undefined errors

#### Scenario: execution of CLI tests with tsx ESM import
- **WHEN** `pnpm run test` (`node --import tsx --test tests/*.test.mjs`) is executed in `apps/cli`
- **THEN** all test suites pass with status 0, resolving workspace packages without loader errors

### Requirement: TypeScript 7 Relative Path Mapping Strictness
When `compilerOptions.baseUrl` is omitted from `tsconfig.json` files operating under TypeScript 7, all path values defined in `paths` mappings SHALL explicitly begin with a relative prefix (`./` or `../`), adhering to TS5090 validation rules.

#### Scenario: tsc compilation without TS5090 errors
- **WHEN** `tsc --build` is executed across workspace packages
- **THEN** compiler path resolution completes without emitting TS5090 non-relative path errors
