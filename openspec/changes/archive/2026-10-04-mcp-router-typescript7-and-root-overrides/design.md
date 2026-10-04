# Design: MCP Router Toolchain Alignment and Root Manifest Security Overrides

## Context
See `proposal.md`. `platform/mcp-router` operates as a pnpm + Turborepo monorepo with 6 packages. The root manifest was previously updated to TypeScript 7, but `apps/electron` had internal mismatches (TypeScript 5.9, Playwright 1.57, `moduleResolution=node10`, `baseUrl=.`).

## Goals / Non-Goals

**Goals:**
- Unify TypeScript across `mcp-router` workspaces to TypeScript 7.0.2.
- Configure `moduleResolution: "bundler"` and remove `baseUrl` in root and electron `tsconfig.json`.
- Provide ambient CSS typing via `apps/electron/src/types/css.d.ts`.
- Eliminate 7 transitive CVEs in workstation root manifest for Bruno CLI via `overrides`.

**Non-Goals:**
- Upgrading Electron major versions beyond 39 in this turn (retains native compatibility with active SQLite schemas).

## Decisions

### Decision 1: Ambient CSS type declarations
- **Rationale**: Under TypeScript 7 bundler resolution, side-effect imports (`import '@xyflow/react/dist/style.css'`) trigger `TS2882` unless typed. Creating an ambient `css.d.ts` inside `src/types/` satisfies TypeScript's compiler while preserving Webpack CSS loader bundling.

### Decision 2: Root overrides for Bruno dependencies
- **Rationale**: `@usebruno/cli` depends on older versions of `axios` and `form-data`. Overriding them to `1.20.0` and `4.0.6` eliminates vulnerabilities without breaking Bruno's CLI execution.
