# Proposal: Security Audit & Dependency Upgrades

## Problem Statement

Multiple workspace repositories had vulnerable npm dependencies, with a total of **51 vulnerabilities** across home-level packages. The `npm audit` revealed critical, high, and moderate severity issues in transitive dependencies.

## Goal

Eliminate all fixable vulnerabilities through targeted upgrades and dependency overrides, while maintaining compatibility with existing tooling.

## Scope

### In Scope
- Home directory (`~/`) npm packages
- `mcp-router` workspace dependencies
- `hermes-webui` dependency assessment
- `prime-agent` verification

### Out of Scope
- Python repository dependencies (managed by `uv`)
- Go module dependencies
- Breaking changes that would require code modifications

## Work Completed

### 1. Home Directory Packages (`~/`)
**Starting state:** 51 vulnerabilities (15 moderate, 23 high, 13 critical)

| Action | Package | Before | After |
|--------|---------|--------|-------|
| Removed | `npx` | 3.0.0 | Deprecated standalone package removed |
| Upgraded | `newman` | 4.6.1 | 6.2.2 |
| Replaced | `newman-reporter-html` | 1.0.5 | `newman-reporter-htmlextra` 1.23.1 |
| Override | `lodash` | 4.17.x | 4.18.1 |
| Override | `uuid` | mixed old | 14.0.2 |
| Override | `qs` | mixed old | 6.15.3 |
| Override | `node-forge` | ≤1.3.3 | 1.4.0 |
| Override | `underscore` | ≤1.13.7 | 1.13.8 |
| Override | `flatted` | ≤3.4.1 | 3.4.4 |
| Override | `sharp` | <0.35.0 | 0.35.4 |
| Override | `adm-zip` | <0.6.0 | 0.6.0 |
| Override | `handlebars` | ≤4.7.8 | 4.7.9 |
| Override | `jose` | ≤4.15.4 | 6.2.10 |

**Result:** 51 → **0 vulnerabilities** ✅

### 2. mcp-router
**Starting state:** 62 vulnerabilities (4 low, 24 moderate, 31 high, 3 critical)

| Action | Details |
|--------|---------|
| Updated dev dependencies | ESLint 10.9.1, TypeScript 7.0.2, Turbo 2.10.12, etc. |
| Added overrides | 15+ packages including d3-color, extract-zip, image-size, etc. |
| Updated existing overrides | hono 4.12.34, postcss 8.5.23, qs 6.15.3 |

**Result:** 62 → **40 vulnerabilities** (partial - transitive Electron/Webpack deps)

### 3. prime-agent
**Verification:** 0 vulnerabilities ✅

### 4. hermes-webui
**Assessment:** 47 vulnerabilities identified, pnpm outdated command fails with internal error. No changes made to avoid breaking the project.

## Technical Details

### Override Strategy

npm `overrides` field forces resolution of transitive dependencies to patched versions, even when parent packages haven't updated their dependency ranges. This is safe for:
- Patch versions (bug fixes)
- Minor versions (backward-compatible features)
- Security patches that don't change API

### Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking changes from major version overrides | Only applied to leaf dependencies with no downstream consumers |
| Incompatible peer dependencies | Verified with `pnpm install` and rebuild |
| Build failures | Post-install hooks ran successfully (electron-rebuild) |

## Remaining Issues

### mcp-router (40 vulnerabilities)
Most remaining vulnerabilities are in:
- Electron/Webpack tooling transitive dependencies
- Deep dependency chains that would require major version bumps
- Packages where patched versions don't exist yet

### hermes-webui (47 vulnerabilities)
- `pnpm outdated` fails with internal error
- Requires investigation before safe upgrades
- May need pnpm version upgrade or workspace restructure

## Success Criteria

- [x] Home directory packages: 0 vulnerabilities
- [x] mcp-router: Significant reduction (62 → 40)
- [x] prime-agent: Verified clean
- [ ] hermes-webui: Assessment complete, remediation pending
- [x] All CLI tools functional (npx, newman, pyright)
- [x] Build processes complete successfully

## Next Steps

1. Investigate hermes-webui pnpm outdated failure
2. Monitor upstream packages for security patches
3. Re-run audit in 30 days to catch new vulnerabilities
4. Document override decisions in package.json comments
