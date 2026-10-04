# Tasks

## 1. MCP Router Toolchain Modernization

- [x] 1.1 Upgrade `typescript` to `^7.0.2` and `playwright` to `^1.63.0` in `platform/mcp-router/apps/electron/package.json`
- [x] 1.2 Refactor `tsconfig.json` and `apps/electron/tsconfig.json` to remove `baseUrl` and set `moduleResolution: "bundler"`
- [x] 1.3 Add ambient declaration `apps/electron/src/types/css.d.ts` for CSS side-effect imports
- [x] 1.4 Run `pnpm install` to update `pnpm-lock.yaml` and execute `electron-rebuild` for native modules
- [x] 1.5 Verify `pnpm run typecheck` (8/8 packages passed) and `pnpm run build`

## 2. Workstation Root Manifest Overrides Hardening

- [x] 2.1 Add security overrides for `axios` (`^1.20.0`), `form-data` (`4.0.6`), `js-yaml` (`>=4.3.2`), and `yaml` (`>=2.8.3`) in `/Users/androidteam/package.json`
- [x] 2.2 Run `npm install` and verify `bru --version` (4.2.0) and `newman --version` (6.2.2)
- [x] 2.3 Verify `npm audit` reports zero Bruno-related CVEs

## 3. Evidence and Validation

- [x] 3.1 Author `evidence.md` with execution outputs
- [x] 3.2 Validate change via strict OpenSpec validator
