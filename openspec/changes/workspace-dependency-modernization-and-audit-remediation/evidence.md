# Verification Evidence: workspace-dependency-modernization-and-audit-remediation

**Date**: 2026-10-03  
**Status**: Verified & Validated  

---

## 1. Fresh-Process Audit & Verification Summary

| Target | Tool | Observed Status | Exit Code | Verification Gates & Evidence |
|---|---|---|---|---|
| `/Users/androidteam` | `npm audit` / `npm outdated` | Clean outdated; 10 high unpatched residuals | 1 | `newman@6.2.2`, `newman-reporter-htmlextra@1.23.1`, `sharp@0.35.5`, `jose@6.2.12`, `csv-parse@7.0.3`. CLI smoke tests pass (exit 0). |
| `platform/mcp-router` | `pnpm audit` | 9 high unpatched residuals | 1 | `pnpm --filter @mcp_router/electron run typecheck` (exit 0); `pnpm run build` (exit 0 across 6 packages). Zero `package-lock.json`. |
| `tdt/realtime/frontend` | `npm audit` | 4 high unpatched residuals (`http-cache-semantics`) | 1 | `npm run type-check` (exit 0); Vitest property test (exit 0, 6 passed); `npm run build` (exit 0). Zero `pnpm-lock.yaml`. |
| `platform/prime-agent` | `npm audit` | 11 high unpatched residuals | 1 | `npm run check` (Biome 0 errors, tsgo clean, installer check pass, browser smoke pass - exit 0). Extension runtime deduplicated. |

---

## 2. Lockfile Hygiene Invariants

- **`mcp-router`**: Strictly pnpm-managed. Verified zero `package-lock.json` in repository.
- **`realtime/frontend`**: Strictly npm-managed. Verified zero `pnpm-lock.yaml` in repository. Overrides duplicated in `overrides` and `pnpm.overrides`.

---

## 3. Unpatched Upstream Residuals Inventory

1. **`http-cache-semantics <=4.2.0`** (GHSA-ch52-4w7c-c8xp)
   - Patched: `<0.0.0` (no patch exists)
   - Path: `ably -> got -> cacheable-request -> http-cache-semantics`
2. **`extract-zip <=2.0.1`** (GHSA-jmr9-qjv8-65gv, GHSA-7pqw-9j4j-h8q3)
   - Patched: `<0.0.0` (no patch exists)
   - Path: `@electron-forge/cli -> @electron-forge/core -> @electron/packager -> extract-zip`
3. **`node-forge <=1.4.0`** (GHSA-86w9-cpqp-85rv)
   - Patched: `<0.0.0` (no patch exists)
   - Path: `@anthropic-ai/sandbox-runtime -> node-forge`, `postman-runtime -> node-forge`
4. **`basic-ftp <=6.2.0`** (GHSA-c475-qrg2-pj4r)
   - Patched: `<0.0.0` (no patch exists)
   - Path: `proxy-agent -> pac-proxy-agent -> get-uri -> basic-ftp`
5. **`braces <=3.0.3`** (GHSA-vfj7-8cjw-p6xm)
   - Patched: `<0.0.0` (no patch exists in v3)
   - Path: `shx -> shelljs -> fast-glob -> micromatch -> braces`
