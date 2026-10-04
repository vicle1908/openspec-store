# Verification Evidence: Modernize Toolchain and Major Dependencies

## Date: 2026-10-04

### 1. Workstation Root Tooling (`/Users/androidteam/package.json`)

#### 1.1 Newman CLI & HTML Extra Reporter
- **Command**: `/Users/androidteam/node_modules/.bin/newman --version`
- **Output**: `6.2.2` (Exit: 0)
- **Collection Execution**:
  - Test command: `/Users/androidteam/node_modules/.bin/newman run /tmp/smoke-coll.json -r htmlextra --reporter-htmlextra-export /tmp/test-report.html`
  - Result: 0 failures, emitted 44 KB report at `/tmp/test-report.html`.
- **Overrides**:
  - `fast-uri`: `4.2.1` (major bump; validated with `ajv@8.20.0` and `ajv-formats@3.0.1` -> `URI validation: true false`)
  - `ip-address`: `10.7.3`
  - `hono`: `4.13.12`
  - `@faker-js/faker`: retained at `5.5.3` for `postman-collection` compatibility.

### 2. Ascend Presentation Toolkit (`ascend/tmz-case-challenge`)

#### 2.1 Dependencies & Version Verification
- **Manifest**: `commander` (`^15.0.0`), `jszip` (`^3.10.2`)
- **CLI Command**: `node output/pptx-toolkit/cli.js --help`
- **Output**:
  ```
  Usage: pptx-tools [options] [command]
  PPTX manipulation toolkit for consistent formatting and validation
  ```
- **Info Command**: `node output/pptx-toolkit/cli.js info` -> Exited 0 with toolkit summary.
- **Audit Verification**: `npm audit` -> `found 0 vulnerabilities` (Exit: 0).

### 3. Realtime Frontend Platform (`tdt/realtime/frontend`)

#### 3.1 TypeScript 7.0.2 & Configuration Migration
- **Compiler Config**: Removed obsolete `compilerOptions.baseUrl` from `tsconfig.json` and `tsconfig.test.json`.
- **Type Check Command**: `npm run type-check` (`tsc --noEmit`)
- **Result**: 0 errors, passed in 2.34s (Exit: 0).

#### 3.2 Production Bundle Execution
- **Command**: `npm run build` (`tsc && vite build`)
- **Result**: Transformed 2,981 modules, generated production chunks in `dist/assets/`, passed in 1.44s (Exit: 0).

#### 3.3 Test Suite Execution
- **Stack**: `jsdom@^30.1.1`, `@testing-library/jest-dom@^7.0.1`, `vitest@^5.0.3`
- **Focused Execution**:
  - `src/__tests__/smoke.test.ts`: 1/1 passed
  - `src/components/ErrorBoundary/__tests__/ErrorBoundary.test.tsx`: 7/7 passed
  - Total: 8/8 tests passed (Exit: 0).

### 4. Prime Agent Upstream Sync & Global CLI (`platform/prime-agent`)

#### 4.1 Repository Synchronization
- **Preservation Branch**: `backup/ts-custom-patches` (retains local TS commits)
- **Archive Directory**: `.git/ts-working-tree-backup/` (preserves TS node_modules and packages)
- **Upstream Reset**: `git reset --hard origin/main` to commit `2b962da26` (*feat(tui): factory live page with machine diagram highlighting #3290*)
- **Repo State**: `git status` clean, branch `main` in 100% parity with upstream Rust engine workspace.

#### 4.2 Global CLI Deployment
- **Target**: `/opt/homebrew/lib/prime-agent` upgraded to `v0.9.8` from official release payload.
- **Verification**:
  - `/opt/homebrew/bin/prime-agent -v` -> `0.9.8` (Exit: 0)
  - `npm list -g --depth=0` -> `prime-agent@0.9.8 -> ./prime-agent`

### 5. Residual Vulnerability Tracking

| Component | Advisory | Range | First Patched Version | Residual Assessment |
| :--- | :--- | :--- | :--- | :--- |
| `braces` | GHSA-vfj7-8cjw-p6xm | `<=3.0.3` | None | Open upstream PRs #72 & #75 in `micromatch/braces`. Unpatched upstream residual. |
| `node-forge` | GHSA-86w9-cpqp-85rv | `<=1.4.0` | None | Latest tag is `v1.4.0`. No patched release exists. Unpatched upstream residual. |
| `@faker-js/faker` | GHSA-qxc2-j82w-r537 | `<=10.4.0` | 10.5.0 | Required for Postman collection runtime compatibility (`faker.address.*`). `helpers.fake` is uncalled. Safe residual. |
| `http-cache-semantics` | GHSA-ch52-4w7c-c8xp | `<=4.2.0` | None | Transitive in `ably@2.29.0` via `got`. Unpatched upstream residual. |
