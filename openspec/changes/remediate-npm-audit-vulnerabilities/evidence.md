# Verification Evidence: remediate-npm-audit-vulnerabilities

**Date**: 2026-09-20  
**Status**: Implementation Verified  

---

## 1. Fresh-Process Audit Summary

| Target | Tool | Observed Outcome | Exit Code | Notes |
|---|---|---|---|---|
| `/Users/androidteam` | `npm audit` | `found 0 vulnerabilities` | 0 | Newman v6 peer alignment resolved all 28 vulnerabilities; `adm-zip` override pinned to `0.6.1`. |
| `~/Developer/mcp-router` | `pnpm audit` | `4 vulnerabilities found (4 high)` | 1 | `smol-toml` and `fflate` resolved; remaining 4 are unpatched upstream residuals. |
| `~/Developer/realtime/frontend` | `npm audit` | `found 0 vulnerabilities` | 0 | `js-yaml`, `fflate`, and `vitest` suite vulnerabilities eliminated. |
| `~/Developer/prime-agent` | `npm audit` | `found 0 vulnerabilities` | 0 | Vitest 4.1.11 bump in workspace packages eliminated `@vitest/mocker` redirect mock vulnerability. |

---

## 2. Lockfile Hygiene Invariants

- **`mcp-router`**: Strictly pnpm-managed. Verified that no `package-lock.json` exists anywhere in the repository tree.
- **`realtime/frontend`**: Strictly npm-managed. Verified that no `pnpm-lock.yaml` exists in `realtime/frontend`.

---

## 3. Unpatched Upstream Residual Advisory Inventory (`mcp-router`)

All 4 remaining vulnerabilities in `mcp-router` originate from deep build-time dependencies within `@electron-forge` packages and have `patched: <0.0.0` declared upstream with no available security release:

1. **`image-size`**
   - **Severity**: High
   - **Title**: `image-size: ICNS parser allows denial of service through an infinite loop`
   - **Vulnerable Versions**: `<=2.0.2`
   - **Patched Versions**: `<0.0.0` (no patch available)
   - **Advisory URL**: https://github.com/advisories/GHSA-w3rx-r6r6-pgpr
   - **Dependency Path**: `apps__electron > @electron-forge/maker-dmg > electron-installer-dmg > appdmg > image-size`

2. **`image-size`**
   - **Severity**: High
   - **Title**: `image-size: JXL and HEIF parsers allow denial of service through infinite loops`
   - **Vulnerable Versions**: `<=2.0.2`
   - **Patched Versions**: `<0.0.0` (no patch available)
   - **Advisory URL**: https://github.com/advisories/GHSA-5p2g-fcmc-qvqq
   - **Dependency Path**: `apps__electron > @electron-forge/maker-dmg > electron-installer-dmg > appdmg > image-size`

3. **`extract-zip`**
   - **Severity**: High
   - **Title**: `extract-zip unvalidated symlink path traversal`
   - **Vulnerable Versions**: `<=2.0.1`
   - **Patched Versions**: `<0.0.0` (no patch available)
   - **Advisory URL**: https://github.com/advisories/GHSA-jmr9-qjv8-65gv
   - **Dependency Path**: `apps__electron > @electron-forge/cli > @electron-forge/core > @electron/packager > extract-zip`

4. **`extract-zip`**
   - **Severity**: High
   - **Title**: `extract-zip allows arbitrary file writes through symlink archive entries`
   - **Vulnerable Versions**: `<=2.0.1`
   - **Patched Versions**: `<0.0.0` (no patch available)
   - **Advisory URL**: https://github.com/advisories/GHSA-7pqw-9j4j-h8q3
   - **Dependency Path**: `apps__electron > @electron-forge/cli > @electron-forge/core > @electron/packager > extract-zip`

---

## 4. Build and Test Verification

- **`mcp-router`**:
  - `pnpm --filter @mcp_router/electron run typecheck` passed (exit code 0).
  - `pnpm run build` passed across all packages (`@mcp_router/cli`, `@mcp_router/electron`, `@mcp_router/remote-api-types`, `@mcp_router/shared`, `@mcp_router/ui` - exit code 0).
- **`realtime/frontend`**:
  - `npm run type-check` (`tsc --noEmit`) passed (exit code 0).
  - `npx vitest run src/components/Analytics/__tests__/CorrelationCoefficientDisplay.property.test.tsx` passed (6 tests passed, exit code 0).
- **`prime-agent`**:
  - `npm run check` passed (`biome check`, `tsgo --noEmit`, installer render check, browser smoke check - exit code 0).
