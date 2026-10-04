# Tasks

## 1. Workstation Root Manifest Modernization

- [x] 1.1 Upgrade Newman to ^6.2.2 in `/Users/androidteam/package.json`, eliminating legacy Newman v4/v5 CVEs and fixing `uuid/v4` export runtime crash
- [x] 1.2 Update security overrides for `fast-uri` to 4.2.1, `ip-address` to 10.7.3, and `hono` to 4.13.12 while preserving `@faker-js/faker@5.5.3` for Postman runtime
- [x] 1.3 Verify Newman execution with `htmlextra` reporter against sample collection

## 2. Ascend Presentation Toolkit Modernization

- [x] 2.1 Upgrade `commander` to ^15.0.0 and `jszip` to ^3.10.2 in `ascend/tmz-case-challenge/package.json`
- [x] 2.2 Verify CLI command parsing and toolkit info reports via `pptx-tools info` and `validate`
- [x] 2.3 Verify 0 vulnerabilities reported by `npm audit` in `ascend/tmz-case-challenge`

## 3. Realtime Frontend Toolchain and Test Stack Upgrades

- [x] 3.1 Upgrade `typescript` to ^7.0.2 in `tdt/realtime/frontend/package.json`
- [x] 3.2 Refactor `tsconfig.json` and `tsconfig.test.json` to remove deprecated `compilerOptions.baseUrl`
- [x] 3.3 Upgrade `jsdom` to ^30.1.1, `@testing-library/jest-dom` to ^7.0.1, `eslint-plugin-react-refresh` to ^0.5.7, and `lucide-react` to ^1.51.0
- [x] 3.4 Synchronize `pnpm.overrides` lockstep with `overrides` (`js-yaml`, `dompurify`, `brace-expansion`, `sharp`, `csv-parse`)
- [x] 3.5 Verify `npm run type-check` (0 errors), `npm run build` (clean Vite/Rolldown production bundle), and Vitest test execution

## 4. Prime Agent Upstream Sync and Global CLI Deployment

- [x] 4.1 Create preservation branch `backup/ts-custom-patches` and archive untracked TypeScript artifacts to `.git/ts-working-tree-backup/`
- [x] 4.2 Reset `platform/prime-agent` `main` branch to upstream `origin/main` commit 2b962da26 (Rust engine workspace v0.9.8)
- [x] 4.3 Stage and deploy official release `v0.9.8` to `/opt/homebrew/lib/prime-agent` and make CLI executable
- [x] 4.4 Verify `/opt/homebrew/bin/prime-agent -v` and `npm list -g --depth=0`

## 5. End-to-End Verification

- [x] 5.1 Run smoke tests across all upgraded repositories and CLI tools
- [x] 5.2 Validate audit reports and unpatched upstream residuals
