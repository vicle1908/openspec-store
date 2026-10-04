# Proposal: Modernize Toolchain and Major Dependencies

## Why
Workspace packages and CLI runtimes accumulated dependency drift, unpatched peer conflicts, and legacy compiler constraints across `/Users/androidteam/package.json`, `tdt/realtime/frontend`, `ascend/tmz-case-challenge`, and `platform/prime-agent`. Upgrading to latest major compiler and library releases—including TypeScript 7, jsdom 30, Jest-DOM 7, Commander 15, Newman 6.2.2, and syncing Prime Agent with upstream Rust architecture—ensures supply-chain security, eliminates obsolete configuration keys (`baseUrl`), and unifies global runtime tooling.

## What Changes
- **Workstation Root Tooling (`/Users/androidteam/package.json`)**:
  - Upgraded `newman` to `^6.2.2` (major bump), eliminating 7 CVEs (`semver`, `tough-cookie`, `word-wrap`, `postman-request`, `postman-collection-transformer`) and fixing the upstream `uuid/v4` export runtime crash.
  - Upgraded security overrides: `fast-uri` to `4.2.1`, `ip-address` to `10.7.3`, `hono` to `4.13.12`.
  - Retained `@faker-js/faker@5.5.3` within Postman Collection to preserve dynamic variable generator runtime compatibility (`faker.address.city`).
- **Ascend Toolkit (`ascend/tmz-case-challenge`)**:
  - Upgraded `commander` to `^15.0.0` (major bump) and `jszip` to `^3.10.2`.
  - Verified CLI option parsers and reports (`pptx-tools info` and `validate`).
- **Realtime Frontend Platform (`tdt/realtime/frontend`)**:
  - **BREAKING (Compiler)**: Upgraded `typescript` to `^7.0.2` (major bump). Removed removed option `baseUrl: "."` from `tsconfig.json` and `tsconfig.test.json` while maintaining module alias paths (`@/*`).
  - Upgraded `jsdom` to `^30.1.1` (major bump).
  - Upgraded `@testing-library/jest-dom` to `^7.0.1` (major bump).
  - Upgraded `eslint-plugin-react-refresh` to `^0.5.7` and `lucide-react` to `^1.51.0`.
  - Synchronized `pnpm.overrides` with root `overrides` (`js-yaml`, `dompurify`, `brace-expansion`, `sharp`, `csv-parse`).
  - Verified `tsc --noEmit` (0 errors), `vite build` (clean bundle in 1.44s), and vitest suites.
- **Prime Agent Architecture & Runtime (`platform/prime-agent` & Global CLI)**:
  - Preserved local TypeScript modifications in branch `backup/ts-custom-patches` and archived working tree files into `.git/ts-working-tree-backup/`.
  - Synchronized repository `main` cleanly with upstream remote `origin/main` (`2b962da26`, Rust engine workspace v0.9.8).
  - Upgraded global CLI `/opt/homebrew/lib/prime-agent` to official release `v0.9.8` with Mach-O binary and bundle permissions verified.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Extend requirements to mandate TypeScript 7 compiler option normalization (removal of `baseUrl`), testing library major updates (`jsdom@30`, `jest-dom@7`), Commander 15 CLI alignment, Newman 6.2.2 supply chain remediation, and upstream Rust runtime migration synchronization.

## Non-Goals
- Downgrading `newman` back to `5.3.2` via `npm audit fix --force`.
- Overriding `@faker-js/faker` to v10+ in Postman Collection runtime (which causes fatal `city` property access crashes).
- Upgrading `@babel/preset-*` to 8.0.x in `realtime/frontend` while `@vitejs/plugin-react` maintains peer dependencies on `@babel/core@^7.0.0`.
- Arbitrary manual edits to upstream `braces` or `node-forge` where upstream maintainers have not cut patched npm releases.

## Affected Ownership Boundaries
- **Workstation CLI Tooling**: `/Users/androidteam`
- **Partner Services**: `ascend/tmz-case-challenge`
- **TDT Platform Realtime**: `tdt/realtime/frontend`
- **Platform Engineering**: `platform/prime-agent` and `/opt/homebrew/lib/prime-agent`
