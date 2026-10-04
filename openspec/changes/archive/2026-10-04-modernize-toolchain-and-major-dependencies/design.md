# Design: Modernize Toolchain and Major Dependencies

## Context
See `proposal.md` for background. The workspace coordinates multiple package managers (npm, pnpm, uv) across distinct repositories (`tdt/realtime/frontend`, `ascend/tmz-case-challenge`, `platform/prime-agent`, and workstation root `/Users/androidteam`). Previous updates pinned certain dependencies to avoid breaking changes, but recent upstream releases of TypeScript 7, jsdom 30, Jest-DOM 7, Commander 15, and the Rust migration of Prime Agent enable significant modernization.

## Goals / Non-Goals

**Goals:**
- Eliminate obsolete `baseUrl` options in frontend `tsconfig` files to achieve clean TypeScript 7 compatibility.
- Upgrade testing infrastructure (`jsdom@30`, `@testing-library/jest-dom@7`) and verify DOM test executions.
- Safely synchronize `platform/prime-agent` with upstream remote (`origin/main`), preserving prior local TypeScript work in a dedicated branch.
- Upgrade global `prime-agent` to `v0.9.8` using official distribution binaries without breaking Homebrew symlinks.
- Modernize `ascend/tmz-case-challenge` dependencies to Commander 15 and jszip 3.10.2.

**Non-Goals:**
- Upgrading Babel to v8 while `@vitejs/plugin-react` peer dependencies conflict with `@babel/core@8`.
- Forcing `@faker-js/faker` upgrades in Newman/Postman Collection runtime where legacy `faker.address.*` APIs are required.
- Building the Rust workspace of `prime-agent` locally from source (pre-built official R2 Mach-O tarball is utilized).

## Decisions

### Decision 1: Remove `baseUrl` in favor of strict `paths` in TypeScript 7
- **Rationale**: In TypeScript 7, `compilerOptions.baseUrl` has been removed (TS5102 error). Modern bundlers (Vite/Rolldown) and TypeScript resolve alias paths directly from `"paths": { "@/*": ["./src/*"] }` relative to the tsconfig file location.
- **Alternative considered**: Pinning TypeScript to 5.9.3. Rejected because TypeScript 7 brings significant performance improvements and modern syntax support.

### Decision 2: Local TS Branch Preservation for Prime Agent
- **Rationale**: Before resetting `platform/prime-agent` to `origin/main` (which deleted `package.json` in favor of Cargo crates), all local commits and files were committed to `backup/ts-custom-patches`, and untracked TypeScript artifacts were moved to `.git/ts-working-tree-backup/`.
- **Alternative considered**: Discarding all prior local commits without backup. Rejected to prevent loss of custom provider extensions and bundling configs.

### Decision 3: Official Release Binary Deployment for Global CLI
- **Rationale**: Prime Agent upstream publishes pre-compiled native Mach-O ARM64 binaries and npm packages to an R2 channel (`https://pub-728493de92a943e2a9b2d17b4719f318.r2.dev`). Staging `prime-agent-0.9.8.tgz` into `/opt/homebrew/lib/prime-agent` updates the runtime to `v0.9.8` while preserving existing `/opt/homebrew/bin/prime-agent` symlink architecture.

## Risks / Trade-offs

- **Risk: Postman Faker runtime breaks**:
  - *Mitigation*: Strictly maintained `@faker-js/faker@5.5.3` within Postman Collection runtime; avoided conflicting overrides in `/Users/androidteam/package.json`.
- **Risk: Toolchain mismatch between local repo and global binary**:
  - *Mitigation*: Both the `platform/prime-agent` repository on `main` and the global CLI binary `/opt/homebrew/bin/prime-agent` are synchronized to version `0.9.8`.
