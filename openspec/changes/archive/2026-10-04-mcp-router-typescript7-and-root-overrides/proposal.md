# Proposal: MCP Router Toolchain Alignment and Root Manifest Security Overrides

## Why
While the root workspace of `platform/mcp-router` had upgraded to TypeScript 7, its `apps/electron` workspace maintained legacy TypeScript 5.9 and Playwright 1.57 versions, along with obsolete `baseUrl` and deprecated `moduleResolution=node10` configurations. Additionally, workstation root manifest (`/Users/androidteam/package.json`) required security overrides (`axios`, `form-data`, `js-yaml`, `yaml`) to eliminate transitive vulnerabilities introduced by the newly added Bruno CLI without breaking existing Newman test runs.

## What Changes
- **MCP Router Platform (`platform/mcp-router`)**:
  - Aligned `apps/electron` to `typescript@^7.0.2` and `@playwright/test@^1.63.0`.
  - Refactored `tsconfig.json` and `apps/electron/tsconfig.json` to eliminate obsolete `baseUrl` options and set `moduleResolution: "bundler"`.
  - Added ambient CSS module declarations (`apps/electron/src/types/css.d.ts`) to satisfy TypeScript 7 bundler-mode side-effect import checks.
  - Rebuilt native modules (`argon2`, `better-sqlite3`) and verified turbo typecheck across all 6 workspace packages (8/8 successful).
- **Workstation Root Manifest (`/Users/androidteam/package.json`)**:
  - Injected targeted security overrides for `axios` (`^1.20.0`), `form-data` (`4.0.6`), `js-yaml` (`>=4.3.2`), and `yaml` (`>=2.8.3`), eliminating 7 transitive CVEs from `@usebruno/cli`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Extend contracts to govern Electron workspace TypeScript 7 and Playwright 1.63 alignment, bundler-mode ambient CSS typing, and root manifest transitive overrides for Git-native API testing tooling.

## Non-Goals
- Migrating `better-sqlite3` to pure WASM (native C++ bindings remain optimal for Electron SQLite performance).
- Modifying `mcp-router`'s uncommitted graphify report artifacts.

## Affected Ownership Boundaries
- `platform/mcp-router`
- `/Users/androidteam/package.json`
